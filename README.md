# Movie Ticket Stub (电影票根生成器)

将用户的电影票照片、购票短信、选座截图或观影记录，全自动转化为极具收藏价值与设计感的 **9:16 瑞士国际主义风格（Swiss International Typographic Style）** 纪念票根。

与原始网页项目 `EverStub` 保持 **100% 像素级一致**（完全复用原版 Tailwind 布局与动态自适应字号阶梯）。

---

## 目录结构

```text
movie-ticket-stub/
├── SKILL.md                  # 主技能指导书（4阶段流水线定义）
├── README.md                 # 技能概述与独立使用文档
├── references/
│   ├── prompt_templates.md   # 固化的瑞士风生图 Prompt 与数据规范
│   └── visual_spec.md        # 9:16 视觉排版网格、动态字号阶梯与条形码规范
├── templates/
│   └── ticket_template.html  # 原版 Tailwind + Google Fonts 票根模板
└── scripts/
    └── render_ticket.py      # 本地无头浏览器截图渲染脚本（支持 4x 视网膜高清）
```

---

## 命令行独立使用示例

```bash
# 1. 使用 JSON 文件渲染
python scripts/render_ticket.py --data "ticket_data.json" --output "ticket.png"

# 2. 指定输出为 1080x1920 (默认输出原版 1536x2732)
python scripts/render_ticket.py --data "ticket_data.json" --output "ticket.png" --scale 2.8125

# 3. 使用 Base64 编码传参（规避 Windows 控制台引号问题）
python scripts/render_ticket.py --data-b64 "<BASE64_STRING>" --output "ticket.png"
```
