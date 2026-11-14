#!/usr/bin/env bash
# 新设备：初始化文档库环境
# 用法: bash scripts/migrate-setup.sh [迁移包.tar.gz]
#   迁移包由旧设备的 scripts/migrate-export.sh 生成；不给参数则跳过 skills 安装
# 目标：A 站点全量迁移（自动完成）；B 收集能力（精读/开源解读 + ima 归档，装好 skills 后补凭证即可）
# 金融日报链路不在迁移范围（Python 环境不作为前置）
set -euo pipefail

BUNDLE="${1:-}"
REPO_URL="https://github.com/banzheshenghuo/document-site.git"
DEST="${DEST:-$HOME/Documents/codebase/ai-document}"

say() { echo "[setup] $*"; }
die() { echo "[setup][错误] $*" >&2; exit 1; }

# 1. 前置检查（Node/git 硬性；python3 仅金融日报需要，缺了只提醒）
for cmd in git node npm; do
  command -v "$cmd" >/dev/null || die "缺少 $cmd，先安装（见 docs/MIGRATION.md §3.1）"
done
say "环境: Node $(node --version)"
if ! command -v python3 >/dev/null; then
  say "提示: 无 python3——金融日报脚本本次不迁移，不影响站点与收集；将来需要时再装"
fi
if ! command -v gh >/dev/null; then
  say "提示: 未装 gh CLI——部署监控/私有仓库 clone 需要它（brew install gh && gh auth login）"
fi

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

# 5. 安装依赖 + 构建验证（目标 A）
say "npm ci 安装依赖..."
npm ci
say "构建验证中..."
BUILD_LOG="${TMPDIR:-/tmp}/docsite-build.log"
if npm run build > "$BUILD_LOG" 2>&1; then
  PAGES=$(grep -oE "[0-9]+ page\(s\) built" "$BUILD_LOG" | tail -1)
  say "✓ 构建通过（${PAGES:-ok}）——目标 A 完成"
else
  die "构建失败，日志: $BUILD_LOG"
fi

# 6. 收集能力（目标 B）状态检查
if [ -f "$HOME/.config/ima/client_id" ] && [ -f "$HOME/.config/ima/api_key" ]; then
  say "✓ ima 凭证已就绪"
else
  say "⚠️  ima 凭证缺失——精读/收藏上传 ima 会报 code:-100。补齐方式见 docs/MIGRATION.md §3.3："
  echo "     方式 A: scp 旧设备:~/.config/ima/{client_id,api_key} ~/.config/ima/"
  echo "     方式 B: 打开 https://ima.qq.com/agent-interface 领取后写入 ~/.config/ima/"
fi
command -v ego-browser >/dev/null && say "✓ ego-browser 已安装（抓取引擎）" \
  || say "⚠️  未装 ego-browser——抓取网页需要它，按 ego-browser skill 安装说明补装"

# 7. 收尾提示
cat <<'EOF'
[setup] 初始化完成。验证清单（docs/MIGRATION.md §四）:
  —— A 层（站点）——
  1) 本地预览: npm run dev → http://localhost:4321
  2) 推送权限: 改测试文件 commit + push → Actions 变绿
     （新机器需先: gh auth login / ssh-keygen 加公钥）
  —— B 层（收集: 精读 + 开源解读）——
  3) ima 凭证: 见上方检查结果，缺了按提示补
  4) 闭环演练: 对 AI 说"精读 <URL>" 或 "开源解读 <URL>"
  —— 可选 ——
  5) 逐字稿: gh repo clone banzheshenghuo/bili2text（先 gh auth login）
  金融日报不在迁移范围；将来要跑见 docs/MIGRATION.md §五-6
EOF
