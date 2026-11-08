#!/usr/bin/env python3
"""daily-market-data.py — 金融日报取数脚本（akshare）
输出 Markdown 片段（各板块表格），供每日 07:00 金融日报任务直接引用。
任一数据块失败输出『数据暂缺』，绝不中断整个脚本。
用法: python3 scripts/daily-market-data.py [--out /tmp/market-data.md]
"""
import sys, argparse, traceback
from datetime import datetime, timedelta

OUT_LINES = []
SEC = lambda t: OUT_LINES.append(f"\n### {t}\n")
ROW = lambda s: OUT_LINES.append(s)

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

def prev_trading_day_hint():
    today = datetime.now()
    d = today - timedelta(days=1)
    while d.weekday() >= 5:  # 跳过周末，具体节假日无法本地判断
        d -= timedelta(days=1)
    return d.strftime("%Y-%m-%d")

@safe("A股主要指数")
def a_indices():
    import akshare as ak
    df = ak.stock_zh_index_spot_em(symbol="沪深重要指数")
    want = ["上证指数", "深证成指", "创业板指", "科创50"]
    sub = df[df["名称"].isin(want)][["名称", "最新价", "涨跌幅", "成交额"]]
    ROW("| 指数 | 收盘 | 涨跌幅 | 成交额 |")
    ROW("|---|---|---|---|")
    for _, r in sub.iterrows():
        amt = float(r["成交额"]) / 1e8 if r["成交额"] else 0
        ROW(f"| {r['名称']} | {r['最新价']} | {r['涨跌幅']}% | {amt:.0f}亿 |")

@safe("港股指数")
def hk_indices():
    import akshare as ak
    df = ak.stock_hk_index_spot_em()
    sub = df[df["名称"] == "恒生指数"][["名称", "最新价", "涨跌幅"]]
    ROW("| 指数 | 收盘 | 涨跌幅 |")
    ROW("|---|---|---|")
    for _, r in sub.iterrows():
        ROW(f"| {r['名称']} | {r['最新价']} | {r['涨跌幅']}% |")
    # 恒生科技现货不在 spot 列表，用日行情接口
    try:
        tech = ak.stock_hk_index_daily_em(symbol="HSTECH")
        r, prev = tech.iloc[-1], tech.iloc[-2]
        pct = (float(r["close"]) - float(prev["close"])) / float(prev["close"]) * 100
        ROW(f"| 恒生科技 | {r['close']} | {pct:+.2f}% |")
    except Exception as e:
        print(f"[warn] 恒生科技: {e}", file=sys.stderr)

@safe("美股指数")
def us_indices():
    import akshare as ak
    df = ak.index_us_stock_sina(symbol=".INX")  # 先拉标普确认接口可用
    ROW("| 指数 | 最新 | 涨跌幅 |")
    ROW("|---|---|---|")
    for sym, label in [(".DJI", "道琼斯"), (".INX", "标普500"), (".IXIC", "纳斯达克")]:
        d2 = ak.index_us_stock_sina(symbol=sym)
        r = d2.iloc[-1]
        prev = d2.iloc[-2]["close"] if len(d2) > 1 else 0
        pct = (float(r["close"]) - float(prev)) / float(prev) * 100 if prev else 0
        ROW(f"| {label} | {r['close']} | {pct:+.2f}% |")

@safe("行业板块涨跌")
def boards():
    import akshare as ak
    df = ak.stock_board_industry_name_em()
    df = df.sort_values("涨跌幅", ascending=False)
    ROW("**领涨板块**：")
    ROW(", ".join(f"{r['板块名称']}({r['涨跌幅']:+.2f}%)" for _, r in df.head(5).iterrows()))
    ROW("\n**领跌板块**：")
    ROW(", ".join(f"{r['板块名称']}({r['涨跌幅']:+.2f}%)" for _, r in df.tail(5).iloc[::-1].iterrows()))

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

@safe("北向资金")
def north():
    import akshare as ak
    df = ak.stock_hsgt_fund_flow_summary_em()
    ROW(df.head(4).to_string(index=False))

@safe("汇率与商品")
def fx():
    import akshare as ak
    from datetime import datetime, timedelta
    end = datetime.now().strftime("%Y%m%d")
    start = (datetime.now() - timedelta(days=10)).strftime("%Y%m%d")
    # 美元人民币（中国银行牌价）
    try:
        d = ak.currency_boc_sina(symbol="美元", start_date=start, end_date=end)
        r = d.iloc[-1]
        mid = r["央行中间价"] if r.get("央行中间价") not in (None, "NaN") and str(r.get("央行中间价", "")) != "nan" else r["中行折算价"]
        ROW(f"- 美元/人民币: {float(mid)/100:.4f}（{r['日期']}，中行牌价）")
    except Exception as e:
        ROW(f"- 美元/人民币: 数据暂缺（{type(e).__name__}）")
    # 黄金（上海金交所）
    try:
        g = ak.spot_hist_sge(symbol="Au99.99")
        r = g.iloc[-1]
        ROW(f"- 上海金 Au99.99: {r['close']} 元/克（{r['date']}）")
    except Exception as e:
        ROW(f"- 黄金: 数据暂缺（{type(e).__name__}）")
    # 原油
    try:
        o = ak.futures_foreign_hist(symbol="CL")  # NYMEX WTI 主力
        r = o.iloc[-1]
        ROW(f"- WTI 原油期货: {r['close']} 美元/桶（{r['date']}）")
    except Exception as e:
        ROW(f"- 原油: 数据暂缺（{type(e).__name__}）")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/tmp/market-data.md")
    args = ap.parse_args()
    ROW(f"<!-- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 数据接口: akshare(东方财富等) -->")
    a_indices(); hk_indices(); us_indices(); boards(); stocks(); north(); fx()
    text = "\n".join(OUT_LINES)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(text)
    print(text)
    print(f"\n[done] 已写入 {args.out}", file=sys.stderr)

if __name__ == "__main__":
    main()
