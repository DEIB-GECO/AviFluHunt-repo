import taxoniq
import requests
from xml.etree import ElementTree

from requests import HTTPError


class Taxonomer:

    _instance = None

    class SpeciesNotFoundError(Exception):

        def __init__(self):
            self.message = "Species was not found"
            super().__init__(self.message)

    def __init__(self):
        if Taxonomer._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Taxonomer._instance = self

    def retrieve_scientific_name_from_ncbi(self, common_name):

        xml_data = self.__search_taxonomy_by_common_name(common_name)
        if not xml_data:
            raise self.SpeciesNotFoundError

        taxid = self.__get_taxid_from_search_result(xml_data)
        if taxid:
            scientific_name = self.__fetch_scientific_name_from_taxid(taxid)
        else:
            return self.SpeciesNotFoundError

        if not scientific_name:
            raise self.SpeciesNotFoundError
        return scientific_name

    @staticmethod
    def __search_taxonomy_by_common_name(common_name):
        search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=taxonomy&term={common_name}&retmode=xml"
        response = requests.get(search_url)

        if response.status_code != 200:
            raise HTTPError

        return response.content

    @staticmethod
    def __get_taxid_from_search_result(xml_data):
        """Extract the TaxID from the XML search result."""
        try:
            root = ElementTree.fromstring(xml_data)
            id_list = root.find("IdList")
            if id_list is not None:
                return id_list.find("Id").text
            else:
                return None
        except Exception as e:
            return None

    @staticmethod
    def __fetch_scientific_name_from_taxid(taxid):
        """Fetch the scientific name from NCBI using the TaxID."""
        summary_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=taxonomy&id={taxid}&retmode=xml"
        response = requests.get(summary_url)

        if response.status_code != 200:
            raise HTTPError

        try:
            root = ElementTree.fromstring(response.content)
            docsum = root.find("DocSum")
            if docsum is not None:
                scientific_name = docsum.find("Item[@Name='ScientificName']").text
                return scientific_name
            else:
                return None
        except Exception as e:
            return None

    @staticmethod
    def retrieve_taxonomy_from_scientific_name(scientific_name):
        return taxoniq.Taxon(scientific_name=scientific_name)

