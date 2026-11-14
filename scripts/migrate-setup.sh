#!/usr/bin/env bash
# 新设备：初始化文档库环境
# 用法: bash scripts/migrate-setup.sh [迁移包.tar.gz]
#   迁移包由旧设备的 scripts/migrate-export.sh 生成；不给参数则跳过 skills 安装
set -euo pipefail

BUNDLE="${1:-}"
REPO_URL="https://github.com/banzheshenghuo/document-site.git"
DEST="${DEST:-$HOME/Documents/codebase/ai-document}"

say() { echo "[setup] $*"; }
die() { echo "[setup][错误] $*" >&2; exit 1; }

# 1. 前置检查
for cmd in git node npm python3; do
  command -v "$cmd" >/dev/null || die "缺少 $cmd，先安装（见 docs/MIGRATION.md 第三节）"
done
say "环境: Node $(node --version), $(python3 --version 2>&1 | awk '{print $2}')"

# 2. clone 仓库（公开仓库，无需认证；push 时才需要）
if [ -d "$DEST/.git" ]; then
  say "仓库已存在，跳过 clone: $DEST"
else
  mkdir -p "$(dirname "$DEST")"
  git clone "$REPO_URL" "$DEST"
  say "仓库已 clone 到 $DEST"
fi
cd "$DEST"

# 3. 安装 skills + ZCode 记忆
if [ -n "$BUNDLE" ]; then
  [ -f "$BUNDLE" ] || die "迁移包不存在: $BUNDLE"
  T="$(mktemp -d)"
  tar -xzf "$BUNDLE" -C "$T"
  mkdir -p "$HOME/.agents/skills"
  for s in "$T"/skills/*; do
    [ -e "$s" ] || continue
    rsync -a "$s/" "$HOME/.agents/skills/$(basename "$s")/"
    say "skill 已安装: $(basename "$s")"
  done
  if [ -d "$T/zcode-memory" ] && [ -n "$(ls -A "$T/zcode-memory" 2>/dev/null)" ]; then
    mkdir -p "$HOME/.zcode/cli/memories/projects"
    cp -R "$T"/zcode-memory/* "$HOME/.zcode/cli/memories/projects/"
    say "ZCode 项目记忆已拷贝（若新设备项目 hash 不同则不自动加载，内容不丢）"
  fi
  rm -rf "$T"
else
  say "未提供迁移包，跳过 skills/记忆安装"
fi

# 4. 路径适配：skill 内的旧设备绝对路径 → 新设备 $HOME
TOOLKIT="$HOME/.agents/skills/article-toolkit"
if [ -d "$TOOLKIT" ]; then
  OLD_HOME="$(grep -rhoE "/Users/[A-Za-z0-9_.-]+" "$TOOLKIT" 2>/dev/null | sort -u | grep -v "^$HOME" | head -1 || true)"
  if [ -n "${OLD_HOME:-}" ]; then
    while IFS= read -r f; do
      sed -i.bak "s|$OLD_HOME|$HOME|g" "$f" && rm -f "$f.bak"
      say "路径适配: ${f#"$TOOLKIT"/}"
    done < <(grep -rl "$OLD_HOME" "$TOOLKIT" 2>/dev/null)
  else
    say "skill 路径无需适配"
  fi
fi

# 5. 安装依赖 + 构建验证
say "npm ci 安装依赖..."
npm ci
say "构建验证中（约 1 分钟）..."
BUILD_LOG="${TMPDIR:-/tmp}/docsite-build.log"
if npm run build > "$BUILD_LOG" 2>&1; then
  PAGES=$(grep -oE "[0-9]+ page\(s\) built" "$BUILD_LOG" | tail -1)
  say "✓ 构建通过（${PAGES:-ok}）"
else
  die "构建失败，日志: $BUILD_LOG"
fi

# 6. 收尾提示
cat <<'EOF'
[setup] 初始化完成。剩余手工步骤（见 docs/MIGRATION.md 第四节验证清单）:
  1) gh auth login            —— 部署监控与私有仓库 clone
  2) ssh -T git@github.com    —— 确认推送权限（新机器需先加 SSH key）
  3) 对 AI 说"精读 <某URL>"    —— 真实演练入库流水线
  4) 逐字稿需求: gh repo clone banzheshenghuo/bili2text（私有，先 gh auth login）
EOF
