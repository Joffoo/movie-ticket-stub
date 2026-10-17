---
name: movie-ticket-stub
description: 将电影票截图、购票订单或纸质票照片，以及观影打卡文本，转化为 9:16 瑞士国际主义风格纪念票根。当用户发送票据/购票凭证截图并要求出票、说"做一张电影票根"或给出观影记录出票时触发；常规影评与票根之外的海报排版不触发。
---

# Movie Ticket Stub (电影票根生成器)

把电影票截图、电子购票凭证或观影打卡记录，合成为 9:16 瑞士国际主义风格（Swiss International Typographic Style）纪念票根。视觉层与原型网页项目 EverStub 像素级一致，排版渲染全离线。

---

## 执行流水线

```text
0. 配置 ─► 1. 票据解析 ─► 2. 海报垫图 ─► 3. 垫图矢量重绘 ─► 4. 离线排版出票 ─► 5. 交付
```

每一步的输入以上一步的输出为准，顺序执行；步骤 1 与步骤 2 各有一个必须通过再继续的完成标准。

---

### 步骤 0：配置

按 当前目录 `.ticket_config.json` → Skill 目录 → `~/.config/movie-ticket/config.json` 的顺序读取第一个存在的配置，随后的每次运行静默沿用，只问一次：

- `image_generator`：`auto` / `native`（宿主原生生图工具，如 Antigravity `generate_image`）、`dall-e-3` / `custom_api`（商业生图 API，Key 由用户在本地配置自填）、`poster_crop`（零成本纯排版：原海报 1:1 居中裁切）
- `output_dir`：`auto` 即 `./output/`，或自定义路径

---

### 步骤 1：多模态票据解析 (Ticket Parser)

观察用户提供的票据截图、照片或文本，提取标准 `TicketData`：

| 字段 | 提取规范 |
| :--- | :--- |
| `mode` | `THEATER` 线下影院（票/订单/截图）；`HOME` 流媒体打卡。字段缺失时填 `THEATER` |
| `movie_cn` | 纯净中文片名，去除"IMAX 3D / 杜比视界"制式后缀 |
| `movie_en` | 官方全大写英文全名（如 `RESIDENT EVIL`） |
| `time_val` | `YYYY.MM.DD HH:MM`（HOME 模式为 `YYYY.MM.DD`）。以票面原样为准，老票保留原有年份 |
| `location_val` | 两行、`\n` 分隔：第一行影院名（HOME 模式：地点），第二行分店名（HOME 模式：平台名）。不写影厅与座位号 |
| `price_val` | 用户实付金额带货币符号（如 `¥32.00`）；赠票或无标价填 `INVITATION` |

**🔴 CHECKPOINT · 逐字段落实后出票**

片名、时间、影院、实付价四项中任何一项反光、褪色或缺失：逐项列出，各向用户问一句，得到确认再继续。片名存在同名翻拍/重制版或信息互相矛盾时，同样先问清是哪一部。**完成标准**：每个字段有票面依据，或已经向用户逐项确认——满足后才进入步骤 2。

---

### 步骤 2：海报与英文名路由 (Fetch & Route)

- `movie_en` 缺外文名时，联网核对官方全大写英文名（如 `THE GRAND BUDAPEST HOTEL`）。
- **一律垫图**：联网检索该影片的官方院线/先导海报原图，下载暂存本地作为 `ImagePaths`；用户已提供海报或剧照的，优先用用户图。公开原图检索不到时，直接请用户提供一张海报或剧照作为垫图。
- **完成标准**：手头已有一张真实海报（本地路径确定），方可进入步骤 3。

---

### 步骤 3：垫图矢量重绘 (Swiss Vectorizer)

调用生图工具，比例锁定 `1:1`，传入步骤 2 的海报垫图。院线海报下部 20%~30% 常为密集演职员文字，先截取上部纯视觉画面再作垫图。提示词严格以原海报的真实视觉结构为准：

```text
SYSTEM ROLE: Senior Visual Designer
TASK: Swiss International Typographic Style Illustration (Reference-Guided Style Transfer)

INPUT:
- Reference Image (ImagePaths): Official theatrical poster visual artwork.

VISUAL TARGET & STEERING:
1. COMPOSITION: Strictly inherit the primary subject silhouettes, focal perspective, and spatial layout from the reference poster image.
2. STYLE: Swiss International Typographic Style, Bauhaus modernist flat vector illustration. High contrast bold solid color cutouts with clean geometric planes and cohesive color palette derived from the film's visual identity.
3. TEXT PURGING: Completely ignore, omit, and eliminate all typography, titles, letters, credits, billing blocks, and logos from the reference image. Transform all textual areas into pure abstract negative space or solid vector geometry.
4. FINISH: Edge-to-edge full bleed 1:1 square vector artwork. No frames, no borders.

OUTPUT: A single 1:1 square vector illustration.
```

- 配色与构图继承海报本体；海报中的全部文字区域转为负空间或纯几何色块。
- `render_ticket.py` 内置 `autocrop_borders`，生图偶带的边缘留白会被自动切除，贴合出血。

---

### 步骤 4：离线排版出票 (Headless Rendering)

```bash
python scripts/render_ticket.py --data "<TicketData JSON 路径>" [--output "<路径或auto>"]
```

- 以本机 Chrome/Edge 无头模式渲染模板截图，默认导出 1536×2732，`--scale 2.8125` 时为 1080×1920。
- `--data-b64 "<BASE64>"` 传参可规避 Windows 控制台引号问题。
- 文件名按 `{English_Title}_Ticket.png`（仅有中文名时 `{中文片名}_Ticket.png`），默认输出至 `./output/`。

---

### 步骤 5：交付

1. 展示生成的 PNG 票根。
2. 附数据核对表：片名、影院与分店、场次与实付票价。
3. 说明微调方式：改时间、影院或更换插画，直接回复即可重新出票。
