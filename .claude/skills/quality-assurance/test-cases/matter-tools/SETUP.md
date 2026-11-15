# Matter tools: setup

The cases in this suite talk to an AI Agent that makes, changes and finds matters and starts workflows. The agent's routing table, the board, the users and the workflow are too large to build through the UI on each run, so this SETUP only checks that they exist and fails when one is missing.

## Cleanup

Remove the matters that earlier runs of this suite made. Delete only these rows, never other matters on the board.

1. From the Matters menu, open the board named `AI-Aliens`.
2. Do steps 3 to 5 once for `Northwind Freight` and once for `Fabrikam`.
3. Use the board's search to find the name.
4. Select every row whose subject starts with `{TEST}` and contains the name, and no other row. Delete the selected rows with the board's bulk delete, and confirm it.
5. Search again. That name is done when no such row is left. If there were no such rows, it is done.

## Setup

Check each prerequisite by finding its name in the UI. If one is missing, SETUP fails with `not found: <name>`.

1. An AI Agent named `Ask Kes Anything`, in the AI Agent section.
2. A board named `AI-Aliens`, in the Matters menu.
3. People named `Kesnavi Parammanandhan` and `Grace Li`, who are members of that board: the board's assignee filter or people list shows each name.
4. A workflow named `[KITBAG] Self Service NDA` in the team `Legal Team`, in the Workflows menu.
5. The file `${CLAUDE_SKILL_DIR}/test-cases/matter-tools/files/Fabrikam_DPA.docx`: check it with `ls`.
