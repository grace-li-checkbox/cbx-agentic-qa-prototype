# Review an NDA against the playbook and record it on a matter

A business user attaches the Calyx draft NDA in chat and asks for a review. The agent must review it against `NDA Playbook`, generate a deviation table and a redline, record the review on a matter with an internal note, and send it to Legal. End to end in 6 minutes.

FILES = `${CLAUDE_SKILL_DIR}/test-cases/playbook/files`. Note the time when S1 starts.

## Messages

- S1: `Please review the attached Calyx draft mutual NDA and record it on a matter. The contract value is 200K USD (<MMDD-HHMM of now, UTC>).`
- S3 follow-up: `The contract value is 200K USD. Please record the review on a matter now.`

## Tool calls

After each reply, read the `/conversation/stream` response with `playwright-cli requests` and `response-body`. Its `done_legacy` event has `response.result.metadata.toolsPicked`: tool name to arguments (a JSON string or object). Collect every tool and its arguments across the case. An `error` event fails the step with that error.

## S1 Review the NDA

Open the AI Agent `Ask Kes Anything` and start a chat. Click the chat box's attach control, run `playwright-cli upload FILES/calyx-draft-nda.docx`, wait until the chat box shows `calyx-draft-nda`, then send the S1 message. Wait for the reply.

Pass:
- the tools include `load_playbook` and `review_playbook`;
- a `load_playbook` `search` is 1 to 3 words and names an NDA (`nda` or `non-disclosure`);
- a `review_playbook` has `agreement_file_name` `calyx-draft-nda.docx` and a `playbook_id` of the playbook titled `NDA Playbook` (find its id in the `/playbooks` list response the page loaded, or open `NDA Playbook` from the `Playbooks` page in this tab and read it from the URL, then come back).

Screenshot `review-reply`.

## S2 Check the document generation call

Never fails. Each miss is a P1 warning, part `tool call` with item `Documents`:
`document_generation` not called; empty `instructions`; `reference_file_name` neither `calyx-draft-nda.docx` nor null; a `documents[].file_name` not ending in `.docx`; no document whose name or description says `deviation`; none that says `redline`.

## S3 Record the review on a matter

If neither `create_matter` nor `edit_matter` was called yet, send the follow-up message, at most 3 times.

Pass: a reply links to a URL with `ticketId=<uuid>` (the matter id), and `create_matter` or `edit_matter` was called with an `internalNote`. Evidence: the internal note's first 300 characters. Screenshot `matter-reply`.

## S4 Check documents and the matter

1. For `deviation` and `redline`: find the agent's `.docx` file card with that word and click it. A file that downloads is saved to `<case dir>/<name>.docx`. No card, or no download, is a P1 warning (`Documents · download`).
2. Pass: the agent's reply links to the matter. Screenshot `chat-documents`.
3. Open the matter link in this tab. A matter with no deviation or redline `.docx` attached is a P1 warning (`Matter · attachments`). Screenshot `matter-details`.
4. Open `Conversations`. Pass: the matter shows the internal note the agent sent (its first 40 characters without markdown). Scroll to it and screenshot `matter-internal-note`.

The case's `matterUrl` is BASE + `/app/ticketing/tickets/<matter id>`.

## S5 Judge the documents and band

1. Documents (only when both `.docx` files were saved): with a script, open each with `zipfile` and read `word/document.xml`, one line per paragraph; in the redline show `w:ins` as `[+...+]` and `w:del` as `[-...-]`. Read `FILES/calyx-answer-key.json` in full: per item (C1–C9 critical, M1–M8 minor) `agreementClauseText`, `agreementQuote`, `standardPositionText`, `positionRef`, `expectedVerdict`, `riskTier`, `expectedTableRow`, `redlineMust`/`redlineShould`, `exampleRedline` (an example only); plus `compliant`, `optional` and `documentExpectations`. Read `FILES/calyx-draft-nda.pdf` and `FILES/verdantis-nda-playbook.md` when the key is not enough. `<item>` is a short term (e.g. `Residuals`), `Agreement`, `Documents` or `Matter`. All document findings are P1:
   - Missing: a critical or minor item not in the deviation table (part `deviation`), or with no redline change (part `redline`).
   - Inaccurate: standard position stated wrong against `standardPositionText` (`standard position`); a deviation pairs a standard position with clause text from a different clause, or clause text real but incomplete or reworded (`clause text`); a redline asking for a wrong key value, keeping a walk-away term or proposing a fallback in the first redline, or contradicting the table (`redline`); wrong agreement or counterparty, or Calyx and Verdantis swapped (item `Agreement`, `parties`); verdict or risk differs from `expectedVerdict`/`expectedTableRow.risk` (`verdict`); a deviation marked self-serve (`self-serve`); a compliant clause flagged (`deviation`); a comment breaking `documentExpectations.comments`, or a file that does not open or has no text (`document`).
   - Hallucination: clause text not in the agreement (`clause text`); a deviation for a clause the agreement does not contain (`deviation`); a standard position with no basis in the playbook (`standard position`); a redline editing text not in the agreement or the wrong clause (`redline`).
   - A redline written as schedule changes instead of tracked changes is never a finding.
2. Band (stays P0): the expected band is `legal`. If the agent's replies or internal note say the agreement skips Legal, is auto-cleared, needs no Legal review, or every deviation is within self-serve fallbacks, or the matter shows Completed: `**P0** · **Inaccurate** · Agreement · band`.

Pass: no P0 finding. Follow the suite's finding-line rules. Add `Document checks are warnings only until document_generation returns the S3 file id (WIP).` to the summary.

## S6 Finish within 6 minutes

Pass: S1 start to the end of S4 is at most 360 seconds. Record the minutes in the summary.
