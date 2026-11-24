#!/usr/bin/env python3
"""Check or regenerate the self-contained Python playground runners."""

import argparse
from pathlib import Path
import re

# Repository name, import package, default policy, snapshot, local native-tool cache.
TARGETS = [
    ("BashAssay", "bash_assay", "examples/policy.json", None, "shellcheck"),
    ("ContractAssay", "contract_assay", "examples/ondc/policy.json", None, None),
    ("DhallAssay", "dhall_assay", "examples/policy.json", None, "dhall"),
    ("DuckDBAssay", "duckdb_assay", "examples/policy.json", "examples/snapshot.json", None),
    ("GitHubActionsAssay", "github_actions_assay", "examples/playground-44739374322.json", None, None),
    ("OpenSearchAssay", "opensearch_assay", "examples/policy.json", "examples/snapshot.json", None),
    ("OracleAssay", "oracle_assay", "examples/policy-23.json", None, None),
    ("PostgresAssay", "postgres_assay", "examples/policy.json", "examples/snapshot.json", None),
    ("PowerShellAssay", "powershell_assay", "examples/policy.json", None, "powershell"),
]
FIELDS = ("REPOSITORY", "PACKAGE", "POLICY", "SNAPSHOT", "NATIVE_CACHE")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worktrees", type=Path, required=True)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    template = Path(__file__).with_name("playground_runner.py.in").read_text()
    differences = []
    for target in TARGETS:
        values = dict(zip(FIELDS, target, strict=True))
        path = args.worktrees / target[0] / "playground/run.py"
        if not path.is_file():
            parser.error(f"runner checkout missing: {path}")
        rendered = re.sub(r"@([A-Z_]+)@", lambda match: repr(values[match[1]]), template)
        if path.read_text() != rendered:
            differences.append(path)
            if args.write:
                path.write_text(rendered)
    if differences and not args.write:
        for path in differences:
            print(path)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
