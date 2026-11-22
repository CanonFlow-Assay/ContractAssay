"""Bind the Inventory loopback wire samples to selected OpenAPI contracts."""

import argparse
from copy import deepcopy
import json
from pathlib import Path


def write(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n")


def property_record(values):
    return {"type": "object", "required": list(values), "additionalProperties": False,
            "properties": values}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wire", type=Path)
    args = parser.parse_args()
    base = args.wire
    request = property_record({
        "requestId": {"type": "string", "minLength": 1}, "sku": {"type": "string", "minLength": 1},
        "quantity": {"type": "integer", "minimum": 1, "maximum": 3},
    })

    def response(status):
        return property_record({
            "status": {"enum": [status]}, "reservationId": {"type": "string"},
            "remaining": {"type": "integer", "minimum": 0}, "reason": {"type": "string"},
        })

    def content(name):
        return {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/" + name}}}}

    spec = {
        "openapi": "3.1.0", "info": {"title": "Inventory reservation fixture", "version": "1.0.0"},
        "paths": {"/reservations": {"post": {
            "requestBody": {"required": True, **content("Request")},
            "responses": {code: {"description": label, **content(name)}
                          for code, label, name in (("201", "Reservation committed", "Committed"),
                                                    ("200", "Reservation replayed", "Replayed"),
                                                    ("400", "Invalid reservation", "Invalid"))},
        }}},
        "components": {"schemas": {"Request": request, "Committed": response("reserved"),
                                  "Replayed": response("replayed"), "Invalid": response("invalid")}},
    }

    contracts = []
    mapping = {"producer": "origin.json", "base": "base.json", "candidate": "candidate.json"}
    for role in ("request", "committed", "replayed", "invalid"):
        selected = json.loads((base / (role + ".json")).read_text())["http"]
        body = {"http": selected, "body": {}}
        rejection = role + "-rejected"
        write(base / (rejection + ".json"), body)
        mapping[role] = role + ".json"
        mapping[rejection] = rejection + ".json"
        contracts.append({"id": role, "selector": selected, "direction": "request" if role == "request" else "response",
                          "accepted": [role], "rejected": [rejection]})
    policy = {"schemaVersion": 1, "profile": "directional-json", "files": mapping,
              "expects": {"format": "openapi-3.1", "contracts": contracts}}
    write(base / "policy.json", policy)
    write(base / "base.json", spec)
    write(base / "candidate.json", spec)

    narrow = deepcopy(spec)
    narrow["components"]["schemas"]["Request"]["properties"]["quantity"]["maximum"] = 1
    write(base / "candidate-narrow.json", narrow)
    missing_status = deepcopy(spec)
    del missing_status["paths"]["/reservations"]["post"]["responses"]["200"]
    write(base / "candidate-status-removed.json", missing_status)

    for case in ("narrow", "status-removed"):
        mutated = deepcopy(policy)
        mutated["files"]["candidate"] = f"candidate-{case}.json"
        write(base / f"policy-{case}.json", mutated)


if __name__ == "__main__":
    main()
