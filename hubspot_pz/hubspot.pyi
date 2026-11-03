from typing import Any

class HubspotPZ:
    def __init__(self, token: str) -> None:
        """Initialize the HubSpot API client.

        :param token: HubSpot private access token (Bearer token).
        """
    # Properties
    def getContactPropertyInfo(self, property_name: str) -> dict[str, Any] | None:
        """Retrieve metadata and schema definition for a contact property.

        :param property_name: Internal name of the contact property.
        :return: Property definition metadata dictionary, or None on error.
        """

    def getCompanyPropertyInfo(self, property_name: str) -> dict[str, Any] | None:
        """Retrieve metadata and schema definition for a company property.

        :param property_name: Internal name of the company property.
        :return: Property definition metadata dictionary, or None on error.
        """
    # All Objects
    def getAllContacts(
        self, properties_names: list[str]
    ) -> list[dict[str, Any]] | None:
        """Retrieve all contacts with the specified properties and associated companies.

        Handles pagination automatically.

        :param properties_names: List of property names to retrieve for each contact.
        :return: List of contact dictionaries (including 'id', 'associations', and properties), or None on error.
        """

    def getAllCompanies(
        self, properties_names: list[str]
    ) -> list[dict[str, Any]] | None:
        """Retrieve all companies with the specified properties and associated contacts.

        Handles pagination automatically.

        :param properties_names: List of property names to retrieve for each company.
        :return: List of company dictionaries (including 'id', 'associations', and properties), or None on error.
        """

    def getAllDeals(self, properties_names: list[str]) -> list[dict[str, Any]] | None:
        """Retrieve all deals with the specified properties and associated contacts and companies.

        Handles pagination automatically.

        :param properties_names: List of property names to retrieve for each deal.
        :return: List of deal dictionaries (including 'id', 'associations', and properties), or None on error.
        """
    # Single Objects
    def createContact(self, properties: dict[str, str]) -> str | None:
        """Create a new contact on HubSpot.

        :param properties: Dictionary of contact properties to set.
        :return: ID of the created contact, or None on error.
        """

    def createCompany(self, properties: dict[str, str]) -> str | None:
        """Create a new company on HubSpot.

        :param properties: Dictionary of company properties to set.
        :return: ID of the created company, or None on error.
        """

    def archiveContact(self, contact_id: str) -> bool:
        """Archive (delete) a contact by ID.

        :param contact_id: HubSpot contact record ID.
        :return: True if archived successfully, False otherwise.
        """

    def archiveCompany(self, company_id: str) -> bool:
        """Archive (delete) a company by ID.

        :param company_id: HubSpot company record ID.
        :return: True if archived successfully, False otherwise.
        """

    def updateContact(self, contact_id: str, properties: dict[str, str]) -> bool:
        """Update properties of an existing contact.

        :param contact_id: HubSpot contact record ID.
        :param properties: Dictionary of properties to update.
        :return: True if updated successfully, False otherwise.
        """

    def updateCompany(self, company_id: str, properties: dict[str, str]) -> bool:
        """Update properties of an existing company.

        :param company_id: HubSpot company record ID.
        :param properties: Dictionary of properties to update.
        :return: True if updated successfully, False otherwise.
        """

    def getContact(
        self, contact_id: str, properties_names: list[str] | None = ...
    ) -> dict[str, Any] | None:
        """Retrieve a single contact by ID along with associated companies.

        :param contact_id: HubSpot contact record ID.
        :param properties_names: List of property names to retrieve.
        :return: Dictionary of contact properties, ID, and associations, or None on error.
        """

    def getContactByEmail(
        self, contact_email: str, properties_names: list[str] | None = ...
    ) -> dict[str, Any] | None:
        """Retrieve a single contact by email address along with associated companies.

        :param contact_email: Email address of the contact.
        :param properties_names: List of property names to retrieve.
        :return: Dictionary of contact properties, ID, and associations, or None on error.
        """

    def getCompany(
        self, company_id: str, properties_names: list[str] | None = ...
    ) -> dict[str, Any] | None:
        """Retrieve a single company by ID along with associated contacts.

        :param company_id: HubSpot company record ID.
        :param properties_names: List of property names to retrieve.
        :return: Dictionary of company properties, ID, and associations, or None on error.
        """

    def createAgentDeal(self, properties: dict[str, str]) -> str | None:
        """Create a new deal in the Agent pipeline (pipeline ID: '2405411057').

        :param properties: Dictionary of deal properties.
        :return: ID of the created deal, or None on error.
        """

    def createContactDeal(self, properties: dict[str, str]) -> str | None:
        """Create a new deal in the Contact pipeline (pipeline ID: '59157733').

        :param properties: Dictionary of deal properties.
        :return: ID of the created deal, or None on error.
        """

    def getPipelineInfo(
        self, object_type: str, pipeline_id: str
    ) -> dict[str, Any] | None:
        """Retrieve pipeline definition and stage metadata for an object type and pipeline ID.

        :param object_type: CRM object type (e.g. 'deals').
        :param pipeline_id: Pipeline ID.
        :return: Pipeline metadata dictionary, or None on error.
        """
    # Objects Batch
    def createContactBatch(
        self, properties_list: list[dict[str, str]]
    ) -> list[str] | None:
        """Batch create multiple contacts in chunks of up to 100.

        :param properties_list: List of property dictionaries for each contact to create.
        :return: List of created contact IDs, or None on error.
        """

    def createCompanyBatch(
        self, properties_list: list[dict[str, str]]
    ) -> list[str] | None:
        """Batch create multiple companies in chunks of up to 100.

        :param properties_list: List of property dictionaries for each company to create.
        :return: List of created company IDs, or None on error.
        """

    def archiveContactBatch(self, id_list: list[str]) -> bool:
        """Batch archive multiple contacts by ID in chunks of up to 100.

        :param id_list: List of contact IDs to archive.
        :return: True if all batches succeeded, False otherwise.
        """

    def archiveCompanyBatch(self, id_list: list[str]) -> bool:
        """Batch archive multiple companies by ID in chunks of up to 100.

        :param id_list: List of company IDs to archive.
        :return: True if all batches succeeded, False otherwise.
        """

    def updateContactBatch(
        self, id_to_properties_list: dict[str, dict[str, str]]
    ) -> bool:
        """Batch update multiple contacts in chunks of up to 100.

        :param id_to_properties_list: Dictionary mapping contact IDs to property updates.
        :return: True if all batches succeeded, False otherwise.
        """

    def updateCompanyBatch(
        self, id_to_properties_list: dict[str, dict[str, str]]
    ) -> bool:
        """Batch update multiple companies in chunks of up to 100.

        :param id_to_properties_list: Dictionary mapping company IDs to property updates.
        :return: True if all batches succeeded, False otherwise.
        """

    def getContactBatch(
        self, id_list: list[str], properties_names: list[str]
    ) -> list[dict[str, Any]] | None:
        """Batch retrieve multiple contacts by IDs with specified properties.

        :param id_list: List of contact IDs to retrieve.
        :param properties_names: List of property names to fetch.
        :return: List of contact dictionaries with requested properties and 'id', or None on error.
        """

    def getCompanyBatch(
        self, id_list: list[str], properties_names: list[str]
    ) -> list[dict[str, Any]] | None:
        """Batch retrieve multiple companies by IDs with specified properties.

        :param id_list: List of company IDs to retrieve.
        :param properties_names: List of property names to fetch.
        :return: List of company dictionaries with requested properties and 'id', or None on error.
        """
    # Lists
    def getListMembersIds(
        self,
        list_id: str,
        accumulated_ids: list[str] | None = ...,
        after: str | None = ...,
    ) -> list[str] | None:
        """Retrieve record IDs of all members in a HubSpot list with automatic pagination.

        :param list_id: ID of the HubSpot list.
        :param accumulated_ids: Accumulated IDs during recursive pagination calls.
        :param after: Pagination cursor.
        :return: List of member record IDs, or None on error.
        """

    def getAgentsListMembersIds(self) -> list[str] | None:
        """Retrieve all contact IDs belonging to the default agents list (ID: 67).

        :return: List of agent contact IDs, or None on error.
        """
    # Associations
    def getContactAssociatedCompanies(self, contact_id: str) -> list[str] | None:
        """Retrieve IDs of companies associated with a given contact.

        :param contact_id: HubSpot contact record ID.
        :return: List of associated company IDs, or None on error.
        """

    def getCompanyAssociatedContacts(self, company_id: str) -> list[str] | None:
        """Retrieve IDs of contacts associated with a given company.

        :param company_id: HubSpot company record ID.
        :return: List of associated contact IDs, or None on error.
        """
    # Associations Batch
    def getContactsAssociatedCompaniesBatch(
        self, contacts_ids: list[str]
    ) -> dict[str, list[str]] | None:
        """Batch retrieve associated company IDs for multiple contact IDs.

        :param contacts_ids: List of contact record IDs.
        :return: Mapping of contact ID to list of associated company IDs, or None on error.
        """

    def getCompaniesAssociatedContactsBatch(
        self, companies_ids: list[str]
    ) -> dict[str, list[str]] | None:
        """Batch retrieve associated contact IDs for multiple company IDs.

        :param companies_ids: List of company record IDs.
        :return: Mapping of company ID to list of associated contact IDs, or None on error.
        """

    def getContactsAssociatedContactsBatch(
        self, contacts_ids: list[str]
    ) -> dict[str, list[str]] | None:
        """Batch retrieve associated contact IDs for multiple contact IDs.

        :param contacts_ids: List of contact record IDs.
        :return: Mapping of contact ID to list of associated contact IDs, or None on error.
        """

    def createContactsAssociatedCompaniesBatch(
        self, associations: list[tuple[str, str]]
    ) -> bool:
        """Batch create associations between contacts and companies (association type ID: 1).

        :param associations: List of (contact_id, company_id) tuples.
        :return: True if successful, False otherwise.
        """

    def archiveContactsAssociatedCompaniesBatch(
        self, associations: list[tuple[str, str]]
    ) -> bool:
        """Batch archive (delete) associations between contacts and companies.

        :param associations: List of (contact_id, company_id) tuples.
        :return: True if successful, False otherwise.
        """

    def createContactsAssociatedContactsBatch(
        self, associations: list[tuple[str, str]]
    ) -> bool:
        """Batch create associations between contacts and other contacts (association type ID: 449).

        :param associations: List of (contact_id_from, contact_id_to) tuples.
        :return: True if successful, False otherwise.
        """

    def createContactsAssociatedDealsBatch(
        self, associations: list[tuple[str, str]]
    ) -> bool:
        """Batch create associations between deals and contacts (association type ID: 3).

        :param associations: List of (deal_id, contact_id) tuples.
        :return: True if successful, False otherwise.
        """
    # Actions
    def mergeCompanies(self, main_company_id: str, company_to_merge_id: str) -> bool:
        """Merge two company records on HubSpot.

        :param main_company_id: ID of the primary company record to keep.
        :param company_to_merge_id: ID of the company record to merge into the primary record.
        :return: True if successfully merged, False otherwise.
        """

    def mergeContacts(self, main_contact_id: str, contact_to_merge_id: str) -> bool:
        """Merge two contact records on HubSpot.

        :param main_contact_id: ID of the primary contact record to keep.
        :param contact_to_merge_id: ID of the contact record to merge into the primary record.
        :return: True if successfully merged, False otherwise.
        """
    # Files
    def get_file_signed_url(self, file_id: str) -> dict[str, Any] | None:
        """Retrieve the signed download URL information for a HubSpot file.

        :param file_id: HubSpot file record ID.
        :return: File metadata dictionary containing signed URL, or None on error.
        """
