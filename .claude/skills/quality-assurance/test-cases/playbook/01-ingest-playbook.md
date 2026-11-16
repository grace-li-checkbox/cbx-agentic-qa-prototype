# Upload the NDA playbook and check its extracted positions

A playbook owner pastes the Verdantis NDA playbook into a new playbook. The app must extract the 23 positions in it, word for word, without making any up.

FILES = `${CLAUDE_SKILL_DIR}/test-cases/playbook/files`. TITLE = `QA ingestion <MMDD-HHMM of now, UTC>`.

## S1 Create the playbook

Open the AI Agent `Ask Kes Anything`, then its `Playbooks` page. Click `Create playbook`, fill the title box with TITLE and click `Continue`.

The playbook is too long to type. Run `python3 ${CLAUDE_SKILL_DIR}/scripts/paste.py FILES/verdantis-nda-playbook.md /tmp/qa-run/paste.js`, then `playwright-cli run-code --filename=/tmp/qa-run/paste.js`. It pastes the text into the editor the way a person pasting would. This is the only `run-code` the suite allows.

Pass: the editor shows `Standard Exclusions from Confidential Information`.

## S2 Save and time the ingestion

Note the time, click `Save changes`, then wait with `wait.py 5` and a snapshot until the page leaves the editor or shows an error, for at most 5 minutes.

Pass: the page shows the playbook TITLE, and its URL ends in the new playbook's id. Record the seconds from click to saved in the summary. Over 30 seconds is a P1 warning (`⚠ Ingestion took <s>s (over 30s)`), not a failure.

## S3 Read the extracted positions

Run `playwright-cli requests` and find the latest response for `/playbooks/<id>` (the POST that saved it, or the GET that loaded the page). Save its body with `playwright-cli response-body <index>` and write the `positions` array to `<case dir>/extracted-positions.json`.

Pass: `positions` has at least one entry. Record the count in the summary as `<n>/23 positions`.

## S4 Judge the positions

Inputs: `FILES/verdantis-expected-positions.json` (use `judgeRules.matching` and each position's `acceptable`), `<case dir>/extracted-positions.json`, `FILES/verdantis-nda-playbook.md`. Write each script to a file and run it with `python3`.

1. Script: split every extracted standardPosition and fallback text into sentences, strip markdown (`**`, `<u>`, leading `> `/`• `, decode `&amp;`), collapse whitespace, and look each up in the playbook with the same normalisation. List the sentences not found word for word (ignore label-only fragments like `Duration.`). For each: no counterpart anywhere in the playbook is Hallucination; a paraphrase or altered copy of a real sentence is Inaccurate.
2. Script: list extracted fallbacks whose `selfServe` is true. Every fallback must be `selfServe: false` (playbook Section 1A).
3. Classify each difference from the expected positions. `<item>` is `§<section> <short term>` (e.g. `§6.3 Non-solicitation`); `<part>` is `position`, `standard position`, `fallback <N>` or `walk-away`.
   - **P0 · Missing**: an expected position with no extracted position (part `position`); an expected standard position or fallback entirely missing.
   - **P1 · Missing**: an expected walk-away entirely missing.
   - **P0 · Hallucination**: a standard position or fallback with no basis in the playbook.
   - **P0 · Inaccurate**: a standard position whose key values are wrong (a number, period, duration, deadline, limit, party or required element); a fallback self-serve flag that differs.
   - **P1 · Inaccurate**: standard-position wording differs but key values are right; any fallback wording or key value differs; fallbacks in a different order, rung or count, repeated across rungs, or a walk-away or approval sentence turned into a fallback (report the extracted rung number).
   - Allow every variation in `acceptable`. isRequired and walk-away wording differences are never findings.

Pass: no P0 finding. Follow the suite's finding-line rules.

## S5 Delete the playbook

Open the playbook's `Delete playbook` action and confirm `Delete`.

Pass: back on the `Playbooks` page, TITLE is not listed.
