# Skill Publisher（技能发布器）

> [EN](README.md) | 中文

一个聚焦的、有主见的 **Agent Skill**（基于 `SKILL.md`）发布工具。一个文件夹进去 → 两个市场上架：**ClawHub** 和 **skills.sh**。

```
┌─────────────────┐
│  你的 skill     │
│  文件夹          │
│  (SKILL.md +    │
│   scripts/,     │
│   references/)  │
└────────┬────────┘
         │
         ▼
   skill-publisher
   ─────────────────
   1. 校验 SKILL.md
   2. /skill-optimizer  (可选)
   3. /release-skill    (可选)
   4. 确保 skill-card.md + README.md + README.zh-cn.md 存在
   5. 起草 RELEASE_NOTES.md
   6. 剥离点文件和凭证
         │
         ├──────────────────────┐
         ▼                      ▼
   ┌──────────┐           ┌──────────┐
   │ ClawHub  │           │ skills.sh│
   │ @mebusw/ │           │ github   │
   │  <slug>  │           │ /mebusw/ │
   │          │           │  <slug>  │
   └──────────┘           └──────────┘
```

---

## 为什么需要这个 skill

大多数 skill 作者在「发布」这一步投入不足。他们常常：

- 忘了写 `skill-card.md`，被 ClawHub 拒收。
- 忘了中文 README，丢掉一半受众。
- 把 `.DS_Store`、`.git/`、`.env` 一起打进 bundle。
- 没有 release note。
- 只发了一个市场，忘了另一个。

本 skill 通过一份清单强制把发布做对，让发布这件事变得无聊且可复刻。真正难的部分——*设计*一个好的 skill——仍然取决于你；`skill-publisher` 只负责 *把它发出去*。

---

## 安装

```bash
npx skills add https://github.com/mebusw/skill-publisher
```

或通过 ClawHub：

```bash
openclaw skills install @mebusw/skill-publisher
```

---

## 快速开始

安装后，在任何 agent 中调用本 skill：

```
把 /path/to/my-skill 发布到 clawhub 和 skills.sh
```

本 skill 会：

1. 校验 `SKILL.md`（frontmatter、命名、长度）。
2. （可选）运行 `/skill-optimizer` 优化 description。
3. （可选）运行 `/release-skill` 升级版本。
4. 确保 `skill-card.md`、`README.md`、`README.zh-cn.md` 存在且是新鲜的。
5. 从最新的 changelog 起草 `RELEASE_NOTES.md`。
6. 从 bundle 中剥离点文件、构建产物和凭证。
7. 执行 `openclaw skills install @mebusw/<slug>`。
8. 执行 `npx skills add https://github.com/mebusw/<slug>`。
9. 输出 8 行确认信息，包含两个市场的 URL。

---

## 标志位

| 标志 | 效果 |
|------|------|
| `--dry-run` | 走完 9 个步骤，但不修改任何文件、不发布。仅打印将要执行的动作。 |
| `--skip-optimizer` | 跳过可选的 `/skill-optimizer` 预步骤。 |
| `--skip-release-skill` | 跳过可选的 `/release-skill` 预步骤。 |
| `--force` | 重新发布同一版本（默认会拒绝重复发布）。 |

用自然语言传入即可：

```
发布我的 skill，--dry-run
发布我的 skill --skip-optimizer --force
```

---

## 本 skill 强制要求的产物

每个发布的 skill 最终必须是这样的文件结构：

```
<your-skill>/
├── SKILL.md              # frontmatter 中 description 必须为英文
├── skill-card.md         # ClawHub 元数据（英文）
├── README.md             # 英文文档
├── README.zh-cn.md       # 中文文档
├── RELEASE_NOTES.md      # 最近的发布说明
├── references/           # 详细参考文档（可选）
├── scripts/              # 捆绑的可执行脚本（可选）
├── assets/               # 模板、图标（可选）
└── （不要有点文件、凭证、构建产物）
```

发布器会用捆绑的模板补齐任何缺失的文件，刷新任何过时的内容（错误的版本号、坏掉的安装命令），并移除任何不属于 skill 的东西。

---

## 九步流水线

完整细节见 [`SKILL.md`](SKILL.md)。简要流程：

| 步骤 | 是否必需 | 作用 |
|------|----------|------|
| 1. 校验 | 是 | 对 `SKILL.md` 做第一维度规范检查 |
| 2. `/skill-optimizer` | 可选 | 优化 description 和触发准确性 |
| 3. `/release-skill` | 可选 | 升级版本 + 写 changelog |
| 4. 确保文档三件套 | 是 | 创建/刷新 skill-card.md + 两个 README |
| 5. 起草发布说明 | 是 | 从 CHANGELOG 或 git log 抽取 |
| 6. 清理 bundle | 是 | 移除点文件、凭证、构建产物 |
| 7. 发布到 ClawHub | 是 | `openclaw skills install @mebusw/<slug>` |
| 8. 发布到 skills.sh | 是 | `npx skills add https://github.com/mebusw/<slug>` |
| 9. 确认 | 是 | 打印市场 URL + git tag + bundle 大小 |

---

## 文件结构

```
skill-publisher/
├── SKILL.md                              # Skill 定义（英文 description）
├── skill-card.md                         # 本 skill 的 ClawHub 元数据
├── README.md                             # 英文文档
├── README.zh-cn.md                       # 本文件（中文）
├── references/
│   ├── skill-card-template.md           # skill-card.md 模板
│   ├── clawhub-bundle.md                # ClawHub 扩展名白名单 + 大小限制
│   ├── skills-sh-publish.md             # npx skills add 如何解析仓库
│   └── release-notes-template.md        # RELEASE_NOTES.md 模板
└── scripts/
    └── strip_bundle.py                   # 遍历文件夹，移除非 bundle 文件
```

---

## 前置依赖

要跑完整流水线，用户的机器上需要：

- `git` — 用于检测 tag、生成 changelog
- `python3` — 用于 `scripts/strip_bundle.py`
- `node` + `npx` — 用于 `npx skills add`（skills.sh）
- `openclaw` CLI — 用于 `openclaw skills install`（ClawHub）。通过 `npm i -g openclaw` 安装。
- 网络可访问 `clawhub.ai`、`github.com`、npm registry。

本 skill 在第 7 步会检测缺失的前置依赖，并在执行任何发布命令之前打印清晰的错误信息。

---

## 局限性

- **单一发布者账号。** 本 skill 全部以 `@mebusw` / `github.com/mebusw` 名义发布。如果你想用其他 GitHub owner，请 fork 本 skill 并修改硬编码的 slug。
- **没有回滚。** 一旦版本发布到 ClawHub，无法通过 CLI 撤销。需要去 ClawHub Web 界面手动下架。
- **不支持中英以外的多语言 README。** 如果需要日语、韩语等版本，请在发布后手动添加。
- **清理步骤偏保守。** 它会移除任何无法归类为 skill 本体的文件。如果你的 skill 真的需要放在标准目录之外的 `config.yaml`，可能需要编辑 `scripts/strip_bundle.py`。

---

## 相关 skill

- [`skill-creator`](https://github.com/anthropics/skills/tree/main/skills/skill-creator) — 从零设计一个 skill。在本 skill 之前使用。
- [`skill-optimizer`](https://github.com/mebusw/skill-optimizer) — 审计和打磨现有的 `SKILL.md`。常作为预步骤调用。
- [`release-skills`](https://github.com/mebusw/release-skills) — 通用版本升级 + changelog 工作流。常作为预步骤调用。

---

## 参考资料

- [ClawHub Skill Format](https://docs.openclaw.ai/clawhub/skill-format) — bundle 结构和文件白名单
- [skills.sh docs](https://skills.sh/docs) — `npx skills add` 如何解析仓库
- [agentskills.io Specification](https://agentskills.io/specification) — 怎样的 `SKILL.md` 才算合法
- [agentskills.io Best Practices](https://agentskills.io/skill-creation/best-practices) — 怎样的 skill 才是好 skill

---

## 许可证

MIT-0。任何人可自由使用、修改和再分发，包括商业用途。

---

[English version →](README.md)