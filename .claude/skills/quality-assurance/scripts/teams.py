import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from urllib.parse import urlparse

STEP_MARKS = {"passed": ("✓", "Good"), "failed": ("✕", "Attention"), "skipped": ("–", "Default")}
CASE_PILLS = {
    "passed": ("✓ Passed", "good", "Good"),
    "failed": ("✕ Failed", "attention", "Attention"),
    "skipped": ("– Not run", "emphasis", "Default"),
}


def text(value, **options):
    return {"type": "TextBlock", "text": value, "wrap": True, **options}


def banner(title, detail, style):
    return {"type": "Container", "style": style, "spacing": "Medium", "items": [text(title, weight="Bolder"), text(detail, spacing="None")]}


def plural(count, word):
    return f"{count} {word}" if count == 1 else f"{count} {word}s"


def clock(seconds):
    whole = int(round(seconds))
    return f"{whole // 60}:{whole % 60:02d}"


def duration(seconds):
    whole = int(round(seconds))
    return f"{whole // 60} min {whole % 60} s" if whole >= 60 else f"{whole} s"


def load_cases(summary):
    cases = []
    for suite in summary.get("suites", []):
        for case in suite.get("cases", []):
            path = os.path.join(case["dir"], "run.json") if case.get("dir") else ""
            run = {}
            if path and os.path.exists(path):
                with open(path) as handle:
                    run = json.load(handle)
            cases.append((suite, case, run))
    return cases


def case_number(case):
    number = case.get("name", "").split("-", 1)[0]
    return number if number.isdigit() else ""


def not_run_reason(suite, case):
    if suite.get("setup", {}).get("status") == "failed":
        return "Not run: setup failed."
    for earlier in suite.get("cases", []):
        if earlier is case:
            break
        if earlier.get("status") == "failed":
            return f"Not run: {case_number(earlier) or earlier.get('name')} failed first."
    return "Not run."


def verdict(summary, cases):
    if summary.get("result") == "BLOCKED":
        return "Blocked, nothing ran", "Warning"
    statuses = [case.get("status") for _, case, _ in cases]
    total, passed, failed = len(statuses), statuses.count("passed"), statuses.count("failed")
    not_run = total - passed - failed
    if summary.get("result") == "PASS":
        return f"{passed} of {plural(total, 'case')} passed", "Good"
    if failed == 0:
        setup_failed = any(suite.get("setup", {}).get("status") == "failed" for suite in summary.get("suites", []))
        return ("Setup failed, " if setup_failed else "") + f"{plural(not_run, 'case')} not run", "Attention"
    if not_run == 0:
        return f"{failed} of {plural(total, 'case')} failed", "Attention"
    return f"{plural(failed, 'case')} failed, {not_run} not run", "Attention"


def step_row(number, step, link):
    status = step.get("status") if step.get("status") in STEP_MARKS else "skipped"
    mark, mark_color = STEP_MARKS[status]
    tone = {"color": "Attention"} if status == "failed" else {"isSubtle": True}
    detail = [text(f"S{number} {step.get('title', '')}", weight="Bolder", **({"color": "Attention"} if status == "failed" else {"isSubtle": status == "skipped"}))]
    summary = step.get("summary") or ("Not run." if status == "skipped" else "")
    if summary:
        detail.append(text(summary, spacing="None", **tone))
    if status == "failed" and step.get("error"):
        detail.append(text(step["error"], fontType="Monospace", size="Small", spacing="Small", color="Attention"))
    if status != "skipped" and step.get("evidence"):
        shown = ("Page showed: " if status == "failed" else "") + step["evidence"]
        detail.append(text(shown, fontType="Monospace", size="Small", spacing="Small", maxLines=3, **tone))
    columns = [
        {"type": "Column", "width": "auto", "items": [text(mark, weight="Bolder", color=mark_color)]},
        {"type": "Column", "width": "stretch", "items": detail},
    ]
    if link and status != "skipped" and step.get("offsetSec") is not None:
        columns.append({"type": "Column", "width": "auto", "items": [text(f"[Watch {clock(step['offsetSec'])}]({link}#s{number})", size="Small")]})
    row = {"type": "ColumnSet", "spacing": "Small", "columns": columns}
    if status == "failed":
        row["style"] = "attention"
    return row


def case_block(index, suite, case, run, link):
    status = case.get("status") if case.get("status") in CASE_PILLS else "skipped"
    label, style, color = CASE_PILLS[status]
    steps = run.get("steps", []) if status != "skipped" else []
    title = " ".join(part for part in (case_number(case), case.get("title") or case.get("name", "")) if part)
    if status == "skipped":
        detail = not_run_reason(suite, case)
    else:
        failed_at = next((number for number, step in enumerate(steps, start=1) if step.get("status") == "failed"), None)
        parts = [f"Failed at S{failed_at}"] if failed_at else []
        if steps:
            passed = sum(step.get("status") == "passed" for step in steps)
            parts.append(f"{passed} of {plural(len(steps), 'step')} passed")
        if run.get("matterUrl"):
            parts.append(f"[Open matter]({run['matterUrl']})")
        detail = " · ".join(parts)
    heading = [text(title, weight="Bolder")]
    if detail:
        heading.append(text(detail, size="Small", isSubtle=True, spacing="None"))
    columns = [
        {"type": "Column", "width": "auto", "style": style, "items": [text(label, size="Small", weight="Bolder", color=color)]},
        {"type": "Column", "width": "stretch", "items": heading},
    ]
    key = f"case{index}"
    expanded = status == "failed"
    if steps:
        toggle = []
        if run.get("durationSec"):
            toggle.append(text(duration(run["durationSec"]), size="Small", isSubtle=True, horizontalAlignment="Right"))
        toggle.append(text(f"Show {plural(len(steps), 'step')}", id=f"{key}-show", isVisible=not expanded, size="Small", color="Accent", horizontalAlignment="Right", spacing="None"))
        toggle.append(text("Hide steps", id=f"{key}-hide", isVisible=expanded, size="Small", color="Accent", horizontalAlignment="Right", spacing="None"))
        columns.append({
            "type": "Column",
            "width": "auto",
            "items": toggle,
            "selectAction": {"type": "Action.ToggleVisibility", "targetElements": [f"{key}-steps", f"{key}-show", f"{key}-hide"]},
        })
    items = [{"type": "ColumnSet", "columns": columns}]
    if status == "failed" and not any(step.get("status") == "failed" for step in steps):
        failure = run.get("failure") or {}
        reason = " ".join(part for part in (failure.get("what"), failure.get("why")) if part)
        items.append(text(reason or "No results were saved.", size="Small", color="Attention"))
    if steps:
        rows = [step_row(number, step, link) for number, step in enumerate(steps, start=1)]
        items.append({"type": "Container", "id": f"{key}-steps", "isVisible": expanded, "items": rows})
    return {"type": "Container", "separator": True, "spacing": "Medium", "items": items}


def build_card(summary, title, artifact, publish_error, mentions):
    cases = load_cases(summary)
    heading, color = verdict(summary, cases)
    host = urlparse(summary.get("baseUrl", "")).hostname or ""
    now = datetime.now(timezone.utc)
    body = [
        text(" · ".join(part for part in (title, host, f"{now.day} {now:%b %Y}") if part), size="Small", isSubtle=True),
        text(heading, size="Large", weight="Bolder", color=color, spacing="None"),
    ]
    entities = []
    if mentions:
        tags = []
        for name, email in mentions:
            tag = f"<at>{name}</at>"
            tags.append(tag)
            entities.append({"type": "mention", "text": tag, "mentioned": {"id": email, "name": name}})
        body.append(text("cc " + " ".join(tags), spacing="Small"))
    if summary.get("result") == "BLOCKED":
        body.append(banner("Nothing could run", summary.get("blockedReason") or "No reason was given.", "warning"))
    for suite in summary.get("suites", []):
        setup = suite.get("setup", {})
        if setup.get("status") == "failed":
            body.append(banner(f"Setup of {suite.get('name')} failed", setup.get("error") or "No reason was given.", "attention"))
    for index, (suite, case, run) in enumerate(cases):
        body.append(case_block(index, suite, case, run, artifact if index == 0 else None))
    if publish_error:
        body.append(banner("The recording page was not updated", publish_error, "warning"))
    ran = any(case.get("status") in ("passed", "failed") for _, case, _ in cases)
    actions = [{"type": "Action.OpenUrl", "title": "Watch the recording", "url": artifact}] if artifact and ran else []
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
