---
name: movie-ticket-stub
description: 将电影票截图、纸质票照片或观影打卡记录转化为 9:16 瑞士国际主义风格极简纪念票根。包含票据多模态结构化提取、官方海报垫图矢量重绘与全离线无头排版。当用户提到“电影票根”、“制作票根”、“观影打卡”、“瑞士风票根”、“票根生成器”、“movie ticket”或发送电影票截图时触发。不用于常规影评撰写或非票根类普通海报排版。
---

# Movie Ticket Stub (电影票根生成器): 瑞士国际主义风格电影票根生成器

将用户的电影票截图、电子购票凭证或观影打卡记录，一键转化为极具设计感的 9:16 瑞士国际主义风格（Swiss International Typographic Style）纪念票根。本技能在视觉层与原版 EverStub 网页应用保持 100% 像素级一致，内置全离线独立排版引擎、假白边自适应裁剪与首启偏好记忆。

---

## 触发场景

- 用户发送或粘贴电影票截图（淘票票/猫眼/万达/大麦）、纸质票照片或流媒体打卡截图。
- 用户表达“帮我做一张电影票根”、“制作观影纪念卡”、“生成瑞士风电影海报卡片”。
- 用户提供观影文本（如“昨晚看了《奥本海默》，19:30 场次，万达影城 天佑城店，实付 32 元”）并要求出票。

---

## 执行流水线 (Pipeline)

```text
[用户输入: 票据截图 / 文本] 
   │
   ▼
0. 偏好嗅探 ──► 读取 .ticket_config.json（首启自动记忆引擎与输出偏好，后续零打扰）
   │
   ▼
1. 信息提取 ──► 多模态解析 TicketData（片名/英文名/时间/影城与分店/实付票价/模式）
   │
   ▼
2. 资产路由 ──► 官方海报检索（无论冷门热门，一律优先联网检索并下载官方海报原图）
   │
   ▼
3. 矢量重绘 ──► 垫图风格转换（以原海报为 ImagePaths，提示词严格忽略所有文字，生成 1:1 纯艺术插画）
   │
   ▼
4. 离线渲染 ──► scripts/render_ticket.py 驱动全本地无头实例，导出 1536x2732 Retina 票根
   │
   ▼
[交付归档]   ──► 规范归档（默认输出至 ./output/，支持自定义路径）
```

---

## 阶段详解

### 步骤 0：首启偏好嗅探 (Config & Preferences)

优先查找当前目录 `.ticket_config.json` -> Skill 目录 -> `~/.config/movie-ticket/config.json`：
- **生图引擎 (`image_generator`)**：
  - `auto` / `native`：宿主原生生图工具（如 Antigravity `generate_image`）。
  - `dall-e-3` / `custom_api`：商业生图 API。
  - `poster_crop`：零成本纯排版（原海报 1:1 几何居中裁切，无 Token 消耗）。
- **输出路径 (`output_dir`)**：
  - `auto`：默认规范输出至 `./output/`（可通过配置文件或 CLI `--output` 自定义）。
- **免打扰原则**：配置建立后，后续执行**一律静默加载，严禁重复弹窗问询**。

---

### 步骤 1：多模态票据解析 (Ticket Parser)

观察用户提供的图片或文本，提取为标准 `TicketData`：

1. **场景模式 (`mode`)**：
   - `THEATER`：线下影院出票、纸质票、购票订单截图。
   - `HOME`：家庭影院、流媒体播放界面（Netflix、Bilibili、Apple TV 等）。
2. **字段提取规范**：
   - `movie_cn`：纯净中文片名（去除“IMAX 3D / 杜比视界”等制式后缀）。
   - `movie_en`：官方大写英文全名（UPPERCASE，如 `RESIDENT EVIL`）。
   - `time_val`：放映时间标准化为 `YYYY.MM.DD HH:MM`（家庭模式为 `YYYY.MM.DD`）。**严禁擅自将老票据年份篡改为当前年份**；若票面缺年份且无法判断，保留原始月日时间。
   - `location_val`：极简双行展示（换行符 `\n` 分隔）。第一行影院名（如 `中影晟阳影城`），第二行分店名（如 `天佑城店`）。不录入具体影厅与座位号，保护隐私并维持排版平衡。
   - `price_val`：**优先取用户实际支付金额（实付价）**，带货币符号（如 `¥32.00`）；赠票或无标价填 `INVITATION`。
3. **🔴 CHECKPOINT · 信息核验与人审求证**：
   - **模糊看不清或字段缺失**：若票据因反光、折痕、褪色或截图不全导致片名、时间、影院或实付价格看不清或缺失，**严禁自行捏造臆测，也严禁自行填充占位符，必须直接向用户发问确认**后再继续。
   - **片名多义与版本歧义**：若片名存在多部完全同名的不同年份/翻拍版本影片或信息存在矛盾，必须主动向用户简短求证是哪一部。

---

### 步骤 2：海报与英文名路由 (Fetch & Route)

- **官方大写英文名**：若票面缺少外文名，快速核对并锁定全大写官方名（如 `THE GRAND BUDAPEST HOTEL`）。
- **强制垫图原则（无论热门冷门，一律垫图）**：
  - 触发 Agent 联网检索该影片的官方院线/先导海报，下载并暂存到本地（作为 `ImagePaths` 垫图）；
  - 若用户自行提供了海报或剧照，则优先使用用户提供的图片作为垫图；
  - 若网络检索不到公开的官方院线/先导海报原图，**直接向用户请求提供一张海报或剧照作为垫图，严禁脱离真实海报凭空盲画**。

---

### 步骤 3：正向视觉矢量重绘 (Swiss Vectorizer)

调用生图工具时，比例锁定 `1:1`，传入步骤 2 准备好的海报垫图（`ImagePaths`）。严格执行**构图继承与文字剔除（Composition Inheritance & Text Purging）**，提示词必须严格以原海报的真实视觉结构为准，**严禁 Agent 凭空臆想与垫图构图不符的额外剧情描写**：

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

- **海报预处理（去字裁剪）**：院线海报下部 20%~30% 通常为密集演职员文字，优先截取上部纯视觉画面为 1:1 垫图传入，从源头杜绝文字干扰。
- **全画幅自动去白边**：`render_ticket.py` 内部已集成 `autocrop_borders` 算法，会自动检测并切除生图模型偶尔附带的边缘留白，确保 100% 贴合出血。

---

### 步骤 4：全离线无头排版出票 (Headless Rendering)

将结构化数据与生成的插画合成为最终的 9:16 票根：

```bash
python scripts/render_ticket.py --data "<数据JSON文件路径>" [--output "<目标路径或auto>"]
```

- **全离线与零依赖**：模板内联核心排版 CSS 与预计算 84 根静态条形码，彻底切断所有外部 CDN 与 Google Fonts 请求，无惧网络卡顿与超时；
- **全平台支持**：自动适配 Windows、macOS 与 Linux 的 Chrome/Edge 浏览器；
- **产物命名规范**：最终导出的票根文件命名推荐遵从 `{English_Title}_Ticket.png` 格式（如 `The_Odyssey_Ticket.png`、`Resident_Evil_Ticket.png`，若仅有中文片名则为 `{中文片名}_Ticket.png`），默认输出至 `./output/` 目录下。

---

### 步骤 5：成果交付

在对话中向用户呈现：
1. **票根图像卡片**：直接展示或嵌入生成的 PNG 票根（如 `{English_Title}_Ticket.png`）。
2. **数据核对表**：展示片名、影院地点、场次与实付票价。
3. **微调指引**：说明若想微调时间、影院或更换插画镜头，直接回复即可重新出票。
