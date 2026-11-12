#!/usr/bin/env python3
"""daily-report-guard.py — 金融日报漏跑自检
检查今天（或指定日期）的日报是否已生成。用于发现定时任务因机器睡眠而未派发。
用法:
  python3 scripts/daily-report-guard.py           # 检查今天
  python3 scripts/daily-report-guard.py 2026-11-11 # 检查指定日期
退出码: 0=已存在, 1=缺失
"""
import sys, glob, os
from datetime import datetime, timedelta

POSTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "content", "posts")

def check(date_str):
    hits = glob.glob(os.path.join(POSTS, f"{date_str}-*[[]金融日报[]]*.md"))
    return hits

def main():
    if len(sys.argv) > 1:
        target = sys.argv[1]
        dates = [target]
    else:
        now = datetime.now()
        dates = [now.strftime("%Y-%m-%d"),
                 (now - timedelta(days=1)).strftime("%Y-%m-%d")]

    if len(sys.argv) == 1:
        # 日常巡检：今天缺失属正常（尚未到 21:00），只看昨天
        target = dates[1]
        hits = check(target)
        if hits:
            print(f"OK  {target} 日报已存在: {os.path.basename(hits[0])}")
            return 0
        print(f"MISSING  {target} 日报缺失（机器睡眠导致定时任务未派发？）")
        return 1
    else:
        hits = check(dates[0])
        if hits:
            print(f"OK  {dates[0]} 日报已存在: {os.path.basename(hits[0])}")
            return 0
        print(f"MISSING  {dates[0]} 日报缺失")
        return 1

if __name__ == "__main__":
    sys.exit(main())
