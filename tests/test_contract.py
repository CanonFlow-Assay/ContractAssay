from copy import deepcopy

from consumer import Consumer

SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object", "required": ["message", "state"], "additionalProperties": False,
    "properties": {"message": {"type": "string"}, "state": {"enum": ["ready"]}},
}


class ContractEvidence(Consumer):
    def setUp(self):
        super().setUp()
        self.contract = {"id": "contract", "direction": "consumer", "selector": None,
                         "accepted": ["good"], "rejected": ["bad"]}
        self.policy = {"schemaVersion": 1, "profile": "directional-json",
                       "files": {"base": "base.json", "candidate": "candidate.json", "good": "good.json", "bad": "bad.json"},
                       "expects": {"format": "json-schema", "contracts": [self.contract]}}
        self.write("base.json", SCHEMA)
        self.write("candidate.json", SCHEMA)
        self.write("good.json", {"message": "hello", "state": "ready"})
        self.write("bad.json", {"state": "ready"})

    def test_positive_and_negative_cases_qualify(self):
        self.assertTrue(self.invoke(0)["authoritative"])
        self.assertEqual(self.invoke(2, "scan")["verdict"], "Inconclusive")

    def test_new_required_field_breaks_old_request(self):
        new = deepcopy(SCHEMA)
        new["required"].append("version")
        new["properties"]["version"] = {"type": "integer"}
        self.write("candidate.json", new)
        self.failed_rule(self.invoke(1), "CT004")

    def test_new_enum_and_nullable_response_defeat_old_consumers(self):
        self.contract["direction"] = "producer"
        base = deepcopy(SCHEMA)
        new = deepcopy(SCHEMA)
        new["properties"]["state"]["enum"].append("fresh")
        new["properties"]["message"]["type"] = ["string", "null"]
        for case in ({"message": "ok", "state": "fresh"}, {"message": None, "state": "ready"}):
            with self.subTest(case=case):
                self.write("candidate.json", new)
                self.write("base.json", base)
                self.write("good.json", case)
                self.failed_rule(self.invoke(1), "CT004")

    def test_invalid_or_unavailable_schema_evidence_stays_distinct(self):
        self.write("candidate.json", {**SCHEMA, "type": "integer-array"})
        self.failed_rule(self.invoke(1), "CT001")
        self.write("candidate.json", {**SCHEMA, "$ref": "https://example.invalid/schema"})
        self.assertEqual(self.invoke(2)["verdict"], "Inconclusive")

    def test_bad_fixture_is_not_a_passing_regression_control(self):
        self.write("bad.json", {"message": "good", "state": "ready"})
        self.failed_rule(self.invoke(1), "CT005")

    def test_source_fixture_cannot_bypass_its_own_contract(self):
        self.write("good.json", {"message": "good", "state": "mismatched"})
        self.failed_rule(self.invoke(1), "CT003")

    def test_explicit_date_time_assertion_uses_the_native_format_checker(self):
        schema = deepcopy(SCHEMA)
        schema["properties"]["message"]["format"] = "date-time"
        self.write("base.json", schema)
        self.write("candidate.json", schema)
        self.write("good.json", {"message": "not-a-date", "state": "ready"})
        self.failed_rule(self.invoke(1), "CT003")
        self.write("good.json", {"message": "2026-11-22T00:00:00Z", "state": "ready"})
        self.invoke(0)

    def test_openapi_selected_status_and_component_reference_exist(self):
        selector = {"path": "/objects", "method": "post", "status": 201, "mediaType": "application/json"}
        self.contract["direction"] = "response"
        self.contract["selector"] = selector
        self.policy["expects"]["format"] = "openapi-3.1"
        schema = deepcopy(SCHEMA)
        del schema["$schema"]
        operation = {"responses": {"201": {"content": {
            "application/json": {"schema": {"$ref": "#/components/schemas/Result"}}
        }}}}
        spec = {"openapi": "3.1.0", "paths": {"/objects": {"post": operation}},
                "components": {"schemas": {"Result": schema}}}
        self.write("base.json", spec)
        self.write("candidate.json", spec)
        self.write("good.json", {"http": selector, "body": {"message": "hello", "state": "ready"}})
        self.write("bad.json", {"http": selector, "body": {}})
        self.invoke(0)
        self.write("good.json", {"http": {**selector, "status": 200}, "body": {"message": "ok", "state": "ready"}})
        self.failed_rule(self.invoke(1), "CT006")
        self.write("good.json", {"http": selector, "body": {"message": "hello", "state": "ready"}})
        spec["paths"]["/objects"]["post"]["responses"] = {}
        self.write("candidate.json", spec)
        self.failed_rule(self.invoke(1), "CT002")
