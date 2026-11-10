#!/usr/bin/env python3
"""backfill-market-data.py — 按交易日回补历史行情数据（金融日报补发用）
用法: python3 scripts/backfill-market-data.py 2026-11-02 2026-11-06  → 输出 /tmp/backfill/market-<date>.md
每个数据块失败标注"数据暂缺"，不中断。
"""
import sys, os, argparse
from datetime import datetime, timedelta

def safe(fn):
    def wrap(*a, **k):
        try:
            return fn(*a, **k)
        except Exception as e:
            print(f"[warn] {fn.__name__}: {type(e).__name__} {e}", file=sys.stderr)
            return None
    return wrap

@safe
def a_indices(date_str):
    import akshare as ak
    rows = []
    for sym, name in [("000001","上证指数"),("399001","深证成指"),("399006","创业板指"),("000688","科创50")]:
        d = ak.index_zh_a_hist(symbol=sym, period="daily", start_date="20261025", end_date=date_str.replace("-",""))
        r = d.iloc[-1]
        amt = float(r["成交额"])/1e8
        rows.append(f"| {name} | {r['收盘']} | {float(r['涨跌幅']):+.2f}% | {amt:.0f}亿 |")
    out = ["| 指数 | 收盘 | 涨跌幅 | 成交额 |", "|---|---|---|---|"] + rows
    return "### A股\n\n" + "\n".join(out)

@safe
def hk_indices(date_str):
    import akshare as ak
    out = ["| 指数 | 收盘 | 涨跌幅 |", "|---|---|---|"]
    for sym, name in [("HSI","恒生指数"),("HSTECH","恒生科技")]:
        d = ak.stock_hk_index_daily_em(symbol=sym)
        d = d[d["date"].astype(str).str[:10] <= date_str]
        r, prev = d.iloc[-1], d.iloc[-2]
        close = r["latest"] if "latest" in d.columns else r["close"]
        pc = prev["latest"] if "latest" in d.columns else prev["close"]
        pct = (float(close)-float(pc))/float(pc)*100
        out.append(f"| {name} | {close} | {pct:+.2f}% |")
    return "### 港股\n\n" + "\n".join(out)

@safe
def us_indices(date_str):
    import akshare as ak
    out = ["| 指数 | 收盘 | 涨跌幅 |", "|---|---|---|"]
    for sym, name in [(".DJI","道琼斯"),(".INX","标普500"),(".IXIC","纳斯达克")]:
        d = ak.index_us_stock_sina(symbol=sym)
        d["date"] = d["date"].astype(str).str[:10]
        d = d[d["date"] <= date_str]
        r, prev = d.iloc[-1], d.iloc[-2]
        pct = (float(r["close"])-float(prev["close"]))/float(prev["close"])*100
        day = r["date"]
        out.append(f"| {name} | {r['close']} | {pct:+.2f}% |")
        if day != date_str:
            out.append(f"<!-- 注意: {name} 最新数据日为 {day} -->")
    return "### 美股\n\n" + "\n".join(out)

@safe
def flows(date_str):
    import akshare as ak
    lines = []
    for sym, label in [("港股通沪", "南向·港股通(沪)"), ("港股通深", "南向·港股通(深)")]:
        try:
            d = ak.stock_hsgt_hist_em(symbol=sym)
            d["日期"] = d["日期"].astype(str).str[:10]
            r = d[d["日期"] == date_str]
            if len(r):
                net = r.iloc[-1].get("当日成交净买额")
                if net is not None and str(net) != "nan":
                    lines.append(f"- {label}: 净买额 {float(net):+.2f} 亿")
        except Exception as e:
            print(f"[warn] flows {sym}: {e}", file=sys.stderr)
    lines.append("- 北向（沪股通/深股通）: 官方自 2024 年起停止披露每日净买额，数据暂缺")
    return "### 南北向资金\n\n" + "\n".join(lines)

@safe
def fx_gold_oil(date_str):
    import akshare as ak
    out = []
    start = (datetime.strptime(date_str, "%Y-%m-%d") - timedelta(days=10)).strftime("%Y%m%d")
    end = date_str.replace("-", "")
    try:
        d = ak.currency_boc_sina(symbol="美元", start_date=start, end_date=end)
        r = d.iloc[-1]
        mid = r.get("央行中间价")
        val = mid if mid not in (None,) and str(mid) != "nan" else r["中行折算价"]
        out.append(f"- 美元/人民币: {float(val)/100:.4f}（{r['日期']}，中行牌价）")
    except Exception as e:
        out.append(f"- 美元/人民币: 数据暂缺（{type(e).__name__}）")
    try:
        g = ak.spot_hist_sge(symbol="Au99.99")
        g["date"] = g["date"].astype(str).str[:10]
        r = g[g["date"] <= date_str].iloc[-1]
        out.append(f"- 上海金 Au99.99: {r['close']} 元/克（{r['date']}）")
    except Exception as e:
        out.append(f"- 黄金: 数据暂缺（{type(e).__name__}）")
    try:
        o = ak.futures_foreign_hist(symbol="CL")
        o["date"] = o["date"].astype(str).str[:10]
        r = o[o["date"] <= date_str].iloc[-1]
        out.append(f"- WTI 原油期货: {r['close']} 美元/桶（{r['date']}）")
    except Exception as e:
        out.append(f"- 原油: 数据暂缺（{type(e).__name__}）")
    return "### 汇率与商品\n\n" + "\n".join(out)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dates", nargs="+")
    ap.add_argument("--out", default="/tmp/backfill")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    for date_str in args.dates:
        parts = [f"<!-- 数据日: {date_str} | 生成: {datetime.now().strftime('%F %T')} -->"]
        titles = [("A股主要指数", a_indices), ("港股指数", hk_indices), ("美股指数", us_indices), ("南北向资金", flows), ("汇率与商品", fx_gold_oil)]
        for title, fn in titles:
            block = fn(date_str)
            if block:
                parts.append(block)
            else:
                parts.append(f"### {title}\n\n数据暂缺\n")
        text = "\n\n".join(parts)
        path = os.path.join(args.out, f"market-{date_str}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"[done] {path}")

if __name__ == "__main__":
    main()
