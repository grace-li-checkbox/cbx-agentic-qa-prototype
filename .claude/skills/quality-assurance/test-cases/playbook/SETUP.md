# Playbook: setup

The cases upload the Verdantis NDA playbook to the AI Agent `Ask Kes Anything` and check what it extracted, then review the Calyx draft NDA in its chat against the existing `NDA Playbook`. The readers are software engineers, not lawyers: report only what the app got wrong.

## Finding lines

Both cases write their judge findings as one line each, nothing more: `**P0|P1** · **Missing|Inaccurate|Hallucination** · <item> · <part>`. No reason, no quotes. One line per item, part and category; take the highest severity that applies.

- A P0 finding fails the step it belongs to. Its `error` lists the P0 lines.
- A P1 finding is a warning: the step still passes, its `summary` starts with `<n> warnings:` and its `evidence` lists the P1 lines (up to 300 characters, then `+<k> more`). Write every finding line, P0 first, to `<case dir>/findings.md` too and copy it with the case.

Document generation note: until document_generation returns the S3 file id (work in progress), generated documents cannot be reliably attached to the matter or downloaded on dev. Every finding about document generation or the generated documents is P1, never P0.

## Reading network responses

Two checks need what the app sent back, which the page does not show (extracted positions, tool calls). Read them from the browser's own traffic: `playwright-cli requests`, then `playwright-cli response-body <index>`. This only reads requests the page already made; never send one yourself.

## Cleanup

Remove playbooks earlier runs of this suite made.

1. In the AI Agent section, open the AI Agent named `Ask Kes Anything`, then its `Playbooks` page.
2. For each playbook whose title starts with `QA ingestion`, open its actions menu, choose `Delete`, and confirm `Delete` in the `Delete playbook?` dialog. Never delete any other playbook.
3. Take a snapshot. Cleanup is done when no title starting with `QA ingestion` is left.

## Setup

Check each prerequisite by finding its name in the UI. When one is missing, SETUP fails with `not found: <name>`.

1. An AI Agent named `Ask Kes Anything`, in the AI Agent section.
2. A playbook titled exactly `NDA Playbook` on its `Playbooks` page.
3. The files `verdantis-nda-playbook.md`, `verdantis-expected-positions.json`, `calyx-draft-nda.docx`, `calyx-draft-nda.pdf` and `calyx-answer-key.json` in `${CLAUDE_SKILL_DIR}/test-cases/playbook/files/`: check them with `ls`.
