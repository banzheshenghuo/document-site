#!/usr/bin/env python3
"""daily-report-guard.py — 金融日报漏跑自检 v2（2026-11-28）

v2 变更：
- 交易日历以 akshare 新浪交易日历（tool_trade_date_hist_sina）为主，本地缓存 7 天；
  拉取失败退回「工作日 + EXTRA_HOLIDAYS」粗判（调休覆盖表仍保留作兜底，需逐年更新）。
- 缺报回查改为全量：自最近一篇已有日报之后，列出全部缺失的交易日
  （不含今天——今天的日报由本次任务生成）。
- 今天是非交易日时明确输出 NONTRADING 提示，禁止生成当日日报。

用法:
  python3 scripts/daily-report-guard.py             # 巡检（20:30 任务第 0 步）
  python3 scripts/daily-report-guard.py 2026-11-27  # 检查指定日期
退出码: 0=无需补发, 1=存在缺失的交易日（需补发）
"""
import sys, os, glob, json, datetime as dt

POSTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "content", "posts")
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache", "trade_dates.json")

# 兜底用额外休市日（交易日历缺失/超范围时生效；有新调休安排时在此补充）
EXTRA_HOLIDAYS = {
    "2026-01-01", "2026-01-02",                                    # 元旦
    "2026-02-16", "2026-02-17", "2026-02-18", "2026-02-19", "2026-02-20",  # 春节
    "2026-04-06",                                                  # 清明
    "2026-05-01", "2026-05-04", "2026-05-05",                      # 劳动节
    "2026-06-19",                                                  # 端午
    "2026-09-25",                                                  # 中秋
    "2026-10-01", "2026-10-02", "2026-10-05", "2026-10-06", "2026-10-07",  # 国庆
    "2027-01-01",                                                  # 元旦
}
FALLBACK_MIN = "2026-01-01"   # 粗判模式的回溯下限
MAX_LOOKBACK = 15             # 全量回查的时间窗（天）


def load_calendar():
    """返回交易日日期集合；akshare 拉取失败时用缓存（即便过期），再失败返回 None。"""
    cached = None
    try:
        with open(CACHE, encoding="utf-8") as f:
            j = json.load(f)
        cached = set(j["dates"])
        age = dt.datetime.now().timestamp() - os.path.getmtime(CACHE)
        if age < 7 * 86400:
            return cached
    except Exception:
        cached = None if cached is None else cached
    try:
        import akshare as ak
        cal = ak.tool_trade_date_hist_sina()
        dates = sorted(cal["trade_date"].astype(str).str[:10].unique().tolist())
        os.makedirs(os.path.dirname(CACHE), exist_ok=True)
        with open(CACHE, "w", encoding="utf-8") as f:
            json.dump({"updated": dt.date.today().isoformat(), "dates": dates}, f)
        return set(dates)
    except Exception as e:
        print(f"[warn] 交易日历拉取失败（{type(e).__name__}），退回工作日+休市表粗判", file=sys.stderr)
        return cached


def is_trading(date_str, cal):
    if cal is not None:
        # 日历只覆盖到其最大日期；超出范围的年份退回粗判（新版日历每年底才发布）
        if date_str <= max(cal):
            return date_str in cal
        print(f"[warn] {date_str} 超出交易日历范围（{max(cal)}），退回粗判", file=sys.stderr)
    d = dt.datetime.strptime(date_str, "%Y-%m-%d")
    return d.weekday() < 5 and date_str not in EXTRA_HOLIDAYS


def existing_report_dates():
    out = set()
    for p in glob.glob(os.path.join(POSTS, "*-[[]金融日报[]]*.md")):
        head = os.path.basename(p)[:10]
        try:
            dt.date.fromisoformat(head)
            out.add(head)
        except ValueError:
            continue
    return out


def check(date_str, cal):
    """单日模式：0=有/无需生成，1=缺失"""
    if not is_trading(date_str, cal):
        print(f"SKIP  {date_str} 非交易日（周末/休市），无需日报")
        return 0
    hits = glob.glob(os.path.join(POSTS, f"{date_str}-*[[]金融日报[]]*.md"))
    if hits:
        print(f"OK  {date_str} 日报已存在: {os.path.basename(hits[0])}")
        return 0
    print(f"MISSING  {date_str} 日报缺失")
    return 1


def patrol(today, cal):
    """巡检模式：列出最近一篇日报之后全部缺失的交易日（不含今天）。"""
    today = today.date() if isinstance(today, dt.datetime) else today
    today_str = today.strftime("%Y-%m-%d")
    if not is_trading(today_str, cal):
        print(f"NONTRADING  今天 {today_str} 非交易日：不要生成今日日报。")
    dates = existing_report_dates()
    missing = []
    if dates:
        last = max(dates)
        d = dt.date.fromisoformat(last) + dt.timedelta(days=1)
        while d < today:
            s = d.strftime("%Y-%m-%d")
            if is_trading(s, cal):
                missing.append(s)
            d += dt.timedelta(days=1)
        window_hint = f"（最近一篇: {last}）"
    else:
        # 全新安装：只检查前一个交易日
        d = today - dt.timedelta(days=1)
        for _ in range(MAX_LOOKBACK):
            s = d.strftime("%Y-%m-%d")
            if is_trading(s, cal):
                missing = [s]
                break
            d -= dt.timedelta(days=1)
        window_hint = "（未找到任何历史日报）"
    missing = [m for m in missing if (dt.date.today() - dt.date.fromisoformat(m)).days <= MAX_LOOKBACK]
    if missing:
        for m in missing:
            print(f"MISSING  {m} 日报缺失（需补发）")
        return 1
    print("OK  无缺失的交易日日报" + window_hint)
    return 0


def main():
    cal = load_calendar()
    if len(sys.argv) > 1:
        sys.exit(check(sys.argv[1], cal))
    sys.exit(patrol(dt.datetime.now(), cal))


if __name__ == "__main__":
    main()
