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
    NICOLAS_1_CONTACT_ID = "311400202443" # nicolasamadori2002@gmail.com
    NICOLAS_2_CONTACT_ID = "464026798284" # nicolas.amadori02@gmail.com
    PZ_COMPANY_ID = "6751536075" # PERSONAL ZUCCHERO SRL (501.00001)
    AMADORI_DEAL_ID = "523248658633"

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
    # email = "nicolas.amadori02@gmail.com"
    # contact = client.getContactByEmail(email, ["email", "firstname", "lastname"])
    # pretty_print("Contact details", contact)

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
    # TEST MIGRATED ASSOCIATIONS (2026-09)
    # -------------------------------------------------------------
    print(f"\n[+] Active Associations API Version: {client._ASSOCIATIONS_API_VERSION}")

    # TESTED: Batch Read Associations (Contacts -> Contacts)
    # print("\n--- Testing Batch Read Associations (Contacts -> Contacts) ---")
    # associated_contacts = client.getContactsAssociatedContactsBatch([NICOLAS_1_CONTACT_ID, NICOLAS_2_CONTACT_ID])
    # pretty_print("Contacts -> Contacts Associations", associated_contacts)

    # TESTED: Batch Read Associations (Contacts -> Companies)
    # print("\n--- Testing Batch Read Associations (Contacts -> Companies) ---")
    # associated_companies = client.getContactsAssociatedCompaniesBatch([NICOLAS_1_CONTACT_ID, NICOLAS_2_CONTACT_ID])
    # pretty_print("Contacts -> Companies Associations", associated_companies)

    # TESTED: Batch Read Associations (Companies -> Contacts)
    # print("\n--- Testing Batch Read Associations (Companies -> Contacts) ---")
    # associated_contacts = client.getCompaniesAssociatedContactsBatch([PZ_COMPANY_ID])
    # pretty_print("Companies -> Contacts Associations", associated_contacts)

    # TESTED: Batch Create Associations (Contacts -> Contacts, type 449)
    # print("\n--- Testing Batch Create Associations (Contacts -> Contacts) ---")
    # contact_assoc_created = client.createContactsAssociatedContactsBatch([(NICOLAS_1_CONTACT_ID, NICOLAS_2_CONTACT_ID)])
    # print(f"Contacts -> Contacts Association Created: {contact_assoc_created}")

    # TESTED: Batch Create Associations (Deals -> Contacts, type 3)
    # print("\n--- Testing Batch Create Associations (Deals -> Contacts) ---")
    # deal_assoc_created = client.createContactsAssociatedDealsBatch([(AMADORI_DEAL_ID, NICOLAS_1_CONTACT_ID), (AMADORI_DEAL_ID, NICOLAS_2_CONTACT_ID)])
    # print(f"Deals -> Contacts Association Created: {deal_assoc_created}")

    # TESTED: Batch Create Associations (Contacts -> Companies, type 1)
    # print("\n--- Testing Batch Create Associations (Contacts -> Companies) ---")
    # company_assoc_created = client.createContactsAssociatedCompaniesBatch([(NICOLAS_1_CONTACT_ID, PZ_COMPANY_ID), (NICOLAS_2_CONTACT_ID, PZ_COMPANY_ID)])
    # print(f"Contacts -> Companies Association Created: {company_assoc_created}")

    # TESTED: Single Object Association Read (Contact -> Companies)
    # print("\n--- Testing Single Object Associations Read (Contact -> Companies) ---")
    # associated_companies = client.getContactAssociatedCompanies(NICOLAS_1_CONTACT_ID)
    # pretty_print("Contact -> Companies IDs", associated_companies)
        


if __name__ == "__main__":
    main()
