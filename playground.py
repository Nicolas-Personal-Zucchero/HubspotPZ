"""
Manual development playground for HubspotPZ.
This script is not part of the distributed package and can be used
to test API calls interactively during development.

Setup:
1. Create a '.env' file by copying 'template.env':
   cp template.env .env
2. Insert your private HubSpot token in '.env'
3. Run:
   python playground.py
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from hubspot_pz import HubspotPZ


def load_env_file(filepath: str | Path = ".env") -> None:
    """Load variables from a .env file into the system environment (no external dependencies)."""
    env_path = Path(filepath)
    if not env_path.is_file():
        return

    with env_path.open(encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, val = stripped.split("=", 1)
            key = key.strip()
            val = val.strip().strip("'\"")
            os.environ.setdefault(key, val)


def pretty_print(title: str, data: object) -> None:
    """Print formatted JSON output."""
    print(f"\n{'='*25} {title} {'='*25}")
    print(json.dumps(data, indent=2, default=str))


def main() -> None:
    load_env_file()
    token = os.getenv("HUBSPOT_TOKEN")

    if not token or token == "your_private_token_here":
        print("[!] HubSpot token not found!")
        print("    Copy 'template.env' to '.env' and set your HUBSPOT_TOKEN before running the script.")
        return

    client = HubspotPZ(token)
    print("[+] HubspotPZ initialized successfully.")

    # -------------------------------------------------------------
    # 1. READ OBJECTS
    # -------------------------------------------------------------
    # print("\n--- Fetching contacts ---")
    # contacts = client.getAllContacts(["email", "firstname", "lastname"])
    # pretty_print("First 2 contacts", contacts[:2] if contacts else [])

    # -------------------------------------------------------------
    # 2. SINGLE CONTACT
    # -------------------------------------------------------------
    email = "nicolas.amadori02@gmail.com"
    contact = client.getContactByEmail(email, ["email", "firstname", "lastname"])
    pretty_print("Contact details", contact)

    # -------------------------------------------------------------
    # 3. CREATE, UPDATE, AND ARCHIVE
    # -------------------------------------------------------------
    # new_id = client.createContact({
    #     "email": "test_dev_playground@example.com",
    #     "firstname": "Playground",
    #     "lastname": "Test"
    # })
    # print(f"Contact created with ID: {new_id}")
    #
    # if new_id:
    #     updated = client.updateContact(new_id, {"firstname": "PlaygroundUpdated"})
    #     print(f"Contact update: {updated}")
    #
    #     archived = client.archiveContact(new_id)
    #     print(f"Contact archive: {archived}")

    # -------------------------------------------------------------
    # 4. TEST NEW FEATURES
    # -------------------------------------------------------------
    # Insert calls to new methods you are developing or testing:
    # result = client.yourMethod(...)
    # pretty_print("New feature result", result)


if __name__ == "__main__":
    main()
