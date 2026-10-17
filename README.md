<div align="center">

# 🎞️ Movie Ticket Stub · 电影票根生成器

**[English](#english) | [中文](#中文)**

</div>

---

<a id="中文"></a>

# 中文

将用户的电影票照片、购票短信、选座截图或观影记录，全自动转化为极具收藏价值与设计感的 **9:16 瑞士国际主义风格（Swiss International Typographic Style）** 纪念票根。

与原始网页项目 `EverStub` 保持 **100% 像素级一致**（完全复用原版 Tailwind 布局与动态自适应字号阶梯）。

## ✨ 特性

- **全自动流水线**：票据多模态结构化提取 → 官方海报检索 → 矢量风格重绘 → 全离线无头排版，一气呵成
- **瑞士国际主义排版**：包豪斯现代主义 + 高对比色块 + 动态自适应字号阶梯
- **海报垫图重绘**：以官方海报为参考图进行风格转换，并彻底去除文字干扰
- **全离线渲染**：模板内联全部排版 CSS 与 84 根静态条形码，零外部请求，无惧网络卡顿
- **Retina 高清输出**：支持 4x 缩放导出 1536×2732 高分辨率票根
- **首启偏好记忆**：配置一次，后续零打扰（引擎选择 + 输出路径自动记忆）

## 📁 目录结构

```text
movie-ticket-stub/
├── SKILL.md                     # 主技能指导书（5 步流水线定义）
├── README.md                    # 技能概述与独立使用文档
├── templates/
│   └── ticket_template.html     # 原版 Tailwind 票根模板（排版与字号阶梯全部内联）
└── scripts/
    ├── render_ticket.py         # 本地无头浏览器截图渲染脚本（支持 4x 视网膜高清）
    └── config_manager.py        # 首启偏好记忆引擎
```

---

## 🚀 快速开始

### 作为 Agent Skill 使用

将本仓库放入 skills 目录（如 `.agents/skills/` 或 `~/.claude/skills/`），当用户提到「电影票根」「制作票根」「观影打卡」或发送电影票截图时自动触发。

### 依赖

- **Python 3.10+**
- 本机任一 **Chrome / Edge / Chromium** 浏览器（用于无头渲染，Python 包零依赖）

### 命令行独立使用示例

```bash
# 1. 使用 JSON 文件渲染
python scripts/render_ticket.py --data "ticket_data.json" --output "ticket.png"

# 2. 指定输出为 1080x1920 (默认输出原版 1536x2732)
python scripts/render_ticket.py --data "ticket_data.json" --output "ticket.png" --scale 2.8125

# 3. 使用 Base64 编码传参（规避 Windows 控制台引号问题）
python scripts/render_ticket.py --data-b64 "<BASE64_STRING>" --output "ticket.png"
```

### 票据数据格式（TicketData）

```json
{
  "mode": "THEATER",
  "movie_cn": "奥本海默",
  "movie_en": "OPPENHEIMER",
  "time_val": "2025.08.12 19:30",
  "location_val": "万达影城\n天佑城店",
  "price_val": "¥32.00",
  "artwork_path": "artwork.png"
}
```

> 复制 `.ticket_config.example.json` 为 `.ticket_config.json` 即可自定义引擎与输出偏好。

---

<a id="english"></a>

# English

Turn your movie tickets — photos, booking text messages, seat-selection screenshots, or watch logs — into collectible, gallery-quality **9:16 Swiss International Typographic Style** memorial ticket stubs, fully automatically.

It stays **100% pixel-identical** with the original web project `EverStub` (reusing the original Tailwind layout and dynamic adaptive font-size ladder).

## ✨ Features

- **Fully automated pipeline**: multimodal ticket extraction → official poster retrieval → vector-style redecorating → fully offline headless typesetting
- **Swiss typographic style**: Bauhaus modernism, bold high-contrast color planes, dynamic adaptive font-size ladder
- **Reference-guided poster redecorating**: stylized from the official theatrical poster with all text purged
- **Fully offline rendering**: template inlines all layout CSS and a precomputed 84-bar static barcode — zero external requests
- **Retina-quality output**: exports up to 1536×2732 at 4x scale
- **First-launch preference memory**: configure once, never bother again (engine choice + output path)

## 📁 Structure

```text
movie-ticket-stub/
├── SKILL.md                     # Main skill guide (5-stage pipeline)
├── README.md                    # Overview & standalone usage (this file)
├── templates/
│   └── ticket_template.html     # Original Tailwind stub template (layout & font ladder fully inlined)
└── scripts/
    ├── render_ticket.py         # Headless browser rendering (4x retina)
    └── config_manager.py        # Config management (first-launch memory)
```

## 🚀 Quick Start

### As an Agent Skill

Drop this repo into your skills directory (e.g. `.agents/skills/` or `~/.claude/skills/`). It auto-triggers when users mention "movie ticket stub", "make a stub", send a ticket screenshot, or share watch logs.

### Prerequisites

- **Python 3.10+**
- Any local **Chrome / Edge / Chromium** browser (for headless rendering — no Python packages required)

### CLI Usage

```bash
# 1. Render from a JSON file
python scripts/render_ticket.py --data "ticket_data.json" --output "ticket.png"

# 2. Output 1080x1920 (default is the original 1536x2732)
python scripts/render_ticket.py --data "ticket_data.json" --output "ticket.png" --scale 2.8125

# 3. Pass data as Base64 (avoids Windows console quoting issues)
python scripts/render_ticket.py --data-b64 "<BASE64_STRING>" --output "ticket.png"
```

### Ticket Data Format (TicketData)

```json
{
  "mode": "THEATER",
  "movie_cn": "奥本海默",
  "movie_en": "OPPENHEIMER",
  "time_val": "2025.08.12 19:30",
  "location_val": "Cinema Park Branch\nWanda Cinemas",
  "price_val": "$9.90",
  "artwork_path": "artwork.png"
}
```

> Copy `.ticket_config.example.json` to `.ticket_config.json` to customize the rendering engine and output preferences.

## 📄 License

MIT
