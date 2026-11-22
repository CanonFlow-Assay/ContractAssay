"""Capture declared examples from the existing C# Inventory HTTP producer."""

import argparse
import hashlib
import json
from pathlib import Path
import os
import socket
import subprocess
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

HOST = "127.0.0.1"
PORT = 5080
ROUTE = "/reservations"


def request(body):
    selected = {"path": ROUTE, "method": "post", "mediaType": "application/json"}
    payload = json.dumps(body).encode()
    req = Request(f"http://{HOST}:{PORT}{ROUTE}", payload,
                  {"Content-Type": "application/json"}, method="POST")
    try:
        response = urlopen(req, timeout=4)
    except HTTPError as error:
        response = error
    with response:
        return ({"http": {**selected, "status": None}, "body": body},
                {"http": {**selected, "status": response.status,
                          "mediaType": response.headers.get_content_type()},
                 "body": json.loads(response.read(64 * 1024))})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    # The caller supplies the connection only from the reviewed owned fixture tool.
    if not os.getenv("ASSAY_INVENTORY_DATABASE", "").startswith("Host=127.0.0.1;"):
        raise RuntimeError("use the Playground's owned loopback database fixture")
    with socket.socket() as availability:
        availability.bind((HOST, PORT))
    repo = args.playground.resolve()
    dll = repo / "samples/80-inventory-reservation/src/Inventory.Api/bin/Release/net11.0/Inventory.Api.dll"
    args.out.mkdir(parents=True, exist_ok=False)
    app = subprocess.Popen(["dotnet", str(dll)], cwd=repo, stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, start_new_session=True)
    try:
        deadline = time.monotonic() + 20
        while True:
            if app.poll() is not None:
                raise RuntimeError("the Inventory producer exited")
            try:
                with socket.create_connection((HOST, PORT), timeout=0.3):
                    break
            except OSError:
                if time.monotonic() >= deadline:
                    raise RuntimeError("Inventory loopback server did not start")
                time.sleep(0.2)
        payload = {"requestId": "contract-fixture", "sku": "widget", "quantity": 2}
        submitted, committed = request(payload)
        _, replayed = request(payload)
        _, invalid = request({"requestId": None, "sku": "widget", "quantity": 1})
        outputs = {"request": submitted, "committed": committed, "replayed": replayed, "invalid": invalid}
        if [committed["http"]["status"], replayed["http"]["status"], invalid["http"]["status"]] != [201, 200, 400]:
            raise RuntimeError("native producer did not meet the response fixture requirements")
        for name, value in outputs.items():
            (args.out / f"{name}.json").write_text(json.dumps(value, indent=2) + "\n")
        origin = {"head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip(),
                  "dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=repo)),
                  "producerSha256": hashlib.sha256(dll.read_bytes()).hexdigest(),
                  "sdk": subprocess.check_output(["dotnet", "--version"], cwd=repo, text=True).strip()}
        (args.out / "origin.json").write_text(json.dumps(origin, indent=2) + "\n")
        print(json.dumps({"status": "Pass", "responses": [201, 200, 400], **origin}))
    finally:
        app.terminate()
        try:
            app.wait(timeout=5)
        except subprocess.TimeoutExpired:
            app.kill()
            app.wait(timeout=5)


if __name__ == "__main__":
    main()
