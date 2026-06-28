## Description: <br>
Publishes Agent Skills to clawhub.ai and skills.sh in one workflow. Validates SKILL.md against the agentskills.io spec, ensures the skill-card.md + bilingual README trio exists, strips dot-files and credentials from the bundle, drafts a release note, and drives `openclaw skills install @mebusw/<slug>` plus `npx skills add https://github.com/mebusw/<slug>` end to end. Optionally chains `/skill-optimizer` (description and trigger accuracy) and `/release-skill` (version bump + changelog) as pre-steps. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[mebusw](https://clawhub.ai/user/mebusw) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
Skill authors and maintainers use this skill when they want to ship a SKILL.md-based Agent Skill to multiple marketplaces from a single command. It handles the parts people forget — bilingual README, dot-file cleanup, credential scrubbing, release note — and chains to skill-optimizer and release-skill so the artifact is polished and versioned before it ships. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: The bundle cleanup step can accidentally remove files the skill needs to function at runtime (config files, required assets). <br>
Mitigation: The cleanup script preserves any file under `references/`, `scripts/`, `assets/`, `templates/`, and any explicitly required config. It also prints every removed file so the user can review before publish. <br>
Risk: Credential files (`.env`, `*.key`, `*.pem`, `secrets.*`) can leak into the bundle if cleanup is skipped or bypassed. <br>
Mitigation: `scripts/strip_bundle.py` detects credential-looking filenames and refuses to publish until the user explicitly acknowledges them. The publish command does not run if cleanup has not been confirmed. <br>
Risk: Publishing the same version twice creates a duplicate on the marketplace, which the marketplace may reject or display as confusing history. <br>
Mitigation: The skill checks the current git tag against the latest marketplace version before publishing and refuses to publish the same version without an explicit `--force` flag. <br>
Risk: Running `/skill-optimizer` or `/release-skill` automatically can make changes the user did not intend to ship. <br>
Mitigation: Both pre-steps ask for confirmation before mutating files; auto-invocation only happens when the user has passed an explicit opt-in flag. <br>
Risk: The `openclaw skills install` and `npx skills add` commands require network access and (for the npm variant) Node.js on the user's machine. <br>
Mitigation: The skill detects missing prerequisites before running and prints a clear error with install instructions, rather than failing mid-publish. <br>


## Reference(s): <br>
- [ClawHub Skill Page](https://clawhub.ai/mebusw/skills/skill-publisher) <br>
- [skills.sh Listing](https://skills.sh/mebusw/skill-publisher) <br>
- [ClawHub Bundle Spec](references/clawhub-bundle.md) <br>
- [skills.sh Publish Guide](references/skills-sh-publish.md) <br>
- [Skill Card Template](references/skill-card-template.md) <br>
- [Release Notes Template](references/release-notes-template.md) <br>
- [Agent Skills Specification](https://agentskills.io/specification) <br>


## Skill Output: <br>
**Output Type(s):** [text, markdown, shell commands, configuration, guidance] <br>
**Output Format:** [Markdown report with inline shell commands, file diffs, and a final 8-line confirmation block covering both marketplaces] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Mutates the source skill folder (creates/refreshes skill-card.md, README.md, README.zh-cn.md, RELEASE_NOTES.md; removes dot-files and credentials), then performs two marketplace publish operations. All side effects are listed in the cleanup log before they happen.] <br>

## Skill Version(s): <br>
0.1.0 (source: skill frontmatter) <br>

## Ethical Considerations: <br>
Users should evaluate whether publishing a given skill is appropriate for their environment, review the bundle cleanup log to confirm no sensitive files are included, and confirm that the published artifact's license and attribution are correct before release. Organizations should apply their own safety, security, and compliance review to any externally-published AI skill before adopting it. <br>