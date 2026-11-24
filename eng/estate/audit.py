#!/usr/bin/env python3
"""Inventory the Assay repositories or execute a versioned local evidence plan."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

REGISTRY = Path(__file__).with_name("lanes.json")
EXITS = {"Pass": 0, "Inconclusive": 2, "Fail": 1, "ToolFailure": 3}
RAW_FORMATS = {
    "playground": ("schemaVersion", "canonflow.assay.playground-receipt/v2", "verdict"),
    "expenseguard": ("schema", "assay-playground/0.1", "verdict"),
    "fsassay": ("schemaVersion", "fsassay-authority-receipt/1.1.0", "outcome"),
    "data-assay": ("schemaVersion", "data-assay-receipt/1", "verdict"),
}


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], text=True, timeout=10).rstrip("\n")


def candidate(root):
    if not root.is_dir() or Path(git(root, "rev-parse", "--show-toplevel")).resolve() != root:
        raise ValueError("checkout is missing or has an unexpected Git root")
    return {
        "path": str(root),
        "branch": git(root, "branch", "--show-current"),
        "commit": git(root, "rev-parse", "HEAD"),
        "tree": git(root, "rev-parse", "HEAD^{tree}"),
        "changes": git(root, "status", "--porcelain=v1", "--untracked-files=all"),
    }


def locate(name, estate, worktrees):
    primary = (estate / name).resolve()
    linked = worktrees / name
    if not linked.exists():
        return primary
    path = linked.resolve()
    registrations = git(primary, "worktree", "list", "--porcelain").splitlines()
    if f"worktree {path}" not in registrations:
        raise ValueError("candidate directory is not registered with the primary repository")
    return path


def hash_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def receipt_verdict(name, spec, directory, stdout, exit_code):
    key, schema, outcome = RAW_FORMATS[spec["format"]]
    raw = directory / spec["file"] if "file" in spec else stdout
    if not raw.is_file():
        if exit_code != 0:
            return "ToolFailure", "command ended before publishing its declared receipt"
        return "Inconclusive", "declared receipt is missing"
    try:
        receipt = json.loads(raw.read_bytes())
    except (ValueError, OSError):
        return "ToolFailure", "declared receipt is invalid JSON"
    if not isinstance(receipt, dict) or receipt.get(key) != schema:
        return "ToolFailure", "unexpected receipt schema"
    if spec["format"] == "playground" and receipt.get("repository") != name:
        return "ToolFailure", "receipt names a different repository"
    verdict = receipt.get(outcome)
    if not isinstance(verdict, str) or EXITS.get(verdict) != exit_code:
        return "ToolFailure", "receipt verdict disagrees with process exit"
    if spec["format"] == "fsassay" and verdict == "Pass" and receipt.get("authoritative") is not True:
        return "ToolFailure", "FsAssay Pass lacks authority"
    if spec["format"] == "expenseguard" and verdict == "Pass" and receipt.get("completed") is not True:
        return "ToolFailure", "ExpenseGuard Pass lacks completed evidence"
    return verdict, None


def run_step(name, step, source, directory, ordinal):
    stdout = directory / f"{ordinal}.stdout"
    stderr = directory / f"{ordinal}.stderr"
    args = [argument.replace("{python}", sys.executable).replace("{output}", str(directory))
            for argument in step["argv"]]
    for variable, flag in step.get("argumentFromEnvironment", {}).items():
        if os.environ.get(variable):
            args.extend((flag, os.environ[variable]))
    env = step.get("environment", {})
    timeout = step.get("timeout", 240)
    exit_code = None
    reason = None
    with stdout.open("wb") as output, stderr.open("wb") as errors:
        try:
            process = subprocess.run(args, cwd=source, env={**os.environ, **env},
                                     stdout=output, stderr=errors, timeout=timeout)
            exit_code = process.returncode
        except (OSError, subprocess.TimeoutExpired) as error:
            reason = str(error)
    if reason is not None:
        verdict = "ToolFailure"
    elif "receipt" in step:
        verdict, reason = receipt_verdict(name, step["receipt"], directory, stdout, exit_code)
    elif exit_code == 0:
        marker = step.get("testCountPattern")
        if marker and not re.search(marker, stdout.read_text(errors="replace"), re.MULTILINE):
            verdict, reason = "Inconclusive", "nonzero executed test count is missing"
        else:
            verdict = "Pass"
    elif exit_code == 1:
        verdict, reason = "Fail", "required command exited 1"
    else:
        verdict, reason = "ToolFailure", "unexpected process exit"
    run = {"scope": step["scope"], "argv": args, "environmentOverrides": env, "cwd": str(source),
           "exitCode": exit_code, "verdict": verdict, "reason": reason,
           "stdoutSha256": hash_file(stdout), "stderrSha256": hash_file(stderr)}
    if "receipt" in step:
        raw = directory / step["receipt"]["file"] if "file" in step["receipt"] else stdout
        if raw.is_file():
            run["receipt"] = {"path": str(raw), "sha256": hash_file(raw)}
    return run


def worst(verdicts):
    return max(verdicts, key=tuple(EXITS).index)


def inspect(name, plan, args, output):
    row = {"repository": name, "steps": []}
    try:
        root = locate(name, args.estate, args.worktrees)
        row["before"] = candidate(root)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        return {**row, "reason": str(error), "verdict": "Inconclusive"}
    if args.mode == "inventory":
        return {**row, "verdict": "Inconclusive", "reason": "inventory only"}
    if not plan:
        return {**row, "verdict": "Inconclusive", "reason": "required command plan is missing"}
    directory = output / name
    directory.mkdir()
    for ordinal, step in enumerate(plan, 1):
        execution = run_step(name, step, root, directory, ordinal)
        row["steps"].append(execution)
        if execution["verdict"] != "Pass":
            break
    row["notRun"] = [step["scope"] for step in plan[len(row["steps"]):]]
    verdicts = [step["verdict"] for step in row["steps"]]
    try:
        row["after"] = candidate(root)
        if row["before"] != row["after"] or row["before"]["changes"]:
            verdicts.append("Inconclusive")
            row["reason"] = "source identity changed or checkout has uncommitted inputs"
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        verdicts.append("ToolFailure")
        row["reason"] = str(error)
    row["verdict"] = worst(verdicts)
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["inventory", "run"])
    parser.add_argument("--estate", type=lambda p: Path(p).resolve(), required=True)
    parser.add_argument("--worktrees", type=lambda p: Path(p).resolve(), required=True)
    parser.add_argument("--output", type=lambda p: Path(p).resolve(), required=True)
    registry = json.loads(REGISTRY.read_bytes())
    parser.add_argument("--repository", choices=registry, action="append")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("--output must be a fresh directory")
    if args.output.is_relative_to(args.estate) or args.output.is_relative_to(args.worktrees):
        parser.error("--output must be outside source checkouts")
    args.output.mkdir(parents=True)
    scope = sorted(set(args.repository or registry))
    rows = [inspect(name, registry[name], args, args.output) for name in scope]
    verdict = worst(row["verdict"] for row in rows)
    receipt = {"schemaVersion": "canonflow.assay.estate-observation/v2",
               "mode": args.mode, "verdict": verdict, "scope": scope,
               "planSha256": hash_file(REGISTRY), "repositories": rows}
    path = args.output / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(path)
    return EXITS[verdict] if args.mode == "run" else 0


if __name__ == "__main__":
    raise SystemExit(main())
