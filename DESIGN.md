# Design System: 安昙的知识库（ai-document）

> 单一设计真源。所有新页面、新组件（含分类筛选）必须遵循本文件。
> 基线评估：Density 5（Daily App Balanced）/ Variance 4（Offset Asymmetric）/ Motion 5（Fluid CSS）。

## 1. Visual Theme & Atmosphere

一间安静的工程书房：Zinc 中性基调、克制的高对比排版、唯一的蓝色强调。
信息密度是日常应用级——不空洞、不拥挤。列表区依靠 1px 结构线与负空间分区，
而非层层卡片投影。交互反馈用短促的 transform 位移与边框色变，绝无霓虹光晕。

## 2. Color Palette & Roles

**Light（默认）**

- **Canvas White**（#FAFAFA）— 页面主背景
- **Secondary Wash**（#F4F4F5）— 次级面板、代码块、标签底（Zinc-100）
- **Charcoal Ink**（#18181B）— 主文本（Zinc-950，替代纯黑）
- **Muted Steel**（#71717A）— 次级文本、日期、元数据（Zinc-500）
- **Whisper Border**（#E4E4E7）— 1px 结构线、卡片描边（Zinc-200）
- **Signal Blue**（#2563EB）— 唯一强调色：激活 Tab、链接、焦点环、悬停标题
- **Signal Hover**（#1D4ED8）— 强调色悬停态

**Dark（`[data-theme='dark']`）**

- Canvas #09090B / Secondary #18181B / Text #FAFAFA / Muted #A1A1AA / Border #27272A / Signal #60A5FA / Hover #93C5FD

**约束**：全站唯一强调色为 Signal Blue。卡片顶条的 read/collect 渐变（蓝 / amber-red）
是仅有的两处语义色，只允许出现在 3px 装饰条上。禁止新增紫色、霓虹渐变、纯黑 #000000。

## 3. Typography Rules

- **Display（H1）**：系统中文栈（PingFang SC 优先）— 2.75rem / 800 / letter-spacing -0.03em，层级靠字重与颜色，不靠尖叫字号
- **Body**：系统中文栈 — 1rem，行高 1.6–1.7，单行 ≤ 65ch
- **Mono（元数据专用）**：JetBrains Mono — Tab、计数、日期、标签、序号一律 mono，0.625–0.8125rem，letter-spacing 0.02–0.15em
- **Banned**：Inter 作为主字体、generic serif（Georgia/Times）进入 UI、正文小于 0.75rem

## 4. Component Stylings

- **Filter Chip（筛选按钮，两维统一语言）**：999px 胶囊、mono 0.8125rem、
  min-height 36px（移动端 44px）。默认 border + Zinc-500 文字；hover 边框与文字
  转 Signal Blue + 6% 蓝底；active 为 Signal Blue 实底白字 +
  `0 2px 8px rgba(37,99,235,0.25)` 柔影，active 按压 -1px。计数 0.6875rem、60% 透明度。
  两个筛选维度（阅读类型/主题分类）**共用同一按钮样式**，靠行首 mono 行标
  （0.6875rem、Muted Steel）区分维度。移动端行内横向滚动，行标固定不滚。
- **Card**：0.5rem 圆角、1px Whisper Border、3px 纯色顶条（蓝=精读 / 琥珀=收藏 /
  灰=无类型，**不放文字**）。类型文字在 meta 行以 chip 呈现：精读=8% 蓝底蓝字、
  收藏=12% 琥珀底琥珀字（dark 模式 #fbbf24 / 15% 琥珀底），4px 圆角 mono 0.625rem。
  hover：-4px translateY + 边框转 25% 蓝 + 鼠标跟踪径向微光（6% 蓝）。
- **Empty State**：居中、4rem 留白、Muted Steel 文案，明确指出该分类/筛选无内容，绝不放 "No data"。
- **Buttons**：扁平面 + 1px 边框，active 时 -1px 视觉下压；无外发光、无自定义光标。

## 5. Layout Principles

- 首页容器 max-width 900px 居中；卡片网格 `repeat(auto-fill, minmax(280px, 1fr))`，gap 1.25rem
- Hero 左对齐（Variance > 4，禁止居中 Hero）；统计行用 4px 圆点分隔，mono 数字
- 两维筛选各自独立成行，垂直 gap 0.75rem：每行 = mono 行标 + 胶囊按钮组（阅读类型 / 主题分类）
- 移动端（< 640px）：网格塌陷单列、pill 行横向滚动、触控目标 ≥ 44px
- 禁止：元素重叠、绝对定位堆叠、flex 百分比算术、`calc()` hack

## 6. Motion & Interaction

- 卡片入场：opacity 0 + 16px translateY → IntersectionObserver 触发 0.4s ease 渐入，
  同批卡片 40ms 级联错峰（最多 8 级）
- 筛选切换：重置分页（PAGE_SIZE 18），卡片重新走渐入流程——列表绝不瞬间整体闪变
- 只动画 `transform` / `opacity` / `border-color` / `box-shadow`，禁止动画 top/left/width/height
- 加载更多：按钮点击 + 200px rootMargin 滚动哨兵双通道

## 7. Anti-Patterns (Banned)

- 禁 emoji 进入 UI
- 禁 Inter 主字体、generic serif 进入界面
- 纯黑 #000000、霓虹/外发光阴影、过饱和强调色、紫色渐变
- 元素重叠与绝对定位堆叠
- `LABEL // YEAR` 式装饰前缀（眉标用纯 mono 大写 + letter-spacing，不加 `//`）
- AI 文案陈词：Elevate / Seamless / Unleash / Next-Gen
- 填充性 UI 文案："Scroll to explore"、滚动箭头、弹跳 chevron
- 捏造数据：任何未经内容集合真实统计的数字、百分比、指标卡
- 等宽三列卡片阵列；用 auto-fill 网格或非对称布局替代
