# skills.sh Publish Guide

How `npx skills add https://github.com/mebusw/<slug>` resolves a GitHub repo and turns it into a skills.sh entry.

Source: [skills.sh/docs](https://skills.sh/docs) (consult for the latest authoritative version).

---

## What skills.sh is

skills.sh is a registry of Agent Skills indexed from public GitHub repos. It is read-only — you do not push skills to it. Instead, you push your skill to GitHub, and skills.sh indexes it on the next crawl.

That is why the install command is:

```bash
npx skills add https://github.com/mebusw/<slug>
```

This installs from GitHub directly. The skills.sh registry is just a search-and-discovery layer.

---

## Repo requirements

For `npx skills add` to work, the repo must:

1. Be **public** on GitHub.
2. Contain a `SKILL.md` at the repo root or at the path specified by `--skill <subdir>`.
3. The `SKILL.md` frontmatter must have a valid `name` (kebab-case) and `description`.
4. The repo must have at least one commit on the default branch.

For multi-skill monorepos, use:

```bash
npx skills add https://github.com/mebusw/<repo> --skill <subdir>
```

For example, if your monorepo has `skills/foo/` and `skills/bar/`:

```bash
npx skills add https://github.com/mebusw/agent-toolkit --skill foo
npx skills add https://github.com/mebusw/agent-toolkit --skill bar
```

---

## The install command

```bash
npx skills add https://github.com/mebusw/<slug>
```

### Flags

| Flag | Effect |
|------|--------|
| `--skill <name>` | When the repo has multiple skills, pick which one to install. |
| `-g, --global` | Install to the global skills directory instead of the current project. |
| `-y, --yes` | Skip the confirmation prompt. |

### What it does

1. Clones (shallow) the repo to a temp directory.
2. Resolves which skill to install based on the `--skill` flag or the repo root.
3. Validates `SKILL.md` against the agentskills.io spec.
4. Copies the skill folder to the destination:
   - Local install: `./.claude/skills/<slug>/` (or wherever the user's `skills.sh` config points)
   - Global install: `~/.claude/skills/<slug>/`
5. Optionally links binaries in `./.claude/bin/`.

### Exit codes

| Code | Meaning |
|------|---------|
| `0` | Installed successfully. |
| `1` | Validation failed or repo not found. |
| `2` | User declined confirmation. |

---

## How skills.sh indexes your skill

skills.sh crawls GitHub for repos with `SKILL.md` files. After you push to `github.com/mebusw/<slug>`, your skill typically appears in the registry within a few hours.

To speed up indexing, you can submit your repo URL via the skills.sh web UI. But the default crawl picks up new repos automatically — manual submission is rarely needed.

skills.sh reads `SKILL.md` frontmatter to populate the listing:

- `name` → skill display name
- `description` → skill description
- `metadata` → optional structured fields
- `license` → shown if present

It does **not** parse `skill-card.md`. That format is ClawHub-specific.

---

## Versioning

skills.sh does not have a built-in version concept — the install command always pulls `main`. If you want version pinning, you must:

1. Tag the commit: `git tag v1.2.3`.
2. Have users install a specific tag manually:

   ```bash
   npx skills add https://github.com/mebusw/<slug>#v1.2.3
   ```

This works because `npx skills add` accepts any git ref. But it is not the typical usage — most users want the latest.

---

## The README install command

The README's install section should always be exactly:

```bash
npx skills add https://github.com/mebusw/<slug>
```

Do not paraphrase, do not add `--skill` unless the repo is a monorepo, and do not use shorthand (`github.com/mebusw/<slug>` without `https://`). The publisher skill enforces this in Step 4.

---

## What to put in `README.md` for skills.sh discoverability

Beyond the install command, skills.sh uses the `description` field of `SKILL.md` as the listing description. To get more installs:

- Make the `description` field concrete and keyword-rich.
- List common trigger phrases ("use when...", "for...", "if you need...").
- Include a "Quick start" section in `README.md` with a copy-paste example.

---

## Troubleshooting

### "Repository not found"

- The repo does not exist at that URL.
- The repo is private.
- You have a typo. Double-check `mebusw/<slug>` against the actual GitHub URL.

### "SKILL.md not found"

- The repo has `SKILL.md` in a subfolder. Use `--skill <subdir>`.
- The file is named `skill.md` (lowercase) or `Skills.md`. Rename to `SKILL.md` (capital, kebab-name match).

### "Invalid SKILL.md"

Run `npx skills add` with `--verbose` (if available) to see the specific validation error. Common causes:

- Missing or invalid frontmatter.
- `name` contains uppercase or non-kebab-case characters.
- `description` is empty or contains `<` or `>`.

### "Permission denied" when installing globally

You need sudo on macOS/Linux to write to `~/.claude/skills/`. Either:

- Use a local install (drop the `-g` flag): `npx skills add https://github.com/mebusw/<slug>`.
- Or fix permissions on `~/.claude/skills/`.

---

## Practical checklist before pushing to GitHub

- [ ] Repo exists at `github.com/mebusw/<slug>` and is public.
- [ ] `SKILL.md` is at the root (or under a known subdir).
- [ ] Frontmatter is valid YAML with `name` and `description`.
- [ ] `name` field matches the directory name.
- [ ] All bundled files are text-based (no binaries).
- [ ] No `.env`, `*.key`, or `*.pem` files in the repo.
- [ ] `.gitignore` excludes `node_modules/`, `__pycache__/`, `.DS_Store`, etc.
- [ ] At least one commit on `main` (or the default branch).
- [ ] README install command is exactly `npx skills add https://github.com/mebusw/<slug>`.

After all of these are green, run the install command yourself to verify it works end-to-end before announcing the release.