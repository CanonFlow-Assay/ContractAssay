# Qualified contract examples

The ONDCFlow example uses its checked-in evidence-bundle schema with
positive and rejected structural specimens. The SDK's transport and
business acceptance have their own evidence.

The Inventory example retains actual HTTP requests and 201, 200 and 400
responses from the Playground API on a disposable PostgreSQL database.
The origin file binds the observed producer binary and .NET SDK. The
selected OpenAPI 3.1 schema describes the fixture's four obligations.
Narrowing the request quantity and removing the replay response are
separate failing controls. The consumer tests execute the original
Playground .NET suites.

- [OpenAPI 3.1 specification](https://spec.openapis.org/oas/v3.1.2.html)
- [JSON Schema validation](https://json-schema.org/draft/2020-12/json-schema-validation)
- [Inventory fixture source](https://github.com/CanonFlow-Assay/CSharpAssay.Playground/tree/main/samples/80-inventory-reservation)

Use eng/probe-inventory.py with the already built Inventory API and the
Playground's owned database helper. Clear ASSAY_INVENTORY_DATABASE when
invoking the helper so it creates a fixture for the capture. The probe
uses the sample's loopback port 5080. Then eng/inventory-plan.py prepares
the policy and two wire controls in the output directory.
