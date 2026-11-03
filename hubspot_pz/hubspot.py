#pip install .
from __future__ import annotations

from datetime import date, datetime
from typing import Any, ClassVar

import requests


class HubspotPZ:
    _BASER_URL = "https://api.hubapi.com"
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

    def __init__(self, token: str) -> None:
        self._initialize_hubspot_headers(token)

    def _initialize_hubspot_headers(self, token: str) -> None:
        self._headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        }

    def _convert_date(self, time_millisecond: str) -> date | None:
        if time_millisecond == "":
            return None
        millisecond = int(time_millisecond)
        timestamp = millisecond / 1000  # Convert milliseconds to seconds by dividing by 1000
        data = datetime.fromtimestamp(timestamp)
        return data.date()

    ##########Properties############################################

    def _get_property_info(self, object_type: str, property_name: str) -> Any:
        endpoint = self._BASER_URL + f'/crm/properties/{self._CRM_API_VERSION}/{object_type}/{property_name}'
        r = requests.get(url=endpoint, headers=self._headers)
        
        if r.status_code != 200:
            print(f"Error {r.status_code} during the retrieval of a property information on HubSpot.\nResponse Body: {r.text}")
            return None
        return r.json()

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
        associations_objects: list[str] | None = None,
        accumulated_objects: list[dict[str, str]] | None = None,
        after: str | None = None
    ) -> list[dict[str, str]]:
        """
        Generic function to retrieve all objects of a given type (contacts, companies, etc.) from HubSpot.
        API Version 2026-09.
        
        :param object_type: Type of objects (e.g. 'contacts' or 'companies')
        :param properties_names: List of property names to retrieve for each object
        :param accumulated_objects: List of accumulated objects during recursive calls
        :param after: Pagination cursor for the next page
        :return: List of requested objects
        """
        if accumulated_objects is None:
            accumulated_objects = []

        params: list[tuple[str, Any]] = [("limit", 100)]
        if after:
            params.append(("after", after))
        for prop in properties_names:
            params.append(("properties", prop))
        if associations_objects is not None:
            params.append(("associations", ",".join(associations_objects)))

        endpoint = self._BASER_URL + f'/crm/objects/{self._CRM_API_VERSION}/{object_type}'

        r = requests.get(url=endpoint, headers=self._headers, params=params)

        if r.status_code != 200:
            print(f"Error {r.status_code} during the retrieval of all contacts.\nResponse Body: {r.text}")
            return None
        
        for result in r.json().get("results", []):
            retrieved_properties = {prop: result.get("properties", {}).get(prop) or None for prop in properties_names}
            retrieved_properties["id"] = result.get("id")
            retrieved_properties = dict(sorted(retrieved_properties.items()))
            retrieved_properties["associations"] = result.get("associations", None)
            accumulated_objects.append(retrieved_properties)

        next_page = r.json().get("paging", {}).get("next", {}).get("after")
        if next_page:
            return self._get_all_objects(object_type, properties_names, associations_objects, accumulated_objects, next_page)

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

        endpoint = self._BASER_URL + f'/crm/objects/{self._CRM_API_VERSION}/{object_type}'
        r = requests.post(url=endpoint, headers=self._headers, json={ "properties": properties })
        
        if r.status_code != 201:
            print(f"Error {r.status_code} during the creation of an object on HubSpot.\nResponse Body: {r.text}")
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

        endpoint = self._BASER_URL + f'/crm/objects/{self._CRM_API_VERSION}/{object_type}/{object_id}'
        r = requests.delete(url=endpoint, headers=self._headers)
        
        if r.status_code != 204:
            print(f"Error {r.status_code} during the archivation of an object on HubSpot.\nResponse Body: {r.text}")
            return False
        
        return True
    
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

        endpoint = self._BASER_URL + f'/crm/objects/{self._CRM_API_VERSION}/{object_type}/{object_id}'
        r = requests.patch(url=endpoint, headers=self._headers, json={ "properties": properties })
        
        if r.status_code != 200:
            print(f"Error {r.status_code} during the update of an object on HubSpot.\nResponse Body: {r.text}")
            return False
        
        return True  # Use .get to avoid KeyError if ID does not exist
    
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

        params: list[tuple[str, str]] = []
        if identifying_property != "id":
            params.append(("idProperty", identifying_property))
        for prop in properties_names:
            params.append(("properties", prop))
        if associations_objects is not None:
            params.append(("associations", ",".join(associations_objects)))

        endpoint = self._BASER_URL + f'/crm/objects/{self._CRM_API_VERSION}/{object_type}/{object_id}'
        r = requests.get(url=endpoint, headers=self._headers, params=params)
        
        if r.status_code != 200:
            print(f"Error {r.status_code} during the retrieval of an object on HubSpot.\nResponse Body: {r.text}")
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
        endpoint = self._BASER_URL + f'/crm/objects/{self._CRM_API_VERSION}/{object_type}/search'
        r = requests.post(url=endpoint, headers=self._headers,
                         json={"properties": properties_names,
                               "filterGroups":[
                                   {"filters": [ 
                                       {"propertyName": name, "operator": "EQ", "value": value } for name, value in search_params.items()
                                       ]}]})
        
        if r.status_code != 200:
            print(f"Error {r.status_code} during the search of an object on HubSpot.\nResponse Body: {r.text}")
            return None
        
        output = []
        for result in r.json().get("results", []):
            retrieved_properties = {prop: result.get("properties").get(prop) for prop in properties_names}
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
        properties["pipeline"] = "2405411057"
        return self._create_object("deals", properties)
    
    def createContactDeal(self, properties: dict[str, str]) -> str | None:
        #https://app-eu1.hubspot.com/property-settings/25378285/properties?type=0-3&eschref=%2Fcontacts%2F25378285%2Fobjects%2F0-3%2Frestore&search=pip&action=edit&property=pipeline
        properties["pipeline"] = "59157733"
        return self._create_object("deals", properties)
    
    def getPipelineInfo(self, object_type: str, pipeline_id: str) -> Any:
        endpoint = self._BASER_URL + f'/crm/v3/pipelines/{object_type}/{pipeline_id}'
        r = requests.get(url=endpoint, headers=self._headers)
        
        if r.status_code != 200:
            print(f"Error {r.status_code} during the retrieval of a pipeline information on HubSpot.\nResponse Body: {r.text}")
            return None
        return r.json()
    
    ##########Objects Batch############################################

    def _create_object_batch(
        self,
        object_type: str,
        properties_list: list[dict[str, str]],
        accumulated_ids: list[str] | None = None
    ) -> list[str] | None:
        """
        Generic function to batch create objects (contacts, companies, etc.) on HubSpot.
        API Version 2026-09.
        In this implementation associations are not handled (batch creation of objects only, without relations).
        
        :param object_type: Type of object (e.g. 'contacts' or 'companies')
        :param properties_list: List of property dictionaries
        :param accumulated_ids: List of accumulated IDs during recursive calls
        :return: List of created object IDs, or None on error
        """

        if accumulated_ids is None:
            accumulated_ids = []

        # Base recursive case: if the list is empty, return accumulated IDs
        if not properties_list:
            return accumulated_ids if accumulated_ids else None

        # Take up to the maximum batch size
        batch = properties_list[:self._MAX_BATCH_SIZE]
        remaining = properties_list[self._MAX_BATCH_SIZE:]

        endpoint = self._BASER_URL + f'/crm/objects/{self._CRM_API_VERSION}/{object_type}/batch/create'
        r = requests.post(url=endpoint,
                          headers=self._headers,
                          json={ "inputs": [{"properties": properties} for properties in batch] })

        if r.status_code not in (200, 201):
            # Status code 207 is multi-status (some objects may have succeeded and others failed)
            print(f"Error {r.status_code} during the creation of a batch of objects on HubSpot.\nResponse Body: {r.text}")
            # return None
        else:
            results = r.json().get("results", [])
            accumulated_ids.extend([result.get("id") for result in results if result.get("id")])
        
        return self._create_object_batch(object_type, remaining, accumulated_ids)

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

        # Base recursive case: if the list is empty, return True
        if not id_list:
            return True

        # Take up to the maximum batch size
        batch = id_list[:self._MAX_BATCH_SIZE]
        remaining = id_list[self._MAX_BATCH_SIZE:]
        
        endpoint = self._BASER_URL + f'/crm/objects/{self._CRM_API_VERSION}/{object_type}/batch/archive'
        r = requests.post(url=endpoint,
                          headers=self._headers,
                          json={ "inputs": [{"id": id} for id in batch] })

        if r.status_code not in (200, 204):
            print(f"Error {r.status_code} during the archivation of a batch of objects on HubSpot.\nResponse Body: {r.text}")
            return False
        
        return self._archive_object_batch(object_type, remaining)
        
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

        # Base recursive case: if dictionary is empty, return True
        if not id_to_properties_list:
            return True
        
        # Take up to the maximum batch size
        batch = dict(list(id_to_properties_list.items())[:self._MAX_BATCH_SIZE]) # First MAX_BATCH_SIZE elements
        remaining = dict(list(id_to_properties_list.items())[self._MAX_BATCH_SIZE:]) # Remaining elements
        
        endpoint = self._BASER_URL + f'/crm/objects/{self._CRM_API_VERSION}/{object_type}/batch/update'
        r = requests.post(url=endpoint,
                          headers=self._headers,
                          json={ "inputs": [{"id": id, "properties": properties} for id, properties in batch.items()] })

        if r.status_code != 200:
            # Status code 207 is multi-status (some objects may have succeeded and others failed)
            print(f"Error {r.status_code} during the update of a batch of objects on HubSpot.\nResponse Body: {r.text}")
            return False
        
        return self._update_object_batch(object_type, remaining)

    def _get_object_batch(
        self,
        object_type: str,
        id_list: list[str],
        properties_names: list[str],
        accumulated_objects: list[dict[str, str]] | None = None
    ) -> list[dict[str, str]] | None:
        """
        Generic function to batch retrieve objects (contacts, companies, etc.) from HubSpot.
        API Version 2026-09.
        
        :param object_type: Type of objects (e.g. 'contacts' or 'companies')
        :param id_list: List of IDs to retrieve
        :param properties_names: List of property names to retrieve
        :param accumulated_objects: Accumulated objects during recursive calls
        :return: List of dictionaries with requested properties, or None on error
        """

        if accumulated_objects is None:
            accumulated_objects = []

        # Base recursive case: if the list is empty, return accumulated objects
        if not id_list:
            return accumulated_objects if accumulated_objects else None
        
        # Take up to the maximum batch size
        batch = id_list[:self._MAX_BATCH_SIZE]
        remaining = id_list[self._MAX_BATCH_SIZE:]

        endpoint = self._BASER_URL + f'/crm/objects/{self._CRM_API_VERSION}/{object_type}/batch/read'
        r = requests.post(url=endpoint,
                          headers=self._headers,
                          json={ "inputs": [{"id": id} for id in batch], "properties": properties_names })

        if r.status_code not in (200, 207):
            print(f"Error {r.status_code} during the retrieval of a batch of objects on HubSpot.\nResponse Body: {r.text}")
            return None
        
        output = []
        for result in r.json().get("results", []):
            retrieved_properties = {prop: result.get("properties", {}).get(prop) or None for prop in properties_names}
            retrieved_properties["id"] = result.get("id")
            retrieved_properties = dict(sorted(retrieved_properties.items()))
            output.append(retrieved_properties)
        accumulated_objects.extend(output)
        
        return self._get_object_batch(object_type, remaining, properties_names, accumulated_objects)
     
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
        list_id: str,
        accumulated_ids: list[str] | None = None,
        after: str | None = None
    ) -> list[str] | None:
        """
        Generic function to retrieve contact IDs belonging to a list on HubSpot.
        API Version V3.
        
        :param list_id: ID of the list to retrieve members from
        :param accumulated_ids: Accumulated IDs during recursive calls
        :param after: Pagination cursor for the next page
        :return: List of member IDs, or None on error
        """
        if accumulated_ids is None:
            accumulated_ids = []
        
        endpoint = self._BASER_URL + f'/crm/v3/lists/{list_id}/memberships?limit=250'
        if after:
            endpoint += f"&after={after}"

        r = requests.get(url=endpoint, headers=self._headers)

        if r.status_code != 200:
            print(f"Error {r.status_code} during the retrieval of the members of a list.\nResponse Body: {r.text}")
            return None
        
        ids = [result.get("recordId") for result in r.json().get("results", []) if "recordId" in result]
        accumulated_ids.extend(ids)
        next_page = r.json().get("paging", {}).get("next", {}).get("after")
        if next_page:
            return self.getListMembersIds(list_id, accumulated_ids, next_page)

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

        endpoint = self._BASER_URL + f"/crm/objects/{self._CRM_API_VERSION}/{from_object_type}/{from_object_id}/associations/{to_object_type}"

        r = requests.get(url=endpoint, headers=self._headers)
        if r.status_code != 200:
            print(f"Error {r.status_code} during the retrieval of associations between objects.\nResponse Body: {r.text}")
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
        from_object_ids: list[str],
        accumulated_associations: dict[str, list[str]] | None = None
    ) -> dict[str, list[str]] | None:
        """
        Generic function to batch retrieve associations for multiple objects on HubSpot.
        API Version 2026-09.

        :param from_object_type: Source object type
        :param to_object_type: Target object type
        :param from_object_ids: List of source object IDs
        :param accumulated_associations: Accumulated associations mapping
        :return: Mapping of source object IDs to lists of associated IDs, or None on error
        """

        if accumulated_associations is None:
            accumulated_associations = {}

        # Base recursive case: if the list is empty, return accumulated associations
        if not from_object_ids:
            return accumulated_associations if accumulated_associations else None
        
        # Take up to the maximum batch size
        batch = from_object_ids[:self._MAX_BATCH_SIZE]
        remaining = from_object_ids[self._MAX_BATCH_SIZE:]

        endpoint = self._BASER_URL + f"/crm/associations/{self._CRM_API_VERSION}/{from_object_type}/{to_object_type}/batch/read"
        
        for toId in batch:
            # Add key if not present (with empty list default)
            accumulated_associations.setdefault(toId, [])
        
        # Prepare request payload
        r = requests.post(url=endpoint, headers=self._headers, json={ "inputs": [{"id": id} for id in batch] })

        if r.status_code != 200 and r.status_code != 207:
            print(f"Error {r.status_code} during the retrieval in batch of associations between objects.\nResponse Body: {r.text}")
            return None
        
        for result in r.json().get("results", []):
            fromId = str(result.get("from").get("id"))
            toids = [str(to["toObjectId"]) for to in result.get("to", [])]
            accumulated_associations[fromId] = toids

        return self._get_object_associations_batch(from_object_type, to_object_type, remaining, accumulated_associations)
    
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

        # Base recursive case: if the list is empty, return True
        if not associations:
            return True

        endpoint = self._BASER_URL + f"/crm/associations/{self._CRM_API_VERSION}/{from_object_type}/{to_object_type}/batch/create"
        
        batch = associations[:self._MAX_BATCH_SIZE]
        remaining = associations[self._MAX_BATCH_SIZE:]

        r = requests.post(
            url = endpoint,
            headers = self._headers,
            json = {
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
        )

        if r.status_code not in (200, 201):
            print(f"Error {r.status_code} during the creation in batch of associations between objects.\nResponse Body: {r.text}")
            return False
        
        return self._create_object_associations_batch(from_object_type, to_object_type, associationTypeId, remaining)

    def _archive_object_associations_batch(
        self,
        from_object_type: str,
        to_object_type: str,
        associations: list[tuple[str, list[str]]]
    ) -> bool:
        """
        Generic function to batch archive associations between multiple objects on HubSpot.
        API Version 2026-09.

        :param from_object_type: Source object type
        :param to_object_type: Target object type
        :param associations: List of tuples (toId, fromIds) representing associations to archive
        :return: True if successful, False otherwise
        """

        # Base recursive case: if the list is empty, return True
        if not associations:
            return True

        endpoint = self._BASER_URL + f"/crm/associations/{self._CRM_API_VERSION}/{from_object_type}/{to_object_type}/batch/archive"
        
        batch = associations[:self._MAX_BATCH_SIZE]
        remaining = associations[self._MAX_BATCH_SIZE:]

        r = requests.post(url=endpoint, headers=self._headers, json={ "inputs": [{"from": {"id": toId}, "to": [{"id": fromId} for fromId in fromIds]} for toId, fromIds in batch] })

        if r.status_code not in (200, 204):
            print(f"Error {r.status_code} during the archivation in batch of associations between objects.\nResponse Body: {r.text}")
            return False
        
        return self._archive_object_associations_batch(from_object_type, to_object_type, remaining)
    
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

        endpoint = self._BASER_URL + f'/crm/objects/{self._CRM_API_VERSION}/{object_type}/merge'

        r = requests.post(url=endpoint, headers=self._headers, json={ "objectIdToMerge": object_to_merge_id, "primaryObjectId": main_object_id })

        if r.status_code != 200:
            print(f"Error {r.status_code} during the merge of objects {object_type} on HubSpot.\nResponse Body: {r.text}")
            return False
        
        return True
    
    def mergeCompanies(self, main_company_id: str, company_to_merge_id: str) -> bool:
        return self._merge_objects("companies", main_company_id, company_to_merge_id)
    
    def mergeContacts(self, main_contact_id: str, contact_to_merge_id: str) -> bool:
        return self._merge_objects("contacts", main_contact_id, contact_to_merge_id)
    
    ##########Files############################################

    def get_file_signed_url(self, file_id: str) -> Any | None:
        """
        Function to retrieve a signed URL of a file on HubSpot.
        API Version V3.
        
        :param file_id: ID of the file to retrieve
        :return: Signed URL of the file, or None on error
        """

        endpoint = self._BASER_URL + f'/files/v3/files/{file_id}/signed-url'

        r = requests.get(url=endpoint, headers=self._headers)

        if r.status_code != 200:
            print(f"Error {r.status_code} during the retrieval of the signed URL of a file on HubSpot.\nResponse Body: {r.text}")
            return None
        
        return r.json()