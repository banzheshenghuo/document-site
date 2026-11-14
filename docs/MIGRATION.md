# 文档库迁移 SOP（换设备）

> 两个迁移目标：
> **A. GitHub 文档站全量迁移** —— 新设备完整拥有站点：全部内容、构建能力、发布能力。
> **B. 收集能力** —— 精读文章与开源库解读的入库流水线（抓取 → ima 归档 → 发布）在新设备可用。
>
> **金融日报不在迁移范围**：生成脚本随仓库克隆带着，但新设备不要求可运行（需要时另配 Python 环境）。
> 原则：仓库是唯一真源，脚本只搬运仓库之外的东西。

## 一、迁移组件清单

### 目标 A：站点（全量）

| 组件 | 位置（旧设备） | 存放形态 | 迁移方式 |
|------|----------------|----------|----------|
| 全部文章内容（精读/开源解读/金融日报） | `src/content/posts/` | **git 仓库** | `git clone` |
| 站点工程（页面/样式/类型系统） | `src/`、`DESIGN.md` | git 仓库 | 随 clone |
| 运维脚本 | `scripts/` | git 仓库 | 随 clone |
| 部署流水线 | `.github/workflows/deploy.yml` | git 仓库 | 随 clone（push main 自动发布） |
| Node + git + gh + SSH key | 系统环境 | 用户级 | 新设备安装/登录 |

### 目标 B：收集能力（精读 + 开源解读）

| 组件 | 位置（旧设备） | 存放形态 | 迁移方式 |
|------|----------------|----------|----------|
| 入库流水线 skill | `~/.agents/skills/article-toolkit/` | **普通目录（非 git）** | export 脚本打包 |
| ima 归档 skill | `~/.agents/skills/ima-skill/`（含 ima_api.cjs 等脚本） | 普通目录 | export 脚本打包 |
| **ima 凭证** | `~/.config/ima/client_id` + `api_key` | 两个小文件（~100B） | **手工复制**（不进打包件，见 3.3） |
| 抓取引擎 ego-browser | ego lite 二进制 + 浏览器 | 独立安装 | 新设备重装（见 3.1） |

### 明确不在范围

- **金融日报运行环境**：Python 3 / akshare 不作要求；`scripts/daily-market-data.py` 等随仓库带着但新设备不验证
- **逐字稿工具**（bili2text / yt2text）：仅当新设备也要处理视频逐字稿时才装（见 3.4，可选）
- **收藏与原文内容本体**：存在 ima 云端知识库（kb_id 见 article-toolkit/SKILL.md），与设备无关
- **gh/SSH 凭证**：属用户级，新设备重新登录/添加公钥即可（ima 凭证例外，是静态文件，见 3.3）
- **定时任务**：本库无系统级定时任务；金融日报由 ZCode 会话驱动，不在本次范围

## 二、旧设备：导出（1 分钟）

```bash
cd ~/Documents/codebase/ai-document
bash scripts/migrate-export.sh
```

脚本会：检查仓库无未推送提交 → 打包 `article-toolkit`、`ima-skill`、ZCode 记忆到
`~/ai-document-migration-<日期>.tar.gz`（仓库本体不打包，走 git）。

随后准备两样东西随包一起带到新设备：**ima 凭证两个小文件**（`~/.config/ima/`，手工复制）；
新设备的 GitHub 访问凭证（SSH key 或 gh 登录）。

## 三、新设备：初始化

### 3.1 前置安装（一次性）

| 依赖 | 服务于 | 安装 |
|------|--------|------|
| Node ≥ 20（推荐 22） | A 构建 + B ima_api.cjs | `brew install node@22` |
| git | A 仓库 | `brew install git` |
| gh CLI | A 部署监控/私有仓库 clone | `brew install gh && gh auth login` |
| SSH key（推 GitHub） | A git push | `ssh-keygen` + 上传公钥到 GitHub |
| **ego lite（ego-browser）** | **B 网页抓取引擎** | 按 ego-browser skill 的安装说明安装，装完跑 `ego-browser skill` 确认 |
| Python 3 | ~~金融日报~~（不在范围） | 跳过；将来要跑日报再装 |

中国大陆设备访问 GitHub 不稳时先挂代理：`export HTTPS_PROXY=http://127.0.0.1:<端口>`。

### 3.2 运行初始化脚本（目标 A 自动完成）

```bash
bash scripts/migrate-setup.sh ~/Downloads/ai-document-migration-<日期>.tar.gz
```

脚本会：clone 仓库到 `~/Documents/codebase/ai-document` → 安装 skills → 拷贝 ZCode 记忆
→ **自动把 skill 内的绝对路径适配为新设备 $HOME** → `npm ci` → 完整构建验证。

### 3.3 ima 凭证（目标 B 必需）

`ima_api.cjs` 调用 ima OpenAPI 需要 Client ID + API Key（缺凭证时报 `code: -100`）。两种方式：

```bash
# 方式 A：从旧设备复制两个小文件（AirDrop/scp 均可，不进迁移打包件）
mkdir -p ~/.config/ima
scp 旧设备:~/.config/ima/{client_id,api_key} ~/.config/ima/

# 方式 B：重新获取——打开 https://ima.qq.com/agent-interface 领取 Client ID / API Key
mkdir -p ~/.config/ima
echo "your_client_id" > ~/.config/ima/client_id
echo "your_api_key"  > ~/.config/ima/api_key
```

验证（应输出 ✅ Credentials configured）：

```bash
test -f ~/.config/ima/client_id && test -f ~/.config/ima/api_key && echo "✅ Credentials configured"
```

### 3.4 逐字稿工具（可选，仅当新设备也要处理视频）

```bash
gh repo clone banzheshenghuo/bili2text ~/Documents/codebase/bili2text
# 按 bili2text 仓库 README 安装 yt2text 命令
```

## 四、验证清单（按目标分层）

**A 层——站点：**

| # | 验证项 | 命令/操作 | 预期 |
|---|--------|-----------|------|
| 1 | 构建通过 | setup 脚本已跑；或 `npm run build` | 构建完成无报错 |
| 2 | 本地预览 | `npm run dev` → http://localhost:4321 | 首页三频道/文章正常渲染 |
| 3 | 推送权限 | 改个测试文件 commit + push | Actions 变绿，线上更新 |

**B 层——收集（精读 + 开源解读）：**

| # | 验证项 | 命令/操作 | 预期 |
|---|--------|-----------|------|
| 4 | ima 凭证 | §3.3 的 test 命令 | ✅ Credentials configured |
| 5 | 收藏路由 | 对 AI 说"收藏 <URL>" | 只进 ima 对应知识库，站点无痕迹 |
| 6 | 收集闭环 | 对 AI 说"精读 <URL>" 或"开源解读 <URL>" | 原文进 ima + 成品上站 + 部署成功 |

## 五、注意事项

1. **绝对路径**：article-toolkit 的文件内嵌 `/Users/<用户名>/...` 绝对路径，setup 脚本会自动替换
   为新设备 `$HOME`；若新设备用了非标准目录结构，手动检查技能目录下 5 个文件
2. **ZCode 记忆目录名**含项目路径 hash（`ai-document-430e3d445094b620`）：新设备路径与旧设备
   一致时大概率直接生效；不一致时记忆不自动加载，内容仍在，可让 AI 重新沉淀
3. **ZCode 自动化**：若旧设备上有跟本库相关的 ZCode 定时自动化（CronList 查看），需在新设备
   的对应工作区重新创建，不会随文件迁移
4. **ima 知识库 kb_id** 写死在 article-toolkit/SKILL.md，属云端资源，跨设备通用，无需改动
5. **双设备并行**：内容真源是 GitHub 仓库，两台设备各自 pull/push 即可，无锁定问题；
   入库前习惯先 `git pull` 减少冲突
6. **金融日报**：如将来要在新设备跑日报，补装 Python 3 + 依赖后按
   `scripts/daily-market-data.py --help` 使用；跑之前先 `git pull` 拿到最新脚本
