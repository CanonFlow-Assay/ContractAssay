# ContractAssay

Verify compatibility in one declared direction for JSON Schema draft-07,
JSON Schema 2020-12 or selected OpenAPI 3.1 JSON requests and responses.
The verifier runs a pinned native JSON Schema validator against positive
and rejection specimens. Local references resolve from a closed registry.

An old request must still satisfy the candidate receiver. A candidate
response must still satisfy the old consumer. The checker reports the
failed schema keyword, affected fixture or missing selected HTTP status
and media type. Every obligation names its direction and specimens.

## Run

~~~sh
python3 -m venv .venv
.venv/bin/pip install --only-binary=:all: --require-hashes -r requirements.txt
PYTHONPATH=src .venv/bin/python -m contract_assay verify --policy examples/ondc/policy.json
PYTHONPATH=src .venv/bin/python -m contract_assay verify --policy examples/inventory/policy.json
.venv/bin/python eng/qualify.py
~~~

The initial lock targets Python 3.12 on Linux x86-64. The OpenAPI lane
validates the selected JSON operations and referenced schemas.
Compatibility evidence is specific to the supplied specimens.
See [qualification and wire capture](docs/native.md) and the
[evidence contract](CONTRACT.md). Apache-2.0.

## Assay estate checks

The estate coordinator records checkout identity and executes declared
repository checks. The worktree audit includes invocation and evidence limits.
[Estate audit and replay](docs/active-git-worktree-summary.md#replaying-the-repaired-estate-checks)
