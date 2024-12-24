import os
import re
from collections import deque

from rapidfuzz import process, fuzz
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
    def retrieve_common_names_from_ncbi(tax_id=None):

        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        if tax_id:
            url = f"{base_url}esummary.fcgi?db=taxonomy&id={tax_id}&retmode=json"
        else:
            raise ValueError("Either tax_id or scientific_name must be provided.")

        response = requests.get(url).json()
        result = response['result'][str(tax_id)]
        common_names = result.get('othernames', [])

        return common_names

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
        lineage = [taxon.scientific_name for taxon in taxoniq.Taxon(scientific_name=scientific_name).lineage]
        return lineage


def is_vertebrate(taxon_id):
    vertebrate_taxon_id = 7742
    try:
        for tax in taxoniq.Taxon(tax_id=taxon_id).lineage:
            if vertebrate_taxon_id == tax.tax_id:
                return True
        return False
    except KeyError:
        return False


def is_host_avian(host_name, taxonomy):

    # Find taxon
    taxon = None
    try:
        taxon = taxoniq.Taxon(scientific_name=host_name)
    except KeyError:
        for k in taxonomy.keys():
            if host_name in taxonomy[k]["common_names"]:
                taxon = taxoniq.Taxon(scientific_name=taxonomy[k]["scientific_name"])
                break

    if taxon is None: return False
    return "Aves" in [t.scientific_name for t in taxon.lineage]


def retrieve_taxonomy_data_ncbi_dmp(file_path):

    taxon_data = {}

    with open(file_path, "r") as file:
        for line in file:
            # Split the line into fields using the delimiter '\t|\t'
            fields = line.strip().split("\t|\t")

            tax_id = int(fields[0])  # Convert tax_id to integer
            name = fields[1]
            name_type = fields[3].strip()
            name_type = re.sub(r"[^a-zA-Z]", "", name_type)

            if not is_vertebrate(tax_id):
                continue

            # If the tax_id is not in the dictionary, initialize it
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

    taxon_data = {
        tax_id: data
        for tax_id, data in taxon_data.items()
        if data["scientific_name"] is not None
    }

    return taxon_data


taxonomy_file = os.path.join(os.path.dirname(__file__), "../resources/taxonomy/names.dmp")
taxonomy_data = retrieve_taxonomy_data_ncbi_dmp(taxonomy_file)

if __name__ == '__main__':

    taxonomer = Taxonomer()
    hosts = "Other mammals,Avian,Tadorna feruginea,Anser indicus,Goose,Other avian,Gallus gallus domesticus,Phasanius colchicus,Calidris canutus,Duck,mammals,Anas acuta,Chicken,Cairina moschata,Anas platyrhynchos var. domesticus,Meleagris gallopavo,Domestic goose,Cygnus olor,Swine,Gallus gallus,Cygnus atratus,Larus argentatus,Falco peregrinus,Buteo buteo,Phasianus colchicus,Wild bird,Turkey,Human,Anser anser domesticus,Swan,Guineafowl,Anser anser,Cygnus cygnus,Anas platyrhynchos,Branta leucopsis,Anser brachyrhynchus,Chroicocephalus ridibundus,Pavo cristatus,Cygnus columbianus,Accipiter gentilis,Falco tinnunculus,Eurasian curlew,Branta canadensis,Mallard,Greylag goose,Whooper swan,Larus fuscus,Larus melanocephalus,Larus ridibundus,Wild birds,Haliaeetus leucocephalus,Pigeon,Accipiter nisus,Anas sp.,Gull,Halietus albicilla,Eagle,Numida meleagris,Ostrich,Pheasant,Larus canus,Canine,Coturnix,Mink,Black-headed gull,Common teal,Mareca penelope,Hirundo rustica,Leucophaeus,Feline,Necrosyrtes monachus,Falco,Phasianus,Animal,Dove,Sterna hirundo,Herring gull,Larus marinus,Sandpiper,Partridge,Tachybaptus ruficollis,Mouse,Aythya fuligula,Guinea fowl,Falcon,Coturnix sp.,Blue-winged teal,Buteo,Anas platyrhynchos f. domestica,Larus,Tadorna tadorna,Larus brunnicephalus,Larus ichthyaetus,Cygnus melancoryphus,Branta bernicla,Wild waterfowl,Corvus macrorhynchos,Netta peposaca,Copsychus saularis,Pavo,Corvus,Rissa tridactyla,Cormorant,Turnstone,Anas carolinensis,US Quail,Equine,Seal,Anas crecca,Podiceps cristatus,Calidris alba,Dairy cattle,Buteo lineatus,Larus schistisagus,Anas americana,Aix galericulata,Anas formosa,Anser albifrons,Anser rossii,Anser caerulescens,Somateria mollissima,Felis catus,Lophodytes cucullatus,Arenaria interpres,Anas rubripes,White-fronted goose,Anser cygnoides,Crow,Bean goose,Polyplectron bicalcaratum,Teal,Quail,Penguin,Passerine,Anseriformes sp.,Sterna sandvicensis,Poultry,Anas strepera,Alectoris chukar,Rynchops niger,Larosterna inca,Buteo jamaicensis,Aythya affinis,Sacred ibis,Bovine,Great tit,Meerkat,Mallard duck,Larus smithsonianus,Anser sp.,Curlew,Numida sp.,Grey teal,Sterna paradisaea,Gyps fulvus,Larus delawarensis,Ferret,Numenius arquata,Pica,Zosterops japonicus,Phasanius sp.,Rodent,Accipiter trivirgatus,Larus dominicanus,Anas clypeata,Anas boschas,Lophura nycthemera,Anas zonorhyncha,Bucephala clangula,Anas undalata,Nisaetus nipalensis,Anas cyanoptera,Gracula religiosa,Circus,Circus aeruginosus,Morphnus guianensis,Anser fabalis"
    taxonomy_names = [
        name
        for taxon in taxonomy_data.values()
        for name in ([taxon["scientific_name"]] + taxon["common_names"])
    ]

    for host in hosts.split(","):
        scientific_host_name = taxonomer.retrieve_scientific_name_from_ncbi(host)
        if isinstance(scientific_host_name, type):

            host = host

            try:
                partial_match = [match for match in process.extract(host.lower(), taxonomy_names)
                                 if is_host_avian(match[0], taxonomy_data)][0]
            except IndexError:
                partial_match = []

            try:
                fuzzy_match = [match for match in process.extract(host.lower(), taxonomy_names, scorer=fuzz.partial_ratio)
                               if is_host_avian(match[0], taxonomy_data)][0]
            except IndexError:
                fuzzy_match = []

            if partial_match and partial_match[1] > 90:
                match = partial_match
            else:
                match = fuzzy_match

            if match:

                match = list(match)
                try:
                   taxoniq.Taxon(scientific_name=match[0])
                except KeyError:
                    for key in taxonomy_data.keys():
                        if match[0] in taxonomy_data[key]["common_names"]:
                            match[0] = taxonomy_data[key]["scientific_name"]
                            break

                print(host)
                print(match)
                print(partial_match, fuzzy_match)
