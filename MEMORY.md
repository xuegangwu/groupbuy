# MEMORY.md — 长期记忆

> 最后更新：2026-04-04（Phase 2 Week 2）

---

## 关于伍学纲（Wu Xuegang）

- **称呼**：伍学纲，或简称"学纲"
- **时区**：Asia/Shanghai（GMT+8）
- **沟通渠道**：飞书（Feishu）

---

## 三个公司/项目 + 对应服务器

| 项目 | 服务器 | IP | SSH密钥 | 用途 |
|:---|:---|:---|:---|:---|
| **Solaripple** | solaripple | 47.100.20.52 | solaripple.pem | EnOS数字孪生平台 + 公司官网 |
| **Rippleware** | rippleware | 121.43.69.200 | rippleware.pem | 跨境SD-WAN网络解决方案 |
| **Rippleclaw** | rippleclaw | 47.90.138.136 | rippleclaw.pem | 光储龙虾项目（连不上，待修复）|

### SSH配置
- Host配置已写入 `~/.ssh/config.d/rippleware`
- 密钥保存于 `~/clawd/rippleware/keys/`

---

## Solaripple — 工商业光储

**产品**：Ripple EnOS数字孪生平台
- EMS监控运维
- AI调度优化（LSTM/Prophet预测）
- VPP虚拟电厂交易
- 数字孪生3D可视化

**代码位置**：`~/clawd/ems-work/`

**网站结构（2026-04-01 新上线）**：
- **solaripple.com** / **www.solaripple.com** → 公司介绍首页（静态HTML，响应式）
- **enos.solaripple.com** → EnOS数字孪生平台（React SPA，数字孪生+能量流+VPP面板）
- nginx配置：`/etc/nginx/sites-enabled/default`（多server_name）
- 公司名：光之涟漪
- 前端：`client/`（React + TypeScript + Three.js）
- 后端：`server/`（Node.js + MongoDB）
- 架构：monorepo（npm workspaces）

**本地开发环境**：
- 前端：http://localhost:3000
- 后端：http://localhost:8080

**今日Phase 1进展**（2026-04-01）：
- ✅ 安装了Three.js + React Three Fiber
- ✅ 创建了3D组件：Building, SolarArray, BatteryCabinet, ChargingStation
- ✅ 数字孪生页面支持3D/能量流双视图切换
- ✅ 前后端完整部署到 47.100.20.52
- ✅ 公司首页重构（solaripple.com 静态 + enos.solaripple.com SPA）
- ✅ SSL证书（solaripple.com + www + enos）
- ✅ 数字孪生：能量流CSS动画、VPP面板、响应式、Error Boundary
- ⚠️ 3D Tab移动端黑屏 → SMIL→CSS动画修复（已禁用3D Tab）
- ⚠️ 数字溢出 → precision={0} + toLocaleString()修复

**Phase 2 Week 2 成果**（2026-04-04）：
- ✅ SOC感知调度（储能充放电约束：上限95%，下限20%，4.8MWh）
- ✅ 收益测算（AI调度 vs 无优化基准对比，日/月/年预估）
- ✅ 峰谷套利 + 削峰收益 + 碳减排量分别统计
- ✅ AIPrediction页面：收益汇总卡片 + SOC + 收益列 + 调度明细表
- 后端：calcRevenue() + makeDispatch SOC约束版
- 模型版本：LSTM-v2.0-solar-soc

**Phase 2 Week 1 成果**（2026-04-04）：
- ✅ LSTM光伏预测（/api/predict/solar，辐照度模型，bell curve 6am-6pm）
- ✅ 三合一联合预测（/api/predict/three-in-one：光伏+负荷+电价+dispatch）
- ✅ AIPrediction页面：三合一联合图表 + 3列独立图表
- ✅ DigitalTwin VPP面板：新增AI调度Tab（懒加载dispatch建议）
- 3个LSTM模型（load/price/solar）同时训练，约30秒冷启动

**升级路线**（14周）：
- Phase 1（4周）：Three.js 3D场景 ← ✅ 完成
- Phase 2（3周）：光伏LSTM预测 + 负荷预测 ← 🚧 Week 2完成，待TDengine数据接入
- Phase 3（4周）：AI调度引擎 + 削峰填谷
- Phase 4（3周）：VPP市场交易

---

## Rippleware — 跨境SD-WAN

**产品**：七云网络SD-WAN + AI运维
- 核心差异化：AI-Native运维
- 渠道合作：理光香港（MOU已签）
- Pre-A融资中（100万美元目标）

**代码位置**：`~/clawd/rippleware/`
- `www/index.html` — 官网Demo（纯静态HTML/CSS/JS）
- `01-05_*.md` — 商业计划、分析、风险评估等
- `数字孪生平台技术方案_v1.0.md`
- `ENOS_UPGRADE_ROADMAP.md`

**部署**：
- 服务器：121.43.69.200 (rippleware)
- 已部署：http://121.43.69.200/
- ICP备案问题待解决

**待完成**：
- GitHub Pages部署（rippleware.github.io）
- DNS配置 + SSL证书
- 域名：rippleware.com

---

## Rippleclaw — 光储龙虾

**产品**：光储龙虾项目（具体定位待了解）

### Solaripple 服务器 (47.100.20.52)

**部署完成** (2026-04-01):
- solaripple.com + www → /usr/share/nginx/html/ (公司首页)
- enos.solaripple.com → /var/www/enos/ (React SPA)
- 后端：PM2 `solaripple-api` 在 8080
- SSL：Let's Encrypt ECDSA（已覆盖 solaripple.com + www + enos.solaripple.com）
- gzip：已开启
- Nginx：/etc/nginx/sites-enabled/default

---

## Rippleclaw — 光储龙虾

**服务器**：47.90.138.136 (rippleclaw)
- **当前状态**：❌ 端口22连接超时
- 需要登录阿里云控制台检查

---

## 重要决策记录

### 2026-04-01

1. **确定三个项目完整架构**
2. **Solaripple**：继续Phase 1的EnOS 3D升级
3. **Rippleware**：官网已部署到121.43.69.200
4. **Rippleclaw**：服务器连不上，待修复

---

## 工作习惯

- 伍学纲偏好简短指令，直接执行
- 每次对话结束自动保存记忆
- 服务器信息、密钥、项目进展都要记住

## ⚠️ 部署流程（重要）

**每次部署前必须先完成 GitHub 同步：**
1. `git add -A`
2. `git commit -m "描述"`
3. `git push origin main`
4. 确认推送成功后再执行部署

步骤：源码修改 → GitHub 提交 → 构建 → 部署到服务器

---

*每次对话结束后更新此文件和当日memory/文件。*
