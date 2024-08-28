import os
import logging
import json
import jsonschema

from astro_pi_replay.resources import get_resource, get_replay_sequence_dir
import pytest

logger = logging.getLogger(__name__)

if os.environ.get("PYTEST_PROFILE", None) != "INTEGRATION_TESTS":
    pytest.skip("Skipping integration tests", allow_module_level=True)

with get_resource("metadata_schema.json").open() as f:
    schema: dict = json.load(f)

def test_asset_metadata_matches_schema():
    with (get_replay_sequence_dir() / "metadata.json").open() as f:
        to_validate = json.load(f)
    jsonschema.validate(to_validate, schema)
