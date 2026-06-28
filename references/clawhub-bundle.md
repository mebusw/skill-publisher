# ClawHub Bundle Spec

What ClawHub accepts, rejects, and what the `openclaw skills install` command does under the hood.

Source: [docs.openclaw.ai/clawhub/skill-format](https://docs.openclaw.ai/clawhub/skill-format) (consult for the latest authoritative version).

---

## What is a skill bundle?

A skill bundle is a **folder** (or zipped folder) that ClawHub ingests as a single skill. The folder must contain `SKILL.md` at the root.

### Required

- `SKILL.md` — the skill definition. Also accepted: `skill.md` (legacy), `skills.md` (very legacy).

### Recommended for full functionality

- `skill-card.md` — metadata card ClawHub renders on the skill page (see `references/skill-card-template.md`).
- `README.md` — primary user-facing documentation.
- `README.zh-cn.md` — Chinese documentation.
- `references/` — deep-dive docs loaded into context on demand.
- `scripts/` — bundled executable code (Python, Node, etc.).
- `assets/` — templates, icons, fonts used in skill output.

### Optional

- `.clawhubignore` — gitignore-style file listing paths to exclude. Use this instead of editing the cleanup script for skill-specific exclusions.
- `.gitignore` — excluded from bundle automatically.

---

## File allowlist (text-only)

ClawHub only accepts **text-based** files. The exact extension allowlist lives in `packages/schema/src/textFiles.ts` in the OpenClaw repo. The practical subset:

| Category | Extensions |
|----------|-----------|
| Markdown | `.md`, `.markdown`, `.mdx` |
| Code (text) | `.py`, `.js`, `.ts`, `.tsx`, `.jsx`, `.mjs`, `.cjs`, `.sh`, `.bash`, `.zsh`, `.rb`, `.go`, `.rs`, `.java`, `.kt`, `.swift`, `.c`, `.cpp`, `.h`, `.hpp`, `.cs`, `.php`, `.lua`, `.pl`, `.r`, `.scala` |
| Config (text) | `.json`, `.yaml`, `.yml`, `.toml`, `.ini`, `.cfg`, `.conf`, `.env.example` (not real `.env`) |
| Text data | `.txt`, `.csv`, `.tsv`, `.xml`, `.html`, `.htm`, `.css`, `.scss`, `.sass`, `.less` |
| Shell | `.fish`, `.ps1`, `.bat`, `.cmd` |
| Misc | `.gitignore`, `.gitattributes`, `.editorconfig`, `.clawhubignore`, `.lock`, `.log` (excluded by cleanup anyway) |

Anything else — binaries, images, archives, compiled assets — should be excluded from the bundle. The cleanup script removes these by default.

**Note:** if your skill genuinely needs a binary asset (e.g. a font file), host it externally and reference the URL from `references/`. Do not embed binaries in the bundle.

---

## Size limits

| Limit | Value |
|-------|-------|
| Total bundle | 50 MB |
| Files embedded in context | ~40 non-`.md` files plus all `.md` |
| `SKILL.md` body | recommended ≤ 500 lines |

If your bundle exceeds 50 MB, you almost certainly have build artifacts (`node_modules/`, `dist/`) or stray data files (`*.csv` exports, logs) that should be excluded. The cleanup script catches most of these.

---

## The `openclaw skills install` command

```bash
openclaw skills install @<publisher>/<slug>
```

Where `<publisher>` is the ClawHub namespace and `<slug>` is the skill identifier.

For skills published by `@mebusw`, the command is:

```bash
openclaw skills install @mebusw/<slug>
```

### What it does

1. Resolves `@mebusw/<slug>` against the ClawHub registry.
2. Downloads the latest published version of the skill bundle.
3. Validates the bundle against the spec (file allowlist, size limit, `SKILL.md` presence, frontmatter).
4. If the user already has a skill with that slug installed at a lower version, prompts for upgrade confirmation.
5. Installs to the user's local skill directory (`~/.claude/skills/<slug>/` by default, or wherever their agent stores skills).

### Exit codes

| Code | Meaning |
|------|---------|
| `0` | Installed successfully. |
| `1` | Generic failure — see stderr. |
| `2` | Bundle validation failed (size, allowlist, missing `SKILL.md`). |
| `3` | Network or registry error. |
| `4` | User declined the upgrade prompt. |

If you see `2`, the bundle is malformed — re-run the cleanup script and inspect the bundle tree.

### Install location

By default, `openclaw skills install` puts the skill in the agent's standard skill directory. On Claude Code this is `~/.claude/skills/<slug>/`. The user's environment may override this with `--install-dir <path>`.

---

## Versioning

ClawHub tracks version by git tag (preferred) or frontmatter `version` field. If both are present, the git tag wins.

The `openclaw skills install` command always pulls the **latest** version by default. To pin:

```bash
openclaw skills install @mebusw/<slug>@<version>
```

If you re-publish the same version (same git tag), ClawHub will reject the upload as a duplicate. The publisher skill enforces this and refuses to re-publish without an explicit `--force` flag.

---

## How `skill-card.md` is rendered

ClawHub parses `skill-card.md` section headers and uses them as labeled fields on the skill page. The renderer:

- Splits on `## ` and `### ` headers.
- Treats `Risk:` and `Mitigation:` lines as paired fields under the "Known Risks and Mitigations" header.
- Strips `<br>` tags but uses them as paragraph breaks.

If you rename a section header (e.g. `## Description:` → `## Summary:`), ClawHub will not know where to place the content. Use the template headers verbatim.

---

## Practical checklist before publishing

Run through this before running `openclaw skills install`:

- [ ] `SKILL.md` exists and parses (frontmatter is valid YAML).
- [ ] `SKILL.md` `name` field matches the directory name.
- [ ] `skill-card.md` exists with all required sections.
- [ ] `README.md` and `README.zh-cn.md` both exist.
- [ ] No dot-files at the root (`.git/`, `.DS_Store`, `.vscode/`, etc.).
- [ ] No credential files (`.env`, `*.key`, `*.pem`, `secrets.*`).
- [ ] No build artifacts (`node_modules/`, `dist/`, `__pycache__/`).
- [ ] No binary files unless they are part of an externally-hosted asset URL.
- [ ] Bundle size under 50 MB.
- [ ] Git tag exists and matches the version in `skill-card.md` and `README.md`.
- [ ] The install command in `README.md` is exactly `npx skills add https://github.com/mebusw/<slug>`.