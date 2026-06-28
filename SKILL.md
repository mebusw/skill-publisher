---
name: skill-publisher
description: Publish Agent Skills to clawhub.ai and skills.sh in one workflow. Use when the user wants to release, publish, ship, or distribute a SKILL.md-based skill — even if they don't say "publisher" explicitly. Triggers on phrases like "publish my skill", "release to clawhub", "submit to skills.sh", "发布skill", "上传skill", "上架skill", "ship to marketplace", "make my skill available", "auto-release", or any request to push a skill folder to multiple marketplaces. Generates skill-card.md and bilingual README, strips dot-files and credentials, drafts a release note, optionally invokes /skill-optimizer for description tweaks and /release-skill for version bumps, then drives `openclaw skills install @mebusw/<slug>` and `npx skills add https://github.com/mebusw/<slug>` end to end.
---

# Skill Publisher

A focused publisher workflow for **Agent Skills** (`SKILL.md`-based). One skill folder in → two marketplaces out: **ClawHub** (`openclaw skills install @mebusw/<slug>`) and **skills.sh** (`npx skills add https://github.com/mebusw/<slug>`).

The skill is opinionated about what "ready to ship" means. It does not just zip and upload — it cleans, validates, documents, and only then hands off to the marketplace tooling. Most users forget at least one of those steps; this skill enforces the checklist.

---

## When to use

Use this skill for any of:

- "Publish my skill to clawhub" / "上架到 clawhub" / "release to clawhub.ai"
- "Push to skills.sh" / "make `npx skills add` work"
- "Auto-release this skill" / "发布到多个 skill 市场"
- "Ship the skill to all marketplaces"
- "Generate the skill-card for clawhub"
- "Add a Chinese README so non-English users can install"
- Any time a skill folder needs to go from local to public

Do **not** use this skill to:

- Create a skill from scratch → use `skill-creator`.
- Polish or audit an existing SKILL.md → use `skill-optimizer` first (this skill can invoke it as a pre-step, but it is not the primary tool).
- Bump version, write a changelog, push tags → use `release-skills`. (Again, this skill can invoke it as a pre-step.)
- Publish something that is not a SKILL.md-based Agent Skill (a CLI tool, a Node package, etc.).

If you are not sure whether the artifact qualifies as an Agent Skill, look for `SKILL.md` with YAML frontmatter containing `name` and `description`. If it has both, you are in the right place.

---

## Inputs

The skill expects a path to a skill folder. Defaults assume the current working directory contains a `SKILL.md`.

| Input | Default | Notes |
|-------|---------|-------|
| `SKILL_DIR` | current directory | Folder containing `SKILL.md` |
| `SLUG` | directory name | Used in `github.com/mebusw/<slug>` and `@mebusw/<slug>` |
| `VERSION` | derived from git tag | Bump before release if needed |
| `DRY_RUN` | `false` | If true, print actions without executing them |
| `SKIP_OPTIMIZER` | `false` | Skip the optional /skill-optimizer step |
| `SKIP_RELEASE_SKILL` | `false` | Skip the optional /release-skill step |

The publisher handle (`mebusw`) is hardcoded — every skill ships under the same GitHub owner and ClawHub namespace. If you need a different handle, fork the skill.

---

## The publish workflow

The full pipeline is nine steps. Steps marked **(optional)** are conditional; the rest must run every time. The order matters — do not reorder.

### Step 1 — Locate and validate the skill folder

1. Confirm `SKILL_DIR` exists and contains `SKILL.md`.
2. Read the frontmatter. Verify:
   - `name` matches the directory name (kebab-case).
   - `description` is non-empty, in English, ≤ 1024 chars, no angle brackets.
   - Body is ≤ ~500 lines. If longer, flag and recommend moving detail to `references/`.
3. Read `references/specification-checklist.md` from the `skill-optimizer` skill if it is installed, and apply the same Dimension 1 checks. Fail loud if the skill is not spec-valid — ClawHub will reject it anyway.

If the skill fails validation, stop. Tell the user what is broken. Do not silently fix it (that is `skill-optimizer`'s job, not this one's).

### Step 2 — **(optional)** Invoke `/skill-optimizer`

If `SKIP_OPTIMIZER` is false, suggest running `/skill-optimizer` first. This is the right time to:

- Tighten the description for better triggering.
- Catch specification issues (frontmatter, naming, length).
- Run the bundled `scripts/audit_skill.py`.

Only auto-invoke if the user has already opted in by passing a flag or saying "yes, optimize first." Otherwise ask once and wait.

If `/skill-optimizer` makes changes, the user is responsible for committing them before the publish step.

### Step 3 — **(optional)** Invoke `/release-skill`

If `SKIP_RELEASE_SKILL` is false, and the user has uncommitted changes since the last tag, suggest running `/release-skill`. This is the right time to:

- Bump the version (patch / minor / major).
- Generate the changelog entry that becomes the release note.
- Create the git tag.

If no git repo is present, or there are no unreleased commits, skip this step silently.

### Step 4 — Ensure documentation trio exists

Every published skill must have these three files at the root of the skill folder:

| File | Language | Required content |
|------|----------|------------------|
| `skill-card.md` | English | ClawHub-specific metadata card (description, publisher, license, use case, risks, references, output type, version, ethical considerations). See template in `references/skill-card-template.md`. |
| `README.md` | English | English quick-start, install command, file structure, usage. |
| `README.zh-cn.md` | Chinese (Simplified) | Same structure as `README.md`, translated. |

Rules:

- The `description` field in `SKILL.md` must be in **English**. Body text can be English or Chinese.
- `skill-card.md` and `README.md` are **always English**.
- `README.zh-cn.md` is **always Chinese**.
- If any of these files is missing, create it from the templates in `references/`.
- If a file already exists but is stale (wrong version number, missing install command, broken links), refresh it. Preserve any custom sections the user added.
- The install command on `README.md` and `README.zh-cn.md` must be exactly:

  ```bash
  npx skills add https://github.com/mebusw/<slug>
  ```

### Step 5 — Draft the release note

The release note is what ClawHub shows on the skill page. Sources, in priority order:

1. **Latest CHANGELOG entry** — read `CHANGELOG.md` (or `CHANGELOG*.md` for the right language) and use the most recent unreleased section.
2. **Git log since last tag** — `git log $(git describe --tags --abbrev=0)..HEAD --oneline`. Summarize into 3–5 bullets.
3. **Frontmatter description** — if neither of the above exists, lift the first sentence of the `description` field as the headline, and add a "What's new" section pulled from `git diff --stat` of the last 30 days.

Format the release note as Markdown with these sections (omit any that are empty):

```markdown
## What's new

- <bullet 1>
- <bullet 2>

## Install

\`\`\`bash
npx skills add https://github.com/mebusw/<slug>
openclaw skills install @mebusw/<slug>
\`\`\`

## Full Changelog

<commit list or link to compare view>
```

Save the release note to `RELEASE_NOTES.md` at the root of the skill folder. This file ships with the bundle.

### Step 6 — Clean the bundle

ClawHub only accepts text-based files (defined by the extension allowlist — see `references/clawhub-bundle.md`). Before bundling, walk `SKILL_DIR` and remove or exclude:

**Always remove (these are not part of the skill):**

- `.git/` and all Git internals
- `.DS_Store`, `Thumbs.db`, `.idea/`, `.vscode/`, `.playwright-mcp/`
- `node_modules/`, `__pycache__/`, `.pytest_cache/`, `dist/`, `build/`
- `.env`, `.env.*`, `*.key`, `*.pem`, `credentials.*`, `secrets.*` — any file that smells like credentials
- `.claude/` session caches (keep `.claude/settings.json` only if it is required for the skill to function — and never include any tokens)
- `*.log`, `*.tmp`, `*.bak`

**Keep (these are part of the skill):**

- `SKILL.md`, `skill-card.md`, `README.md`, `README.zh-cn.md`, `RELEASE_NOTES.md`
- Anything under `references/`, `scripts/`, `assets/`, `templates/`
- Config files explicitly required for the skill to function (e.g. `config/*.yaml`)

Print a list of every removed file before proceeding. If a removed file is suspicious (looks like a credential), pause and tell the user.

Use `scripts/strip_bundle.py <skill-dir>` to do this mechanically — it logs each removal and exits non-zero if it had to delete anything that looked like a credential, so the user can review.

### Step 7 — Publish to ClawHub

The publish command for ClawHub is:

```bash
openclaw skills install @mebusw/<slug>
```

If `openclaw` is not installed locally, install it first via `npm i -g openclaw` (or the platform-specific equivalent). If the user is on a machine without npm, point them to the manual upload UI on https://clawhub.ai.

Before running the install, do a dry-run that:

1. Shows the cleaned bundle contents (`tree SKILL_DIR` or equivalent).
2. Shows the file count and total size. Fail if the size exceeds 50MB.
3. Asks the user to confirm with **yes / no**.

After confirmation, run the install command. Capture stdout + stderr. If the command exits non-zero, stop — do not proceed to skills.sh.

### Step 8 — Publish to skills.sh

skills.sh uses a one-shot npm command:

```bash
npx skills add https://github.com/mebusw/<slug>
```

This requires:

- The skill repo pushed to `github.com/mebusw/<slug>` on the `main` branch.
- `npx` available on the user's machine.
- Network access to npm registry and github.com.

If the repo is not yet pushed, push it first (`git push origin main --tags`). If `npx` is not available, tell the user.

Like Step 7, do a dry-run that shows the exact command, then ask for confirmation.

### Step 9 — Confirm and report

After both publishes complete, print a summary:

```
✓ Published to ClawHub   — https://clawhub.ai/mebusw/skills/<slug>
✓ Published to skills.sh  — https://skills.sh/mebusw/<slug>
✓ GitHub repo             — https://github.com/mebusw/<slug>
✓ Release tag             — v<VERSION>
✓ Bundle size             — <SIZE> (<FILE_COUNT> files)
✓ Files removed           — <COUNT> (listed above)
```

If any step failed, print what failed, why, and what the user needs to do manually. Do not silently fall back.

---

## Dry-run mode

If `DRY_RUN=true`, run all nine steps except:

- Do not modify any files (Step 4: just report what would be created or refreshed).
- Do not delete anything (Step 6: just list what would be removed).
- Do not execute `openclaw skills install` or `npx skills add` (Steps 7 and 8: just print the commands).

The dry-run output is a checklist the user can read in 30 seconds and approve.

---

## `--dry-run` flag

Equivalent to `DRY_RUN=true`. Use whichever form fits the calling context.

## `--skip-optimizer` / `--skip-release-skill` flags

Bypass the optional pre-steps. Useful when the user has already run them manually, or when they want a faster publish.

---

## Bundled resources

- `references/skill-card-template.md` — Fill-in template for `skill-card.md`, derived from the official ClawHub schema.
- `references/clawhub-bundle.md` — Exact file extension allowlist, size limits, and the `openclaw skills install` command spec.
- `references/skills-sh-publish.md` — How `npx skills add` resolves a repo, what files it scans, and how to debug a failed publish.
- `references/release-notes-template.md` — Markdown structure for `RELEASE_NOTES.md`, with example content.
- `scripts/strip_bundle.py` — Walks a skill folder and removes non-bundle files. Logs every removal and warns on credential-looking files.

Read the relevant reference before each step. Do not try to hold the entire ClawHub spec in your head.

---

## Common pitfalls

These come up over and over. When you see them, name them explicitly.

- **Dot-file leakage** — `.git/`, `.DS_Store`, and `.vscode/` slip into bundles if you skip Step 6. Always run `strip_bundle.py`.
- **Stale version number** — `skill-card.md` and `README.md` reference a version that does not match the git tag. Refresh them in Step 4.
- **README in only one language** — ClawHub will accept the skill, but Chinese-speaking users will bounce. Always produce both.
- **Wrong install command** — Anything other than `npx skills add https://github.com/mebusw/<slug>` will not work. Do not paraphrase.
- **Credentials in the bundle** — The single biggest risk. `strip_bundle.py` warns on `.env`, `*.key`, `*.pem`, etc., but you must inspect the bundle tree before publishing.
- **Publishing before optimizing** — A skill with a weak description under-triggers. Run `/skill-optimizer` first.
- **Publishing without a tag** — Without a git tag, the release note has no anchor and skills.sh cannot resolve the version.
- **Re-publishing the same version** — ClawHub refuses duplicates. Bump the version (or use `--force` if the marketplace exposes it; otherwise delete and re-publish manually).

For the full pitfalls catalog with fixes, see `references/common-pitfalls.md` (TODO if not yet present).

---

## Output format

A single publish run produces, in order:

1. **Validation report** — pass/fail per Dimension 1 check.
2. **Optimizer report** (if invoked) — proposed edits.
3. **Release summary** (if invoked) — version bump + changelog preview.
4. **Documentation refresh log** — which of the three files were created vs. updated.
5. **Release note** — saved to `RELEASE_NOTES.md`.
6. **Bundle cleanup log** — every file removed, with reason.
7. **Two publish confirmations** — one per marketplace.
8. **Final summary** — the eight-line confirmation block from Step 9.

The user can stop after any of these by interrupting. If they stop before Step 6, no files have been touched; if they stop after Step 6 but before Step 7, files have been cleaned but not published.

---

## License

MIT-0. Anyone may use, modify, and redistribute, including commercially.