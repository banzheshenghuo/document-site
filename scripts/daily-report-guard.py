#!/usr/bin/env python3
"""daily-report-guard.py — 金融日报漏跑自检

检查「最近一个交易日」的日报是否已生成，用于发现定时任务因机器睡眠而未派发。
周末与节假日不产生日报属于正常情况，不会误报。

用法:
  python3 scripts/daily-report-guard.py             # 巡检最近一个交易日（用于 cron 第0步）
  python3 scripts/daily-report-guard.py 2026-11-11  # 检查指定日期
退出码: 0=已存在或无需生成(非交易日), 1=缺失
"""
import sys, glob, os
from datetime import datetime, timedelta

POSTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "content", "posts")

# 覆盖调休的额外休市日（有调休安排时在此补充）
EXTRA_HOLIDAYS = {
    "2026-01-01", "2026-01-02",                                    # 元旦
    "2026-02-16", "2026-02-17", "2026-02-18", "2026-02-19", "2026-02-20",  # 春节
    "2026-04-06",                                                  # 清明
    "2026-05-01", "2026-05-04", "2026-05-05",                      # 劳动节
    "2026-06-19",                                                  # 端午
    "2026-09-25",                                                  # 中秋
    "2026-10-01", "2026-10-02", "2026-10-05", "2026-10-06", "2026-10-07",  # 国庆
}


def is_trading_day(date_str):
    """粗略判断：工作日且不在休市表内。仅用于调度决策，不用于取数校验。"""
    d = datetime.strptime(date_str, "%Y-%m-%d")
    if d.weekday() >= 5:          # 5=周六, 6=周日
        return False
    return date_str not in EXTRA_HOLIDAYS


def check(date_str):
    return glob.glob(os.path.join(POSTS, f"{date_str}-*[[]金融日报[]]*.md"))


def last_trading_day(before=None, max_lookback=10):
    """返回 before 之前（含）最近的一个交易日。"""
    d = before or datetime.now()
    for _ in range(max_lookback):
        s = d.strftime("%Y-%m-%d")
        if is_trading_day(s):
            return s
        d -= timedelta(days=1)
    return None


def main():
    explicit = len(sys.argv) > 1
    if explicit:
        target = sys.argv[1]
        if not is_trading_day(target):
            print(f"SKIP  {target} 非交易日（周末/休市），无需日报")
            return 0
    else:
        target = last_trading_day(datetime.now() - timedelta(days=1))

    if target is None:
        print("SKIP  回溯 10 天内未找到交易日")
        return 0

    hits = check(target)
    if hits:
        print(f"OK  {target} 日报已存在: {os.path.basename(hits[0])}")
        return 0
    hint = "（机器睡眠导致定时任务未派发？）" if not explicit else ""
    print(f"MISSING  {target} 日报缺失{hint}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
