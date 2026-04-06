# TOOLS.md - Local Notes

## 🌐 Solaripple 项目工作流

### 修改服务器 → 备份到 GitHub 标准流程

**solaripple.com 静态首页**（/usr/share/nginx/html/）
```bash
# 1. 服务器修改完成后，本地同步
rsync -e "ssh -i ~/clawd/rippleware/keys/solaripple.pem -o StrictHostKeyChecking=no" -av --exclude='.bak' root@47.100.20.52:/usr/share/nginx/html/ ~/solaripple-web/
# 2. 提交
cd ~/solaripple-web && git add -A && git commit -m "描述" && git push origin main
# 3. 如果要部署到服务器（仅静态文件）
rsync -e "ssh ..." -av --exclude='.bak' ~/solaripple-web/ root@47.100.20.52:/usr/share/nginx/html/
```

**enos.solaripple.com**（React SPA，代码在 ~/clawd/ems-work/）
```bash
cd ~/clawd/ems-work && git add -A && git commit -m "描述" && git push origin main
# 然后构建部署（见下方部署脚本）
```

**groupbuy**（~/groupbuy/）
```bash
cd ~/groupbuy && git add -A && git commit -m "描述" && git push origin main
```

### GitHub 仓库汇总
| 项目 | 仓库 | 本地目录 |
|---|---|---|
| solaripple.com 静态站 | xuegangwu/solaripple | ~/solaripple-web |
| enos.solaripple.com | xuegangwu/ems | ~/clawd/ems-work |
| groupbuy | xuegangwu/groupbuy | ~/groupbuy |

### 部署脚本
```bash
# 部署 solaripple.com（静态首页）
./deploy-solaripple.sh

# 部署 enos（React SPA，需要先构建）
cd ~/clawd/ems-work/client && npm run build && cd .. && ./deploy-enos.sh
```

---



Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
