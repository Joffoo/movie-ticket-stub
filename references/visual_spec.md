# EverStub 票根视觉规范与排版细节 (100% 网页版一致性标准)

本文档详细拆解 EverStub 原始网页项目（`TicketPreview.tsx` / `canvasService.ts`）的视觉排版网格、字体阶梯与确定性条形码算法，确保 100% 像素级复刻。

---

## 1. 整体网格与比例系统 (9:16)

原版设计受限于 PC 屏幕文本密度保护原则，将容器精确锁定为 `max-w-sm`（**384px 宽度**），比例严格为 **9:16**（高度为 `384 × 16 / 9 = 682.67px`，取整 `683px`）。
导出采用与原版 `canvasService.ts` 一致的 `pixelRatio: 4`（4倍视网膜采样），输出高清分辨率为 **1536 × 2732 px**。

```text
+------------------------------------------+  0px (总宽 384px)
|                                          |
|        1. 艺术插画区 (Strictly 1:1)       |  384px 高 (aspect-square)
|        384px × 384px 正方形              |
|                                          |
+==========================================+  384px (4px 纯黑底边框 border-b-4)
| 2. 标题区 (Title Section)  H: 112px (h-28)|  padding: 12px 20px (px-5 py-3)
|    - 英文大标题 (Oswald Bold Uppercase)   |  自适应字号与行高 (leading-[0.8]~tight)
|    - 中文片名 (Inter/Swiss Bold)         |  自适应字号
+------------------------------------------+  496px (2px 纯黑分隔线 border-b-2)
| 3. 数据网格 (Data Grid)     H: 96px (h-24)|
|    THEATER:  左55% (TIME/PRICE) | 右45%   |  自适应字号，支持换行
|    HOME:     左50% (DATE)       | 右50%   |
+------------------------------------------+  592px (2px 纯黑分隔线 border-b-2)
| 4. 底部条形码区 (Barcode)   H: ~91px (flex-1)
|    居中展示 84 根确定性条码 (h-6 = 24px) |
+------------------------------------------+  683px 底边 (纯白底色，无任何外边距)
```

---

## 2. 字体规范与 4 级动态自适应阶梯

### 字体栈
- **英文展示字体**：`'Oswald', 'DIN Alternate', sans-serif`（加粗 `700`，字距微收紧 `tracking-tight`，全大写）。
- **正文与中文**：`'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif`（字重 `font-bold` 与 `font-medium`）。

### 4 级文本长度动态自适应规则（严格匹配 `TicketPreview.tsx`）
1. **英文大标题 (`movie_en`)**：
   - 字符数 `< 10`：`text-5xl (48px)`，行高 `leading-[0.8]`
   - 字符数 `10 ~ 17`：`text-4xl (36px)`，行高 `leading-[0.85]`
   - 字符数 `18 ~ 29`：`text-3xl (30px)`，行高 `leading-[0.9]`
   - 字符数 `>= 30`：`text-xl (20px)`，行高 `leading-tight`
2. **中文片名 (`movie_cn`)**：
   - 字符数 `< 8`：`text-2xl (24px)`
   - 字符数 `8 ~ 14`：`text-xl (20px)`
   - 字符数 `>= 15`：`text-base (16px)`
3. **时间和票价字段 (`time_val`, `price_val`)**：
   - 字符数 `< 12`：`text-lg (18px)`
   - 字符数 `12 ~ 17`：`text-base (16px)`
   - 字符数 `>= 18`：`text-sm (14px)`
4. **影院与地点字段 (`location_val`)**：
   - 字符数 `< 20`：`text-sm (14px)`，`leading-tight`
   - 字符数 `20 ~ 39`：`text-xs (12px)`，`leading-tight`
   - 字符数 `>= 40`：`text-[10px]`，`leading-tight`
   - 渲染模式：`whitespace-pre-line`（允许 `\n` 换行展示影院与分店名）。

---

## 3. 确定性条形码算法（Deterministic Barcode）

共 84 根竖线，均匀填充在 `384px - 40px = 344px` 宽度内（`justify-between`）：

```javascript
for (let i = 0; i < 84; i++) {
  const seed = Math.sin(i * 12.9898 + 78.233) * 43758.5453;
  const val = seed - Math.floor(seed);
  let width = '1px';
  if (val > 0.90) width = '4px';
  else if (val > 0.75) width = '3px';
  else if (val > 0.45) width = '2px';
  // 渲染为高 24px (h-6)、宽 width 的纯黑条
}
```

---

## 4. 色彩与交付要求

- **背景底色**：`#FFFFFF`（纯白满幅，无暗黑外边框、无阴影）。
- **边框与分隔线**：纯黑 `#000000`（插画区分割线 `4px`，标题与网格分割线 `2px`）。
- **输出格式**：无损 PNG，默认分辨率 **1536 × 2732 px**（`scale=4`），亦可通过 `scale=2.8125` 输出 **1080 × 1920 px**。
