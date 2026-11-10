#!/usr/bin/env python3
"""daily-market-data.py — 金融日报取数脚本（akshare）
除当日数据外，附周期对比：指数近5日累计、成交额 vs 5日均量、板块5日累计与连续天数、
南向资金当日+近5日累计、汇率/金/油周变动。
任一数据块失败输出『数据暂缺』，绝不中断整个脚本。
用法: python3 scripts/daily-market-data.py [--out /tmp/market-data.md]
"""
import sys, argparse
from datetime import datetime, timedelta

OUT_LINES = []
SEC = lambda t: OUT_LINES.append(f"\n### {t}\n")
ROW = lambda s: OUT_LINES.append(s)

def pct(a, b):
    return (float(a) - float(b)) / float(b) * 100 if b else 0.0

def cum5(closes):
    """近5个交易日累计涨跌幅（复利）"""
    if not closes or len(closes) < 6:
        return None
    return (float(closes[-1]) / float(closes[-6]) - 1) * 100

def start_date(days=15):
    return (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")

def safe(name):
    """装饰器：单块数据失败只记录，不中断"""
    def deco(fn):
        def wrap():
            try:
                SEC(name)
                fn()
            except Exception as e:
                OUT_LINES.append(f"数据暂缺（{name} 拉取失败: {type(e).__name__}）\n")
                print(f"[warn] {name}: {e}", file=sys.stderr)
        return wrap
    return deco

@safe("A股主要指数")
def a_indices():
    import akshare as ak
    codes = [("000001", "上证指数"), ("399001", "深证成指"), ("399006", "创业板指"), ("000688", "科创50")]
    ROW("| 指数 | 收盘 | 当日 | 近5日累计 | 成交额(vs 5日均) |")
    ROW("|---|---|---|---|---|")
    for code, name in codes:
        d = ak.index_zh_a_hist(symbol=code, period="daily", start_date=start_date(),
                               end_date=datetime.now().strftime("%Y%m%d"))
        if len(d) < 6:
            ROW(f"| {name} | 数据暂缺 | — | — | — |")
            continue
        last = d.iloc[-1]
        amt = float(last["成交额"]) / 1e8
        avg5 = d["成交额"].iloc[-6:-1].astype(float).mean() / 1e8
        c5 = cum5(d["收盘"].tolist())
        ROW(f"| {name} | {last['收盘']} | {float(last['涨跌幅']):+.2f}% | "
            f"{c5:+.2f}% | {amt:.0f}亿 / 均{avg5:.0f}亿 |")

@safe("港股指数")
def hk_indices():
    import akshare as ak
    ROW("| 指数 | 收盘 | 当日 | 近5日累计 |")
    ROW("|---|---|---|---|")
    for sym, name in [("HSI", "恒生指数"), ("HSTECH", "恒生科技")]:
        d = ak.stock_hk_index_daily_em(symbol=sym)
        closes = d["latest"].astype(float).tolist()
        ROW(f"| {name} | {closes[-1]:.2f} | {pct(closes[-1], closes[-2]):+.2f}% | {cum5(closes):+.2f}% |")

@safe("美股指数（前一交易日收盘）")
def us_indices():
    import akshare as ak
    ROW("| 指数 | 收盘 | 当日 | 近5日累计 |")
    ROW("|---|---|---|---|")
    for sym, name in [(".DJI", "道琼斯"), (".INX", "标普500"), (".IXIC", "纳斯达克")]:
        d = ak.index_us_stock_sina(symbol=sym)
        closes = d["close"].astype(float).tolist()
        ROW(f"| {name} | {closes[-1]:.2f} | {pct(closes[-1], closes[-2]):+.2f}% | {cum5(closes):+.2f}% |")

@safe("行业板块涨跌（含5日累计与连续天数）")
def boards():
    import akshare as ak
    df = ak.stock_board_industry_name_em().sort_values("涨跌幅", ascending=False)

    def enrich(name, day):
        try:
            h = ak.stock_board_industry_hist_em(symbol=name, start_date=start_date(),
                                                end_date=datetime.now().strftime("%Y%m%d"),
                                                period="日k", adjust="")
            ch = h["涨跌幅"].astype(float).tolist()
            v = 1.0
            for r in ch[-5:]:
                v *= (1 + r / 100)
            c5 = (v - 1) * 100
            streak = 0
            for r in reversed(ch):
                if (day >= 0 and r > 0) or (day < 0 and r < 0):
                    streak += 1
                else:
                    break
            tag = f"连涨{streak}日" if day >= 0 else f"连跌{streak}日"
            return f"{name}({day:+.2f}%, 5日{c5:+.1f}%, {tag})"
        except Exception:
            return f"{name}({day:+.2f}%)"

    ROW("**领涨板块**：")
    ROW(", ".join(enrich(r["板块名称"], float(r["涨跌幅"])) for _, r in df.head(5).iterrows()))
    ROW("\n**领跌板块**：")
    ROW(", ".join(enrich(r["板块名称"], float(r["涨跌幅"])) for _, r in df.tail(5).iloc[::-1].iterrows()))

@safe("个股涨跌与成交")
def stocks():
    import akshare as ak
    df = ak.stock_zh_a_spot_em()
    df["涨跌幅"] = df["涨跌幅"].astype(float)
    df["成交额"] = df["成交额"].astype(float)
    df = df[df["最新价"] > 0]
    top = df.sort_values("涨跌幅", ascending=False).head(5)
    bot = df.sort_values("涨跌幅").head(5)
    vol = df.sort_values("成交额", ascending=False).head(5)
    ROW("**涨幅居前**：" + ", ".join(f"{r['名称']}({r['涨跌幅']:+.2f}%)" for _, r in top.iterrows()))
    ROW("\n**跌幅居前**：" + ", ".join(f"{r['名称']}({r['涨跌幅']:+.2f}%)" for _, r in bot.iterrows()))
    ROW("\n**成交额居前**：" + ", ".join(f"{r['名称']}({float(r['成交额'])/1e8:.0f}亿)" for _, r in vol.iterrows()))

@safe("南向资金（当日+近5日累计）")
def flows():
    import akshare as ak
    ROW("| 通道 | 当日净买额 | 近5日累计 |")
    ROW("|---|---|---|")
    tot5, last_date = 0.0, ""
    for sym, label in [("港股通沪", "港股通(沪)"), ("港股通深", "港股通(深)")]:
        d = ak.stock_hsgt_hist_em(symbol=sym)
        d["日期"] = d["日期"].astype(str).str[:10]
        pairs = [(dt, v) for dt, v in zip(d["日期"].tolist(), d["当日成交净买额"].tolist())
                 if v == v]  # 剔除 NaN（官方停披等）
        vals = [v for _, v in pairs]
        last_date = pairs[-1][0]
        c5 = sum(vals[-5:])
        tot5 += c5
        ROW(f"| {label} | {vals[-1]:+.2f}亿 | {c5:+.2f}亿 |")
    ROW(f"| **合计** | — | **{tot5:+.2f}亿** |")
    ROW(f"\n(最新数据日: {last_date}；北向资金官方自 2024 年起停止披露每日净买额)")

@safe("债基跟踪")
def bond_funds():
    import akshare as ak
    FUND_CODES = [
        ("006961", "南方中债7-10年国开A"),
        ("001235", "中银国有企业债A"),
        ("018192", "建信鑫弘180天持有A"),
        ("019204", "鹏华丰康债券C"),
    ]
    ROW("| 基金 | 最新净值 | 当日 | 近5日 | 近1月 | 今年以来 |")
    ROW("|---|---|---|---|---|---|")
    for code, name in FUND_CODES:
        try:
            d = ak.fund_open_fund_info_em(symbol=code, indicator="单位净值走势")
            d["净值日期"] = d["净值日期"].astype(str).str[:10]
            nav = d["单位净值"].astype(float).tolist()
            dates = d["净值日期"].tolist()
            last_date = dates[-1]

            def rng(n):
                return (nav[-1] / nav[-1 - n] - 1) * 100 if len(nav) > n else None

            year_now = last_date[:4]
            prev = [i for i, dt in enumerate(dates) if dt[:4] != year_now]
            ytd = (nav[-1] / nav[prev[-1]] - 1) * 100 if prev else None
            day = float(d["日增长率"].iloc[-1]) if str(d["日增长率"].iloc[-1]) != "nan" else None
            fmt = lambda v: f"{v:+.2f}%" if v is not None else "—"
            ROW(f"| {name}({code}) | {nav[-1]:.4f}（{last_date}） | {fmt(day)} | "
                f"{fmt(rng(5))} | {fmt(rng(22))} | {fmt(ytd)} |")
        except Exception as e:
            ROW(f"| {name}({code}) | 数据暂缺（{type(e).__name__}） | — | — | — | — |")
    ROW("\n(债基净值晚间陆续更新；当日列非最新交易日时为尚未披露，以最新可得为准)")

@safe("汇率与商品（含近5日变动）")
def fx():
    import akshare as ak
    end = datetime.now().strftime("%Y%m%d")

    def wk(series):
        s = [x for x in series if x == x]
        return pct(s[-1], s[-6]) if len(s) >= 6 else None

    try:
        d = ak.currency_boc_sina(symbol="美元", start_date=start_date(20), end_date=end)
        r = d.iloc[-1]
        mid = r["央行中间价"] if str(r.get("央行中间价", "")) != "nan" and r.get("央行中间价") is not None else r["中行折算价"]
        w = wk(([float(x) if str(x) != "nan" else float("nan") for x in d["央行中间价"]])
               if str(r.get("央行中间价", "")) != "nan" else [float(x) for x in d["中行折算价"]])
        wtxt = f"({w:+.2f}%)" if w is not None else ""
        ROW(f"- 美元/人民币: {float(mid)/100:.4f} {wtxt}（{r['日期']}，中行牌价，近5日）")
    except Exception as e:
        ROW(f"- 美元/人民币: 数据暂缺（{type(e).__name__}）")
    try:
        g = ak.spot_hist_sge(symbol="Au99.99")
        closes = g["close"].astype(float).tolist()
        w = wk(closes)
        wtxt = f"，近5日 {w:+.2f}%" if w is not None else ""
        ROW(f"- 上海金 Au99.99: {closes[-1]} 元/克{wtxt}（{str(g['date'].iloc[-1])[:10]}）")
    except Exception as e:
        ROW(f"- 黄金: 数据暂缺（{type(e).__name__}）")
    try:
        o = ak.futures_foreign_hist(symbol="CL")
        closes = o["close"].astype(float).tolist()
        w = wk(closes)
        wtxt = f"，近5日 {w:+.2f}%" if w is not None else ""
        ROW(f"- WTI 原油期货: {closes[-1]} 美元/桶{wtxt}（{str(o['date'].iloc[-1])[:10]}）")
    except Exception as e:
        ROW(f"- 原油: 数据暂缺（{type(e).__name__}）")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/tmp/market-data.md")
    args = ap.parse_args()
    ROW(f"<!-- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 数据接口: akshare(东方财富等) | "
        f"周期口径: 近5日=最近5个交易日(复利累计)；⚠️ A股交易时段内运行时当日数据为盘中值 -->")
    a_indices(); hk_indices(); us_indices(); boards(); stocks(); flows(); bond_funds(); fx()
    text = "\n".join(OUT_LINES)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(text)
    print(text)
    print(f"\n[done] 已写入 {args.out}", file=sys.stderr)

if __name__ == "__main__":
    main()
