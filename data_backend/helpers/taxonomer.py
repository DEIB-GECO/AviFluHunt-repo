import os
import re
import pandas
import taxoniq
from xml.etree import ElementTree
from rapidfuzz import process, fuzz
from requests import HTTPError, get


class Taxonomer:
    _instance = None
    _manual_pairings = {}
    _taxonomy_data = {}

    class SpeciesNotFoundError(Exception):

        def __init__(self):
            self.message = "Species was not found"
            super().__init__(self.message)

    def __init__(self):
        if Taxonomer._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Taxonomer._instance = self
        self.__create_manual_pairings()
        self.__create_taxonomy_data_ncbi_dmp()

    def retrieve_taxonomy(self, host, preferred_parent_tax_id=None):
        scientific_name = self.retrieve_scientific_name_from_host(self.__clean_host(host), preferred_parent_tax_id)
        if scientific_name is None: return None
        return taxoniq.Taxon(scientific_name=scientific_name).lineage

    def retrieve_scientific_name_from_host(self, host, preferred_parent_tax_id=None):

        # 3 POSSIBILITIES

        # 1) HOST NAME IS SCIENTIFICALLY CORRECT ALREADY
        scientific_host_name = self.retrieve_scientific_name_from_ncbi(host)
        if not isinstance(scientific_host_name, type):
            return None#scientific_host_name

        # 2) MANUAL PAIRING
        id_from_manual_pairing = self.get_manual_pairing(host)
        if id_from_manual_pairing is not None:
            return None#taxoniq.Taxon(id_from_manual_pairing).scientific_name

        # 3) MATCHING
        return self.match_host(host, preferred_parent_tax_id)

    def retrieve_scientific_name_from_ncbi(self, host):

        xml_data = self.__search_taxonomy_by_common_name(host)
        if not xml_data:
            raise self.SpeciesNotFoundError

        taxid = self.__get_taxid_from_search_result(xml_data)
        if taxid:
            scientific_name = self.__fetch_scientific_name_from_taxid(taxid)
        else:
            return self.SpeciesNotFoundError

        if not scientific_name:
            return type
        return scientific_name

    def get_manual_pairing(self, unknown_host):
        try:
            return self._manual_pairings[unknown_host]
        except KeyError:
            return None

    def match_host(self, host, preferred_parent_tax_id=None):

        def is_specific_host(host_name):

            taxon = None
            try:
                taxon = taxoniq.Taxon(scientific_name=host_name)
            except KeyError:
                for k in self._taxonomy_data.keys():
                    if host_name in self._taxonomy_data[k]["common_names"]:
                        taxon = taxoniq.Taxon(scientific_name=self._taxonomy_data[k]["scientific_name"])
                        break

            if taxon is None: return False
            return preferred_parent_tax_id in [t.tax_id for t in taxon.lineage]

        taxonomy_names = [
            name
            for taxon in self._taxonomy_data.values()
            for name in ([taxon["scientific_name"]] + taxon["common_names"])
        ]

        try:
            partial_match = [match for match in process.extract(host.lower(), taxonomy_names)
                             if is_specific_host(match[0])][0]
        except IndexError:
            partial_match = []

        try:
            fuzzy_match = [match for match in process.extract(host.lower(), taxonomy_names, scorer=fuzz.partial_ratio)
                           if is_specific_host(match[0])][0]
        except IndexError:
            fuzzy_match = []

        if partial_match and partial_match[1] > 90:
            match = partial_match
        else:
            match = fuzzy_match

        if match:
            match = list(match)
            return self.resolve_scientific_name(match)

    @staticmethod
    def __search_taxonomy_by_common_name(common_name):
        search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=taxonomy&term={common_name}&retmode=xml"
        response = get(search_url)

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
        response = get(summary_url)

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

    def resolve_scientific_name(self, match):
        try:
            taxoniq.Taxon(scientific_name=match[0])
            return match[0]
        except KeyError:
            for key in self._taxonomy_data.keys():
                if match[0] in self._taxonomy_data[key]["common_names"]:
                    return self._taxonomy_data[key]["scientific_name"]

    def __create_manual_pairings(self):
        file_path = os.path.join(os.path.dirname(__file__), "../resources/taxonomy/manual_tax.xlsx")
        df = pandas.read_excel(file_path)
        df.columns = ['unknown_host', 'ncbi_id']
        self._manual_pairings = dict(zip(df['unknown_host'], df['ncbi_id']))

    def __create_taxonomy_data_ncbi_dmp(self):

        taxon_data = {}
        taxonomy_file = os.path.join(os.path.dirname(__file__), "../resources/taxonomy/names.dmp")

        with open(taxonomy_file, "r") as file:
            for line in file:
                fields = line.strip().split("\t|\t")

                tax_id = int(fields[0])
                name = fields[1]
                name_type = fields[3].strip()
                name_type = re.sub(r"[^a-zA-Z]", "", name_type)

                if tax_id not in taxon_data:
                    taxon_data[tax_id] = {
                        "scientific_name": None,
                        "common_names": []
                    }

                # Populate the scientific_name field
                if name_type == "scientificname":
                    taxon_data[tax_id]["scientific_name"] = name

                # Add to common_names if it's a synonym or a genbank common name
                elif name_type in ["synonym", "genbankcommonname", "commonname"]:
                    taxon_data[tax_id]["common_names"].append(name[:-1] if name.endswith("s") else name)

        self._taxonomy_data = {
            tax_id: data
            for tax_id, data in taxon_data.items()
            if data["scientific_name"] is not None
        }

    @staticmethod
    def __clean_host(host):
        if host.endswith(" sp."): host = host[:-4]
        return host

