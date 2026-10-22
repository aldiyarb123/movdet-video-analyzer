# Contributing

This repository must show continuous, traceable work by each team member. These rules follow the committee's Git requirements.

## Accounts and access

- Every member commits with **their own account** and real author details. No shared accounts.
- Give the supervisor (Shuryn Tutkyshbayeva) and all members access. Give the committee access **before each pre-defense**.

```bash
git config user.name  "Your Name"
git config user.email "your-account-email@example.com"
```

## Workflow

1. Create or pick a YouTrack task `DIP-n` (owner, expected outcome, acceptance criteria, deadline).
2. Branch from `main`: `DIP-n-short-description`, e.g. `DIP-23-database-schema`.
3. Commit small, coherent changes: `DIP-23: Add initial database schema and ER diagram`.
4. Open a Pull Request (GitHub) / Merge Request (GitLab) using the template. It must explain the change, reference the task, and say how it was checked.
5. **Another team member reviews** before merge. Do not self-merge.
6. Put the PR/commit link into the YouTrack task. Close the task only when its acceptance criteria are met.

`main` is the reviewed baseline. Do not push directly to it.

## Commit messages

- Start with the task ID: `DIP-n: Imperative summary`.
- Docs and design changes are commits too.
- Do not squash a whole week of work into one commit. Do not upload everything just before a pre-defense.

## Secrets

Never commit passwords, API keys, personal data or real videos of people. Use `.env.example` with placeholders.

## Tags

At each submission create a tag and never move it afterwards:

```bash
git tag -a pre-defense-1 -m "Pre-defense 1 submission"
git push origin pre-defense-1
```

Tags: `pre-defense-1`, `pre-defense-2`, `final-pre-defense`.

## Suggested first contributions (so each member has real history)

Everything here was drafted as a starting point. Each owner should **read, correct and commit their own part** under their own account, through a branch and reviewed PR.

| Member | Suggested tasks (YouTrack) | Files |
|---|---|---|
| Asylkhan Kozhanov | Review and refine prototype; screen flows; UX notes | `prototype/`, `docs/08-ux-prototype.md` |
| Aldiyar Bazarbayev | Baseline pipeline, API contract, architecture decisions | `src/vision/`, `docs/07-architecture.md`, `docs/adr/` |
| Alikhan Sekenov | Requirements, test plan, tests, risks, project board | `docs/06-requirements.md`, `docs/09-verification-plan.md`, `tests/`, `docs/10-...` |
| All | Literature review sources (each reads and annotates a share), interviews | `docs/03-...`, `docs/02-...`, `docs/evidence/` |
