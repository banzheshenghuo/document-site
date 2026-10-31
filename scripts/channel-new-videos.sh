#!/usr/bin/env bash
# channel-new-videos.sh - 列出 YouTube 频道在最近 N 天内发布、且尚未入库的视频
#
# 数据源用频道 RSS（带精确 UTC 发布时间），比频道页的 "1 day ago" 可靠。
# 已入库判定（任一命中即视为已有，不再重复生成）：
#   1. src/content/posts/*.md 中出现该 video_id
#   2. public/transcripts/<video_id>/ 目录存在
#   3. ~/yt2text_output/*.meta.json 中出现该 video_id
#
# 用法:
#   channel-new-videos.sh [--days N] [--channel UC...] [--site DIR] [--json] [--all]
#
#   --days N     时间窗口：含今天在内往前推 N 天（默认 2 = 昨天 + 今天）
#   --all        忽略时间窗口，列出 RSS 中全部条目（配合去重标记）
#   --json       输出 JSON 数组
#
# 退出码: 0 正常（即使没有新视频）

set -euo pipefail

CHANNEL_ID="${YT_CHANNEL_ID:-UC8gZZWIWmBuCb_gzC8DUrvw}"
SITE_DIR="${YT_SITE_DIR:-/Users/zq/Documents/codebase/ai-document}"
DAYS=2
OUTPUT_JSON=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --channel) CHANNEL_ID="$2"; shift 2 ;;
        --site)    SITE_DIR="$2";   shift 2 ;;
        --days)    DAYS="$2";       shift 2 ;;
        --all)     DAYS=99999;      shift ;;
        --json)    OUTPUT_JSON=true; shift ;;
        -h|--help)
            sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'
            exit 0 ;;
        *) echo "未知参数: $1" >&2; exit 1 ;;
    esac
done

command -v curl >/dev/null || { echo "缺少 curl" >&2; exit 1; }
command -v python3 >/dev/null || { echo "缺少 python3" >&2; exit 1; }

# 与 yt2text 一致的代理探测（macOS 系统代理 + 环境变量）
detect_proxy() {
    local p="${https_proxy:-${HTTPS_PROXY:-${http_proxy:-${HTTP_PROXY:-}}}}"
    if [[ -n "$p" ]]; then echo "$p"; return; fi
    if command -v scutil >/dev/null 2>&1; then
        local en port
        en=$(scutil --proxy 2>/dev/null | awk '/^ *HTTPEnable/{print $3}' | head -1)
        port=$(scutil --proxy 2>/dev/null | awk '/^ *HTTPPort/{print $3}' | head -1)
        if [[ "$en" == "1" && -n "$port" ]]; then echo "http://127.0.0.1:${port}"; return; fi
    fi
    echo ""
}

PROXY=$(detect_proxy)
FEED=$(mktemp "${TMPDIR:-/tmp}/ytfeed.XXXXXX")
trap 'rm -f "$FEED"' EXIT

CURL_ARGS=(-fsS --max-time 45 --retry 2 --retry-delay 2)
[[ -n "$PROXY" ]] && CURL_ARGS+=(-x "$PROXY")

if ! curl "${CURL_ARGS[@]}" \
    "https://www.youtube.com/feeds/videos.xml?channel_id=${CHANNEL_ID}" -o "$FEED"; then
    echo "拉取频道 RSS 失败（channel=$CHANNEL_ID, proxy=${PROXY:-none}）" >&2
    exit 1
fi

python3 - "$FEED" "$SITE_DIR" "$DAYS" "$OUTPUT_JSON" <<'PY'
import datetime
import glob
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

feed_path, site_dir, days, output_json = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4] == "true"
NS = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015"}

posts_dir = os.path.join(site_dir, "src", "content", "posts")
shots_dir = os.path.join(site_dir, "public", "transcripts")
output_dir = os.path.expanduser("~/yt2text_output")

def existing_ids():
    ids = set()
    if os.path.isdir(posts_dir):
        try:
            out = subprocess.run(["grep", "-rhoE", r"watch\?v=[A-Za-z0-9_-]{11}", posts_dir],
                                 capture_output=True, text=True, check=False).stdout
            ids.update(m.split("=", 1)[1] for m in re.findall(r"watch\?v=[A-Za-z0-9_-]{11}", out))
        except OSError:
            pass
    if os.path.isdir(shots_dir):
        ids.update(os.listdir(shots_dir))
    for meta in glob.glob(os.path.join(output_dir, "*.meta.json")):
        try:
            with open(meta, encoding="utf-8") as fh:
                vid = json.load(fh).get("video_id")
            if vid:
                ids.add(vid)
        except Exception:
            continue
    return ids

known = existing_ids()
now = datetime.datetime.now().astimezone()
start = (now - datetime.timedelta(days=days - 1)).replace(hour=0, minute=0, second=0, microsecond=0)

root = ET.parse(feed_path).getroot()
channel = (root.find("a:title", NS).text or "").strip()
entries = []

for e in root.findall("a:entry", NS):
    vid = (e.find("yt:videoId", NS).text or "").strip()
    if not vid:
        continue
    published_raw = (e.find("a:published", NS).text or "").strip()
    try:
        published = datetime.datetime.fromisoformat(published_raw).astimezone()
    except ValueError:
        continue
    if published < start:
        continue
    entries.append({
        "video_id": vid,
        "title": (e.find("a:title", NS).text or "").strip(),
        "published": published.isoformat(timespec="seconds"),
        "published_local": published.strftime("%Y-%m-%d %H:%M"),
        "url": "https://www.youtube.com/watch?v=" + vid,
        "known": vid in known,
    })

new = [x for x in entries if not x["known"]]

if output_json:
    print(json.dumps({"channel": channel, "window_days": days, "new": new, "already": [x for x in entries if x["known"]]},
                     ensure_ascii=False, indent=2))
else:
    print(f"channel: {channel} | window: {days} 天（含今天）| 命中 {len(entries)} 条，新增 {len(new)} 条")
    for x in entries:
        mark = "已有" if x["known"] else "新增"
        print(f"[{mark}] {x['video_id']}  {x['published_local']}  {x['title'][:80]}")
PY
