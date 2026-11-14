import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(__file__))

from login import is_local, parse_cookies
from teams import build_card

HERE = os.path.dirname(__file__)


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


def test_card():
    case_dir = tempfile.mkdtemp()
    run = {"matterUrl": "https://dev.example/app/ticketing/tickets/1", "failure": None, "steps": [
        {"title": "Create", "status": "passed", "summary": "Made it.", "evidence": "link", "error": "", "offsetSec": 1.0},
        {"title": "Edit", "status": "failed", "summary": "Did not.", "evidence": "", "error": "no reply", "offsetSec": 9.0},
    ]}
    with open(os.path.join(case_dir, "run.json"), "w") as handle:
        json.dump(run, handle)
    summary = {"result": "FAIL", "baseUrl": "https://dev.example", "suites": [
        {"name": "s", "setup": {"status": "passed"}, "cases": [{"name": "01-c", "status": "failed", "dir": case_dir}]}]}
    card = build_card(summary, "QA", "https://claude.ai/artifact/x", None, [("Ann", "ann@example.com")])["attachments"][0]["content"]
    texts = json.dumps(card)
    assert card["body"][0]["text"] == "QA: 1/2 passed" and card["body"][0]["color"] == "Attention"
    assert "[Recording](https://claude.ai/artifact/x#s2)" in texts and "no reply" in texts
    assert card["msteams"]["entities"][0]["text"] == "<at>Ann</at>"
    assert [a["title"] for a in card["actions"]] == ["All recordings", "Open matter"]
    blocked = build_card({"result": "BLOCKED", "blockedReason": "no creds", "suites": []}, "QA", None, None, [])
    assert "no creds" in json.dumps(blocked)


if __name__ == "__main__":
    for name, test in list(globals().items()):
        if name.startswith("test_"):
            test()
    print("ok")
