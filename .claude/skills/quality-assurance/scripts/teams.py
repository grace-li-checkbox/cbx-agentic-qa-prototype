import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from urllib.parse import urlparse

MARKS = {"passed": ("Y", "Good"), "failed": ("N", "Attention"), "skipped": ("–", "Warning")}


def text(value, **options):
    return {"type": "TextBlock", "text": value, "wrap": True, **options}


def load_cases(summary):
    cases = []
    for suite in summary.get("suites", []):
        for case in suite.get("cases", []):
            path = os.path.join(case.get("dir", ""), "run.json")
            run = {}
            if os.path.exists(path):
                with open(path) as handle:
                    run = json.load(handle)
            cases.append((suite, case, run))
    return cases


def step_rows(run, step_link):
    rows = []
    for number, step in enumerate(run.get("steps", []), start=1):
        mark, color = MARKS.get(step.get("status"), MARKS["skipped"])
        detail = [
            text(f"S{number} {step.get('title', '')}", weight="Bolder"),
            text(step.get("summary", ""), spacing="None"),
        ]
        note = step.get("error") if step.get("status") == "failed" and step.get("error") else step.get("evidence")
        if note:
            detail.append(text(note, isSubtle=True))
        if step_link and step.get("offsetSec") is not None:
            detail.append(text(f"[Recording]({step_link}#s{number})"))
        rows.append({
            "type": "ColumnSet",
            "separator": True,
            "columns": [
                {"type": "Column", "width": "auto", "items": [text(mark, color=color, weight="Bolder")]},
                {"type": "Column", "width": "stretch", "items": detail},
            ],
        })
    return rows


def build_card(summary, title, artifact, publish_error, mentions):
    cases = load_cases(summary)
    steps = [step for _, _, run in cases for step in run.get("steps", [])]
    passed = sum(step.get("status") == "passed" for step in steps)
    blocked = summary.get("result") == "BLOCKED"
    if blocked:
        heading = text(f"{title}: BLOCKED", size="Large", weight="Bolder", color="Warning")
    else:
        color = "Good" if summary.get("result") == "PASS" else "Attention"
        heading = text(f"{title}: {passed}/{len(steps)} passed", size="Large", weight="Bolder", color=color)
    host = urlparse(summary.get("baseUrl", "")).hostname or ""
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    body = [heading, text(f"{day} · {host}", isSubtle=True, spacing="None")]
    entities = []
    if mentions:
        tags = []
        for name, email in mentions:
            tag = f"<at>{name}</at>"
            tags.append(tag)
            entities.append({"type": "mention", "text": tag, "mentioned": {"id": email, "name": name}})
        body.append(text("cc " + " ".join(tags)))
    if blocked:
        body.append(text(summary.get("blockedReason") or "Nothing could run."))
    for suite in summary.get("suites", []):
        setup = suite.get("setup", {})
        if setup.get("status") == "failed":
            body.append(text(f"Setup of {suite.get('name')} failed: {setup.get('error', '')}", color="Attention"))
    for index, (_, case, run) in enumerate(cases):
        if len(cases) > 1:
            body.append(text(case.get("title") or case.get("name", ""), weight="Bolder", separator=True))
        failure = run.get("failure")
        if failure:
            body.append(text(f"{failure.get('what', '')} {failure.get('why', '')}".strip(), color="Attention"))
        body.extend(step_rows(run, artifact if index == 0 else None))
    if publish_error:
        body.append(text(f"The recording page was not updated: {publish_error}", color="Warning"))
    actions = []
    if artifact:
        actions.append({"type": "Action.OpenUrl", "title": "All recordings", "url": artifact})
    matter = next((run.get("matterUrl") for _, _, run in cases if run.get("matterUrl")), None)
    if matter:
        actions.append({"type": "Action.OpenUrl", "title": "Open matter", "url": matter})
    card = {
        "type": "AdaptiveCard",
        "version": "1.4",
        "msteams": {"width": "Full", "entities": entities},
        "body": body,
        "actions": actions,
    }
    return {"type": "message", "attachments": [{"contentType": "application/vnd.microsoft.card.adaptive", "content": card}]}


def parse_mention(value):
    name, _, email = value.partition("=")
    if not name or not email:
        raise argparse.ArgumentTypeError("use Name=email")
    return name.strip(), email.strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("summary")
    parser.add_argument("--title", default="QA")
    parser.add_argument("--artifact")
    parser.add_argument("--publish-error")
    parser.add_argument("--mention", type=parse_mention, action="append", default=[])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    with open(args.summary) as handle:
        summary = json.load(handle)
    message = build_card(summary, args.title, args.artifact, args.publish_error, args.mention)
    if args.dry_run:
        print(json.dumps(message, indent=1, ensure_ascii=False))
        return
    webhook = os.environ.get("ROUTINE_QA_TEAMS_WEBHOOK")
    if not webhook:
        sys.exit("ROUTINE_QA_TEAMS_WEBHOOK is not set")
    request = urllib.request.Request(
        webhook,
        data=json.dumps(message).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            print(response.status)
    except urllib.error.HTTPError as error:
        sys.exit(f"Teams post failed: HTTP {error.code}")


if __name__ == "__main__":
    main()
