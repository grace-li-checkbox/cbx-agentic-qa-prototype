import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(__file__))

from login import is_local, parse_cookies
from teams import build_card

HERE = os.path.dirname(__file__)
ARTIFACT = "https://claude.ai/artifact/x"
CASE_ONE = ("01-create-edit-find-matter", "Create, edit and find a matter", 133, "https://dev.checkbox.ninja/app/ticketing/tickets/f39c65e9", [
    ("Create the matter in chat", "The agent opened the matter and showed its link.", 'link "{TEST} Northwind Freight 1115-0930"', 8.2),
    ("Edit the matter in the same chat", "The agent reassigned it to Kesnavi and set the status, description and note.", '"Reassigned to Kesnavi Parammanandhan. Status: In Progress."', 52.4),
    ("Find the matter on the board", "The board search shows the matter with Kesnavi and In Progress.", 'row "{TEST} Northwind Freight 1115-0930" Kesnavi Parammanandhan In Progress', 91.0),
    ("Open the matter and check the description and note", "The matter page shows the description and the note.", '"Northwind wants a 30-day payment term and a liability cap at 1x fees"', 118.3),
])
CASE_TWO = ("02-see-requested-matters", "See my requested matters", 72, None, [
    ("Ask for my requested matters", "The agent replied with a list of matters.", '"Here are the matters you requested:"', 6.1),
    ("Find the new matter in the reply", "The list shows the Northwind Freight matter.", '"{TEST} Northwind Freight 1115-0930 · In Progress"', 38.0),
    ("Open the matter from the reply", "The matter page opens.", 'heading "{TEST} Northwind Freight 1115-0930"', 62.5),
])
BOARD_FAILS = {"at": 3, "seconds": 104, "summary": "The board search shows no row for the matter.", "saw": '"No matters match your search."', "error": "not found: row for matter f39c65e9"}
REPLY_FAILS = {"at": 2, "seconds": 58, "summary": "The reply does not list the Northwind Freight matter.", "saw": '"You have no open matter requests."', "error": "not found: {TEST} Northwind Freight 1115-0930"}


def write_case(state_dir, spec, fail=None):
    name, title, seconds, matter, steps = spec
    case_dir = os.path.join(state_dir, name)
    os.makedirs(case_dir, exist_ok=True)
    rows = []
    for number, (step_title, summary, evidence, offset) in enumerate(steps, start=1):
        row = {"title": step_title, "status": "passed", "summary": summary, "evidence": evidence, "error": "", "offsetSec": offset}
        if fail and number == fail["at"]:
            row.update(status="failed", summary=fail["summary"], evidence=fail["saw"], error=fail["error"])
        elif fail and number > fail["at"]:
            row.update(status="skipped", summary="Not run.", evidence="", offsetSec=None)
        rows.append(row)
    failure = {"what": fail["summary"], "why": fail["saw"], "atSec": steps[fail["at"] - 1][3]} if fail else None
    run = {"case": name, "title": title, "result": "FAIL" if fail else "PASS", "durationSec": fail["seconds"] if fail else seconds,
           "matterUrl": matter, "failure": failure, "steps": rows}
    with open(os.path.join(case_dir, "run.json"), "w") as handle:
        json.dump(run, handle)
    return {"name": name, "title": title, "status": "failed" if fail else "passed", "dir": case_dir}


def skip_case(spec):
    return {"name": spec[0], "title": spec[1], "status": "skipped", "dir": ""}


def make_fixtures(root):
    plans = {
        "all-passed": ("PASS", "passed", lambda d: [write_case(d, CASE_ONE), write_case(d, CASE_TWO)]),
        "case-failed": ("FAIL", "passed", lambda d: [write_case(d, CASE_ONE), write_case(d, CASE_TWO, REPLY_FAILS)]),
        "earlier-case-failed": ("FAIL", "passed", lambda d: [write_case(d, CASE_ONE, BOARD_FAILS), skip_case(CASE_TWO)]),
        "setup-failed": ("FAIL", "failed", lambda d: [skip_case(CASE_ONE), skip_case(CASE_TWO)]),
        "blocked": ("BLOCKED", None, lambda d: []),
    }
    paths = {}
    for state, (result, setup, cases) in plans.items():
        state_dir = os.path.join(root, state)
        os.makedirs(state_dir, exist_ok=True)
        suites = []
        if setup:
            error = "The board AI-Aliens is not in the Matters menu." if setup == "failed" else ""
            suites = [{"name": "matter-tools", "setup": {"status": setup, "error": error}, "cases": cases(state_dir)}]
        reason = "ROUTINE_QA_PASSWORD is not set." if result == "BLOCKED" else ""
        paths[state] = os.path.join(state_dir, "summary.json")
        with open(paths[state], "w") as handle:
            json.dump({"result": result, "baseUrl": "https://dev.checkbox.ninja", "blockedReason": reason, "suites": suites}, handle)
    return paths


def cards(artifact=ARTIFACT, publish_error=None):
    built = {}
    for state, path in make_fixtures(tempfile.mkdtemp()).items():
        with open(path) as handle:
            summary = json.load(handle)
        built[state] = build_card(summary, "QA", artifact, publish_error, [("Ann", "ann@example.com")])["attachments"][0]["content"]
    return built


def by_id(node, found=None):
    found = {} if found is None else found
    if isinstance(node, dict):
        if "id" in node:
            found[node["id"]] = node
        for value in node.values():
            by_id(value, found)
    elif isinstance(node, list):
        for value in node:
            by_id(value, found)
    return found


def test_parse_cookies():
    cookies = parse_cookies(["cb_access_token=abc; Path=/; HttpOnly", "cb_refresh_token=x=y; Secure"], "dev.example")
    assert [c["name"] for c in cookies] == ["cb_access_token", "cb_refresh_token"]
    assert cookies[1]["value"] == "x=y"
    assert cookies[0]["domain"] == "dev.example"


def test_is_local():
    assert is_local("localhost") and is_local("henry-kong-1.orb.local")
    assert not is_local("dev.checkbox.ninja")


def test_mark():
    case_dir = tempfile.mkdtemp()
    mark = os.path.join(HERE, "mark.py")
    for name in ("start", "S1", "end"):
        subprocess.run([sys.executable, mark, case_dir, name], check=True, capture_output=True)
    with open(os.path.join(case_dir, "marks.json")) as handle:
        assert set(json.load(handle)) == {"S1", "end"}


def test_card_heading_counts_cases():
    built = cards()
    assert {state: card["body"][1]["text"] for state, card in built.items()} == {
        "all-passed": "2 of 2 cases passed",
        "case-failed": "1 of 2 cases failed",
        "earlier-case-failed": "1 case failed, 1 not run",
        "setup-failed": "Setup failed, 2 cases not run",
        "blocked": "Blocked, nothing ran",
    }
    assert [built[state]["body"][1]["color"] for state in ("all-passed", "case-failed", "blocked")] == ["Good", "Attention", "Warning"]
    assert built["all-passed"]["msteams"]["entities"][0]["text"] == "<at>Ann</at>"


def test_card_opens_only_failed_cases():
    built = cards()
    passed, failed = by_id(built["all-passed"]), by_id(built["case-failed"])
    assert not passed["case0-steps"]["isVisible"] and not passed["case1-steps"]["isVisible"]
    assert passed["case0-show"]["text"] == "Show 4 steps" and not passed["case0-hide"]["isVisible"]
    assert not failed["case0-steps"]["isVisible"] and failed["case1-steps"]["isVisible"]
    rows = failed["case1-steps"]["items"]
    assert [row.get("style") for row in rows] == [None, "attention", None]
    texts = json.dumps(built["case-failed"], ensure_ascii=False)
    assert "Failed at S2 · 1 of 3 steps passed" in texts and "Page showed: \\\"You have no open matter requests.\\\"" in texts
    assert texts.count("[Watch ") == 4 and "(https://claude.ai/artifact/x#s4)" in texts


def test_card_says_why_a_case_did_not_run():
    built = cards()
    cascade = json.dumps(built["earlier-case-failed"], ensure_ascii=False)
    assert "Not run: 01 failed first." in cascade and "Failed at S3 · 2 of 4 steps passed" in cascade
    setup = built["setup-failed"]
    assert "Setup of matter-tools failed" in json.dumps(setup) and not any(key.endswith("-steps") for key in by_id(setup))
    assert setup["actions"] == []
    assert "ROUTINE_QA_PASSWORD is not set." in json.dumps(built["blocked"])


def test_card_without_recordings():
    built = cards(artifact=None, publish_error="the results page refused the publish")
    texts = json.dumps(built["all-passed"])
    assert "The recording page was not updated" in texts and "[Watch " not in texts
    assert built["all-passed"]["actions"] == []
    assert cards()["all-passed"]["actions"][0]["title"] == "Watch the recording"


if __name__ == "__main__":
    if sys.argv[1:2] == ["fixtures"]:
        for state, path in make_fixtures(sys.argv[2]).items():
            print(state, path)
    else:
        for name, test in list(globals().items()):
            if name.startswith("test_"):
                test()
        print("ok")
