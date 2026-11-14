# Agentic QA

End-to-end QA that a Claude agent runs in a real browser with [Playwright CLI](https://www.npmjs.com/package/@playwright/cli). The agent finds its way by labels, the way a new user would, so tests keep working when the UI moves. Each test case is recorded on video.

Everything lives in one Claude Code skill: [`.claude/skills/quality-assurance/`](.claude/skills/quality-assurance/SKILL.md).

| Folder | What it holds |
|---|---|
| `use-cases/<slice>/` | What the product can do. Drafting reads it to write test cases |
| `test-cases/<suite>/` | `SETUP.md` (cleanup, then setup) and `NN-<case>.md` files, one video each |
| `drafting/` | How to draft test cases from a ticket |
| `scripts/` | Sign-in, video marks, waiting, and the Teams card |

## Run locally

```sh
git clone https://github.com/m4ch374/cbx-agentic-qa-prototype.git
./cbx-agentic-qa-prototype/install.sh
export ROUTINE_QA_EMAIL=<test user on your stack>
export ROUTINE_QA_PASSWORD=<its password>
```

Then, in Claude Code inside your app checkout:

- `/quality-assurance run` runs every suite.
- `/quality-assurance run matter-tools/01-create-edit-find-matter` runs one case.
- `/quality-assurance draft <ticket>` drafts or changes test cases for a ticket.

A local run uses the stack that `cbstack here` reports for your checkout, or `https://localhost:8443`. Results go to `/tmp/qa-run/`.

## Run in the cloud

A Claude Code routine with this repo as its source loads the skill from the clone. Its prompt is [`routine-prompt.md`](routine-prompt.md). The routine's environment sets `ROUTINE_QA_BASE_URL`, `ROUTINE_QA_EMAIL`, `ROUTINE_QA_PASSWORD` and `ROUTINE_QA_TEAMS_WEBHOOK`.
