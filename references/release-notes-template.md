# Release Notes Template

`RELEASE_NOTES.md` is what ClawHub shows on a skill's "Release" tab. It is generated automatically by the publisher from your `CHANGELOG.md` or git log, then saved at the root of the skill folder so it ships with the bundle.

This file is the template the publisher follows. You can also write release notes by hand following the same structure.

---

## The template

```markdown
## <VERSION> — <YYYY-MM-DD>

### What's new

- <bullet 1 — most important change first>
- <bullet 2>
- <bullet 3>

### Install

\`\`\`bash
npx skills add https://github.com/mebusw/<slug>
openclaw skills install @mebusw/<slug>
\`\`\`

### Full changelog

<commit list or compare URL>

### Contributors

- @<username> — <contribution>
```

---

## Section guidance

### Version line

`<VERSION>` is the semver (e.g. `1.2.3`). `<YYYY-MM-DD>` is the release date in UTC. Format:

```markdown
## 1.2.3 — 2026-06-28
```

If you do not have a version yet, use `0.1.0 — YYYY-MM-DD` for the first release.

### What's new

3–5 bullets. Each bullet:

- Starts with a verb in past tense ("Added", "Fixed", "Improved").
- Names the user-visible change, not the implementation detail.
- Is one line. Multi-line bullets are hard to scan.

**Good:**

```markdown
- Added `--dry-run` flag to preview the publish pipeline without mutating files.
- Fixed dot-file leakage when bundles included `.playwright-mcp/` directories.
- Improved release note generation by falling back to git log when CHANGELOG is missing.
```

**Bad:**

```markdown
- Code changes
- Bug fixes
- Refactor
```

If a section is empty (e.g. no breaking changes), omit it entirely. Do not write "None."

### Install

Always include both install commands — ClawHub users go to ClawHub, skills.sh users go to npm. The two command format must be exactly:

```bash
npx skills add https://github.com/mebusw/<slug>
openclaw skills install @mebusw/<slug>
```

### Full changelog

Either:

- A bullet list of commits since the last tag:

  ```markdown
  - feat: add dry-run mode (abc1234)
  - fix: strip .playwright-mcp directories (def5678)
  - docs: update README install command (9ab0123)
  ```

- Or a compare URL:

  ```markdown
  https://github.com/mebusw/<slug>/compare/v1.2.2...v1.2.3
  ```

Pick whichever is more readable. For small releases, the compare URL is enough.

### Contributors

Only include third-party contributors — anyone whose GitHub username is **not** `mebusw`. Format:

```markdown
- @contributor-name — what they contributed
```

If the release is single-author, omit the section entirely.

---

## How the publisher generates this

When the publisher runs Step 5, it tries the following sources in order:

1. **Latest CHANGELOG section** — reads `CHANGELOG.md` (or `CHANGELOG.zh.md` for Chinese). If a section matches the current version, lifts the bullets verbatim.

2. **Git log since last tag** — runs:

   ```bash
   git log $(git describe --tags --abbrev=0)..HEAD --oneline
   ```

   Summarizes each commit into a "What's new" bullet. Conventional commit prefixes (`feat:`, `fix:`, `docs:`) are used as bullet prefixes.

3. **Frontmatter + git diff** — if neither of the above produces anything useful, lifts the first sentence of `description` as the headline, and runs `git diff --stat` over the last 30 days to populate "What's new" with file-level changes.

The generated notes are saved to `RELEASE_NOTES.md` at the skill root and shipped with the bundle. You can edit them by hand after generation — the publisher will not regenerate over an existing file unless the file is stale (older than the most recent commit).

---

## Staleness check

Before generating, the publisher checks whether the existing `RELEASE_NOTES.md` is fresh:

```bash
NEWER_COMMITS=$(git log --since="$(stat -f %Sm RELEASE_NOTES.md)" --oneline | wc -l)
```

If `NEWER_COMMITS > 0`, the file is stale and the publisher regenerates. If zero, the publisher leaves the existing file alone.

This means hand-edited release notes survive across publishes, as long as you commit them.

---

## Example: filled-in release notes

```markdown
## 1.2.3 — 2026-06-28

### What's new

- Added `--dry-run` flag to preview the publish pipeline without mutating files.
- Fixed dot-file leakage when bundles included `.playwright-mcp/` directories.
- Improved release note generation by falling back to git log when CHANGELOG is missing.

### Install

\`\`\`bash
npx skills add https://github.com/mebusw/skill-publisher
openclaw skills install @mebusw/skill-publisher
\`\`\`

### Full changelog

https://github.com/mebusw/skill-publisher/compare/v1.2.2...v1.2.3

### Contributors

- @reviewer-name — caught the `.playwright-mcp/` dot-file leak in code review.
```

---

## What NOT to include

- **Emoji** — ClawHub and skills.sh render plain Markdown. Emoji renders inconsistently.
- **Marketing copy** — release notes are for users who already use the skill, not prospects.
- **Internal references** — "JIRA-1234", "ticket", "internal doc" — meaningless to outside readers.
- **Long commit messages** — link to the compare view instead.
- **Placeholder text** — "TBD", "TODO", "..." — fill in or omit the section.