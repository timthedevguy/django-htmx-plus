---
name: release-notes
description: Generate or update the release notes for a specific GitHub release/tag in this repo by reading the commits since the previous release and formatting the ones that follow Conventional Commits into grouped sections (Features, Bug Fixes, etc.), then writing the result back onto the GitHub release. Trigger whenever the user names a version and asks to "create release notes", "generate the changelog", "write up what's in this release", or "update the release notes" for it — e.g. "create release notes for v1.4.0" or "generate release notes for 2.3.0". Requires the GitHub CLI (`gh`), authenticated against this repo.
---

# Release Notes from Conventional Commits

Turns the commit history for one release into readable, grouped release notes and publishes them to that GitHub release. The input is always a version the user names (e.g. `v1.4.0`, `1.4.0`) — never guess which release they mean.

## Prerequisites

- `gh` CLI installed and authenticated (`gh auth status`). This skill uses `gh` for everything GitHub-related — reading the release, listing releases to find the previous one, and writing the updated notes back. If `gh` isn't available or isn't authenticated, tell the user and stop rather than guessing at API calls.
- The repo's tags are up to date locally: run `git fetch --tags --quiet` before diffing commit ranges, since the changelog is built from `git log`, not the GitHub API.

## Step 1 — Resolve the version to a real release

Normalize what the user typed against what actually exists — users say "1.4.0" as often as "v1.4.0":

```bash
gh release view <version> --json tagName,name,body,publishedAt,isDraft,isPrerelease
```

If that fails, retry with the other prefix convention (`v` added or stripped). If it still fails, list releases (`gh release list --limit 20`) and ask the user which one they meant rather than assuming.

## Step 2 — Find the previous release, to bound the commit range

```bash
gh release list --json tagName,createdAt,isDraft --limit 100
```

Sort by `createdAt` and find the entry immediately before the target release — that tag is the lower bound. Use chronological order here, not a semver sort: pre-releases, hotfix tags, and out-of-order version bumps make semver ordering unreliable, while "the release published right before this one" is what a reader actually expects the notes to cover.

If the target release is the oldest one in the repo, the range is "everything up to that tag" — use the tag alone (`git log <tag>`) instead of a `prev..tag` range.

## Step 3 — Collect the commits in range

```bash
git log <previous_tag>..<tag> --no-merges --pretty=format:"%H%x09%s"
```

`--no-merges` skips merge-bubble commits ("Merge pull request #123 from ..."), which are never themselves Conventional Commits. This works cleanly for squash-merge workflows, where the squashed commit subject *is* the PR title. If a scan of the log shows mostly merge commits and few real ones — a sign this repo merges branches rather than squashing — fall back to `gh pr list --state merged --search "merged:<date-range>"` and use PR titles as the commit list instead, since that's where the real conventional-commit-style summaries will live.

## Step 4 — Parse each commit against the Conventional Commits format

Format: `type(scope)!: description` — see the `conventional-commits` skill for the full spec if you need the details on types or breaking-change markers. For each commit line:

- Match `^(\w+)(\([\w./-]+\))?(!)?: (.+)$` against the subject.
- If it matches, capture type, optional scope, breaking-marker, and description.
- If it doesn't match, keep the commit but mark it as non-conventional — don't silently drop it. A commit that doesn't fit the format is still a real change the reader should see.

## Step 5 — Group into sections

Map types to sections, in this display order:

| Type(s) | Section heading |
|---|---|
| commits with `!` or a `BREAKING CHANGE:` footer | `### ⚠ BREAKING CHANGES` (always first, regardless of type) |
| `feat` | `### Features` |
| `fix` | `### Bug Fixes` |
| `perf` | `### Performance Improvements` |
| `revert` | `### Reverts` |
| `refactor` | `### Refactoring` |
| `docs` | `### Documentation` |
| `build`, `ci` | `### Build & CI` |
| `style`, `test`, `chore` | `### Chores` |
| unparseable commits | `### Other Changes` |

Skip a section entirely if it has no entries — don't print empty headers.

Format each entry as a bullet with the short hash linked to the commit, scope bolded when present:

```
- **auth:** add password reset flow ([a1b2c3d](https://github.com/<owner>/<repo>/commit/<full-sha>))
- fix login redirect loop on expired sessions ([e4f5a6b](...))
```

For the `BREAKING CHANGES` section, pull the full explanation from the `BREAKING CHANGE:` footer if one exists; if the commit only has `!` with no footer, use the description itself.

## Step 6 — Confirm before publishing

Publishing overwrites the release's existing notes on GitHub — a visible, shared change. Show the user the generated markdown and the release's current body side by side before writing anything. If the current body has hand-written content worth keeping (a summary paragraph, upgrade instructions, contributor shout-outs), ask whether to prepend/preserve it above the generated sections or replace the body outright — don't assume either way.

## Step 7 — Publish

```bash
gh release edit <tag> --notes-file <path-to-generated-notes.md>
```

Write the notes to a temp file first (avoids shell-escaping problems with markdown special characters), pass that file, then confirm the update by re-running `gh release view <tag>` and showing the user the published result.
