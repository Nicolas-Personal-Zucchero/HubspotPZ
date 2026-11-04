from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Any, ClassVar

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


class HubspotPZ:
    _BASE_URL = "https://api.hubapi.com"
    _MAX_BATCH_SIZE = 100
    _CRM_API_VERSION = "2026-09"

    _AGENT_LIST_ID = 67
    _AGENT_CONTACTS_LIST_ID = 64

    _DEFAULT_CONTACT_PROPERTY_LIST: ClassVar[list[str]] = ["email","firstname","lastname","phone","mobilephone","numero_referente","hs_additional_emails", "fonte"]
    _DEFAULT_AGENT_PROPERTY_LIST: ClassVar[list[str]] = ["codice_mexal", "nome_mexal", "frequenza_liquidazione", "ruolo", "address", "cap", "city", "provincia", "data_inizio_contratto", "data_fine_contratto", "tipologia_contratto", "regione", "province", "note_zona", "dettagli_particolare"]
    _DEFAULT_COMPANY_PROPERTY_LIST: ClassVar[list[str]] = ['codice_mexal','name','alias','partita_iva','categoria_mexal','segmento','city','provincia','region','paese','lingua','data_ultima_fattura','hs_country_code','stagionalita__cloned_','precancellata']
    _DEFAULT_DEAL_PROPERTY_LIST: ClassVar[list[str]] = ["dealname", "dealstage", "nome_cliente", "preventivo_confermato", "bozza_confermata"]

    _CONTACT_PIPELINE_ID = "59157733"
    _CONTACT_DEAL_PROPERTY_LIST: ClassVar[list[str]] = ["pipeline", "dealname", "dealstage", "createdate", "closedate", "tipologia_prodotto_2", "rivenditore", "nome_cliente", "bozza_confermata", "amount", "motivo_rifiuto", "note", "pretrattativa", "fonte"]

    _AGENT_PIPELINE_ID = "2405411057"
    _AGENT_DEAL_PROPERTY_LIST: ClassVar[list[str]] = ["pipeline", "dealname", "dealstage", "createdate", "closedate", "motivo_rifiuto", "note"]

    def __init__(self, token: str, logger: logging.Logger | None = None) -> None:
        self._session: requests.Session = requests.Session()
        self._setup_session_retries()
        self._initialize_hubspot_headers(token)
        self._logger: logging.Logger = logger if logger is not None else logging.getLogger("hubspot_pz")

    def _setup_session_retries(self) -> None:
        """Configure automatic retry behavior with exponential backoff for rate limits and transient errors."""
        retries = Retry(
            total=3,
            backoff_factor=1.0,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=None,
            raise_on_status=False,
            respect_retry_after_header=True
        )
        adapter = HTTPAdapter(max_retries=retries)
        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)

    def _initialize_hubspot_headers(self, token: str) -> None:
        self._headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        }
        self._session.headers.update(self._headers)

    def close(self) -> None:
        """Close the underlying requests.Session and release connection pool resources."""
        self._session.close()

    def __enter__(self) -> HubspotPZ:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def _request(
        self,
        method: str,
        endpoint: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
        expected_status: int | tuple[int, ...] = 200,
        error_context: str = "an operation on HubSpot"
    ) -> requests.Response | None:
        """
        Internal helper to execute HTTP requests with standardized headers and error reporting.

        :param method: HTTP method ('GET', 'POST', 'PATCH', 'DELETE', etc.)
        :param endpoint: URL endpoint (relative path or full URL)
        :param params: Optional URL query parameters
        :param json: Optional JSON serializable body payload
        :param expected_status: Accepted HTTP status code(s) for success (e.g. 200, 201, or (200, 201))
        :param error_context: Description for the error message if the request fails
        :return: requests.Response object if status matches expected, None on failure
        """
        url = endpoint if endpoint.startswith("http") else f"{self._BASE_URL}{endpoint}"
        valid_statuses = (expected_status,) if isinstance(expected_status, int) else expected_status

        try:
            r = self._session.request(
                method=method.upper(),
                url=url,
                headers=self._headers,
                params=params,
                json=json
            )
        except requests.RequestException as e:
            self._logger.error(f"Network error during {error_context}: {e}")
            return None

        if r.status_code not in valid_statuses:
            self._logger.error(f"Error {r.status_code} during {error_context}.\nResponse Body: {r.text}")
            return None

        return r

    def _convert_date(self, time_millisecond: str) -> date | None:
        if time_millisecond == "":
            return None
        millisecond = int(time_millisecond)
        timestamp = millisecond / 1000  # Convert milliseconds to seconds by dividing by 1000
        data = datetime.fromtimestamp(timestamp)
        return data.date()

    ##########Properties############################################

    def _get_property_info(self, object_type: str, property_name: str) -> Any:
        endpoint = f'/crm/properties/{self._CRM_API_VERSION}/{object_type}/{property_name}'
        r = self._request("GET", endpoint, error_context="the retrieval of a property information on HubSpot")
        return r.json() if r is not None else None

    def getContactPropertyInfo(self, property_name: str) -> Any:
        return self._get_property_info("contacts", property_name)
    
    def getCompanyPropertyInfo(self, property_name: str) -> Any:
        return self._get_property_info("companies", property_name)
    
    ##########All Objects############################################

    #Tested and working
    def _get_all_objects(
        self,
        object_type: str,
        properties_names: list[str],
        associations_objects: list[str] | None = None
    ) -> list[dict[str, str]] | None:
        """
        Generic function to retrieve all objects of a given type (contacts, companies, etc.) from HubSpot.
        API Version 2026-09.
        
        :param object_type: Type of objects (e.g. 'contacts' or 'companies')
        :param properties_names: List of property names to retrieve for each object
        :param associations_objects: Associated objects to retrieve
        :return: List of requested objects, or None on error
        """
        accumulated_objects: list[dict[str, str]] = []

        endpoint = f'/crm/objects/{self._CRM_API_VERSION}/{object_type}'
        current_after: str | None = None

        while True:
            params: dict[str, Any] = {"limit": 100}
            if current_after:
                params["after"] = current_after
            if properties_names:
                params["properties"] = properties_names
            if associations_objects is not None:
                params["associations"] = ",".join(associations_objects)

            r = self._request("GET", endpoint, params=params, error_context=f"the retrieval of all {object_type}")
            if r is None:
                return None

            for result in r.json().get("results", []):
                retrieved_properties = {prop: result.get("properties", {}).get(prop) or None for prop in properties_names}
                retrieved_properties["id"] = result.get("id")
                retrieved_properties = dict(sorted(retrieved_properties.items()))
                retrieved_properties["associations"] = result.get("associations", None)
                accumulated_objects.append(retrieved_properties)

            next_page = r.json().get("paging", {}).get("next", {}).get("after")
            if not next_page:
                break
            current_after = next_page

        return accumulated_objects
    
    def getAllContacts(self, properties_names: list[str]) -> list[dict[str, str]]:
        return self._get_all_objects("contacts", properties_names, associations_objects=["companies"])
    
    def getAllCompanies(self, properties_names: list[str]) -> list[dict[str, str]]:
        return self._get_all_objects("companies", properties_names, associations_objects=["contacts"])
    
    def getAllDeals(self, properties_names: list[str]) -> list[dict[str, str]]:
        return self._get_all_objects("0-3", properties_names, associations_objects=["contacts", "companies"])

    ##########Single Objects############################################
    
    #Tested and working
    def _create_object(
        self,
        object_type: str,
        properties: dict[str, str]
    ) -> str | None:
        """
        Generic function to create an object (contact, company, etc.) on HubSpot.
        API Version 2026-09.
        
        :param object_type: Type of object (e.g. 'contacts' or 'companies')
        :param properties: Properties of the object to create
        :return: ID of the created object, or None on error
        """
        endpoint = f'/crm/objects/{self._CRM_API_VERSION}/{object_type}'
        r = self._request(
            "POST",
            endpoint,
            json={"properties": properties},
            expected_status=201,
            error_context="the creation of an object on HubSpot"
        )
        if r is None:
            return None
        return r.json().get("id", None)  # Use .get to avoid KeyError if ID does not exist

    #Tested and working
    def _archive_object(
        self,
        object_type: str,
        object_id: str
    ) -> bool:
        """
        Generic function to archive an object (contact, company, etc.) on HubSpot.
        API Version 2026-09.
        
        :param object_type: Type of object (e.g. 'contacts' or 'companies')
        :param object_id: ID of the object to archive
        :return: True if successfully archived, False otherwise
        """
        endpoint = f'/crm/objects/{self._CRM_API_VERSION}/{object_type}/{object_id}'
        r = self._request(
            "DELETE",
            endpoint,
            expected_status=204,
            error_context="the archivation of an object on HubSpot"
        )
        return r is not None
    
    #Tested and working
    def _update_object(
        self,
        object_type: str,
        object_id: str,
        properties: dict[str, str]
    ) -> bool:
        """
        Generic function to update an object (contact, company, etc.) on HubSpot.
        API Version 2026-09.
        
        :param object_type: Type of object (e.g. 'contacts' or 'companies')
        :param object_id: ID of the object to update
        :param properties: Properties of the object to update
        :return: True if successfully updated, False otherwise
        """
        endpoint = f'/crm/objects/{self._CRM_API_VERSION}/{object_type}/{object_id}'
        r = self._request(
            "PATCH",
            endpoint,
            json={"properties": properties},
            error_context="the update of an object on HubSpot"
        )
        return r is not None
    
    #Tested and working
    def _get_object(
        self,
        object_type: str,
        object_id: str,
        properties_names: list[str] | None = None,
        identifying_property: str = "id",
        associations_objects: list[str] | None = None,
    ) -> dict[str, str] | None:
        """
        Generic function to retrieve an object (contact, company, etc.) from HubSpot.
        API Version 2026-09.
        
        :param object_type: Type of object (e.g. 'contacts' or 'companies')
        :param object_id: ID of the object to retrieve (can be any unique field, like email, passed in identifying_property)
        :param properties_names: Properties of the object to retrieve
        :param identifying_property: Identifying property name (default 'id')
        :param associations_objects: Associated objects to retrieve
        :return: Dictionary with requested object properties, or None on error
        """
        if properties_names is None:
            properties_names = []

        params: dict[str, Any] = {}
        if identifying_property != "id":
            params["idProperty"] = identifying_property
        if properties_names:
            params["properties"] = properties_names
        if associations_objects is not None:
            params["associations"] = ",".join(associations_objects)

        endpoint = f'/crm/objects/{self._CRM_API_VERSION}/{object_type}/{object_id}'
        r = self._request(
            "GET",
            endpoint,
            params=params,
            error_context="the retrieval of an object on HubSpot"
        )
        if r is None:
            return None
        
        retrieved_properties = {prop: r.json().get("properties", {}).get(prop) or None for prop in properties_names}
        retrieved_properties["id"] = r.json().get("id")
        retrieved_properties["associations"] = r.json().get("associations", None)
        return dict(sorted(retrieved_properties.items()))

    #Tested and working
    def _search_object(
        self,
        object_type: str,
        search_params: dict[str, str],
        properties_names: list[str]
    ) -> dict[str, str] | None:
        """
        Generic function to search for an object (contact, company, etc.) on HubSpot.
        API Version 2026-09.
        
        :param object_type: Type of object (e.g. 'contacts' or 'companies')
        :param search_params: Properties and values to filter the search by
        :param properties_names: Properties of the object to retrieve
        :return: Dictionary with requested object properties, or None on error
        """
        endpoint = f'/crm/objects/{self._CRM_API_VERSION}/{object_type}/search'
        payload = {
            "properties": properties_names,
            "filterGroups": [
                {
                    "filters": [
                        {"propertyName": name, "operator": "EQ", "value": value}
                        for name, value in search_params.items()
                    ]
                }
            ]
        }
        r = self._request(
            "POST",
            endpoint,
            json=payload,
            error_context="the search of an object on HubSpot"
        )
        if r is None:
            return None
        
        output = []
        for result in r.json().get("results", []):
            retrieved_properties = {prop: (result.get("properties") or {}).get(prop) for prop in properties_names}
            retrieved_properties["id"] = result.get("id")
            output.append(retrieved_properties)
        return output
    
    #Tested and working
    def createContact(self, properties: dict[str, str]) -> str | None:
        # Mandatory legal basis for contact creation
        properties["hs_legal_basis"] = "Legitimate interest – existing customer"
        return self._create_object("contacts", properties)

    #Tested and working
    def createCompany(self, properties: dict[str, str]) -> str | None:
        return self._create_object("companies", properties)
    
    #Tested and working
    def archiveContact(self, contact_id: str) -> bool:
        return self._archive_object("contacts", contact_id)

    #Tested and working
    def archiveCompany(self, company_id: str) -> bool:
        return self._archive_object("companies", company_id)

    #Tested and working
    def updateContact(self, contact_id: str, properties: dict[str, str]) -> bool:
        return self._update_object("contacts", contact_id, properties)
    
    #Tested and working
    def updateCompany(self, company_id: str, properties: dict[str, str]) -> bool:
        return self._update_object("companies", company_id, properties)
    
    #Tested and working
    def getContact(self, contact_id: str, properties_names: list[str] | None = None) -> dict[str, str] | None:
        return self._get_object("contacts", contact_id, properties_names, associations_objects=["companies"])

    #Tested and working
    def getContactByEmail(self, contact_email: str, properties_names: list[str] | None = None) -> dict[str, str] | None:
        return self._get_object("contacts", contact_email, properties_names, "email", associations_objects=["companies"])
    
    #Tested and working
    def getCompany(self, company_id: str, properties_names: list[str] | None = None) -> dict[str, str] | None:
        return self._get_object("companies", company_id, properties_names, associations_objects=["contacts"])
    
    def createAgentDeal(self, properties: dict[str, str]) -> str | None:
        #https://app-eu1.hubspot.com/property-settings/25378285/properties?type=0-3&eschref=%2Fcontacts%2F25378285%2Fobjects%2F0-3%2Frestore&search=pip&action=edit&property=pipeline
        properties["pipeline"] = self._AGENT_PIPELINE_ID
        return self._create_object("deals", properties)
    
    def createContactDeal(self, properties: dict[str, str]) -> str | None:
        #https://app-eu1.hubspot.com/property-settings/25378285/properties?type=0-3&eschref=%2Fcontacts%2F25378285%2Fobjects%2F0-3%2Frestore&search=pip&action=edit&property=pipeline
        properties["pipeline"] = self._CONTACT_PIPELINE_ID
        return self._create_object("deals", properties)
    
    def getPipelineInfo(self, object_type: str, pipeline_id: str) -> Any:
        endpoint = f'/crm/pipelines/{self._CRM_API_VERSION}/{object_type}/{pipeline_id}'
        r = self._request("GET", endpoint, error_context="the retrieval of a pipeline information on HubSpot")
        return r.json() if r is not None else None
    
    ##########Objects Batch############################################

    def _create_object_batch(
        self,
        object_type: str,
        properties_list: list[dict[str, str]]
    ) -> list[str] | None:
        """
        Generic function to batch create objects (contacts, companies, etc.) on HubSpot.
        API Version 2026-09.
        In this implementation associations are not handled (batch creation of objects only, without relations).
        
        :param object_type: Type of object (e.g. 'contacts' or 'companies')
        :param properties_list: List of property dictionaries
        :return: List of created object IDs, or None on error
        """
        if not properties_list:
            return None

        accumulated_ids: list[str] = []

        endpoint = f'/crm/objects/{self._CRM_API_VERSION}/{object_type}/batch/create'

        for i in range(0, len(properties_list), self._MAX_BATCH_SIZE):
            batch = properties_list[i : i + self._MAX_BATCH_SIZE]
            r = self._request(
                "POST",
                endpoint,
                json={"inputs": [{"properties": properties} for properties in batch]},
                expected_status=(200, 201),
                error_context="the creation of a batch of objects on HubSpot"
            )
            if r is not None:
                results = r.json().get("results", [])
                accumulated_ids.extend([result.get("id") for result in results if result.get("id")])

        return accumulated_ids if accumulated_ids else None

    def _archive_object_batch(
        self,
        object_type: str,
        id_list: list[str]
    ) -> bool:
        """
        Generic function to batch archive objects (contacts, companies, etc.) on HubSpot.
        API Version 2026-09.
        
        :param object_type: Type of objects (e.g. 'contacts' or 'companies')
        :param id_list: List of IDs to archive
        :return: True if successfully archived, False otherwise
        """
        if not id_list:
            return True

        endpoint = f'/crm/objects/{self._CRM_API_VERSION}/{object_type}/batch/archive'

        for i in range(0, len(id_list), self._MAX_BATCH_SIZE):
            batch = id_list[i : i + self._MAX_BATCH_SIZE]
            r = self._request(
                "POST",
                endpoint,
                json={"inputs": [{"id": id} for id in batch]},
                expected_status=(200, 204),
                error_context="the archivation of a batch of objects on HubSpot"
            )
            if r is None:
                return False

        return True
        
    def _update_object_batch(
        self,
        object_type: str,
        id_to_properties_list: dict[str, dict[str, str]]
    ) -> bool:
        """
        Generic function to batch update objects (contacts, companies, etc.) on HubSpot.
        API Version 2026-09.
        
        :param object_type: Type of object (e.g. 'contacts' or 'companies')
        :param id_to_properties_list: Dictionary mapping object IDs to property dictionaries to update
        :return: True if successfully updated, False otherwise
        """
        if not id_to_properties_list:
            return True

        endpoint = f'/crm/objects/{self._CRM_API_VERSION}/{object_type}/batch/update'
        items = list(id_to_properties_list.items())

        for i in range(0, len(items), self._MAX_BATCH_SIZE):
            batch = items[i : i + self._MAX_BATCH_SIZE]
            r = self._request(
                "POST",
                endpoint,
                json={"inputs": [{"id": id, "properties": properties} for id, properties in batch]},
                expected_status=200,
                error_context="the update of a batch of objects on HubSpot"
            )
            if r is None:
                return False

        return True

    def _get_object_batch(
        self,
        object_type: str,
        id_list: list[str],
        properties_names: list[str]
    ) -> list[dict[str, str]] | None:
        """
        Generic function to batch retrieve objects (contacts, companies, etc.) from HubSpot.
        API Version 2026-09.
        
        :param object_type: Type of objects (e.g. 'contacts' or 'companies')
        :param id_list: List of IDs to retrieve
        :param properties_names: List of property names to retrieve
        :return: List of dictionaries with requested properties, or None on error
        """
        if not id_list:
            return None

        accumulated_objects: list[dict[str, str]] = []

        endpoint = f'/crm/objects/{self._CRM_API_VERSION}/{object_type}/batch/read'

        for i in range(0, len(id_list), self._MAX_BATCH_SIZE):
            batch = id_list[i : i + self._MAX_BATCH_SIZE]
            r = self._request(
                "POST",
                endpoint,
                json={"inputs": [{"id": id} for id in batch], "properties": properties_names},
                expected_status=(200, 207),
                error_context="the retrieval of a batch of objects on HubSpot"
            )
            if r is None:
                return None

            output = []
            for result in r.json().get("results", []):
                retrieved_properties = {prop: result.get("properties", {}).get(prop) or None for prop in properties_names}
                retrieved_properties["id"] = result.get("id")
                retrieved_properties = dict(sorted(retrieved_properties.items()))
                output.append(retrieved_properties)
            accumulated_objects.extend(output)

        return accumulated_objects if accumulated_objects else None
     
    def createContactBatch(self, properties_list: list[dict[str, str]]) -> list[str] | None:
        for properties in properties_list:
            # Mandatory legal basis for contact creation
            properties["hs_legal_basis"] = "Legitimate interest – existing customer"
        return self._create_object_batch("contacts", properties_list)

    def createCompanyBatch(self, properties_list: list[dict[str, str]]) -> list[str] | None:
        return self._create_object_batch("companies", properties_list)
    
    def archiveContactBatch(self, id_list: list[str]) -> bool:
        return self._archive_object_batch("contacts", id_list)

    def archiveCompanyBatch(self, id_list: list[str]) -> bool:
        return self._archive_object_batch("companies", id_list)
    
    def updateContactBatch(self, id_to_properties_list: dict[str, dict[str, str]]) -> bool:
        return self._update_object_batch("contacts", id_to_properties_list)

    def updateCompanyBatch(self, id_to_properties_list: dict[str, dict[str, str]]) -> bool:
        return self._update_object_batch("companies", id_to_properties_list)
    
    def getContactBatch(self, id_list: list[str], properties_names: list[str]) -> list[dict[str, str]] | None:
        return self._get_object_batch("contacts", id_list, properties_names)

    def getCompanyBatch(self, id_list: list[str], properties_names: list[str]) -> list[dict[str, str]] | None:
        return self._get_object_batch("companies", id_list, properties_names)

    ##########Lists############################################

    #Tested and working
    def getListMembersIds(
        self,
        list_id: str
    ) -> list[str] | None:
        """
        Generic function to retrieve contact IDs belonging to a list on HubSpot.
        API Version 2026-09.
        
        :param list_id: ID of the list to retrieve members from
        :return: List of member IDs, or None on error
        """
        accumulated_ids: list[str] = []

        endpoint = f'/crm/lists/{self._CRM_API_VERSION}/{list_id}/memberships'
        current_after: str | None = None

        while True:
            params: dict[str, Any] = {"limit": 250}
            if current_after:
                params["after"] = current_after

            r = self._request(
                "GET",
                endpoint,
                params=params,
                error_context="the retrieval of the members of a list"
            )
            if r is None:
                return None

            ids = [result.get("recordId") for result in r.json().get("results", []) if "recordId" in result]
            accumulated_ids.extend(ids)

            next_page = r.json().get("paging", {}).get("next", {}).get("after")
            if not next_page:
                break
            current_after = next_page

        return accumulated_ids

    #Tested and working
    def getAgentsListMembersIds(self) -> list[str] | None:
        return self.getListMembersIds(self._AGENT_LIST_ID)
    
    ##########Associations############################################

    def _get_object_associations(
        self,
        from_object_type: str,
        to_object_type: str,
        from_object_id: str
    ) -> list[str] | None:
        """
        Generic function to retrieve associations of an object on HubSpot.
        Recursive calls are not implemented as associations are capped at 500.
        API Version 2026-09.

        :param from_object_type: Source object type
        :param to_object_type: Target object type
        :param from_object_id: Source object ID
        :return: List of associated object IDs, or None on error
        """

        endpoint = f"/crm/objects/{self._CRM_API_VERSION}/{from_object_type}/{from_object_id}/associations/{to_object_type}"
        r = self._request(
            "GET",
            endpoint,
            error_context="the retrieval of associations between objects"
        )
        if r is None:
            return None

        toIds = []
        for to in r.json().get("results", []):
            if "toObjectId" in to:
                toIds.append(str(to["toObjectId"]))
            elif "to" in to and isinstance(to["to"], dict) and "toObjectId" in to["to"]:
                toIds.append(str(to["to"]["toObjectId"]))
        return toIds
    
    def getContactAssociatedCompanies(self, contact_id: str) -> list[str] | None:
        return self._get_object_associations("contacts", "companies", contact_id)

    def getCompanyAssociatedContacts(self, company_id: str) -> list[str] | None:
        return self._get_object_associations("companies", "contacts", company_id)
    
    ##########Associations Batch############################################

    def _get_object_associations_batch(
        self,
        from_object_type: str,
        to_object_type: str,
        from_object_ids: list[str]
    ) -> dict[str, list[str]] | None:
        """
        Generic function to batch retrieve associations for multiple objects on HubSpot.
        API Version 2026-09.

        :param from_object_type: Source object type
        :param to_object_type: Target object type
        :param from_object_ids: List of source object IDs
        :return: Mapping of source object IDs to lists of associated IDs, or None on error
        """
        if not from_object_ids:
            return None

        accumulated_associations: dict[str, list[str]] = {}

        endpoint = f"/crm/associations/{self._CRM_API_VERSION}/{from_object_type}/{to_object_type}/batch/read"

        for i in range(0, len(from_object_ids), self._MAX_BATCH_SIZE):
            batch = from_object_ids[i : i + self._MAX_BATCH_SIZE]

            for toId in batch:
                accumulated_associations.setdefault(toId, [])

            r = self._request(
                "POST",
                endpoint,
                json={"inputs": [{"id": id} for id in batch]},
                expected_status=(200, 207),
                error_context="the retrieval in batch of associations between objects"
            )
            if r is None:
                return None

            for result in r.json().get("results", []):
                fromId = str(result.get("from").get("id"))
                toids = [str(to["toObjectId"]) for to in result.get("to", [])]
                accumulated_associations[fromId] = toids

        return accumulated_associations if accumulated_associations else None
    
    def _create_object_associations_batch(
        self,
        from_object_type: str,
        to_object_type: str,
        associationTypeId: int,
        associations: list[tuple[str, str]]
    ) -> bool:
        """
        Generic function to batch create associations between multiple objects on HubSpot.
        API Version 2026-09.

        :param from_object_type: Source object type
        :param to_object_type: Target object type
        :param associationTypeId: ID of the association type to create
        :param associations: List of tuples (fromId, toId) representing associations to create
        :return: True if successful, False otherwise
        """
        if not associations:
            return True

        endpoint = f"/crm/associations/{self._CRM_API_VERSION}/{from_object_type}/{to_object_type}/batch/create"

        for i in range(0, len(associations), self._MAX_BATCH_SIZE):
            batch = associations[i : i + self._MAX_BATCH_SIZE]
            payload = {
                "inputs": [
                    {
                        "from": {"id": fromId},
                        "to": {"id": toId},
                        "types": [{
                            "associationCategory": "HUBSPOT_DEFINED",
                            "associationTypeId": associationTypeId
                        }]
                    } for fromId, toId in batch
                ]
            }
            r = self._request(
                "POST",
                endpoint,
                json=payload,
                expected_status=(200, 201),
                error_context="the creation in batch of associations between objects"
            )
            if r is None:
                return False

        return True

    def _archive_object_associations_batch(
        self,
        from_object_type: str,
        to_object_type: str,
        associations: list[tuple[str, str]]
    ) -> bool:
        """
        Generic function to batch archive associations between multiple objects on HubSpot.
        API Version 2026-09.

        :param from_object_type: Source object type
        :param to_object_type: Target object type
        :param associations: List of tuples (from_id, to_id) representing associations to archive
        :return: True if successful, False otherwise
        """
        if not associations:
            return True

        endpoint = f"/crm/associations/{self._CRM_API_VERSION}/{from_object_type}/{to_object_type}/batch/archive"

        for i in range(0, len(associations), self._MAX_BATCH_SIZE):
            batch = associations[i : i + self._MAX_BATCH_SIZE]
            inputs = []
            for from_id, to_id in batch:
                inputs.append({
                    "from": {"id": str(from_id)},
                    "to": [{"id": str(to_id)}]
                })

            r = self._request(
                "POST",
                endpoint,
                json={"inputs": inputs},
                expected_status=(200, 204),
                error_context="the archivation in batch of associations between objects"
            )
            if r is None:
                return False

        return True
    
    def getContactsAssociatedCompaniesBatch(self, contacts_ids: list[str]) -> dict[str, list[str]] | None:
        return self._get_object_associations_batch("contacts", "companies", contacts_ids)
    
    def getCompaniesAssociatedContactsBatch(self, companies_ids: list[str]) -> dict[str, list[str]] | None:
        return self._get_object_associations_batch("companies", "contacts", companies_ids)
    
    def getContactsAssociatedContactsBatch(self, contacts_ids: list[str]) -> dict[str, list[str]] | None:
        return self._get_object_associations_batch("contacts", "contacts", contacts_ids)

    def createContactsAssociatedCompaniesBatch(self, associations: list[tuple[str, str]]) -> bool:
        return self._create_object_associations_batch("contacts", "companies", 1, associations)
    
    def archiveContactsAssociatedCompaniesBatch(self, associations: list[tuple[str, str]]) -> bool:
        return self._archive_object_associations_batch("contacts", "companies", associations)
    
    def createContactsAssociatedContactsBatch(self, associations: list[tuple[str, str]]) -> bool:
        return self._create_object_associations_batch("contacts", "contacts", 449, associations)
    
    def createContactsAssociatedDealsBatch(self, associations: list[tuple[str, str]]) -> bool:
        return self._create_object_associations_batch("deals", "contacts", 3, associations)

    ##########Actions############################################

    def _merge_objects(
        self,
        object_type: str,
        main_object_id: str,
        object_to_merge_id: str
    ) -> bool:
        """
        Function to merge two objects on HubSpot.
        API Version 2026-09.
        
        :param object_type: Type of object (e.g. 'companies' or 'contacts')
        :param main_object_id: ID of the primary object
        :param object_to_merge_id: ID of the object to merge into primary object
        :return: True if merged successfully, False otherwise
        """

        endpoint = f'/crm/objects/{self._CRM_API_VERSION}/{object_type}/merge'
        payload = {"objectIdToMerge": object_to_merge_id, "primaryObjectId": main_object_id}
        r = self._request(
            "POST",
            endpoint,
            json=payload,
            error_context=f"the merge of objects {object_type} on HubSpot"
        )
        return r is not None
    
    def mergeCompanies(self, main_company_id: str, company_to_merge_id: str) -> bool:
        return self._merge_objects("companies", main_company_id, company_to_merge_id)
    
    def mergeContacts(self, main_contact_id: str, contact_to_merge_id: str) -> bool:
        return self._merge_objects("contacts", main_contact_id, contact_to_merge_id)
    
    ##########Files############################################

    def get_file_signed_url(self, file_id: str, expiration_seconds: int | None = 604800) -> Any | None:
        """
        Function to retrieve a signed URL of a file on HubSpot.
        API Version 2026-09.
        
        :param file_id: ID of the file to retrieve
        :param expiration_seconds: Time in seconds for the signed URL to remain valid (default: 604800 = 7 days)
        :return: Signed URL of the file, or None on error
        """

        endpoint = f'/files/{self._CRM_API_VERSION}/files/{file_id}/signed-url'

        params: dict[str, Any] = {}
        if expiration_seconds is not None:
            params["expirationSeconds"] = expiration_seconds

        r = self._request(
            "GET",
            endpoint,
            params=params,
            error_context="the retrieval of the signed URL of a file on HubSpot"
        )
        return r.json() if r is not None else None