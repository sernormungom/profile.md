"""Check that profile.md still holds one valid YAML document with unique IDs.

Run after every edit to profile.md, from the repo root:

    job-search/.venv/bin/python validate_profile.py

Needs PyYAML, which is installed in job-search/.venv (see job-search/requirements.txt).
Exits with status 1 and a message when the YAML does not parse or an ID appears twice.
"""

import re
import sys
from collections import Counter
from pathlib import Path

import yaml

PROFILE = Path(__file__).with_name("profile.md")


def collect_ids(node, found):
    """Record every value of a key ending in '_id', except source_id."""
    if isinstance(node, dict):
        for key, value in node.items():
            # source_id is a reference to a source, so it repeats on purpose.
            if key.endswith("_id") and key != "source_id" and isinstance(value, str):
                found.append(value)
            collect_ids(value, found)
    elif isinstance(node, list):
        for item in node:
            collect_ids(item, found)


def main():
    text = PROFILE.read_text(encoding="utf-8")
    blocks = re.findall(r"^```ya?ml\n(.*?)^```", text, re.S | re.M)
    if len(blocks) != 1:
        sys.exit(f"profile.md: expected one YAML block, found {len(blocks)}")
    try:
        data = yaml.safe_load(blocks[0])
    except yaml.YAMLError as err:
        sys.exit(f"profile.md: YAML does not parse:\n{err}")
    ids = []
    collect_ids(data, ids)
    repeated = sorted(i for i, n in Counter(ids).items() if n > 1)
    if repeated:
        sys.exit("profile.md: IDs used more than once: " + ", ".join(repeated))
    print(f"profile.md: valid YAML, {len(ids)} unique IDs")


if __name__ == "__main__":
    main()
