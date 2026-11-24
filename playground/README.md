# ContractAssay playground

The wrapper selects the ONDC evidence-bundle policy. It exercises the
pinned JSON Schema validator on the checked-in accepted and rejected
specimens. [ONDC policy](../examples/ondc/policy.json)

Install the locked validator dependencies and run the wrapper with the
virtual environment interpreter. The wrapper prefers the shared locked
interpreter at `~/.cache/canonflow-portfolio/contracts-locked/bin/python`
when that file exists. [Repository setup](../README.md)

```sh
.venv/bin/python playground/run.py
```

The v2 receipt preserves command arguments, exits, and raw logs for
readiness, catalogue explanations, source tests, the showcase verification,
and the provisional scan control. The scan control expects
`Inconclusive` with exit `2`. The wrapper propagates a failed or
incomplete showcase and refuses a contradictory receipt and process exit.

For the native receipt alone, run each command independently.

```sh
PYTHONPATH=src .venv/bin/python -m contract_assay scan --policy examples/ondc/policy.json
PYTHONPATH=src .venv/bin/python -m contract_assay verify --policy examples/ondc/policy.json
```

A `Pass` from `verify` covers the declared ONDC wire obligations. The example
`scan` reports `Inconclusive` with exit `2`. Invoke `verify` with the Inventory
policy to check its recorded capture. [Inventory policy](../examples/inventory/policy.json)
