# Skill Card Template

`skill-card.md` is the metadata card that ClawHub displays on each skill's page. Every published skill must have one at the root.

The format is fixed — ClawHub's renderer parses the section headers. Do not rename, reorder, or omit sections.

---

## The template

Copy this block into your skill folder as `skill-card.md`, then fill in the placeholders. Keep the `<br>` tags — ClawHub uses them for line breaks in the rendered card.

```markdown
## Description: <br>
<One or two sentences describing what the skill does and when to use it. Pull from the `description` field of your SKILL.md, then add the headline value prop.> <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[mebusw](https://clawhub.ai/user/mebusw) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
<Who is the target user? What problem does this skill solve? When would they reach for it?> <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: <Realistic risk — not theoretical>. <br>
Mitigation: <What the skill does, or what the user should do, to reduce the risk.> <br>
Risk: <Another risk>. <br>
Mitigation: <Mitigation>. <br>
Risk: <Another risk>. <br>
Mitigation: <Mitigation>. <br>


## Reference(s): <br>
- [ClawHub Skill Page](https://clawhub.ai/mebusw/skills/<slug>) <br>
- [skills.sh Listing](https://skills.sh/mebusw/<slug>) <br>
- <Link to the skill's GitHub repo> <br>
- <Link to any key reference doc, e.g. `references/api.md`> <br>
- [Agent Skills Specification](https://agentskills.io/specification) <br>


## Skill Output: <br>
**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance] <br>
**Output Format:** <One-line description of the output shape, e.g. "Markdown report with inline shell commands"> <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** <Any caveats — destructive operations, network calls, required tools, etc.> <br>

## Skill Version(s): <br>
<X.Y.Z (source: <how you determined this — git tag, server response, frontmatter>)> <br>

## Ethical Considerations: <br>
<One or two sentences on what the user should evaluate before adopting the skill. Mention review of generated files, environment suitability, and any compliance obligations.> <br>
```

---

## Field guidance

### Description

One or two sentences. Pull from the `description` field of your `SKILL.md`, then add what the skill uniquely buys the user. ClawHub shows this in the search results.

**Good:** "Publishes Agent Skills to clawhub.ai and skills.sh in one workflow. Strips dot-files and credentials, drafts a release note, drives both marketplaces end to end."

**Bad:** "A skill for publishing skills." (Too vague — says nothing about what makes this one different.)

### Use Case

Name the user, the problem, and the trigger context. Be concrete.

**Good:** "Skill authors and maintainers use this skill when they want to ship a SKILL.md-based Agent Skill to multiple marketplaces from a single command."

**Bad:** "Useful for many scenarios." (Avoid "useful for many scenarios.")

### Known Risks and Mitigations

List 2–4 realistic risks. Each risk should be plausible, not theoretical. Each mitigation should be a concrete action the skill takes, or that the user should take.

Common risks worth listing if they apply:

- Network calls (mitigation: opt-in flag, clear log of what is sent).
- Destructive operations (mitigation: dry-run mode, confirmation step).
- Credential handling (mitigation: never log secrets, scrub before publishing).
- Long-running external processes (mitigation: timeout + cancellation).
- Filesystem mutations (mitigation: snapshot before, list after).

### Reference(s)

Always include:

- The ClawHub skill page URL.
- The skills.sh listing URL.
- The GitHub repo URL.
- A link to `references/` content if any.
- The agentskills.io spec link.

### Skill Output

`Output Type(s)` — pick from the list that matches your skill. You can list multiple.

`Output Format` — one line, in plain English.

`Output Parameters` — leave `[1D]` unless your output is genuinely 2D (e.g. a table the user might pivot).

`Other Properties Related to Output` — call out anything the user needs to know: side effects, required tools, error behavior.

### Skill Version(s)

Format: `X.Y.Z (source: <how you determined this>)`.

- If you have a git tag: `source: git tag vX.Y.Z`.
- If you only have a frontmatter version: `source: skill frontmatter`.
- If neither, write `source: initial release` and add a TODO.

### Ethical Considerations

One or two sentences. Always mention that the user should review generated files before relying on them. Always mention that organizations should apply their own safety/security/compliance review.

---

## Common mistakes

- **Omitting `<br>` tags.** The ClawHub renderer treats line breaks as whitespace. Without `<br>`, the card runs together into one paragraph.
- **Wrong section headers.** The headers must match exactly (`## Description:`, `## Publisher:`, etc.). Case matters.
- **Risk/mitigation mismatch.** Each risk must be paired with a real mitigation. "Risk: X. Mitigation: Y" where Y does not actually reduce X is worse than no risk at all.
- **Outdated version.** Update the version field whenever you bump. ClawHub shows it on the card.
- **No GitHub link.** The Reference(s) section must include the GitHub repo. Without it, reviewers cannot audit the skill.

---

## Validation checklist

Before publishing, run through this list:

- [ ] All section headers match the template exactly.
- [ ] Description is 1–2 sentences and includes what the skill *does*, not just *is*.
- [ ] Use Case names a specific user and trigger context.
- [ ] At least 2 Known Risks, each with a real mitigation.
- [ ] Reference(s) section includes ClawHub page, skills.sh listing, and GitHub repo.
- [ ] Output Parameters is `[1D]` unless genuinely 2D.
- [ ] Skill Version(s) matches the git tag or frontmatter version.
- [ ] Ethical Considerations is present and concrete.
- [ ] No `<` or `>` characters anywhere in the body (ClawHub rejects them).
- [ ] All `<br>` tags are in place.