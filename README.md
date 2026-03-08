# Agent Skills  <!-- omit from toc -->

This repository hosts reusable Agent Skills that can be installed with the Skills CLI.

The Skills CLI installs skills into your assistant's local skills directory. In Claude-style environments, this is typically `~/.agents/skills`. Other assistants use the same `SKILL.md` format but may use a different folder, such as `~/.claude/skills` for Claude Code.

For the general format and workflow, see the official Agent Skills documentation: <https://agentskills.io/home> and Skills CLI documentation: <https://skills.sh/docs>.

## Table of Contents  <!-- omit from toc -->

- [Installation](#installation)
- [Skills In This Repo](#skills-in-this-repo)
- [Explore More Skills](#explore-more-skills)
- [Recommended Other Skills](#recommended-other-skills)

## Installation

Install Node.js first to get `npx`:

```bash
brew install node
```

The Skills CLI can be run directly with `npx`, so no separate installation is required.

Install this repo and choose a skill interactively:

```bash
npx skills add https://github.com/baptiste-pasquier/skills
```

Install a specific skill directly:

```bash
npx skills add https://github.com/baptiste-pasquier/skills --skill smart-rebase
```

## Skills In This Repo

| Skill          | Description                                                                                                                                        | Install                                                                           |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| `smart-rebase` | Help the user safely rebase a feature branch onto `main`, `develop`, or another target branch while preserving feature behavior through conflicts. | `npx skills add https://github.com/baptiste-pasquier/skills --skill smart-rebase` |

## Explore More Skills

Browse the wider skill ecosystem on <https://skills.sh/>.

If you want to create new skills, a strong starting point is Anthropic's `skill-creator`: <https://skills.sh/anthropics/skills/skill-creator>.

## Recommended Other Skills

| Skill                     | Description                                                                                                                                                                                                     | Link                                                                                                               |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `make-repo-contribution`  | Follow repository contribution guidance before creating issues, branches, commits, pushes, or pull requests.                                                                                                    | [github/awesome-copilot/make-repo-contribution](https://skills.sh/github/awesome-copilot/make-repo-contribution)   |
| `git-flow-branch-creator` | Intelligent Git Flow branch creator that analyzes git status and diff, then creates an appropriate semantic branch name.                                                                                        | [github/awesome-copilot/git-flow-branch-creator](https://skills.sh/github/awesome-copilot/git-flow-branch-creator) |
| `git-commit`              | Execute git commit with conventional commit message analysis, intelligent staging, and message generation.                                                                                                      | [github/awesome-copilot/git-commit](https://skills.sh/github/awesome-copilot/git-commit)                           |
| `code-reviewer`           | Use this skill to review code. It supports both local changes (staged or working tree) and remote Pull Requests (by ID or URL). It focuses on correctness, maintainability, and adherence to project standards. | [google-gemini/gemini-cli/code-reviewer](https://skills.sh/google-gemini/gemini-cli/code-reviewer)                 |
| `gh-address-comments`     | Help address review or issue comments on the open GitHub PR for the current branch using `gh` CLI.                                                                                                              | [openai/skills/gh-address-comments](https://skills.sh/openai/skills/gh-address-comments)                           |
| `refactor`                | Improve maintainability with surgical refactors that preserve behavior, such as extracting functions, renaming variables, and tightening types.                                                                 | [github/awesome-copilot/refactor](https://skills.sh/github/awesome-copilot/refactor)                               |
| `jupyter-notebook`        | Create, scaffold, or edit Jupyter notebooks for experiments, explorations, or tutorials, using the bundled templates when possible.                                                                             | [openai/skills/jupyter-notebook](https://skills.sh/openai/skills/jupyter-notebook)                                 |
