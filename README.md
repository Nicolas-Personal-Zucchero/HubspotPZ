# HubspotPZ

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-1.0.8-green.svg)](pyproject.toml)
[![Type Checked](https://img.shields.io/badge/types-py.typed-informational.svg)](hubspot_pz/py.typed)
[![HubSpot API](https://img.shields.io/badge/HubSpot_API-v3_%7C_2026--09-orange.svg)](https://developers.hubspot.com/)

**HubspotPZ** is a Python client library designed for clean, robust interaction with the HubSpot CRM API. Tailored for Personal Zucchero workflows, it provides high-level abstractions over HubSpot's CRM v3 and the modern `2026-09` Associations API.

Key highlights include **automatic cursor pagination**, **transparent 100-item batch chunking**, **PEP 561 static typing stubs**, pipeline helpers, and utilities for contacts, companies, deals, lists, associations, record merging, and signed file URLs.

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Authentication & Setup](#authentication--setup)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
  - [Contacts](#contacts)
  - [Companies](#companies)
  - [Deals & Pipelines](#deals--pipelines)
  - [Batch Operations](#batch-operations)
  - [Associations (2026-09 API)](#associations-2026-09-api)
  - [Lists](#lists)
  - [Record Merging](#record-merging)
  - [Files & Signed URLs](#files--signed-urls)
  - [Property Metadata](#property-metadata)
- [Preset Properties & Configuration Constants](#preset-properties--configuration-constants)
- [Type Hinting & Static Analysis](#type-hinting--static-analysis)
- [Development & Playground](#development--playground)
- [Project Architecture](#project-architecture)
- [Author & License](#author--license)

---

## Features

- **Modern HubSpot API Versions**: Built on HubSpot CRM API v3 and updated to the `2026-09` Associations endpoints.
- **Transparent Pagination**: Methods such as `getAllContacts`, `getAllCompanies`, `getAllDeals`, and `getListMembersIds` automatically follow pagination cursors (`after`), retrieving complete datasets without manual looping.
- **Built-in Batch Chunking**: Automatically breaks large collections into 100-item chunks (`_MAX_BATCH_SIZE = 100`) as required by HubSpot's batch endpoints, recursing until all items are processed.
- **Strict Typing & Stubs**: Fully typed with PEP 561 compliance (`py.typed`) and detailed `.pyi` interface stubs for first-class autocomplete and type safety in VS Code, PyCharm, and `mypy`.
- **Personal Zucchero Presets**: Out-of-the-box support for Mexal ERP fields, custom deal pipelines (Agent & Contact pipelines), and agent membership lists.
- **Lightweight**: Minimal surface area powered by `requests`.

---

## Installation

### From Source

Clone the repository and install in editable mode:

```bash
git clone https://github.com/personalzucchero/HubspotPZ.git
cd HubspotPZ
pip install -e .
```

### Dependencies

Ensure `requests` is installed in your Python environment:

```bash
pip install requests
```

---

## Authentication & Setup

`HubspotPZ` authenticates using a **HubSpot Private App Access Token** (Bearer token).

1. In HubSpot, navigate to **Settings > Integrations > Private Apps**.
2. Create a Private App with the required CRM scopes:
   - `crm.objects.contacts.read`, `crm.objects.contacts.write`
   - `crm.objects.companies.read`, `crm.objects.companies.write`
   - `crm.objects.deals.read`, `crm.objects.deals.write`
   - `crm.lists.read`
   - `files`
3. Copy your access token.
4. For local testing, copy `template.env` to `.env`:
   ```bash
   cp template.env .env
   ```
   Add your token:
   ```env
   HUBSPOT_TOKEN=pat-na1-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   ```

---

## Quick Start

```python
import logging
import os
from hubspot_pz import HubspotPZ

# Initialize the client (optional logger)
token = os.getenv("HUBSPOT_TOKEN", "your_token_here")
logger = logging.getLogger("my_app")
client = HubspotPZ(token, logger=logger)

# Retrieve contacts with requested properties
contacts = client.getAllContacts(["email", "firstname", "lastname", "phone"])

if contacts:
    for contact in contacts[:5]:
        print(f"[{contact.get('id')}] {contact.get('firstname')} {contact.get('lastname')} - {contact.get('email')}")

# Close the session when done (or use context manager: `with HubspotPZ(token) as client:`)
client.close()
```

---

## API Reference

### Contacts

#### Retrieve All Contacts (Paginated)
Fetches all contacts in your portal with the specified properties. Includes associated company IDs automatically.
```python
contacts = client.getAllContacts(["email", "firstname", "lastname", "phone", "city"])
```

#### Get a Single Contact
```python
# By contact record ID
contact = client.getContact("311400202443", ["email", "firstname", "lastname"])

# By contact email address
contact = client.getContactByEmail("mario.rossi@example.com", ["email", "firstname", "lastname"])
```

#### Create, Update, and Archive Contacts
```python
# Create contact (returns the new contact record ID or None)
contact_id = client.createContact({
    "email": "mario.rossi@example.com",
    "firstname": "Mario",
    "lastname": "Rossi",
    "phone": "+390123456789"
})

# Update contact properties (returns True if successful)
success = client.updateContact(contact_id, {
    "phone": "+390987654321"
})

# Archive (soft-delete) contact (returns True if successful)
archived = client.archiveContact(contact_id)
```

---

### Companies

#### Retrieve All Companies (Paginated)
Fetches all companies in your portal with the specified properties. Includes associated contact IDs automatically.
```python
companies = client.getAllCompanies(["name", "domain", "city", "partita_iva"])
```

#### Get a Single Company
```python
company = client.getCompany("6751536075", ["name", "partita_iva", "city", "domain"])
```

#### Create, Update, and Archive Companies
```python
# Create company (returns record ID or None)
company_id = client.createCompany({
    "name": "Acme S.r.l.",
    "domain": "acme.it",
    "partita_iva": "IT12345678901",
    "city": "Bologna"
})

# Update company properties
success = client.updateCompany(company_id, {
    "city": "Milano"
})

# Archive company
archived = client.archiveCompany(company_id)
```

---

### Deals & Pipelines

`HubspotPZ` includes built-in methods for Personal Zucchero's custom sales pipelines:

- **Contact Pipeline**: ID `59157733`
- **Agent Pipeline**: ID `2405411057`

#### Retrieve All Deals (Paginated)
Fetches all deals, including associated contacts and companies:
```python
deals = client.getAllDeals(["dealname", "dealstage", "amount", "closedate"])
```

#### Create Deals in Specific Pipelines
```python
# Create deal in the Contact Pipeline (59157733)
contact_deal_id = client.createContactDeal({
    "dealname": "Fornitura Zucchero Personalizzato - Acme",
    "dealstage": "appointmentscheduled",
    "amount": "12500",
    "nome_cliente": "Acme S.r.l."
})

# Create deal in the Agent Pipeline (2405411057)
agent_deal_id = client.createAgentDeal({
    "dealname": "Contratto Agente - Rossi",
    "dealstage": "contractsent",
    "motivo_rifiuto": ""
})
```

#### Get Pipeline Metadata
Inspect available stages and pipeline definitions:
```python
pipeline_data = client.getPipelineInfo("deals", "59157733")
```

---

### Batch Operations

HubSpot restricts batch calls to **100 objects per request**. All batch methods in `HubspotPZ` handle slicing, recursive execution, and aggregation transparently.

#### Batch Create
```python
# Batch create contacts (returns list of created IDs)
contact_ids = client.createContactBatch([
    {"email": "user1@example.com", "firstname": "User", "lastname": "One"},
    {"email": "user2@example.com", "firstname": "User", "lastname": "Two"}
])

# Batch create companies
company_ids = client.createCompanyBatch([
    {"name": "Company Alpha", "city": "Roma"},
    {"name": "Company Beta", "city": "Torino"}
])
```

#### Batch Read
```python
contacts = client.getContactBatch(
    id_list=["311400202443", "464026798284"],
    properties_names=["email", "firstname", "lastname"]
)

companies = client.getCompanyBatch(
    id_list=["6751536075"],
    properties_names=["name", "partita_iva"]
)
```

#### Batch Update
```python
# Maps object ID -> dictionary of properties to update
success = client.updateContactBatch({
    "311400202443": {"firstname": "Mario"},
    "464026798284": {"firstname": "Luigi"}
})

success = client.updateCompanyBatch({
    "6751536075": {"city": "Modena"}
})
```

#### Batch Archive
```python
client.archiveContactBatch(["311400202443", "464026798284"])
client.archiveCompanyBatch(["6751536075"])
```

---

### Associations (2026-09 API)

Association methods utilize HubSpot's `2026-09` endpoints and support standard HubSpot association types:

- **Contact to Company**: Type ID `1`
- **Contact to Contact**: Type ID `449`
- **Deal to Contact**: Type ID `3`

#### Read Associations
```python
# Single record associations
company_ids = client.getContactAssociatedCompanies("311400202443")
contact_ids = client.getCompanyAssociatedContacts("6751536075")

# Batch read associations (returns dict: { from_id: [to_ids...] })
contacts_to_companies = client.getContactsAssociatedCompaniesBatch(["311400202443", "464026798284"])
companies_to_contacts = client.getCompaniesAssociatedContactsBatch(["6751536075"])
contacts_to_contacts   = client.getContactsAssociatedContactsBatch(["311400202443"])
```

#### Create Associations in Batch
```python
# Contacts -> Companies (Type ID 1)
client.createContactsAssociatedCompaniesBatch([
    ("311400202443", "6751536075"),
    ("464026798284", "6751536075")
])

# Contacts -> Contacts (Type ID 449)
client.createContactsAssociatedContactsBatch([
    ("311400202443", "464026798284")
])

# Deals -> Contacts (Type ID 3)
client.createContactsAssociatedDealsBatch([
    ("523248658633", "311400202443")
])
```

#### Archive Associations in Batch
```python
client.archiveContactsAssociatedCompaniesBatch([
    ("311400202443", "6751536075")
])
```

---

### Lists

Fetch member record IDs from HubSpot lists with automatic cursor pagination:

```python
# Retrieve all member record IDs from any list ID
list_member_ids = client.getListMembersIds("12345")

# Retrieve contact IDs from the default Agents list (List ID: 67)
agent_ids = client.getAgentsListMembersIds()
```

---

### Record Merging

Merge duplicate records into a designated primary record via HubSpot's merge API:

```python
# Merges company_to_merge_id into main_company_id
client.mergeCompanies(
    main_company_id="6751536075",
    company_to_merge_id="9876543210"
)

# Merges contact_to_merge_id into main_contact_id
client.mergeContacts(
    main_contact_id="311400202443",
    contact_to_merge_id="464026798284"
)
```

---

### Files & Signed URLs

Fetch a secure, time-limited signed URL to download private files stored in HubSpot's File Manager (defaults to 7 days validity, configurable via `expiration_seconds`):

```python
# Default expiration: 7 days (604800 seconds)
file_info = client.get_file_signed_url("1234567890")
if file_info:
    download_url = file_info.get("url")
    print("Signed URL:", download_url)

# Custom expiration (e.g. 24 hours)
short_file_info = client.get_file_signed_url("1234567890", expiration_seconds=86400)
```

---

### Property Metadata

Retrieve property schemas, types, options, and metadata definitions:

```python
contact_meta = client.getContactPropertyInfo("email")
company_meta = client.getCompanyPropertyInfo("partita_iva")
```

---

## Preset Properties & Configuration Constants

The library defines built-in defaults and constants for Personal Zucchero workflows:

| Constant | Value / Type | Purpose |
|---|---|---|
| `_BASE_URL` | `"https://api.hubapi.com"` | Base URL for HubSpot REST API |
| `_MAX_BATCH_SIZE` | `100` | HubSpot batch limit ceiling |
| `_CRM_API_VERSION` | `"2026-09"` | Active HubSpot CRM API version
| `_AGENT_LIST_ID` | `67` | Pre-configured Agent list ID |
| `_AGENT_CONTACTS_LIST_ID` | `64` | Agent contacts list ID |
| `_CONTACT_PIPELINE_ID` | `"59157733"` | Primary contact deal pipeline |
| `_AGENT_PIPELINE_ID` | `"2405411057"` | Agent deal pipeline |
| `_DEFAULT_CONTACT_PROPERTY_LIST` | `list[str]` | Standard contact fields (`email`, `phone`, `fonte`, etc.) |
| `_DEFAULT_COMPANY_PROPERTY_LIST` | `list[str]` | Standard company & Mexal ERP fields (`codice_mexal`, `partita_iva`, etc.) |
| `_DEFAULT_AGENT_PROPERTY_LIST` | `list[str]` | Agent contract & Mexal fields (`frequenza_liquidazione`, etc.) |
| `_DEFAULT_DEAL_PROPERTY_LIST` | `list[str]` | General deal fields (`dealname`, `dealstage`, etc.) |
| `_CONTACT_DEAL_PROPERTY_LIST` | `list[str]` | Contact pipeline specific deal fields |
| `_AGENT_DEAL_PROPERTY_LIST` | `list[str]` | Agent pipeline specific deal fields |

---

## Type Hinting & Static Analysis

`HubspotPZ` is packaged with PEP 561 compliance:
- Contains `hubspot_pz/py.typed`.
- Provides complete stub definitions in `hubspot_pz/hubspot.pyi` and `hubspot_pz/__init__.pyi`.
- Full typing support for `mypy`, `pyright`, and modern Python IDEs (VS Code Pylance, PyCharm).

To verify types with `mypy`:
```bash
pip install mypy
mypy hubspot_pz
```

---

## Development & Playground

A development script ([playground.py](playground.py)) is included to test API calls interactively without modifying production scripts.

1. Create a `.env` file from the template:
   ```bash
   cp template.env .env
   ```
2. Edit `.env` and set your `HUBSPOT_TOKEN`.
3. Run the playground:
   ```bash
   python playground.py
   ```

---

## Project Architecture

```
HubspotPZ/
├── hubspot_pz/
│   ├── __init__.py         # Package export (HubspotPZ)
│   ├── __init__.pyi        # Stubs for package exports
│   ├── hubspot.py          # Core client implementation
│   ├── hubspot.pyi         # Public interface stubs & docstrings
│   └── py.typed            # PEP 561 marker
├── playground.py           # Interactive development and testing script
├── pyproject.toml          # Packaging metadata & build system (setuptools)
├── template.env            # Environment configuration template
└── README.md               # Library documentation
```

---

## Author & License

- **Author**: Nicolas Amadori ([nicolas.amadori02@gmail.com](mailto:nicolas.amadori02@gmail.com))
- **Organization**: Personal Zucchero S.r.l.
