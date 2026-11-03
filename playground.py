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

    # =============================================================
    # MANUAL TESTS: CONTACTS & COMPANIES (MIGRATED TO 2026-09)
    # Uncomment the section you wish to test.
    # =============================================================

    # -------------------------------------------------------------
    # 1. PROPERTIES INFO (2026-09) -> TESTED
    # -------------------------------------------------------------
    # print("\n--- Testing Contact Property Info ---")
    # property_name = "firstname"
    # contact_prop = client.getContactPropertyInfo(property_name)
    # pretty_print(f"Contact '{property_name}' Property Info", contact_prop)

    # print("\n--- Testing Company Property Info ---")
    # property_name = "name"
    # company_prop = client.getCompanyPropertyInfo(property_name)
    # pretty_print(f"Company '{property_name}' Property Info", company_prop)

    # -------------------------------------------------------------
    # 2. READ ALL OBJECTS (2026-09, Automatic Pagination) -> TESTED
    # -------------------------------------------------------------
    # print("\n--- Fetching All Contacts (first 3) ---")
    # contacts = client.getAllContacts(["email", "firstname", "lastname"])
    # print("Total Contacts:", len(contacts) if contacts else 0)
    # pretty_print("Contacts (first 3)", contacts[:3] if contacts else [])

    # print("\n--- Fetching All Companies (first 3) ---")
    # companies = client.getAllCompanies(["name", "domain", "city"])
    # print("Total Companies:", len(companies) if companies else 0)
    # pretty_print("Companies (first 3)", companies[:3] if companies else [])

    # -------------------------------------------------------------
    # 3. SINGLE OBJECT READ (2026-09) -> TESTED
    # -------------------------------------------------------------
    # print("\n--- Testing Get Contact by ID ---")
    # contact = client.getContact(NICOLAS_1_CONTACT_ID, ["email", "firstname", "lastname"])
    # pretty_print("Contact by ID", contact)

    # print("\n--- Testing Get Contact by Email ---")
    # contact_by_email = client.getContactByEmail("nicolas.amadori02@gmail.com", ["email", "firstname", "lastname"])
    # pretty_print("Contact by Email", contact_by_email)

    # print("\n--- Testing Get Company by ID ---")
    # company = client.getCompany(PZ_COMPANY_ID, ["name", "city", "partita_iva"])
    # pretty_print("Company by ID", company)

    # -------------------------------------------------------------
    # 4. SINGLE CONTACT LIFECYCLE (2026-09: Create -> Update -> Archive) -> TESTED
    # -------------------------------------------------------------
    # print("\n--- Testing Contact Lifecycle (Create -> Update -> Archive) ---")
    # test_contact_id = client.createContact({
    #     "email": "test_playground_2026_09@example.com",
    #     "firstname": "Playground",
    #     "lastname": "Tester"
    # })
    # print(f"Created Contact ID: {test_contact_id}")
    
    # if test_contact_id:
    #     updated = client.updateContact(test_contact_id, {"firstname": "PlaygroundUpdated"})
    #     print(f"Contact Updated: {updated}")
        
    #     fetched = client.getContact(test_contact_id, ["email", "firstname", "lastname"])
    #     pretty_print("Fetched Updated Contact", fetched)
    
    #     archived = client.archiveContact(test_contact_id)
    #     print(f"Contact Archived: {archived}")

    # -------------------------------------------------------------
    # 5. SINGLE COMPANY LIFECYCLE (2026-09: Create -> Update -> Archive) -> TESTED
    # -------------------------------------------------------------
    # print("\n--- Testing Company Lifecycle (Create -> Update -> Archive) ---")
    # test_company_id = client.createCompany({
    #     "name": "Playground Test Srl",
    #     "city": "Bologna"
    # })
    # print(f"Created Company ID: {test_company_id}")
    
    # if test_company_id:
    #     updated = client.updateCompany(test_company_id, {"city": "Modena"})
    #     print(f"Company Updated: {updated}")
        
    #     fetched = client.getCompany(test_company_id, ["name", "city"])
    #     pretty_print("Fetched Updated Company", fetched)
    
    #     archived = client.archiveCompany(test_company_id)
    #     print(f"Company Archived: {archived}")

    # -------------------------------------------------------------
    # 6. BATCH OPERATIONS: CONTACTS (2026-09: Create -> Read -> Update -> Archive) -> TESTED
    # -------------------------------------------------------------
    # print("\n--- Testing Contacts Batch Operations ---")
    # batch_contact_ids = client.createContactBatch([
    #     {"email": "batch_test_1@example.com", "firstname": "Batch1", "lastname": "Test"},
    #     {"email": "batch_test_2@example.com", "firstname": "Batch2", "lastname": "Test"}
    # ])
    # print(f"Batch Contacts Created IDs: {batch_contact_ids}")
    
    # if batch_contact_ids:
    #     batch_read = client.getContactBatch(batch_contact_ids, ["email", "firstname", "lastname"])
    #     pretty_print("Batch Read Contacts", batch_read)
    
    #     updates = {cid: {"firstname": f"BatchUpdated_{i}"} for i, cid in enumerate(batch_contact_ids)}
    #     batch_updated = client.updateContactBatch(updates)
    #     print(f"Batch Update Contacts Success: {batch_updated}")

    #     batch_read = client.getContactBatch(batch_contact_ids, ["email", "firstname", "lastname"])
    #     pretty_print("Batch Read Updated Contacts", batch_read)
    
    #     batch_archived = client.archiveContactBatch(batch_contact_ids)
    #     print(f"Batch Archive Contacts Success: {batch_archived}")

    # -------------------------------------------------------------
    # 7. BATCH OPERATIONS: COMPANIES (2026-09: Create -> Read -> Update -> Archive) -> TESTED
    # -------------------------------------------------------------
    # print("\n--- Testing Companies Batch Operations ---")
    # batch_company_ids = client.createCompanyBatch([
    #     {"name": "Batch Company Alpha", "city": "Milano"},
    #     {"name": "Batch Company Beta", "city": "Torino"}
    # ])
    # print(f"Batch Companies Created IDs: {batch_company_ids}")
    
    # if batch_company_ids:
    #     batch_read_companies = client.getCompanyBatch(batch_company_ids, ["name", "city"])
    #     pretty_print("Batch Read Companies", batch_read_companies)
    
    #     comp_updates = {cid: {"city": "Firenze"} for cid in batch_company_ids}
    #     batch_comp_updated = client.updateCompanyBatch(comp_updates)
    #     print(f"Batch Update Companies Success: {batch_comp_updated}")

    #     batch_read_companies = client.getCompanyBatch(batch_company_ids, ["name", "city"])
    #     pretty_print("Batch Read Updated Companies", batch_read_companies)
    
    #     batch_comp_archived = client.archiveCompanyBatch(batch_company_ids)
    #     print(f"Batch Archive Companies Success: {batch_comp_archived}")

    # -------------------------------------------------------------
    # 8. MERGE OPERATIONS (2026-09) -> TESTED
    # CAUTION: Merging records is irreversible in HubSpot.
    # -------------------------------------------------------------
    # print("\n--- Testing Merge Contacts ---")
    # merge_contact_ids = client.createContactBatch([
    #     {"email": "merge_test_1@example.com", "firstname": "Firstname1", "lastname": "Lastname1"},
    #     {"email": "merge_test_2@example.com", "firstname": "Firstname2", "lastname": "Lastname2"}
    # ])
    # print(f"Batch Contacts Created IDs: {merge_contact_ids}")
    # merged_contact = client.mergeContacts(main_contact_id=merge_contact_ids[0], contact_to_merge_id=merge_contact_ids[1])
    # print(f"Contacts Merge Result: {merged_contact}")

    # -------------------------------------------------------------
    # 9. ASSOCIATIONS (2026-09)
    # -------------------------------------------------------------

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
