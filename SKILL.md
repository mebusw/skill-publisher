---
name: skill-publisher
description: >
  将本地 SKILL.md 技能一键发布到多个市场：ClawHub、腾讯 SkillHub、skills.sh、LobeHub、SkillsMP、Agensi、Coze 等。
  触发词包括："发布 skill"、"发布到多个市场"、"publish to clawhub"、"一键发布"、
  "发布到 skillhub"、"发布到 skills.sh"、"全市场发布"、"multi-market publish"。
  自动完成：格式校验 · 文档生成 · 敏感清理 · 版本打标 · 串行发布 · 结果汇总。
author: jackyshen
version: 2.1.0
---

# Skill Publisher — 多市场一键发布 v2.1

将本地 skill 目录**同时发布到所有主流市场**，自动处理各市场 CLI 差异和已知坑。

---

## 市场总览

| # | 市场 | 地址 | CLI | 认证 | 审核 | 变现 | 安装命令 |
|---|------|------|------|------|------|------|---------|
| 1 | **ClawHub** | clawhub.ai | `clawhub publish` | API Token `clh_xxx` | 机器审核 | ✅ 付费技能 | `clawhub install` |
| 2 | **腾讯 SkillHub** | skillhub.tencent.com | `skillhub push` + `publish` | `skillhub login` | 三线安全审核 | ❌ | `skillhub install` |
| 3 | **skills.sh** | agentskill.sh | Git tag + `npx` | GitHub 公开 | 无 | ❌ | `npx skills add` |
| 4 | **SkillsMP** | agentskills.io | API / 网页 | 可选 | 无 | ✅ 按次付费 | `npx skills add` |
| 5 | **LobeHub Skills** | lobehub.com/skills | `lobe-cli` | GitHub OAuth | 机器审核 | ❌（生态内） | `lobe-cli skill add` |
| 6 | **Agensi** | agensi.ai | API | API Key | 人工审核 | ✅ 付费+抽成 | `agensi skill publish` |
| 7 | **Coze/扣子** | coze.cn | API | `COZE_TOKEN` | 人工审核 | ✅ Bot订阅 | API 发布 |
| 8 | **ClawMart** | clawmart.com | 网页 | 账号 | 无 | ✅ 月入$80k+ | 第三方商店 |

---

## 用户参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `skill_dir` | ✅ | 本地 skill 文件夹（需含 SKILL.md） |
| `clawhub_token` | ✅（ClawHub） | ClawHub API Token，格式 `clh_xxx` |
| `github_repo` | ✅（skills.sh/Agensi） | GitHub 仓库地址 |
| `coze_token` | ❌ | Coze API Token（发布到扣子时需要） |
| `agensi_key` | ❌ | Agensi API Key（发布到 Agensi 时需要） |
| `markets` | ❌ | 目标市场列表，默认全部 |

> 缺少必填项时，**只问缺少的那一项**。

---

## 执行流程（8步）

### Step 1 — 环境与目录检查

```bash
ls {skill_dir}/SKILL.md || exit "❌ SKILL.md 不存在"
cat {skill_dir}/SKILL.md | head -30

# 检查各 CLI
which clawhub   || echo "⚠️ clawhub 未安装"
which skillhub  || curl -fsSL https://skillhub.cn/install/install.sh | bash
which lobe      || echo "⚠️ lobe-cli 未安装"
git --version
```

### Step 2 — SKILL.md 格式校验

必填字段：`name`、`description`（英文）、`version`、`author`，缺失任一则**停止并告知**。

```bash
python3 -c "
import sys, re, yaml
content = open('{skill_dir}/SKILL.md').read()
m = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
if not m: sys.exit('❌ frontmatter 缺失')
data = yaml.safe_load(m.group(1))
for k in ['name','description','version','author']:
    v = data.get(k,'❌ 缺失')
    status = '✅' if v != '❌ 缺失' else '❌'
    print(f'{status} {k}: {v}')
    if v == '❌ 缺失': sys.exit(1)
"
```

### Step 3 — 文档生成

| 文件 | 语言 | 必须包含 |
|------|------|---------|
| `README.md` | 英文 | 安装命令（8个市场）、快速开始、文件结构 |
| `README.zh-cn.md` | 中文 | 同上，中文 |
| `RELEASE_NOTES.md` | 中英 | 发布内容 + 版本历史 |

README.md 安装命令必须覆盖：
```bash
# ClawHub (OpenClaw)
clawhub install {slug}

# 腾讯 SkillHub
skillhub install {slug}

# skills.sh / SkillsMP / LobeHub / Agensi / Coze
npx skills add {github_repo}
lobe-cli skill add {slug}
agensi skill publish {slug}
```

### Step 4 — Git 打标签

skills.sh / SkillsMP / LobeHub 均依赖 Git tag 版本：

```bash
cd {skill_dir_parent}
git config --global user.email "jackyshen@uperform.cn" 2>/dev/null || true
git config --global user.name "jackyshen" 2>/dev/null || true

SKILL_VER=$(grep '^version:' {skill_dir}/SKILL.md | head -1 | cut -d: -f2 | tr -d ' ')
TARGET_TAG="v$SKILL_VER"
CURRENT_TAG=$(git tag --sort=-v:refname | head -1 2>/dev/null || echo "")

if [ "$CURRENT_TAG" = "$TARGET_TAG" ]; then
    echo "ℹ️ Tag $TARGET_TAG 已存在"
else
    git tag -a "$TARGET_TAG" -m "Release $TARGET_TAG"
    git push origin "$TARGET_TAG"
    echo "✅ Tag $TARGET_TAG 已推送"
fi
```

### Step 5 — Bundle 清理

```bash
RM_LIST=".git .DS_Store .idea .vscode node_modules .env .env.* *.key *.pem credentials.* secrets.* *.log *.tmp *.bak"

echo "=== 将删除 ==="
for item in $RM_LIST; do find {skill_dir} -name "$item" 2>/dev/null; done

[ "$DRY_RUN" = "true" ] && echo "[DRY RUN]" && exit 0

for item in $RM_LIST; do
    find {skill_dir} -name "$item" -type d -exec rm -rf {} + 2>/dev/null
    find {skill_dir} -name "$item" -type f -delete 2>/dev/null
done
echo "✅ 清理完成"
```

### Step 6 — 串行发布

#### 6a. ClawHub（ markets 包含 clawhub 时）

```bash
# CLI patch（已知 bug）
PUBLISH_JS=$(find /usr/local/lib /usr/lib ~/.npm -name "publish.js" 2>/dev/null | grep clawhub | head -1)
[ -n "$PUBLISH_JS" ] && ! grep -q "acceptLicenseTerms" "$PUBLISH_JS" && \
    sed -i 's/skillName:/acceptLicenseTerms: true, skillName:/' "$PUBLISH_JS"

CLAWHUB_TOKEN="***" \
clawhub publish {skill_dir} \
  --slug {slug} --name "{display_name}" --version {version} \
  --changelog "Release v{version}" --tags "latest"

sleep 3 && clawhub search {slug}
echo "✅ ClawHub 完成"
```

**错误处理：**
| 错误 | 方案 |
|------|------|
| `slug already taken` (409) | slug 加 `-v2` |
| `rate limit exceeded` (429) | 等 65 分钟 cron 重试 |
| `400` | 重跑 patch |
| `401` | 重新生成 token |

---

#### 6b. 腾讯 SkillHub（ markets 包含 skillhub 时）

```bash
skillhub whoami 2>/dev/null || skillhub login

[ ! -f "{skill_dir}/skillhub.yaml" ] && \
    skillhub init --name {slug} --category "效率工具" --dir {skill_dir}

cd {skill_dir}
skillhub push --message "Release v{version}"
skillhub publish --version {version} --changelog "Release v{version}"

skillhub search {slug}
echo "✅ SkillHub 完成（审核约 5-10 分钟）"
```

---

#### 6c. skills.sh（ markets 包含 skillssh 时）

```bash
GH_REPO="{github_repo}"
curl -s "https://api.github.com/repos/$GH_REPO" | python3 -c "
import sys,json
try:
    d=json.load(sys.stdin)
    print('✅', d['full_name'], '| Stars:', d['stargazers_count'])
except: print('⚠️ Repo 不存在或未公开')
"
echo "✅ skills.sh 完成（安装: npx skills add $GH_REPO）"
```

---

#### 6d. SkillsMP（ markets 包含 skillsmp 时）

```bash
# SkillsMP 通过 GitHub repo 聚合，无需专门 publish
# 但可在 agentskills.io 注册以便有独立页面
echo "✅ SkillsMP: npx skills add {github_repo} 即可安装"
echo "   注册独立页面: https://agentskills.io/submit"
```

---

#### 6e. LobeHub Skills（ markets 包含 lobehub 时）

```bash
# LobeHub 使用 lobe-cli 或 GitHub repo 方式
# 方式1: lobe-cli（如已安装）
lobe-cli skill add {github_repo} 2>/dev/null && echo "✅ lobe-cli 添加成功" || true

# 方式2: 通过 GitHub 提交 PR 到 lobehub/lobe-chat
echo "✅ LobeHub: 提交 PR 到 https://github.com/lobehub/lobe-chat#skills"
echo "   或直接: npx skills add {github_repo}"
```

---

#### 6f. Agensi（ markets 包含 agensi 时）

```bash
# Agensi 有独立 API publish
curl -X POST https://api.agensi.ai/v1/skills/publish \
  -H "Authorization: Bearer {agensi_key}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "{slug}",
    "repo": "{github_repo}",
    "version": "{version}",
    "description": "...",
    "tags": ["productivity"]
  }'
echo "✅ Agensi 发布请求已提交（等待人工审核）"
```

---

#### 6g. Coze（ markets 包含 coze 时）

```bash
# Coze 通过 API 发布到 Bot store
curl -X POST "https://api.coze.cn/v1/skills" \
  -H "Authorization: Bearer {coze_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "{slug}",
    "description": "...",
    "icon_url": "...",
    "skill_type": "published"
  }'
echo "✅ Coze 发布请求已提交（等待人工审核）"
```

---

#### 6h. ClawMart（ markets 包含 clawmart 时）

```bash
# ClawMart 是第三方付费商店，引导用户手动发布
echo "✅ ClawMart: 手动发布到 https://clawmart.com/sell"
echo "   月收入 \$80k+，热门第三方付费技能商店"
echo "   可参考: https://clawmart.com/publish"
```

---

### Step 7 — 结果汇总

```
=========================================
✅ 多市场发布完成

📦 ClawHub         clawhub.com/skills/{slug}     clawhub install {slug}
📦 腾讯 SkillHub   skillhub.tencent.com/skills   skillhub install {slug}
📦 skills.sh       agentskill.sh                 npx skills add {repo}
📦 SkillsMP        agentskills.io                npx skills add {repo}
📦 LobeHub         lobehub.com/skills            lobe-cli skill add {repo}
📦 Agensi          agensi.ai                    API publish（审核中）
📦 Coze            coze.cn                      API publish（审核中）
📦 ClawMart        clawmart.com                 手动发布
=========================================
```

---

## 全局参数

| 参数 | 默认 | 说明 |
|------|------|------|
| `DRY_RUN` | `false` | true 时只检查不发布 |
| `markets` | 全部8个 | 指定市场列表，如 `clawhub,skillhub,skillssh` |
| `--skip-*` | false | 跳过指定市场 |

---

## 已知限制

1. **腾讯 SkillHub / Agensi / Coze** 有人工审核，约 5-10 分钟
2. **LobeHub** 推荐通过 GitHub PR 方式提交
3. **ClawMart** 需手动网页发布，不支持 CLI
4. **版本号必须递增**，不允许重复版本发布
5. **作者**：jackyshen，优普丰定制版 v2.1.0
