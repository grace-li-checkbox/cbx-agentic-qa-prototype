# Matter tools: setup

The cases in this suite talk to an AI Agent that makes and changes matters. The agent's routing table, the board and the users are too large to build through the UI on each run, so this SETUP only checks that they exist and fails when one is missing.

## Cleanup

Remove the matters that earlier runs of this suite made. Delete only these rows, never other matters on the board.

1. From the Matters menu, open the board named `AI-Aliens`.
2. Use the board's search to find `Northwind Freight`.
3. Select every row whose subject starts with `{TEST} Northwind Freight`, and no other row.
4. Delete the selected rows with the board's bulk delete, and confirm it.
5. Search again. Cleanup is done when no row whose subject starts with `{TEST} Northwind Freight` is left. If there were no such rows, cleanup is done.

## Setup

Check each prerequisite by finding its name in the UI. If one is missing, SETUP fails with `not found: <name>`.

1. An AI Agent named `Ask Kes Anything`, in the AI Agent section.
2. A board named `AI-Aliens`, in the Matters menu.
3. A person named `Kesnavi Parammanandhan`, who is a member of that board: the board's assignee filter or people list shows the name.
