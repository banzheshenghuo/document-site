#!/usr/bin/env python3
"""daily-market-data.py — 金融日报取数脚本（akshare + 腾讯/东财兜底）
除当日数据外，附周期对比：指数近5日累计、成交额 vs 5日均量（东财失败时用腾讯快照+本地缓存）、
市场宽度（涨跌家数/涨跌停/两市成交额）、板块5日累计与连续天数、南向资金当日+近5日累计、
10Y国债收益率、债基区间收益（日增长率链式复利口径，分红日不再失真）、汇率/金/油周变动。
任一数据块失败输出『数据暂缺』，绝不中断整个脚本。
变更（2026-11-28 V3）：债基区间收益改日增长率链式复利；新增市场宽度/10Y国债；
腾讯快照第三源+成交额本地滚动缓存；涨跌幅榜剔除北交所/新股/ST；北向停披行移除；
各块标注数据日。
用法: python3 scripts/daily-market-data.py [--out /tmp/market-data.md]
"""
import sys, os, csv, json, argparse, subprocess
from datetime import datetime, timedelta

OUT_LINES = []
SEC = lambda t: OUT_LINES.append(f"\n### {t}\n")
ROW = lambda s: OUT_LINES.append(s)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AMT_CACHE = os.path.join(SCRIPT_DIR, ".cache", "index_amount.csv")
QL_BOND10Y = "/Users/zq/Documents/ob/zq/金融/quantlab/cache/series/bond10y.parquet"

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

def _curl_out(url):
    r = subprocess.run(["curl", "-s", "--max-time", "15", url], capture_output=True)
    if r.returncode != 0 or not r.stdout:
        raise RuntimeError(f"curl 失败({r.returncode}): {url[:70]}")
    return r.stdout

def _date_note(dates):
    """若干数据日 -> 尾注文本；全部为 None 返回空串"""
    ds = sorted({d for d in dates if d})
    if not ds:
        return ""
    last = ds[-1]
    tag = "，非今日" if last != datetime.now().strftime("%Y-%m-%d") else ""
    return f"\n(数据日: {last}{tag})"

# ---------------- 成交额本地滚动缓存（东财失败时支撑 5 日均量） ----------------

def _cache_amt(code, date, amount_yi):
    try:
        os.makedirs(os.path.dirname(AMT_CACHE), exist_ok=True)
        rows = []
        if os.path.exists(AMT_CACHE):
            with open(AMT_CACHE, encoding="utf-8") as f:
                rows = [r for r in csv.reader(f) if len(r) == 3 and r[0] != "date"]
        rows = [r for r in rows if not (r[0] == date and r[1] == code)]
        rows.append([date, code, f"{amount_yi:.2f}"])
        rows.sort(key=lambda r: (r[1], r[0]))
        with open(AMT_CACHE, "w", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["date", "code", "amount_yi"])
            w.writerows(rows[-400:])
    except Exception as e:
        print(f"[warn] amt cache write: {e}", file=sys.stderr)

def _avg5_amt_from_cache(code, before_date):
    """before_date 之前最近 5 个成交日的成交额均值（亿）；不足 5 条返回 None"""
    try:
        if not os.path.exists(AMT_CACHE):
            return None
        vals = []
        with open(AMT_CACHE, encoding="utf-8") as f:
            for r in csv.reader(f):
                if len(r) == 3 and r[1] == code and r[0] < before_date:
                    vals.append((r[0], float(r[2])))
        vals.sort()
        if len(vals) < 5:
            return None
        return sum(v for _, v in vals[-5:]) / 5
    except Exception:
        return None

# ---------------- 指数三源：东财 → 腾讯快照 → 新浪 ----------------

def _idx_em(ak, code):
    """东财路径：含涨跌幅与成交额，首选。返回 (close, day, c5, amt, avg5, date)"""
    d = ak.index_zh_a_hist(symbol=code, period="daily", start_date=start_date(),
                           end_date=datetime.now().strftime("%Y%m%d"))
    if len(d) < 6:
        raise ValueError("insufficient rows")
    last = d.iloc[-1]
    amt = float(last["成交额"]) / 1e8
    avg5 = d["成交额"].iloc[-6:-1].astype(float).mean() / 1e8
    date = str(d["日期"].iloc[-1])[:10]
    return float(last["收盘"]), float(last["涨跌幅"]), cum5(d["收盘"].tolist()), amt, avg5, date

def _tencent_snapshot(sym):
    """腾讯实时快照：返回 (close, day%, amt亿, datetime_str)。收盘后为当日最终值。"""
    txt = _curl_out(f"https://qt.gtimg.cn/q={sym}").decode("gbk", "ignore")
    parts = txt.split('"')[1].split("~")
    close, prev = float(parts[3]), float(parts[4])
    amt = float(parts[37]) / 1e4  # 万 -> 亿
    return close, (close / prev - 1) * 100, amt, parts[30]

def _tencent_kline_closes(sym, n=8):
    j = json.loads(_curl_out(f"https://web.ifzq.gtimg.cn/appstock/app/kline/kline?param={sym},day,,,{n}"))
    rows = j["data"][sym].get("day") or []
    return [(r[0], float(r[2])) for r in rows]

def _idx_tencent(sym, code):
    """腾讯路径：快照给当日收盘/成交额，K线给近5日累计；5日均量来自本地缓存。"""
    close, day, amt, _ts = _tencent_snapshot(sym)
    kl = _tencent_kline_closes(sym, 8)
    if len(kl) < 6:
        raise ValueError("tencent kline insufficient")
    closes = [c for _, c in kl]
    date = kl[-1][0]
    avg5 = _avg5_amt_from_cache(code, date)
    return closes[-1], day, (closes[-1] / closes[-6] - 1) * 100, amt, avg5, date

def _idx_sina(ak, sina_sym):
    """新浪降级：无成交额（用成交量亿股代替），涨跌幅由收盘价推算。"""
    d = ak.stock_zh_index_daily(symbol=sina_sym)
    closes = d["close"].astype(float).tolist()
    vols = d["volume"].astype(float).tolist()
    if len(closes) < 6:
        raise ValueError("insufficient rows")
    day = pct(closes[-1], closes[-2])
    vol = vols[-1] / 1e8
    avg5 = sum(vols[-6:-1]) / 5 / 1e8
    date = str(d["date"].iloc[-1])[:10]
    return closes[-1], day, cum5(closes), vol, avg5, date

@safe("A股主要指数")
def a_indices():
    import akshare as ak
    codes = [("000001", "上证指数", "sh000001"), ("399001", "深证成指", "sz399001"),
             ("399006", "创业板指", "sz399006"), ("000688", "科创50", "sh000688")]
    ROW("| 指数 | 收盘 | 当日 | 近5日累计 | 成交额(vs 5日均) |")
    ROW("|---|---|---|---|---|")
    dates = []
    for code, name, sym in codes:
        got = None
        try:
            close, day, c5, amt, avg5, date = _idx_em(ak, code)
            if date == datetime.now().strftime("%Y-%m-%d"):
                _cache_amt(code, date, amt)
            ROW(f"| {name} | {close} | {day:+.2f}% | {c5:+.2f}% | {amt:.0f}亿 / 均{avg5:.0f}亿 |")
            got = date
        except Exception:
            try:
                close, day, c5, amt, avg5, date = _idx_tencent(sym, code)
                note = f"均{avg5:.0f}亿(缓存)" if avg5 is not None else "5日均待缓存累积"
                ROW(f"| {name} | {close:.2f} | {day:+.2f}% | {c5:+.2f}% | {amt:.0f}亿 / {note} |")
                got = date
            except Exception:
                try:
                    close, day, c5, vol, avg5, date = _idx_sina(ak, sym)
                    ROW(f"| {name} | {close:.2f} | {day:+.2f}% | {c5:+.2f}% | "
                        f"量{vol:.1f}亿股 / 均{avg5:.1f}亿股※ |")
                    got = date
                except Exception as e:
                    ROW(f"| {name} | 数据暂缺（{type(e).__name__}） | — | — | — |")
        dates.append(got)
    ROW(_date_note(dates) + "\n(※ 东财与腾讯均不可用时降级新浪源，仅有成交量无成交额；成交额缓存由东财成功日自动累积)")

@safe("港股指数")
def hk_indices():
    import akshare as ak
    ROW("| 指数 | 收盘 | 当日 | 近5日累计 |")
    ROW("|---|---|---|---|")
    dates = []
    for sym, name in [("HSI", "恒生指数"), ("HSTECH", "恒生科技")]:
        closes, day_chg, last_date = None, None, None
        try:
            d = ak.stock_hk_index_daily_em(symbol=sym)
            closes = d["latest"].astype(float).tolist()
            dcol = "date" if "date" in d.columns else d.columns[0]
            last_date = str(d[dcol].iloc[-1])[:10]
        except Exception:
            try:
                d = ak.stock_hk_index_daily_sina(symbol=sym)
                closes = d["close"].astype(float).tolist()
                # 新浪日线 T+1 才更新，若最新日不是今天则用 spot 补当日
                d["date"] = d["date"].astype(str).str[:10]
                last_date = d["date"].iloc[-1]
                if last_date != datetime.now().strftime("%Y-%m-%d"):
                    spot = ak.stock_hk_index_spot_sina()
                    row = spot[spot["代码"] == sym]
                    if len(row):
                        closes = closes + [float(row.iloc[0]["最新价"])]
            except Exception:
                pass
        if closes and len(closes) >= 2:
            ROW(f"| {name} | {closes[-1]:.2f} | {pct(closes[-1], closes[-2]):+.2f}% | {cum5(closes):+.2f}% |")
            dates.append(last_date)
        else:
            ROW(f"| {name} | 数据暂缺 | — | — |")
    ROW(_date_note(dates))

@safe("美股指数（前一交易日收盘）")
def us_indices():
    import akshare as ak
    ROW("| 指数 | 收盘 | 当日 | 近5日累计 |")
    ROW("|---|---|---|---|")
    dates = []
    for sym, name in [(".DJI", "道琼斯"), (".INX", "标普500"), (".IXIC", "纳斯达克")]:
        try:
            d = ak.index_us_stock_sina(symbol=sym)
            d["date"] = d["date"].astype(str).str[:10]
            closes = d["close"].astype(float).tolist()
            last_date = d["date"].iloc[-1]
            ROW(f"| {name} | {closes[-1]:.2f} | {pct(closes[-1], closes[-2]):+.2f}% | {cum5(closes):+.2f}% |")
            dates.append(last_date)
        except Exception as e:
            ROW(f"| {name} | 数据暂缺（{type(e).__name__}） | — | — |")
    ROW(_date_note(dates))

@safe("行业板块涨跌（含5日累计与连续天数）")
def boards():
    import akshare as ak
    try:
        df = ak.stock_board_industry_name_em().sort_values("涨跌幅", ascending=False)
        name_col, chg_col = "板块名称", "涨跌幅"
    except Exception:
        # 新浪降级：无历史序列，只能看当日（连续天数/5日累计不可得）
        df = ak.stock_sector_spot(indicator="新浪行业").sort_values("涨跌幅", ascending=False)
        name_col, chg_col = "板块", "涨跌幅"
        ROW("（东财接口不可用，降级新浪源：无5日累计与连续天数；新浪为盘中快照，须用当日收评交叉验证）")

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
    ROW(", ".join(enrich(r[name_col], float(r[chg_col])) for _, r in df.head(5).iterrows()))
    ROW("\n**领跌板块**：")
    ROW(", ".join(enrich(r[name_col], float(r[chg_col])) for _, r in df.tail(5).iloc[::-1].iterrows()))

@safe("个股涨跌与成交（含市场宽度）")
def stocks():
    import pandas as pd
    import akshare as ak
    try:
        df = ak.stock_zh_a_spot_em()
        src = "em"
    except Exception:
        # 新浪降级（盘中快照，收盘后时段可用；板块/个股结论须用当日收评交叉验证）
        df = ak.stock_zh_a_spot()[["名称", "涨跌幅", "成交额", "最新价"]]
        src = "sina"
        ROW("（东财接口不可用，降级新浪源；榜单须用当日收评交叉验证）")
    for c in ("涨跌幅", "成交额", "最新价"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df[(df["最新价"] > 0) & df["涨跌幅"].notna()]
    has_code = "代码" in df.columns

    # ---- 市场宽度：涨跌家数 / 涨跌停 / 两市成交额（收盘后为最终值） ----
    up = int((df["涨跌幅"] > 0).sum()); down = int((df["涨跌幅"] < 0).sum())
    flat = int((df["涨跌幅"] == 0).sum())
    med = float(df["涨跌幅"].median())
    amt_total = float(df["成交额"].sum()) / 1e8
    ROW(f"**市场宽度**：上涨 {up} / 下跌 {down} / 平盘 {flat}（全市场 {len(df)} 只，中位数 {med:+.2f}%）")
    ROW(f"**两市成交额**：约 {amt_total / 1e4:.2f} 万亿元" + ("" if src == "em" else "（新浪口径，需收评交叉验证）"))
    if has_code:
        code = df["代码"].astype(str)
        is_main = code.str.startswith(("00", "60")); is_20 = code.str.startswith(("30", "68"))
        zt = int(((is_main & (df["涨跌幅"] >= 9.9)) | (is_20 & (df["涨跌幅"] >= 19.9))).sum())
        dtb = int(((is_main & (df["涨跌幅"] <= -9.9)) | (is_20 & (df["涨跌幅"] <= -19.9))).sum())
        ROW(f"**涨跌停**：涨停约 {zt} 家 / 跌停约 {dtb} 家（主板±10%、创科±20%口径，收盘后为最终值）")

    # ---- 涨跌幅榜：剔除北交所(4/8/92开头)、N/C 新股、ST，降噪 ----
    def rank_view(d):
        m = pd.Series(True, index=d.index)
        if has_code:
            m &= ~d["代码"].astype(str).str.match(r"^(4|8|92)")
        m &= ~d["名称"].astype(str).str.contains("ST", na=False)
        m &= ~d["名称"].astype(str).str.match(r"^[NC]", na=False)
        return d[m]

    top = rank_view(df).sort_values("涨跌幅", ascending=False).head(5)
    bot = rank_view(df).sort_values("涨跌幅").head(5)
    vol = df.sort_values("成交额", ascending=False).head(5)
    ROW("\n**涨幅居前**(剔除北交所/新股/ST)："
        + ", ".join(f"{r['名称']}({r['涨跌幅']:+.2f}%)" for _, r in top.iterrows()))
    ROW("\n**跌幅居前**(同上剔除)："
        + ", ".join(f"{r['名称']}({r['涨跌幅']:+.2f}%)" for _, r in bot.iterrows()))
    ROW("\n**成交额居前**："
        + ", ".join(f"{r['名称']}({float(r['成交额'])/1e8:.0f}亿)" for _, r in vol.iterrows()))

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
                 if v == v]  # 剔除 NaN
        vals = [v for _, v in pairs]
        last_date = pairs[-1][0]
        c5 = sum(vals[-5:])
        tot5 += c5
        ROW(f"| {label} | {vals[-1]:+.2f}亿 | {c5:+.2f}亿 |")
    ROW(f"| **合计** | — | **{tot5:+.2f}亿** |")
    ROW(f"\n(最新数据日: {last_date}；北向资金官方自 2024 年起停止披露每日净买额，已不再列示)")

@safe("债市（10年期国债收益率）")
def bond10y():
    """首选 quantlab 缓存（每交易日 18:00 自动刷新）；不可用时走东财 datacenter 兜底。"""
    vals, dates, src = None, None, ""
    try:
        import pandas as pd
        df = pd.read_parquet(QL_BOND10Y).sort_values("date").tail(7)
        vals = df["bond_10y"].astype(float).tolist()
        dates = [str(d)[:10] for d in df["date"].tolist()]
        src = "quantlab 缓存"
    except Exception as e:
        print(f"[warn] bond10y parquet: {type(e).__name__} {e}", file=sys.stderr)
        flt = "%28SOLAR_DATE%3E%3D%27" + start_date(15) + "%27%29"
        url = ("https://datacenter-web.eastmoney.com/api/data/v1/get"
               "?pageSize=30&pageNumber=1&reportName=RPTA_WEB_TREASURYYIELD"
               "&columns=ALL&source=WEB&client=WEB&sortColumns=SOLAR_DATE&sortTypes=-1"
               f"&filter={flt}")
        j = json.loads(_curl_out(url).decode("utf-8", "ignore"))
        lst = (j.get("result") or {}).get("data") or []
        pairs = sorted({(x["SOLAR_DATE"][:10], float(x["EMM00166466"]))
                        for x in lst if x.get("EMM00166466") is not None})
        if len(pairs) < 2:
            raise ValueError("EM bond10y insufficient")
        vals = [v for _, v in pairs]
        dates = [d for d, _ in pairs]
        src = "东财 datacenter"
    day_bp = (vals[-1] - vals[-2]) * 100
    c5 = f"，近5日 {(vals[-1] - vals[-6]) * 100:+.1f}bp" if len(vals) >= 6 else ""
    ROW(f"- 10年期国债: {vals[-1]:.4f}%（{dates[-1]}），当日 {day_bp:+.1f}bp{c5}（{src}）")

@safe("债基跟踪")
def bond_funds():
    """区间收益 = 日增长率链式复利（含分红再投资口径）。
    2026-11-28 前用单位净值比值，分红日（如 006961 2026-06-15 每份派 0.036）被记成单日大跌，
    YTD 长期低估约 3.5 个百分点，已废弃。"""
    import akshare as ak
    FUND_CODES = [
        ("006961", "南方中债7-10年国开A"),
        ("001235", "中银国有企业债A"),
        ("018192", "建信鑫弘180天持有A"),
        ("019204", "鹏华丰康债券C"),
    ]
    ROW("| 基金 | 最新净值 | 当日 | 近5日 | 近1月 | 今年以来 |")
    ROW("|---|---|---|---|---|---|")

    def chain(g):
        v = 1.0
        for x in g:
            if x != x:      # NaN：区间内有未披露日，区间口径不可信
                return None
            v *= (1 + x / 100)
        return (v - 1) * 100

    fmt = lambda v: f"{v:+.2f}%" if v is not None else "—"
    for code, name in FUND_CODES:
        try:
            d = ak.fund_open_fund_info_em(symbol=code, indicator="单位净值走势")
            d["净值日期"] = d["净值日期"].astype(str).str[:10]
            dates = d["净值日期"].tolist()
            nav = d["单位净值"].astype(float).tolist()
            g = d["日增长率"].astype(float).tolist()
            last_date = dates[-1]
            day = g[-1] if g[-1] == g[-1] else pct(nav[-1], nav[-2])
            year = last_date[:4]
            ytd = chain([x for dt, x in zip(dates, g) if dt[:4] == year])
            ROW(f"| {name}({code}) | {nav[-1]:.4f}（{last_date}） | {fmt(day)} | "
                f"{fmt(chain(g[-5:]))} | {fmt(chain(g[-22:]))} | {fmt(ytd)} |")
        except Exception as e:
            ROW(f"| {name}({code}) | 数据暂缺（{type(e).__name__}） | — | — | — | — |")
    ROW("\n(区间收益=日增长率链式复利，含分红口径；债基净值晚间陆续更新；当日列非最新交易日时为尚未披露，以最新可得为准)")

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
    ROW(f"<!-- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 数据接口: akshare(东财/新浪) + 腾讯快照 + 东财datacenter | "
        f"周期口径: 近5日=最近5个交易日(复利累计)；债基区间=日增长率链式复利(含分红)；北向停披已移除；"
        f"⚠️ A股交易时段内运行时当日数据为盘中值 -->")
    a_indices(); hk_indices(); us_indices(); boards(); stocks(); flows(); bond10y(); bond_funds(); fx()
    text = "\n".join(OUT_LINES)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(text)
    print(text)
    print(f"\n[done] 已写入 {args.out}", file=sys.stderr)

if __name__ == "__main__":
    main()
