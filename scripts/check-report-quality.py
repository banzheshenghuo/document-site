#!/usr/bin/env python3
"""check-report-quality.py — 金融日报发布前质量检查（2026-11-28 V3）

在 astro build 之前对当日日报做规则校验；ERROR 必须修复后重跑，全绿才允许构建部署。

用法: python3 scripts/check-report-quality.py <日报文件.md>
退出码: 0=通过（可含 WARNING）, 1=存在 ERROR

ERROR 项：
  - frontmatter 缺关键字段 / type != daily-finance / tags 首标签非「金融日报」
  - 文件名主题部分含小数点（Astro slugify 会剥掉导致 URL 404）
  - 正文以 H1（# ）开头（页面标题由 frontmatter 渲染，正文双 H1 违反排版规范）
  - 正文含运维字样（HTTPEnable/7890/FlClash/scutil）——基础设施细节禁止入文
  - 缺必备章节：速览/昨日验证/债基跟踪/明日关注/主线观察/参考来源
  - 参考来源节链接 < 6 条，或正文内联链接（参考来源之外）< 5 处
  - 缺「不构成投资建议」免责声明或「数据来源」段

WARNING 项：
  - 速览条数 <6 或 >8；明日关注条数 <2 或 >3
  - 含「数据暂缺」→ 人工确认是否可接受
  - 疑似买卖建议措辞；description 超长；参考来源链接重复；字数超 1800-5500 常规区间
"""
import sys, os, re

OPS_TOKENS = ("HTTPEnable", "7890", "FlClash", "scutil")
ADVICE_RE = re.compile(
    r"(建议|推荐|不妨|应当?|应该|可以|赶紧|立即)[^。！？\n]{0,12}"
    r"(买入|卖出|加仓|减仓|抄底|止损|建仓|清仓|上车|离场)")
SECTIONS = ("速览", "昨日验证", "债基跟踪", "明日关注", "主线观察", "参考来源")
LINK_RE = re.compile(r"\[[^\]]*\]\((https?://[^)\s]+)\)")


def split_fm(text):
    if text.startswith("---"):
        end = text.find("\n---", 3)
        return text[3:end], text[end + 4:]
    return "", text


def section(body, name):
    m = re.search(r"^## [^\n]*" + re.escape(name) + r"[^\n]*$", body, re.M)
    if not m:
        return ""
    rest = body[m.end():]
    n = re.search(r"^## ", rest, re.M)
    return rest[: n.start()] if n else rest


def main(path):
    errors, warns = [], []
    raw = open(path, encoding="utf-8").read()
    name = os.path.basename(path)
    fm, body = split_fm(raw)
    fm_low = fm.lower()

    def fm_has(k):
        return re.search(r"^" + k + r":", fm_low, re.M) is not None

    # ---- frontmatter ----
    for k in ("title", "date", "tags", "category", "type"):
        if not fm_has(k):
            errors.append(f"frontmatter 缺字段: {k}")
    if "daily-finance" not in fm:
        errors.append("frontmatter type 必须为 daily-finance")
    if not re.search(r"^tags:\s*\[?\s*['\"]金融日报", fm, re.M):
        errors.append("tags 首标签必须是「金融日报」")
    # 文件名主题含小数点
    m = re.match(r"\d{4}-\d{2}-\d{2}-[\d-]+-\[金融日报\]-(.*)\.md$", name)
    topic = m.group(1) if m else ""
    if topic and re.search(r"\d\.\d", topic):
        errors.append(f"文件名主题含小数点（slugify 会破坏 URL）: {topic}")

    # ---- 正文结构 ----
    first = next((l for l in body.split("\n") if l.strip()), "")
    if first.startswith("# "):
        errors.append(f"正文以 H1 开头（应直接以 blockquote 导读开始）: {first[:50]}")
    for tok in OPS_TOKENS:
        if tok in body:
            errors.append(f"正文含运维字样「{tok}」——基础设施细节禁止写入文章")
    for s in SECTIONS:
        if not re.search(r"^## [^\n]*" + re.escape(s) + r"[^\n]*$", body, re.M):
            errors.append(f"缺必备章节: ## {s}")

    # ---- 链接与来源 ----
    ref = section(body, "参考来源")
    ref_links = LINK_RE.findall(ref)
    all_links = LINK_RE.findall(body)
    inline = len(all_links) - len(ref_links)
    if len(ref_links) < 6:
        errors.append(f"参考来源链接仅 {len(ref_links)} 条（要求 ≥6）")
    if inline < 5:
        errors.append(f"正文内联链接仅 {inline} 处（要求 ≥5）")
    if len(ref_links) != len(set(ref_links)):
        warns.append("参考来源存在重复链接")

    # ---- 免责声明与数据来源 ----
    if "不构成投资建议" not in body:
        errors.append("缺「不构成投资建议」免责声明")
    if "数据来源" not in body:
        errors.append("缺「数据来源」段")

    # ---- 警告级 ----
    su = section(body, "速览")
    n_su = len(re.findall(r"^\s*-\s", su, re.M))
    if n_su and not (6 <= n_su <= 8):
        warns.append(f"速览 {n_su} 条（常规 6-8）")
    mr = section(body, "明日关注")
    n_mr = len(re.findall(r"^\s*(?:\d+\.|-\s)", mr, re.M))
    if n_mr and not (2 <= n_mr <= 3):
        warns.append(f"明日关注 {n_mr} 条（常规 2-3）")
    miss = re.findall(r"^.*数据暂缺.*$", body, re.M)
    for line in miss:
        warns.append(f"含「数据暂缺」，人工确认是否可接受: {line.strip()[:70]}")
    for m2 in ADVICE_RE.finditer(body):
        ctx = body[max(0, m2.start() - 20): m2.end() + 20].replace("\n", " ")
        warns.append(f"疑似买卖建议措辞，人工确认: …{ctx}…")
    desc = re.search(r"^description:\s*['\"](.*)['\"]", fm, re.M)
    if desc and len(desc.group(1)) > 170:
        warns.append(f"description {len(desc.group(1))} 字（常规 ≤170）")
    cjk = len(re.findall(r"[\u4e00-\u9fff]", body))
    if not (1800 <= cjk <= 5500):
        warns.append(f"正文 {cjk} 汉字（常规区间 1800-5500）")

    print(f"== check-report-quality: {name} ==")
    for e in errors:
        print(f"  [ERROR] {e}")
    for w in warns:
        print(f"  [WARN]  {w}")
    print(f"  小结: {len(errors)} error / {len(warns)} warn / 正文 {cjk} 汉字 / 内联链接 {inline} / 参考来源 {len(ref_links)}")
    return 1 if errors else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
