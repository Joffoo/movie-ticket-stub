# EverStub 核心 Prompt 与字段规范

本文档为 movie-ticket-stub 提供标准化提示词与数据契约，严格遵循 /write-for-agents 正向引导规范。

---

## 1. 瑞士国际主义风格垫图风格转换 Prompt (Reference-Guided Style Transfer)

调用生图工具时，比例锁定 1:1（Square），传入预处理后的纯视觉海报垫图（`ImagePaths`）。必须声明构图继承与彻底文字过滤，杜绝 Agent 凭空臆想与垫图冲突的情节：

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

---

## 2. 多模态票据解析结构定义 (TicketData Schema)

```json
{
  "mode": "THEATER",
  "movie_cn": "布达佩斯大饭店",
  "movie_en": "THE GRAND BUDAPEST HOTEL",
  "time_val": "2024.10.28 14:00",
  "location_val": "万达影城\nCBD店",
  "price_val": "¥35.00",
  "artwork_path": "path/to/artwork.png"
}
```

### 字段解析与容错规则：
| 字段 | 说明 | 影院模式 (THEATER) | 家庭模式 (HOME) | 缺漏容错规则 |
| :--- | :--- | :--- | :--- | :--- |
| `mode` | 场景模式 | 实体票/淘票票/猫眼/万达票据 | 电视/流媒体/投屏打卡 | 默认 `THEATER` |
| `movie_cn` | 中文片名 | 去除 IMAX/3D 等制式后缀 | 同左 | 必须项 |
| `movie_en` | 官方英文片名 | 全部大写（UPPERCASE） | 全部大写 | 联网核对官方英文原名 |
| `time_val` | 时间日期 | `YYYY.MM.DD HH:MM`（放映时间） | `YYYY.MM.DD`（观影日期） | 禁猜年份；若无年份则保留原始时间 |
| `location_val` | 影院/平台 | 双行展示：第一行影院名，第二行分店名 | 双行展示：第一行地点，第二行平台 | 不录入具体影厅与座位号 |
| `price_val` | 实付票价 | 优先取实付金额，带货币符号 | 不适用（可留空） | 赠票或无标价填 `INVITATION` |

---

## 3. 命令行调用推荐格式

```bash
# 智能路由与自动输出（推荐）
python scripts/render_ticket.py --data "path/to/data.json" --output auto

# 显式路径指定
python scripts/render_ticket.py --data "path/to/data.json" --output "custom/output.png"
```
