"""Native schema validation over explicitly selected JSON contract fixtures."""

from importlib.metadata import PackageNotFoundError, version
import re
from urllib.parse import quote

EXTRA_FILES = ()
VERSION = "4.26.0"
DRAFT7 = {"http://json-schema.org/draft-07/schema#", "https://json-schema.org/draft-07/schema"}
DRAFT2020 = {"https://json-schema.org/draft/2020-12/schema"}
METHODS = {"get", "put", "post", "delete", "options", "head", "patch", "trace"}
MAPS = ("properties", "patternProperties", "$defs", "definitions", "dependentSchemas")
ARRAYS = ("allOf", "anyOf", "oneOf", "prefixItems")
SINGLES = (
    "additionalProperties", "additionalItems", "unevaluatedProperties", "unevaluatedItems",
    "items", "contains", "if", "then", "else", "not", "propertyNames",
)


def doctor():
    observed = {}
    for package, pin in {"jsonschema": VERSION, "rfc3339-validator": "0.1.4"}.items():
        try:
            installed = version(package)
        except PackageNotFoundError:
            installed = None
        observed[package] = {"version": installed, "required": pin}
    ready = all(item["version"] == item["required"] for item in observed.values())
    return {"nativePackages": observed, "ready": ready}


def checked_schema(node, checker, component_refs=False):
    if type(node) is bool:
        return
    if not isinstance(node, dict):
        raise ValueError("expected a schema object or boolean")
    for key in ("$ref", "$dynamicRef", "$recursiveRef"):
        if key in node:
            reference = node[key]
            if not isinstance(reference, str) or not reference.startswith("#"):
                raise ValueError("external references are outside the selected contract")
            if component_refs and not reference.startswith("#/components/schemas/"):
                raise ValueError("OpenAPI references must name local component schemas")
    if "format" in node and node["format"] not in checker.checkers:
        raise ValueError("unimplemented format assertion")
    for key in MAPS:
        for child in node.get(key, {}).values():
            checked_schema(child, checker, component_refs)
    for key in ARRAYS:
        for child in node.get(key, []):
            checked_schema(child, checker, component_refs)
    for key in SINGLES:
        if key in node:
            children = node[key] if key == "items" and isinstance(node[key], list) else [node[key]]
            for child in children:
                checked_schema(child, checker, component_refs)


def selected(document, selector):
    if not isinstance(document, dict) or not isinstance(document.get("openapi"), str) or not re.fullmatch(
        r"3\.1\.\d+", document["openapi"]
    ):
        raise ValueError("OpenAPI 3.1 document required")
    pointer = ["paths", selector["path"], selector["method"]]
    if selector["status"] is None:
        pointer += ["requestBody"]
    else:
        pointer += ["responses", str(selector["status"])]
    pointer += ["content", selector["mediaType"], "schema"]
    schema = document
    for item in pointer:
        if not isinstance(schema, dict) or item not in schema:
            raise LookupError("selected operation, response, or media schema is absent")
        schema = schema[item]
    fragment = "/" + "/".join(item.replace("~", "~0").replace("/", "~1") for item in pointer)
    return schema, quote(fragment, safe="/~")


def parse_contract(expectation, kind):
    fields = {"id", "direction", "selector", "accepted", "rejected"}
    if not isinstance(expectation, dict) or set(expectation) != fields:
        raise ValueError("invalid contract obligation")
    name = expectation["id"]
    direction = expectation["direction"]
    if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", name):
        raise ValueError("invalid contract identity")
    selector = expectation["selector"]
    if kind == "json-schema":
        if selector is not None or direction not in ("consumer", "producer"):
            raise ValueError("standalone schemas require a directional contract")
    elif not isinstance(selector, dict) or set(selector) != {"path", "method", "status", "mediaType"}:
        raise ValueError("OpenAPI selector is required")
    elif (
        direction not in ("request", "response") or not isinstance(selector["path"], str)
        or not selector["path"].startswith("/") or selector["method"] not in METHODS
        or selector["mediaType"] != "application/json"
        or (direction == "request" and selector["status"] is not None)
        or (direction == "response" and (
            type(selector["status"]) is not int or not 100 <= selector["status"] <= 599
        ))
    ):
        raise ValueError("unsupported OpenAPI selector")
    roles = []
    for field in ("accepted", "rejected"):
        items = expectation[field]
        if not isinstance(items, list) or not 1 <= len(items) <= 24 or any(not isinstance(item, str) for item in items):
            raise ValueError("positive and rejection fixtures are required for each contract")
        roles.extend(items)
    if len(set(roles)) != len(roles) or {"base", "candidate"}.intersection(roles):
        raise ValueError("fixture roles must be unique")
    return name, direction, selector


def validator(document, schema, fragment, side):
    from jsonschema import Draft7Validator, Draft202012Validator, FormatChecker
    from referencing import Registry, Resource
    from referencing.jsonschema import DRAFT202012

    checker = FormatChecker(formats=("date-time", "uuid", "ipv4", "ipv6"))
    if fragment is None:
        if not isinstance(schema, dict):
            raise ValueError("a standalone schema must explicitly identify its dialect")
        dialect = schema.get("$schema")
        if dialect in DRAFT7:
            cls = Draft7Validator
        elif dialect in DRAFT2020:
            cls = Draft202012Validator
        else:
            raise ValueError("unsupported or undeclared JSON Schema dialect")
        cls.check_schema(schema)
        checked_schema(schema, checker)
        return cls(schema, registry=Registry(), format_checker=checker)
    Draft202012Validator.check_schema(schema)
    checked_schema(schema, checker, component_refs=True)
    components = document.get("components", {}).get("schemas", {})
    for component in components.values():
        Draft202012Validator.check_schema(component)
        checked_schema(component, checker, component_refs=True)
    uri = f"urn:canonflow:contract:{side}"
    registry = Registry().with_resource(uri, Resource(document, DRAFT202012))
    return Draft202012Validator({"$ref": uri + "#" + fragment}, registry=registry, format_checker=checker)


def build(evidence, document, kind, selector, side, subject):
    from jsonschema.exceptions import SchemaError

    if document is None:
        evidence.check("CT001", None, subject)
        return None
    if kind == "openapi-3.1":
        try:
            schema, fragment = selected(document, selector)
        except LookupError:
            evidence.check("CT002", False, subject, "selected operation, status or JSON media type is absent")
            return None
        except ValueError as error:
            evidence.check("CT001", None, subject, str(error))
            return None
    else:
        schema, fragment = document, None
    evidence.check("CT002", True, subject)
    try:
        result = validator(document, schema, fragment, side)
    except SchemaError:
        evidence.check("CT001", False, subject, "selected schema does not conform to its meta-schema")
        return None
    except (AttributeError, TypeError, ValueError, RecursionError) as error:
        evidence.check("CT001", None, subject, str(error))
        return None
    evidence.check("CT001", True, subject, {"jsonschema": VERSION})
    return result


def validate(validator, fixture):
    if validator is None:
        return None, None
    from referencing.exceptions import Unresolvable

    try:
        error = next(validator.iter_errors(fixture), None)
    except (Unresolvable, RecursionError):
        return None, "reference or recursion evidence unavailable"
    if error is None:
        return True, None
    # Schema keyword and structural path preserve the failing boundary without echoing payloads.
    return False, {"keyword": str(error.validator), "path": list(error.absolute_path)}


def test_cases(evidence, obligation, pair, name, source, selector, scan):
    accepted = set(obligation["accepted"])
    for role in [*obligation["accepted"], *obligation["rejected"]]:
        subject = f"{name}/{role}"
        raw = evidence.raw(role)
        if raw is None or scan:
            evidence.check("CT003" if role in accepted else "CT005", None, subject)
            continue
        try:
            from .engine import parse_json
            fixture = parse_json(raw)
        except (ValueError, RecursionError):
            evidence.check("CT006", None, subject, "fixture JSON is malformed")
            continue
        if selector is not None:
            match = (
                isinstance(fixture, dict) and set(fixture) == {"http", "body"}
                and fixture["http"] == selector
            )
            evidence.check("CT006", match, subject)
            if not match:
                continue
            fixture = fixture["body"]
        if role in accepted:
            source_ok, detail = validate(pair[source], fixture)
            evidence.check("CT003", source_ok, subject, detail)
            target_ok, detail = validate(pair[1 - source], fixture)
            evidence.check("CT004", target_ok, subject, detail)
        else:
            for index, validator in enumerate(pair):
                ok, detail = validate(validator, fixture)
                evidence.check("CT005", None if ok is None else not ok, f"{subject}/{index}", detail)


def verify(evidence, scan):
    configuration = evidence.expects
    if set(configuration) != {"format", "contracts"}:
        raise ValueError("contract policy requires format and contracts")
    kind = configuration["format"]
    obligations = configuration["contracts"]
    if kind not in ("json-schema", "openapi-3.1") or not isinstance(obligations, list) or not 1 <= len(obligations) <= 24:
        raise ValueError("unsupported contract profile or empty scope")
    names = set()
    if not doctor()["ready"]:
        evidence.check("CT001", None, detail="qualified jsonschema version unavailable")
        return
    baseline = evidence.json("base")
    candidate = evidence.json("candidate")
    for obligation in obligations:
        name, direction, selector = parse_contract(obligation, kind)
        if name in names:
            raise ValueError("duplicate contract obligation")
        names.add(name)
        pair = [build(evidence, document, kind, selector, side, f"{name}/{side}")
                for document, side in ((baseline, "base"), (candidate, "candidate"))]
        source = 0 if direction in ("request", "consumer") else 1
        test_cases(evidence, obligation, pair, name, source, selector, scan)
