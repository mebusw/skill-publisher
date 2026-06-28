# Skill Publisher

> EN | [中文](README.zh-cn.md)

A focused, opinionated publisher for **Agent Skills** (`SKILL.md`-based). One folder in → two marketplaces out: **ClawHub** and **skills.sh**.

```
┌─────────────────┐
│  Your skill     │
│  folder         │
│  (SKILL.md +    │
│   scripts/,     │
│   references/)  │
└────────┬────────┘
         │
         ▼
   skill-publisher
   ─────────────────
   1. validate SKILL.md
   2. /skill-optimizer  (optional)
   3. /release-skill    (optional)
   4. ensure skill-card.md + README.md + README.zh-cn.md
   5. draft RELEASE_NOTES.md
   6. strip dot-files & credentials
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

## Why this skill exists

Most skill authors under-invest in the publishing step. They:

- Forget to write a `skill-card.md` and get rejected by ClawHub.
- Forget the Chinese README and lose half their audience.
- Ship a bundle with `.DS_Store`, `.git/`, and an `.env` file.
- Publish without a release note.
- Publish to one marketplace and forget the other.

This skill enforces a checklist so the publish step is boring and reproducible. The hard part — *designing* a good skill — is still up to you; `skill-publisher` only handles the *ship-it* step.

---

## Installation

```bash
npx skills add https://github.com/mebusw/skill-publisher
```

Or via ClawHub:

```bash
openclaw skills install @mebusw/skill-publisher
```

---

## Quick start

Once installed, invoke the skill from any agent:

```
publish my skill at /path/to/my-skill to clawhub and skills.sh
```

The skill will:

1. Validate the `SKILL.md` (frontmatter, naming, length).
2. Optionally run `/skill-optimizer` to tighten the description.
3. Optionally run `/release-skill` to bump the version.
4. Ensure `skill-card.md`, `README.md`, `README.zh-cn.md` exist and are fresh.
5. Draft a `RELEASE_NOTES.md` from your latest changelog.
6. Strip dot-files, build artifacts, and credentials from the bundle.
7. Run `openclaw skills install @mebusw/<slug>`.
8. Run `npx skills add https://github.com/mebusw/<slug>`.
9. Print an 8-line confirmation with both marketplace URLs.

---

## Flags

| Flag | Effect |
|------|--------|
| `--dry-run` | Walk all 9 steps without mutating files or publishing. Prints the actions it *would* take. |
| `--skip-optimizer` | Bypass the optional `/skill-optimizer` pre-step. |
| `--skip-release-skill` | Bypass the optional `/release-skill` pre-step. |
| `--force` | Re-publish the same version (default: refuse duplicates). |

Pass them on the natural-language command:

```
publish my skill --dry-run
publish my skill --skip-optimizer --force
```

---

## What the skill enforces

Every published skill must end up with this file structure:

```
<your-skill>/
├── SKILL.md              # English description in frontmatter
├── skill-card.md         # ClawHub metadata (English)
├── README.md             # English documentation
├── README.zh-cn.md       # Chinese documentation
├── RELEASE_NOTES.md      # Most recent release notes
├── references/           # Detailed reference docs (optional)
├── scripts/              # Bundled executables (optional)
├── assets/               # Templates, icons (optional)
└── (NO dot-files, NO credentials, NO build artifacts)
```

The publisher will create any missing file from the bundled templates, refresh any stale content (wrong version, broken install command), and remove anything that does not belong.

---

## The 9-step pipeline

For full detail, see [`SKILL.md`](SKILL.md). The summary:

| Step | Required? | Purpose |
|------|-----------|---------|
| 1. Validate | yes | Dimension 1 spec checks on `SKILL.md` |
| 2. `/skill-optimizer` | optional | Polish description and triggering |
| 3. `/release-skill` | optional | Bump version + write changelog |
| 4. Ensure docs trio | yes | Create/refresh skill-card.md + 2 READMEs |
| 5. Draft release note | yes | Pull from CHANGELOG or git log |
| 6. Strip bundle | yes | Remove dot-files, credentials, build artifacts |
| 7. Publish ClawHub | yes | `openclaw skills install @mebusw/<slug>` |
| 8. Publish skills.sh | yes | `npx skills add https://github.com/mebusw/<slug>` |
| 9. Confirm | yes | Print marketplace URLs + git tag + bundle size |

---

## File structure

```
skill-publisher/
├── SKILL.md                              # Skill definition (English description)
├── skill-card.md                         # ClawHub metadata for this skill
├── README.md                             # This file (English)
├── README.zh-cn.md                       # Chinese documentation
├── references/
│   ├── skill-card-template.md           # Template for skill-card.md
│   ├── clawhub-bundle.md                # ClawHub extension allowlist + size limits
│   ├── skills-sh-publish.md             # How npx skills add resolves a repo
│   └── release-notes-template.md        # RELEASE_NOTES.md template
└── scripts/
    └── strip_bundle.py                   # Walk a folder, remove non-bundle files
```

---

## Prerequisites

To run the full pipeline, the user's machine needs:

- `git` — for tag detection and changelog generation
- `python3` — for `scripts/strip_bundle.py`
- `node` + `npx` — for `npx skills add` (skills.sh)
- `openclaw` CLI — for `openclaw skills install` (ClawHub). Install with `npm i -g openclaw`.
- Network access to `clawhub.ai`, `github.com`, and the npm registry.

The skill detects missing prerequisites at Step 7 and prints a clear error before running any publish command.

---

## Limitations

- **Single publisher handle.** This skill publishes everything under `@mebusw` / `github.com/mebusw`. If you publish under a different GitHub owner, fork the skill and change the hardcoded slug.
- **No rollback.** Once a version is published to ClawHub, you cannot unpublish from the CLI. Use the ClawHub web UI for takedowns.
- **No multi-language READMEs beyond English + Chinese.** If you need Japanese, Korean, etc., add them manually after publish.
- **The cleanup step is conservative.** It removes anything it cannot classify as part of the skill. If your skill genuinely needs a `config.yaml` outside the standard folders, you may need to edit `scripts/strip_bundle.py`.

---

## Related skills

- [`skill-creator`](https://github.com/anthropics/skills/tree/main/skills/skill-creator) — Design a skill from scratch. Use *before* this one.
- [`skill-optimizer`](https://github.com/mebusw/skill-optimizer) — Audit and tighten an existing `SKILL.md`. Often invoked as a pre-step.
- [`release-skills`](https://github.com/mebusw/release-skills) — Universal version-bump + changelog workflow. Often invoked as a pre-step.

---

## Sources

- [ClawHub Skill Format](https://docs.openclaw.ai/clawhub/skill-format) — bundle structure and file allowlist
- [skills.sh docs](https://skills.sh/docs) — how `npx skills add` resolves a repo
- [agentskills.io Specification](https://agentskills.io/specification) — what makes a valid `SKILL.md`
- [agentskills.io Best Practices](https://agentskills.io/skill-creation/best-practices) — what makes a good skill

---

## License

MIT-0. Anyone may use, modify, and redistribute, including commercially.

---

[中文文档 / Chinese version →](README.zh-cn.md)