# Drafting test cases from a ticket

Use this while a person works on a ticket. You draft or change test cases and use cases in this skill folder. The person opens a PR on the QA repo; a draft becomes a fixed test case only when that PR merges.

`${CLAUDE_SKILL_DIR}` is a link into the person's clone of the QA repo, so edits made here land in that clone.

## Use cases and test cases

- A **use case** says what the product can do, never how. Good: "Legal Front Door lets users create AI Agents." Bad: "Users open the dashboard and click Create agent."
- Use cases exist only so you can draft test cases. A run never reads them.
- A **test case** says exactly how: the clicks, the labels, the messages to type. It stands alone and never cites a use case, a PRD or a requirement ID.
- So a UI change touches only test cases. A use case changes only when the product gains or loses a capability.

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
| The UI moved, the capability did not | Change the cases that cover it. Leave use cases alone |
| A bug with no case that would catch it | Add a case that fails before the fix and passes after it |
| A new feature or a greenfield epic | Add use-case lines and a case, in a new suite if no suite fits |
| A feature is removed | Delete its use-case lines and the cases that cover it |
| No change a user can see (refactor, infra, tooling) | No QA needed: say why |

## 3. Find the steps in the UI

Open the live UI on the person's local stack and find the real labels, menus and steps for the journey. Take the how from the UI only, never from a use case or the PRD.

## 4. Write

- **Use case.** Edit `use-cases/<product-slice>/<area>.md` only for a new or removed capability. Write each line as "<product> lets users <do what>", plus a link to the PRD. Never write UI labels, screen or page names, routes, URLs, selectors, configuration names or click order. If you find any of these in a use case you read, rewrite that line as a capability.
- **Case.** One file is one video: one user journey from start to end. Name it `NN-<what-it-does>.md` in its suite, numbered after the last case. Write it the way `test-cases/matter-tools/01-create-edit-find-matter.md` is written:
  - a title and one or two sentences on the journey;
  - the exact messages or values to type;
  - steps `S1`, `S2`, … that each say what the user does, then `Pass:` and what the page must show;
  - names, not IDs or URLs, for the things it opens (an AI Agent, a board, a person);
  - a `needs: <case>` line under the title only when it uses what an earlier case made;
  - no link to, or mention of, a use case, a PRD or a requirement ID.
- **SETUP.** A new suite needs `SETUP.md`: first a cleanup that deletes only what earlier runs of this suite made, then the setup that makes or checks each prerequisite by name. A case never creates its own prerequisites.

## 5. Check the draft

Run it on the person's local stack: `run <suite>/<case>`. Fix the draft until it passes on the fixed code. For a bug, it should also fail on the code before the fix, when that is easy to check.

## 6. Hand over

Tell the person which files you changed in the QA repo clone, and that a PR on the QA repo makes the draft a fixed test case.
