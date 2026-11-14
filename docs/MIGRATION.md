# 文档库迁移 SOP（换设备）

> 目标：在新设备上完整恢复「安昙」文档库的**阅读/入库/发布**全流程。
> 原则：仓库是唯一真源，脚本只搬运仓库之外的东西。

## 一、迁移组件清单

| 组件 | 位置（旧设备） | 存放形态 | 迁移方式 |
|------|----------------|----------|----------|
| 文章内容（精读/日报/逐字稿） | `src/content/posts/` | **git 仓库** | `git clone` 即可，无需拷贝 |
| 运维脚本（频道检测/金融数据） | `scripts/` | git 仓库 | 随 clone |
| 部署流水线 | `.github/workflows/deploy.yml` | git 仓库 | 随 clone（push main 自动发布） |
| 入库流水线 skill | `~/.agents/skills/article-toolkit/` | **普通目录（非 git）** | export 脚本打包 |
| ima 归档 skill（收藏用） | `~/.agents/skills/ima-skill/` | 普通目录 | export 脚本打包 |
| 逐字稿工具源码 | `~/Documents/codebase/bili2text` | git 仓库（私有） | setup 脚本 clone |
| 逐字稿命令 | `~/.local/bin/yt2text` | bili2text 安装产物 | 源码 clone 后重装 |
| ZCode 项目记忆 | `~/.zcode/cli/memories/projects/ai-document-*/` | 普通目录 | export 脚本打包（可选） |

**不需要迁移的：**

- **收藏内容本体**：存在 ima 云端知识库（kb_id 见 article-toolkit/SKILL.md），与设备无关
- **已发布文章**：全在 git 里；线上站点是 GitHub Pages 从仓库构建的，与设备无关
- **密钥/token**：本库无任何本地密钥文件；gh/SSH 凭证属用户级，新设备重新登录即可
- **定时任务**：本库无 launchd/crontab 任务；金融日报由 ZCode 会话驱动 `scripts/daily-market-data.py` 生成，换设备无需重建系统级任务

## 二、旧设备：导出（1 分钟）

```bash
cd ~/Documents/codebase/ai-document
bash scripts/migrate-export.sh
```

脚本会：检查仓库无未推送提交 → 打包 `article-toolkit`、`ima-skill`、ZCode 记忆到
`~/ai-document-migration-<日期>.tar.gz`（仓库本体不打包，走 git）。

把生成的 tar.gz 和新设备的访问凭证（SSH key 或 gh 登录）准备好即可。

## 三、新设备：初始化（约 5 分钟）

### 3.1 前置安装（一次性）

| 依赖 | 用途 | 安装 |
|------|------|------|
| Node ≥ 20（推荐 22） | Astro 构建 | `brew install node@22` |
| Python 3 | 金融数据脚本 | `brew install python3` |
| git | 仓库 | `brew install git` |
| gh CLI | 部署监控/私有仓库 clone | `brew install gh && gh auth login` |
| SSH key（推 GitHub） | git push | `ssh-keygen` + 上传公钥到 GitHub |

中国大陆设备访问 GitHub 不稳时先挂代理：`export HTTPS_PROXY=http://127.0.0.1:<端口>`。

### 3.2 运行初始化脚本

```bash
bash scripts/migrate-setup.sh ~/Downloads/ai-document-migration-<日期>.tar.gz
```

脚本会：clone 仓库到 `~/Documents/codebase/ai-document` → 安装 skills → 拷贝 ZCode 记忆
→ **自动把 skill 内的绝对路径适配为新设备 $HOME** → `npm ci` → 完整构建验证。

### 3.3 逐字稿工具（用到 YouTube 逐字稿才需要）

```bash
gh repo clone banzheshenghuo/bili2text ~/Documents/codebase/bili2text
# 按 bili2text 仓库 README 安装 yt2text 命令
```

## 四、验证清单

| # | 验证项 | 命令/操作 | 预期 |
|---|--------|-----------|------|
| 1 | 构建通过 | setup 脚本已跑；或 `npm run build` | 构建完成无报错（页数随内容变动） |
| 2 | 本地预览 | `npm run dev` → http://localhost:4321 | 首页/文章正常渲染 |
| 3 | 推送权限 | 改个测试文件 commit + push | Actions 变绿，线上更新 |
| 4 | 入库流水线 | 找一篇文章对 AI 说"精读" | 文章生成 + push + ima 归档 |
| 5 | 收藏路由 | 对 AI 说"收藏 <URL>" | 只进 ima，站点无痕迹 |
| 6 | 金融数据脚本 | `python3 scripts/daily-market-data.py --help` | 正常输出用法 |

## 五、注意事项

1. **绝对路径**：article-toolkit 的 SKILL.md/fetch.md 等文件内嵌了 `/Users/<用户名>/...` 绝对路径，
   setup 脚本会自动替换为新设备的 `$HOME`；若新设备用了非标准目录结构，手动检查这 5 个文件
2. **ZCode 记忆目录名**含项目路径 hash（`ai-document-430e3d445094b620`）：新设备路径与旧设备
   一致时大概率直接生效；不一致时记忆不自动加载，内容仍在，可让 AI 重新沉淀
3. **ZCode 自动化**：若旧设备上有跟本库相关的 ZCode 定时自动化（CronList 查看），需在新设备
   的对应工作区重新创建，不会随文件迁移
4. **ima 知识库 kb_id** 写死在 article-toolkit/SKILL.md，属云端资源，跨设备通用，无需改动
5. **双设备并行**：内容真源是 GitHub 仓库，两台设备各自 pull/push 即可，无锁定问题；
   入库前习惯先 `git pull` 减少冲突
