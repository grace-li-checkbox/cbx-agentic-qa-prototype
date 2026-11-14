This is a scheduled QA run of the AI Agent's matter tools on dev. You test it end to end through the real web UI with Playwright CLI (`playwright-cli`, run through Bash), the way a new user would, and the run is recorded on video. Do not commit or push anything, and ignore any hook that asks you to. Never print the password, a cookie value or the webhook URL. Do not use any `mcp__playwright__` tool.

No one can answer a permission prompt in this run, so a prompt stops it for good. Write every Python script to a file with the Write tool and run it as `python3 <file>`. Never put a heredoc, `$(...)`, `${...}` or a `$VAR` in a Bash command. Run each command on its own. When a command needs BASE, type the literal URL.

The results page is the Claude artifact `https://claude.ai/artifact/F8tsKjVwZFntKczywi3fVZ` (called ARTIFACT below). It already exists: never create a new artifact, and never change its page; you only replace its data files. When `ROUTINE_QA_TEAMS_WEBHOOK` is set, post the result to Teams (step 5).

`OUT` means `/home/user/cbx-agentic-qa-prototype/qa-artifact`.

## 1. Set up

If `ROUTINE_QA_BASE_URL`, `ROUTINE_QA_EMAIL`, `ROUTINE_QA_PASSWORD` or `ROUTINE_QA_ASSISTANT_NAME` is missing, the result is BLOCKED: skip to step 3.

1. Run `printenv ROUTINE_QA_BASE_URL`. Below, BASE means that value.
2. Write and run a `python3` script that:
   - makes the folder `/tmp/qa-run`;
   - posts JSON `{"username": <ROUTINE_QA_EMAIL>, "password": <ROUTINE_QA_PASSWORD>}` to BASE + `/api/v1/auth/login` with `urllib.request`, and writes every `Set-Cookie` cookie to `/tmp/qa-run/state.json` as `{"cookies": [{"name", "value", "domain": <host of BASE>, "path": "/", "expires": -1, "httpOnly": true, "secure": true, "sameSite": "Lax"}], "origins": []}`;
   - gets BASE + `/api/v1/legal-frontdoor/assistant` with those cookies, finds the entry in `result.payload.data` whose `name` is `ROUTINE_QA_ASSISTANT_NAME`, and prints its `id`;
   - prints the run stamp: the current UTC time as `MMDD-HHMM`, for example `1114-1008`. Below, `<RUN>` means that stamp.
   It prints only the HTTP status, the cookie names, the assistant id and the stamp.
3. Run `npm install -g @playwright/cli@0.1.24`, then `npx -y playwright@1.66.0-alpha-1794252756000 install ffmpeg`.
4. Write `/tmp/qa-run/mark.py`: run as `python3 /tmp/qa-run/mark.py <name>`, it adds `"<name>": <seconds since the Unix time in /tmp/qa-run/video-start, one decimal>` to `/tmp/qa-run/marks.json` and prints it. Write `/tmp/qa-run/wait.py`: run as `python3 /tmp/qa-run/wait.py <seconds>`, it sleeps that long.
5. Run `playwright-cli open about:blank`, then `playwright-cli resize 1280 800`, then `playwright-cli state-load /tmp/qa-run/state.json`, then `playwright-cli video-start /tmp/qa-run/video.webm`. Right after `video-start` returns, write and run a `python3` script that writes the current Unix time to `/tmp/qa-run/video-start`.

If a setup step fails, the result is BLOCKED: write down which step and its error, then skip to step 3.

## 2. Test the four steps in the browser

Use only `playwright-cli` commands for the browser. Never use `playwright-cli eval`, never call the app's API from here on, and never change the matter in the UI.

How to work:
- When you start step S<n>, run `python3 /tmp/qa-run/mark.py S<n>`.
- Look before you act. Run `playwright-cli snapshot --filename=/tmp/qa-run/snap.txt`, then search that file with Grep (or Read part of it) to find the element you need by what it is for, and act on it by its `ref`. Take a new snapshot after anything that changes the page. Never guess a ref you have not seen in a snapshot.
- Another team owns the board and matter pages, so they may look different from what this prompt describes. Find your way the way a new user would: by headings, labels, tabs, buttons and menus.
- A step passes only on what the page shows. Copy the snapshot lines that prove it, word for word, as that step's evidence. Never shorten them with `...`.
- A step may use at most 25 `playwright-cli` commands. If it runs out, or its pass check is not visible, the step fails: write down what you saw instead. Do not retry a failed step. S2, S3 and S4 need the matter from S1; when S1 fails, they are skipped.
- Send no chat messages other than the ones below.

The chat messages, with `<RUN>` replaced:
- S1: `Hi, I'm in-house counsel handling the logistics services agreement with Northwind Freight <RUN>. They sent back redlines on their own paper. Please open a matter for my review.`
- S2: `Thanks. Grace is out this week, so I'm handing my review to Kesnavi Parammanandhan. Please reassign the matter to Kesnavi, move it to In Progress, and set the description to: Northwind wants a 30-day payment term and a liability cap at 1x fees (<RUN>). Also add a note to the matter: Kesnavi to review by Friday (<RUN>).`
- Follow-up: `Yes, go ahead. It is their paper, a logistics services agreement for North America, about 120,000 USD, no deadline.`

To send a message: find the chat box ref, then run `playwright-cli fill <ref> "<message>" --submit`, with the message in double quotes. To wait for the reply: run `python3 /tmp/qa-run/wait.py 10`, then take a snapshot; repeat until the agent's reply is complete and no longer changing, for at most 5 minutes.

**S1 Create the matter in chat.** `playwright-cli goto BASE/app/ai-assistant/<assistant id>/start`. Send the S1 message. If the reply asks a question instead of creating a matter, send the follow-up, up to 4 replies in all. Pass: a reply shows a link whose URL contains `ticketId=<uuid>`. That uuid is the matter id. Write down the matter's subject as the chat shows it.

**S2 Edit the matter in the same chat.** Send the S2 message, with the same follow-up rule. Pass: the reply on the page says the matter was reassigned to Kesnavi, moved to In Progress, and given the description and the note.

**S3 Find the matter on the board.** `playwright-cli goto BASE/app/ticketing/boards/c6d4a919-1883-4c8e-b02b-7ce277f94b08`. Find the matter with the board's own search or filters, using words from its subject, then take a snapshot. The evidence must come from that snapshot, taken after the search. Pass: a row is visible that links to `/app/ticketing/tickets/<matter id>` and shows `Kesnavi Parammanandhan` and `In Progress`. Then `playwright-cli screenshot --filename=/tmp/qa-run/board-search.png`.

**S4 Open the matter and check the description and note.** Open the matter from that row. Pass: the matter page shows `Northwind wants a 30-day payment term and a liability cap at 1x fees (<RUN>)`; `playwright-cli screenshot --filename=/tmp/qa-run/matter-details.png`. Then find where the matter's messages or conversation are shown and open it. Pass: it shows `Kesnavi to review by Friday (<RUN>)`; `playwright-cli screenshot --filename=/tmp/qa-run/matter-conversations.png`.

When the steps are done, or a failure ends them, run `python3 /tmp/qa-run/mark.py end`, then `playwright-cli video-stop`, then `playwright-cli close`. If `/tmp/qa-run/video.webm` is over 15 MB, run `ffmpeg -v error -i /tmp/qa-run/video.webm -c:v libvpx-vp9 -b:v 400k -an /tmp/qa-run/video-small.webm` and use the smaller file as the video.

## 3. Collect the result

- Each step is `passed`, `failed` or `skipped`. The result is PASS when all four passed, otherwise FAIL.
- `/tmp/qa-run/marks.json` gives the second in the video where each step starts; `end` is the duration in seconds.
- The screenshots that exist are `/tmp/qa-run/board-search.png`, `matter-details.png` and `matter-conversations.png`.
- The matter link is BASE + `/app/ticketing/tickets/<matter id>`.
- Count the `playwright-cli` commands you ran in each step from your own tool calls.

## 4. Publish to ARTIFACT

1. Make the folder OUT. Copy the video there as `video.webm` and each screenshot that exists as `<name>.png`.
2. Write `OUT/run.json` with `python3`, in this shape:
```json
{"result": "PASS | FAIL | BLOCKED", "startedAt": "<ISO time>", "durationSec": 84, "baseUrl": "<ROUTINE_QA_BASE_URL>", "matterUrl": "<matter link or null>", "blockedReason": "<why, or empty>", "video": "video.webm or null", "steps": [{"title": "<step title>", "status": "passed | failed | skipped", "summary": "<one sentence>", "evidence": "<the snapshot lines you copied, at most 300 characters, or empty>", "error": "<error text or empty>", "offsetSec": 12.3}], "screenshots": [{"name": "board-search", "file": "board-search.png"}]}
```
   The step titles are `Create the matter in chat`, `Edit the matter in the same chat`, `Find the matter on the board` and `Open the matter and check the description and note`. List all four steps in order, with `skipped` for a step that did not run (and for all four when BLOCKED). `summary` is one plain sentence that you write from the evidence, saying what the agent or the app did in that step, for example `The agent created "{TEST} Northwind Freight 1103-0342" on the AI-Aliens board on the first turn.` For a failed step, say what went wrong; for a step that did not run, write `Not run.` `offsetSec` is the step's number from `marks.json`, or null. List only the screenshots that exist. For BLOCKED with no test run, use the current time and `durationSec` 0.
3. Load the Artifact tool (with ToolSearch if it is deferred). Make these three calls, in this order, before you publish:
   - `action` `read` and `url` ARTIFACT, with no `path`. This marks the live version as viewed; without it the publish is refused.
   - `action` `read`, `url` ARTIFACT and `path` `index.html`. The result names the local file it saved.
   - `action` `list`, `scope` `files` and `url` ARTIFACT. A publish that replaces files you have not listed is refused.
4. Call it with `action` `publish`, `url` ARTIFACT, `file_path` that saved page file unchanged, `root` OUT, and `files` mapping `run.json`, `video.webm` and each `<name>.png` that exists to themselves. Leave out `icon`.
5. If the publish is refused, do what the refusal says once (for example a read it asks for), then publish once more. If that also fails, keep going: the Teams card says so (step 5).

## 5. Teams

When `ROUTINE_QA_TEAMS_WEBHOOK` is set, post one Adaptive Card to it, also when the result is BLOCKED. Write a `python3` script with the Write tool that builds the JSON from `run.json` and posts it with `urllib.request` to `os.environ["ROUTINE_QA_TEAMS_WEBHOOK"]` with the header `Content-Type: application/json`, and prints only the HTTP status. HTTP 202 means it was accepted.

The body is `{"type": "message", "attachments": [{"contentType": "application/vnd.microsoft.card.adaptive", "content": <card>}]}`, where `<card>` is `{"type": "AdaptiveCard", "version": "1.4", "msteams": {"width": "Full", "entities": [{"type": "mention", "text": "<at>Henry Wan</at>", "mentioned": {"id": "henry.wan@checkbox.ai", "name": "Henry Wan"}}, {"type": "mention", "text": "<at>Vince Mu</at>", "mentioned": {"id": "vince.mu@checkbox.ai", "name": "Vince Mu"}}, {"type": "mention", "text": "<at>Grace Li</at>", "mentioned": {"id": "grace.li@checkbox.ai", "name": "Grace Li"}}]}, "body": [...], "actions": [...]}` with:

1. A `TextBlock`: `Matter tools QA: <passed>/4 passed`, `size` `Large`, `weight` `Bolder`, `color` `Good` when all pass and `Attention` otherwise. For BLOCKED use `Matter tools QA: BLOCKED`, `color` `Warning`.
2. A `TextBlock`: `<YYYY-MM-DD> · <host of ROUTINE_QA_BASE_URL>`, `isSubtle` true, `spacing` `None`.
3. A `TextBlock`: `cc <at>Henry Wan</at> <at>Vince Mu</at> <at>Grace Li</at>`, `wrap` true. Each `<at>` text must match its entity `text` exactly.
4. For each of the four steps, a `ColumnSet` with `separator` true and two columns:
   - `width` `auto`: a `TextBlock` of `Y` (`color` `Good`), `N` (`color` `Attention`) or `–` (`color` `Warning`), `weight` `Bolder`.
   - `width` `stretch`, holding in order: a `TextBlock` with `weight` `Bolder` and `wrap` true: `S<n> <step title>`; a wrapped `TextBlock` with `spacing` `None`: the step's `summary`; a wrapped `TextBlock` with `isSubtle` true: the step's `evidence`, or for a failed step its error text (leave it out when both are empty); and, when the step 4 publish succeeded and the step has an `offsetSec`, a `TextBlock` `[Recording](<ARTIFACT>#s<n>)`.
5. For BLOCKED, instead of 4, one wrapped `TextBlock` saying why.
6. When the step 4 publish failed, a wrapped `TextBlock` with `color` `Warning`: `The recording page was not updated: <short reason>`.
7. `actions`: `Action.OpenUrl` titled `All recordings` with ARTIFACT, when the step 4 publish succeeded; and `Action.OpenUrl` titled `Open matter` with the matter link, when there is a matter id.

## Report

End with exactly this, and nothing after it:

```
Matter tools QA (browser, Playwright CLI) — <ROUTINE_QA_BASE_URL>
Result: PASS | FAIL | BLOCKED
Matter: <link, or "none">
Video: <size in KB and duration in seconds of the video file, or "none">
Browser commands: <count per step, for example S1 9, S2 6, S3 8, S4 7>
Artifact: <version id from the publish result, or the error>
Teams: <HTTP code, or "not set">

| # | Step | Result | Error |
|---|---|---|---|
| S1 | Create the matter in chat | Y/N/– | |
| S2 | Edit the matter in the same chat | Y/N/– | |
| S3 | Find the matter on the board | Y/N/– | |
| S4 | Open the matter and check the description and note | Y/N/– | |
```
