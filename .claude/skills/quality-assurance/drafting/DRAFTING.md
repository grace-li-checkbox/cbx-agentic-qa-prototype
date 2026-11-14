# Drafting test cases from a ticket

Use this while a person works on a ticket. You draft or change test cases and use cases in this skill folder. The person opens a PR on the QA repo; a draft becomes a fixed test case only when that PR merges.

`${CLAUDE_SKILL_DIR}` is a link into the person's clone of the QA repo, so edits made here land in that clone.

## 1. Read the context

Read everything you can find about the change. Ask the person only for what you cannot find.

- The ticket: use the Atlassian connector for a Jira key, or read what the person pasted.
- The code: the branch diff against its base, and the files it touches.
- The PRD or spec the ticket links to.
- `${CLAUDE_SKILL_DIR}/use-cases/`: what the product can already do, by product slice.
- `${CLAUDE_SKILL_DIR}/test-cases/`: the suites and cases that exist.

## 2. Decide

Pick one and tell the person which and why:

| Ticket | Result |
|---|---|
| Changes something a user sees or does, and a case covers it | Change that case |
| A bug with no case that would catch it | Add a case that fails before the fix and passes after it |
| A new feature or a greenfield epic | Add a case, in a new suite if no suite fits |
| No change a user can see (refactor, infra, tooling) | No QA needed: say why |

## 3. Write

- **Use case.** When the ticket adds or changes what the product can do, update `use-cases/<product-slice>/<area>.md`: plain sentences about what a user can do, and a link to the PRD.
- **Case.** One file is one video: one user journey from start to end. Name it `NN-<what-it-does>.md` in its suite, numbered after the last case. Write it the way `test-cases/matter-tools/01-create-edit-find-matter.md` is written:
  - a title and one or two sentences on the journey;
  - the exact messages or values to type;
  - steps `S1`, `S2`, … that each say what the user does, then `Pass:` and what the page must show;
  - names, not IDs or URLs, for the things it opens (an AI Agent, a board, a person);
  - a `needs: <case>` line under the title only when it uses what an earlier case made.
- **SETUP.** A new suite needs `SETUP.md`: first a cleanup that deletes only what earlier runs of this suite made, then the setup that makes or checks each prerequisite by name. A case never creates its own prerequisites.

## 4. Check the draft

Run it on the person's local stack: `run <suite>/<case>`. Fix the draft until it passes on the fixed code. For a bug, it should also fail on the code before the fix, when that is easy to check.

## 5. Hand over

Tell the person which files you changed in the QA repo clone, and that a PR on the QA repo makes the draft a fixed test case.
