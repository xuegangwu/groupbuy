# Solaripple 服务器架构设计

## 概述

本文档定义 Solaripple 三台服务器的架构、生产部署流程和安全加固方案。

---

## 服务器角色分工

| 服务器 | IP | 角色 | 主要服务 |
|--------|-----|------|---------|
| **china** | 47.100.20.52 | 🇨🇳 中国区生产服务器 | nginx + SSL、ems 后端 API、SSL 证书服务 |
| **us** | 47.90.138.136 | 🇺🇸 海外节点 / CDN | 前端静态文件、ripple-enos |
| **ali-enos** | 121.43.69.200 | 🧪 预发布 / 测试环境 | staging API、测试前端 |

---

## 架构拓扑图

```
🌏 internet
     │
     ▼
┌─────────────────────────────────────────┐
│           china (47.100.20.52)           │
│              🇨🇳 生产环境                  │
│                                          │
│  443 → nginx (enos.solaripple.com SSL)  │
│         ├── /api → localhost:3001       │
│         │       (ems-work/server)        │
│         └── /     → us:3000 (静态文件)   │
│                                          │
│  3001 → ems-work/server (Node.js)        │
│   5000 → guangchu (Flask) [可选]          │
│                                          │
│  /var/www/ssl/  (Let's Encrypt 证书)     │
└─────────────────────────────────────────┘
         │
         │ 前端资源请求
         ▼
┌─────────────────────────────────────────┐
│             us (47.90.138.136)            │
│            🇺🇸 海外 CDN / 静态服务器        │
│                                          │
│  3000 → nginx (静态文件服务)              │
│         └── ems-work/client              │
│         └── ripple-enos (备选)           │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│        ali-enos (121.43.69.200)          │
│              🧪 预发布环境                 │
│                                          │
│  nginx → staging.enos.solaripple.com     │
│         └── /api → staging server        │
│         └── /     → 预发布前端            │
│                                          │
│  3001 → ems-work/server (staging)        │
│  8080 → 预发布前端静态文件                 │
└─────────────────────────────────────────┘
```

---

## 服务器目录结构

### china 生产服务器

```bash
/var/www/
├── ems/                    # ems-work 主项目
│   ├── client/             # 前端构建产物
│   │   ├── index.html
│   │   └── assets/
│   └── server/             # 后端 Node.js
│       ├── dist/           # 编译后的后端代码
│       └── package.json
├── ssl/                    # SSL 证书（Let's Encrypt）
│   ├── enos.crt
│   └── enos.key
└── nginx/
    └── enos.solaripple.com.conf
```

### us 海外节点

```bash
/var/www/
├── static/                 # 前端静态文件
│   └── ems/
└── nginx.conf
```

### ali-enos 预发布环境

```bash
/var/www/
├── ems-staging/
│   ├── client/
│   └── server/
```

---

## 端口分配

| 端口 | 服务 | 归属服务器 |
|------|------|-----------|
| 80 | HTTP 重定向到 443 | china |
| 443 | nginx (HTTPS) | china |
| 3001 | ems-work/server (Node.js) | china |
| 5000 | guangchu (Flask) | china |
| 3000 | 静态文件服务 | us |
| 3001 | ems-work/server (staging) | ali-enos |

---

## 部署流程

### GitHub Actions 自动部署

```
开发者 push 代码
       │
       ▼
GitHub Actions (ci.yml)
       │
       ├────→ 🇨🇳 china:3001  (ssh + pm2 restart)
       │
       └────→ 🇺🇸 us:3000     (ssh + rsync 同步静态文件)
```

### 手动部署命令（备选）

**部署后端（china）：**
```bash
cd /var/www/ems/server
git pull origin main
npm install
npm run build
pm2 restart ems-server
```

**部署前端（us）：**
```bash
cd /var/www/static/ems
git pull origin main
# 或通过 CI 自动同步构建产物
```

---

## 安全加固清单

### SSH 安全配置

- [x] 禁用密码登录（仅密钥认证）
- [x] 禁止 root 直接登录
- [x] 限制 SSH 监听 IP（仅 0.0.0.0 或指定 IP）
- [ ] 启用 fail2ban 防暴力破解
- [ ] 配置 UFW 防火墙规则

### 防火墙规则（UFW）

```bash
# 允许 SSH（密钥认证后）
ufw allow 22/tcp

# 允许 HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# 允许特定端口（仅业务需要）
ufw allow 3001/tcp   # china 后端
ufw allow 3000/tcp   # us 前端

# 启用防火墙
ufw enable
```

### fail2ban 配置

```bash
# 安装
apt install fail2ban -y

# 配置 /etc/fail2ban/jail.local
[sshd]
enabled = true
port = 22
maxretry = 5
bantime = 3600
findtime = 600
```

---

## 环境变量配置

### ems-work/server (.env)

```bash
NODE_ENV=production
PORT=3001
DATABASE_URL=postgres://user:pass@localhost:5432/ems
JWT_SECRET=your-secret-key-here
CORS_ORIGIN=https://enos.solaripple.com
```

### nginx 配置片段

```nginx
server {
    listen 443 ssl;
    server_name enos.solaripple.com;

    ssl_certificate /var/www/ssl/enos.crt;
    ssl_certificate_key /var/www/ssl/enos.key;

    location /api/ {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location / {
        proxy_pass http://47.90.138.136:3000;
    }
}
```

---

## PM2 进程管理

```bash
# 启动服务
pm2 start dist/index.js --name ems-server

# 查看状态
pm2 status

# 查看日志
pm2 logs ems-server

# 重启
pm2 restart ems-server

# 保存进程列表（开机自启）
pm2 save
pm2 startup
```

---

## SSL 证书（Let's Encrypt）

```bash
# 安装 certbot
apt install certbot python3-certbot-nginx -y

# 申请证书
certbot --nginx -d enos.solaripple.com

# 自动续期
certbot renew --dry-run
```

---

## 监控与日志

### 日志路径

```bash
/var/log/nginx/           # nginx 访问日志
/var/log/auth.log          # SSH 登录日志
~/.pm2/logs/               # PM2 应用日志
```

### 建议监控项

- [ ] 服务器 CPU / 内存 / 磁盘使用率
- [ ] nginx 连接数 / 请求率
- [ ] 后端 API 响应时间
- [ ] SSL 证书过期时间
- [ ] SSH 登录失败尝试（fail2ban）

---

## 备份策略

- [ ] 数据库定期备份（如果有 PostgreSQL）
- [ ] 代码目录 `/var/www/` 定期备份
- [ ] SSL 证书目录 `/var/www/ssl/` 定期备份
- [ ] 配置文件 `/etc/nginx/` 备份

---

## 版本历史

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-03-31 | v1.0 | 初始架构设计 |

