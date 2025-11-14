#!/usr/bin/env python3
"""Fetch API schema and extract field information"""

import json
import os
import sys
from pathlib import Path

import httpx
import yaml

# Load .env if it exists
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

API_KEY = os.getenv("TANGO_API_KEY")
BASE_URL = os.getenv("TANGO_BASE_URL", "https://tango.makegov.com")

if not API_KEY:
    print("ERROR: TANGO_API_KEY not found in environment", file=sys.stderr)
    sys.exit(1)

headers = {"X-API-KEY": API_KEY}

# Fetch schema
print(f"Fetching schema from {BASE_URL}/api/schema/...", file=sys.stderr)
response = httpx.get(f"{BASE_URL}/api/schema/", headers=headers, timeout=30.0)

if response.status_code != 200:
    print(f"ERROR: Failed to fetch schema: {response.status_code}", file=sys.stderr)
    print(f"Response text: {response.text[:500]}", file=sys.stderr)
    sys.exit(1)

# Check content type and parse accordingly
content_type = response.headers.get("content-type", "")
if "yaml" in content_type.lower() or "openapi" in content_type.lower():
    try:
        schema = yaml.safe_load(response.text)
    except yaml.YAMLError as e:
        print(f"ERROR: Failed to parse YAML: {e}", file=sys.stderr)
        sys.exit(1)
elif "json" in content_type.lower():
    try:
        schema = response.json()
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse JSON: {e}", file=sys.stderr)
        sys.exit(1)
else:
    # Try both formats
    try:
        schema = yaml.safe_load(response.text)
    except yaml.YAMLError:
        try:
            schema = response.json()
        except json.JSONDecodeError as e:
            print(f"ERROR: Failed to parse response as YAML or JSON: {e}", file=sys.stderr)
            sys.exit(1)

# Extract component schemas
components = schema.get("components", {}).get("schemas", {})

# Write full schema
output_file = Path("api_schema_full.json")
with open(output_file, "w") as f:
    json.dump(schema, f, indent=2)
print(f"Full schema written to {output_file}", file=sys.stderr)

# Extract and print key model schemas
key_models = [
    "Contract",
    "Entity",
    "Grant",
    "Forecast",
    "Opportunity",
    "Notice",
    "Agency",
    "Location",
    "RecipientProfile",
]

print("\n" + "=" * 80, file=sys.stderr)
print("KEY MODEL SCHEMAS", file=sys.stderr)
print("=" * 80, file=sys.stderr)

for model_name in key_models:
    if model_name in components:
        model_schema = components[model_name]
        properties = model_schema.get("properties", {})

        print(f"\n{model_name}:", file=sys.stderr)
        print("-" * 40, file=sys.stderr)

        for field_name, field_info in sorted(properties.items()):
            field_type = field_info.get("type", "unknown")
            if "$ref" in field_info:
                ref = field_info["$ref"].split("/")[-1]
                field_type = f"ref:{ref}"
            elif "items" in field_info:
                item_type = field_info["items"].get("type", "unknown")
                if "$ref" in field_info["items"]:
                    ref = field_info["items"]["$ref"].split("/")[-1]
                    item_type = f"ref:{ref}"
                field_type = f"array[{item_type}]"

            required = field_name in model_schema.get("required", [])
            optional_str = "" if required else " (optional)"

            print(f"  {field_name}: {field_type}{optional_str}", file=sys.stderr)

# Write extracted schemas to a separate file
extracted = {name: components[name] for name in key_models if name in components}
extracted_file = Path("api_schema_extracted.json")
with open(extracted_file, "w") as f:
    json.dump(extracted, f, indent=2)
print(f"\nExtracted schemas written to {extracted_file}", file=sys.stderr)

# Output JSON for further processing
print(json.dumps(components, indent=2))
