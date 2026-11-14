#!/usr/bin/env bash
# 旧设备：打包文档库周边组件（仓库本体走 git，不在打包范围）
# 用法: bash scripts/migrate-export.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$HOME/ai-document-migration-$(date +%Y%m%d).tar.gz"
TDIR="$(mktemp -d)"
trap 'rm -rf "$TDIR"' EXIT

say() { echo "[export] $*"; }

# 1. 确认仓库干净且已推送（内容真源走 git）
cd "$REPO_ROOT"
git fetch origin -q
UNPUSHED=$(git rev-list "origin/$(git branch --show-current)..HEAD" --count)
[ "$UNPUSHED" != "0" ] && say "⚠️  有 $UNPUSHED 个提交未推送，先 git push 再迁移！" || say "仓库与远端同步 ✓"

# 2. 打包 skills
mkdir -p "$TDIR/skills"
for s in article-toolkit ima-skill; do
  if [ -d "$HOME/.agents/skills/$s" ]; then
    cp -R "$HOME/.agents/skills/$s" "$TDIR/skills/"
    say "已收集 skill: $s"
  else
    say "⚠️  skill 不存在，跳过: $s"
  fi
done

# 3. 打包 ZCode 项目记忆（可选，找不到就跳过）
if compgen -G "$HOME/.zcode/cli/memories/projects/ai-document-*" > /dev/null; then
  mkdir -p "$TDIR/zcode-memory"
  cp -R "$HOME"/.zcode/cli/memories/projects/ai-document-* "$TDIR/zcode-memory/"
  say "已收集 ZCode 项目记忆"
fi

# 4. 压缩
find "$TDIR" -name ".DS_Store" -delete
tar -czf "$OUT" -C "$TDIR" .
say "完成: $OUT ($(du -h "$OUT" | cut -f1 | tr -d ' '))"
say "新设备运行: bash scripts/migrate-setup.sh ~/path/to/$(basename "$OUT")"
