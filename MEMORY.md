# MEMORY.md — 长期记忆

> 最后更新：2026-04-01

---

## 关于伍学纲（Wu Xuegang）

- **称呼**：伍学纲，或简称"学纲"
- **时区**：Asia/Shanghai（GMT+8）
- **沟通渠道**：飞书（Feishu）

---

## 三个公司/项目 + 对应服务器

| 项目 | 服务器 | IP | SSH密钥 | 用途 |
|:---|:---|:---|:---|:---|
| **Solaripple** | solaripple | 47.100.20.52 | solaripple.pem | 工商业光储投资/运维/交易，EnOS平台 |
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
- 前端：`client/`（React + TypeScript + Three.js）
- 后端：`server/`（Node.js + MongoDB）
- 架构：monorepo（npm workspaces）

**本地开发环境**：
- 前端：http://localhost:3000
- 后端：http://localhost:8080

**今日Phase 1进展**（2026-04-01）：
- 安装了Three.js + React Three Fiber
- 创建了3D组件：Building, SolarArray, BatteryCabinet, ChargingStation
- 数字孪生页面支持3D/能量流双视图切换
- 服务器nginx在运行，但后端未部署

**升级路线**（14周）：
- Phase 1（4周）：Three.js 3D场景
- Phase 2（3周）：充电桩+储能模块
- Phase 3（4周）：AI预测+调度引擎
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

---

*每次对话结束后更新此文件和当日memory/文件。*
