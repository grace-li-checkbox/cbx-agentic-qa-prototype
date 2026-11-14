import json
import os
import ssl
import sys
import urllib.error
import urllib.request
from urllib.parse import urlparse


def is_local(host):
    return host in ("localhost", "127.0.0.1") or host.endswith((".localhost", ".orb.local"))


def parse_cookies(headers, host):
    cookies = []
    for header in headers:
        name, _, value = header.split(";", 1)[0].partition("=")
        if name.strip():
            cookies.append({
                "name": name.strip(),
                "value": value.strip(),
                "domain": host,
                "path": "/",
                "expires": -1,
                "httpOnly": True,
                "secure": True,
                "sameSite": "Lax",
            })
    return cookies


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: login.py <base url> <state.json path>")
    base, out = sys.argv[1].rstrip("/"), sys.argv[2]
    host = urlparse(base).hostname or ""
    context = ssl._create_unverified_context() if is_local(host) else None
    body = json.dumps({
        "username": os.environ["ROUTINE_QA_EMAIL"],
        "password": os.environ["ROUTINE_QA_PASSWORD"],
    }).encode()
    request = urllib.request.Request(
        base + "/api/v1/auth/login",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, context=context, timeout=60) as response:
            status = response.status
            headers = response.headers.get_all("Set-Cookie") or []
    except urllib.error.HTTPError as error:
        sys.exit(f"sign-in failed: HTTP {error.code}")
    except urllib.error.URLError as error:
        sys.exit(f"sign-in failed: {error.reason}")
    cookies = parse_cookies(headers, host)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w") as handle:
        json.dump({"cookies": cookies, "origins": []}, handle)
    print(status, [cookie["name"] for cookie in cookies])
    if not cookies:
        sys.exit("sign-in failed: no cookies")


if __name__ == "__main__":
    main()
