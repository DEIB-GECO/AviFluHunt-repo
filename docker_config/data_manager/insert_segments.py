import argparse
import gc
import os
import sys
import shutil
import pandas as pd

sys.path.append('helpers')
sys.path.append('database')
import handler


class MutationDatabaseHandler:

    def __init__(self, metadata_file, fasta_file):

        gc.enable()  # Enable garbage collection

        try:
            shutil.rmtree("tmp")
        except FileNotFoundError:
            pass

        try:
            os.mkdir("tmp")
            os.mkdir("tmp/dna")
            os.mkdir("tmp/protein")
        except FileExistsError:
            pass

        self.log_file = open("tmp/bad_sequences.log", "w")

        self.fasta_file = None
        self.metadata_file = None
        self.database_handler = handler.DatabaseHandler()
        self.taxonomy_handler = taxonomer.Taxonomer()
        self.dna_fasta_by_ref = {}

        self.organize_files(metadata_file, fasta_file)
        self.execute_data_flow()

    def __del__(self):
        self.log_file.close()

    def execute_data_flow(self):

        for key in self.dna_fasta_by_ref.keys():

            subtype_name, segment_type = key.split('_', 1)
            reference = self.get_reference(subtype_name, segment_type)
            if not reference: continue

            aligned_dna_fastas, dna_insertions_file = self.align_sequences(
                "tmp/dna/", key, reference["dna_fasta"], self.dna_fasta_by_ref[f"{key}"])

            annotations = self.get_annotations(segment_type)
            for annotation in annotations:

                inteins = self.get_inteins(annotation["annotation_id"])

                coding_sequences_fasta = self.get_coding_sequences_fasta(
                    aligned_dna_fastas, dna_insertions_file, inteins, reference["dna_fasta"])

                reference_coding_sequence = self.dna2aminoacid(
                    self.extract_coding_sequence(
                        reference["dna_fasta"].upper().replace("T", "U").replace("\n", ""),
                        [(intein["start_pos"], intein["end_pos"]) for intein in inteins], [0, 0, 0]),
                    "")

                aligned_protein_fastas, protein_insertions_file = self.align_sequences(
                    "tmp/protein/", f"{key}_{annotation["annotation_name"]}",
                    reference_coding_sequence, "".join(coding_sequences_fasta))

                for aligned_protein_header, aligned_protein_fasta in aligned_protein_fastas.items():

                    header_dict = self.get_header_dict(aligned_protein_header)
                    segment_id = self.create_segment(header_dict)
                    self.create_segment_data(segment_id, annotation["annotation_id"], aligned_protein_fasta)

                self.database_handler.commit_changes()

        self.database_handler.commit_changes()

    """ --- EXECUTION FUNCTIONS --- """
    # TODO: ugly
    def organize_dna_fasta_by_reference(self):

        header, sequence = None, ""
        for line in self.fasta_file.readlines():
            if line.startswith('>'):

                if header:
                    header_dict = self.get_header_dict(header)
                    if self.is_valid_sequence(sequence) and self.create_isolate(header_dict["isolate_id"]) != -1:
                        self.add_to_dna_fasta_by_ref_dict(header, sequence)

                header = line.strip()
                sequence = ""

            else:
                sequence += line.strip()

        if header:
            header_dict = self.get_header_dict(header)
            if self.is_valid_sequence(sequence):
                if self.create_isolate(header_dict["isolate_id"]) and self.create_isolate(header_dict["isolate_id"]) != -1:
                    self.add_to_dna_fasta_by_ref_dict(header, sequence)

    def get_coding_sequences_fasta(self, aligned_dna_fastas, dna_insertions_file, inteins, reference_fasta):

        try:
            insertions_file = open(dna_insertions_file, "r")
            insertions_csv = pd.read_csv(insertions_file, on_bad_lines='skip', low_memory=False)
        except FileNotFoundError:
            insertions_file, insertions_csv = None, None
        except TypeError:
            insertions_file, insertions_csv = None, None

        coding_sequences_fasta = []

        for aligned_header, aligned_dna_fasta in aligned_dna_fastas.items():

            aligned_dna_fasta = aligned_dna_fasta.upper().replace("T", "U").replace("\n", "")
            if self.is_bad_sequence(aligned_dna_fasta, aligned_header):
                continue

            insertions = []
            if insertions_file:
                for intein in inteins:
                    aligned_dna_fasta, intein_insertions = self.reinsert_insertions(
                        aligned_header, aligned_dna_fasta, intein, insertions_csv, sum(insertions))
                    insertions.append(intein_insertions)

            aligned_cds = self.extract_coding_sequence(
                aligned_dna_fasta, [(intein["start_pos"], intein["end_pos"]) for intein in inteins], insertions)

            # Correct start and end deletion
            aligned_cds = self.correct_start_end_deletions(reference_fasta, aligned_cds)
            aligned_cds = aligned_cds.upper().replace("T", "U").replace("\n", "").replace("-", "")

            try:
                cds_aminoacid = self.dna2aminoacid(aligned_cds, aligned_header)
                coding_sequences_fasta.append(f"{aligned_header}\n{cds_aminoacid}\n")
            except (ValueError, NameError):
                continue

        return coding_sequences_fasta

    def align_sequences(self, path, base_name, reference_fasta, target_fasta):

        reference_file_path = self.create_fasta_file(path, f"{base_name}_reference",
                                                     f">{base_name}_reference\n{reference_fasta}")
        target_file_path = self.create_fasta_file(path, f"{base_name}_target", target_fasta)
        aligned_file_path = path + f"{base_name}_aligned.fasta"

        self.execute_augur(reference_file_path, target_file_path, aligned_file_path)
        aligned_fastas = self.get_aligned_fastas(aligned_file_path)

        insertions_file = aligned_file_path.replace(".fasta", ".fasta.insertions.csv")
        if not os.path.isfile(insertions_file):
            insertions_file = None

        return aligned_fastas, insertions_file

    """ --- FILE HANDLING FUNCTIONS --- """
    def organize_files(self, metadata_file, fasta_file):
        self.read_fasta_and_metadata(metadata_file, fasta_file)
        self.organize_dna_fasta_by_reference()
        self.fasta_file.close()
        del self.metadata_file

    def read_fasta_and_metadata(self, metadata_file, fasta_file):
        self.metadata_file = pd.read_excel(f"{metadata_file}")
        self.fasta_file = open(f"{fasta_file}", "r")

    @staticmethod
    def create_fasta_file(path, file_name, fasta):
        os.makedirs(path, exist_ok=True)
        with open(f"{path}{file_name}.fasta", "w+") as fasta_file:
            fasta_file.write(fasta)
        return f"{path}{file_name}.fasta"

    """ --- DATABASE FUNCTIONS --- """

    """ CREATE FUNCTIONS """
    def create_isolate(self, isolate_epi):

        try:
            isolate_metadata = self.metadata_file.loc[self.metadata_file.iloc[:, 0] == isolate_epi].values.flatten()
        except KeyError:
            return -1

        host = isolate_metadata[17]

        if host:

            host_id = self.search_host_id_in_common_names(host)
            if host_id is None:

                try:
                    taxonomy = self.taxonomy_handler.retrieve_taxonomy(host, 8782)
                    host_taxonomy = [taxon.scientific_name for taxon in taxonomy]
                    host_id = self.create_host_in_db(host_taxonomy)
                    self.create_common_host(host_id, host)
                except TypeError:
                    host_id = -1  # NCBI Problem
        else:
            host_id = -1

        collection_date = isolate_metadata[25]
        location_id = self.get_location_id(isolate_metadata[16])
        subtype_id = self.get_subtype(isolate_metadata[12].split("/")[-1].strip())["subtype_id"]

        #clade = isolate_metadata[14]
        #print(self.extract_clade_levels(clade))

        self.database_handler.insert_row("Isolate",
                                         ["isolate_id", "isolate_epi", "subtype_id",
                                          "host_id", "collection_date", "location_id"],
                                         (None, isolate_epi, subtype_id, host_id, collection_date, location_id,))
        return 0

    @staticmethod
    def extract_clade_levels(clade_str):
        pattern = r'^(\d+)(?:\.(\d+))?(?:\.(\d+))?(?:\.(\d+))?(?:([a-z]))?$'
        match = re.match(pattern, clade_str)
        if not match:
            return None, None, None, None, None

        lv1, lv2, lv3, lv4, suffix = match.groups()
        return lv1, lv2, lv3, lv4, suffix

    def search_clade_id_by_name(self, clade_name):
        clades = self.database_handler.get_rows("Clade", ["clade_name"], (clade_name,))
        if clades:
            return clades[0]["clade_id"]
        return None

    def search_host_id_in_common_names(self, host_name):
        hosts = self.database_handler.get_rows("HostCommonName", ["common_name"], (host_name,))
        if hosts: return hosts[0]["host_id"]
        return None

    def search_host_id_in_scientific_names(self, host_name):
        hosts = self.database_handler.get_rows("Host", ["host_name"], (host_name,))
        if hosts: return hosts[0]["host_id"]
        return None

    def create_host_in_db(self, taxonomy):

        if "Aves" in taxonomy:
            return self.insert_taxonomy_recursively(taxonomy[:taxonomy.index("Aves")+1])
        elif "Mammalia" in taxonomy:
            return self.insert_taxonomy_recursively(taxonomy[:taxonomy.index("Mammalia")+1])

        return -1

    def insert_taxonomy_recursively(self, taxonomy):

        current_host_name = taxonomy[0]

        # Step 1: Check if the current level is already in the database
        current_id = self.search_host_id_in_scientific_names(current_host_name)

        if current_id is not None:
            return current_id

        # Step 2: Process the parent level (remaining taxonomy)
        parent_id = self.insert_taxonomy_recursively(taxonomy[1:])

        # Step 3: Insert the current level and link it to the parent
        return self.create_host_and_taxonomy_link(current_host_name, parent_id)

    def create_host_and_taxonomy_link(self, host_name, parent_id):
        host_id = self.database_handler.insert_row("Host", ["host_id", "host_name"],
                                                   (None, host_name), commit=True)
        self.database_handler.insert_row("Taxonomy", ["host_id", "parent_id"],
                                         (host_id, parent_id), commit=True)
        return host_id

    def create_common_host(self, host_id, common_name):
        self.database_handler.insert_row("HostCommonName", ["host_id", "common_name"],
                                         (host_id, common_name), commit=True)

    def create_segment(self, header_dict):

        isolate_epi = header_dict["isolate_id"]
        segment_type = header_dict["segment_type"]
        segment_epi = header_dict["segment_epi"]
        virus_name = header_dict["virus_name"]
        epi_virus_name = header_dict["segment_id"]

        segments_in_db = self.database_handler.get_rows("Segment", ["epi_virus_name"], (epi_virus_name,))
        if segments_in_db:
            return segments_in_db[0]["segment_id"]

        return self.database_handler.insert_row("Segment",
                                                ["segment_id", "isolate_epi", "segment_type",
                                                 "segment_epi", "virus_name", "epi_virus_name"],
                                                (None, isolate_epi, segment_type,
                                                 segment_epi, virus_name, epi_virus_name),
                                                commit=True)

    def create_segment_data(self, segment_id, annotation_id, sequence):
        self.database_handler.insert_row("SegmentData",
                                         ["segment_id", "annotation_id", "sequence"],
                                         (segment_id, annotation_id, sequence,))

    """ GET FUNCTIONS """
    def get_location_id(self, location_string):

        location_metadata = [item.strip() for item in location_string.split("/")] + ["None"] * 3
        region, state, city = location_metadata[:3]

        locations = self.database_handler.get_rows("Location", ["region", "state", "city"], (region, state, city,))
        if locations:
            return locations[0]["location_id"]

        return self.database_handler.insert_row("Location", ["region", "state", "city"], (region, state, city,),
                                                commit=True)

    def get_subtype(self, subtype_name):
        subtypes = self.database_handler.get_rows("Subtype", ["name"], (subtype_name,))
        if subtypes:
            return subtypes[0]
        return None

    def get_reference(self, subtype_name, segment_type):

        subtype = self.get_subtype(subtype_name)
        if subtype:
            try:
                reference = self.database_handler.get_rows(
                    "ReferenceSegment", ["subtype_id", "segment_type"],
                    (subtype["subtype_id"], segment_type,))[0]
                return reference
            except IndexError:
                return None

    def get_annotations(self, segment_type):
        return self.database_handler.get_rows("Annotation", ["segment_type"], (segment_type,))

    def get_inteins(self, annotation_id):
        return self.database_handler.get_rows("Intein", ["annotation_id"], (annotation_id,))

    """ --- HELPER FUNCTIONS --- """

    def add_to_dna_fasta_by_ref_dict(self, header, sequence):
        segment = header.split("|")[1]
        subtype = header.split("|")[5][-4:]

        key = f"{subtype}_{segment}"
        entry = f"{header}\n{sequence}\n"

        if key in self.dna_fasta_by_ref:
            self.dna_fasta_by_ref[key] += entry
        else:
            self.dna_fasta_by_ref[key] = entry

    @staticmethod
    def execute_augur(reference_path, target_path, aligned_path):
        os.system("augur align"
                  f" --reference-sequence {reference_path}"
                  f" --sequences {target_path}"
                  f" --output {aligned_path}  --nthreads 4 --remove-reference")

    @staticmethod
    def get_aligned_fastas(aligned_path):

        fasta_dict = {}
        header = None
        sequence = []

        with open(aligned_path, "r") as file:
            for line in file:
                line = line.strip()
                if line.startswith('>'):
                    if header:
                        fasta_dict[header] = ''.join(sequence)
                    header = line
                    sequence = []
                else:
                    sequence.append(line)

        if header:
            fasta_dict[header] = ''.join(sequence)

        return fasta_dict

    @staticmethod
    def get_header_dict(header):

        # Split the header line by '|'
        header_parts = header.split('|')

        # Extract the individual components
        segment_epi = header_parts[0][1:]
        segment_type = header_parts[1]
        virus_name = header_parts[2]
        isolate_id = header_parts[3]
        # If there's an additional part for the subtype, extract it
        segment_subtype = header_parts[-1].split('_')[-1] if '_' in header_parts[-1] else None

        # Construct the segment_id
        segment_id = f"{segment_epi}:{virus_name}"

        # Create the dictionary
        return {
            "segment_type": segment_type,
            "segment_epi": segment_epi,
            "virus_name": virus_name,
            "segment_id": segment_id,
            "isolate_id": isolate_id,
            "segment_subtype": segment_subtype
        }

    @staticmethod
    def extract_coding_sequence(whole_fasta, inteins_positions, additions):

        whole_fasta = whole_fasta.strip()
        cumulative_sum = 0
        substrings = []

        for i, (start, end) in enumerate(inteins_positions):
            adjusted_start = start + cumulative_sum
            adjusted_end = end + cumulative_sum

            if i < len(additions):
                adjusted_end += additions[i]
                cumulative_sum += additions[i]

            substrings.append(whole_fasta[adjusted_start - 1: adjusted_end])

        # Join substrings to form the final result string
        result_string = ''.join(substrings)
        return result_string

    def dna2aminoacid(self, sequence, header):

        codon_table = {
            "UUU": "F", "UUC": "F", "UUA": "L", "UUG": "L", "UCU": "S", "UCC": "S", "UCA": "S", "UCG": "S",
            "UAU": "Y", "UAC": "Y", "UAA": "*", "UAG": "*", "UGU": "C", "UGC": "C", "UGA": "*", "UGG": "W",
            "CUU": "L", "CUC": "L", "CUA": "L", "CUG": "L", "CCU": "P", "CCC": "P", "CCA": "P", "CCG": "P",
            "CAU": "H", "CAC": "H", "CAA": "Q", "CAG": "Q", "CGU": "R", "CGC": "R", "CGA": "R", "CGG": "R",
            "AUU": "I", "AUC": "I", "AUA": "I", "AUG": "M", "ACU": "T", "ACC": "T", "ACA": "T", "ACG": "T",
            "AAU": "N", "AAC": "N", "AAA": "K", "AAG": "K", "AGU": "S", "AGC": "S", "AGA": "R", "AGG": "R",
            "GUU": "V", "GUC": "V", "GUA": "V", "GUG": "V", "GCU": "A", "GCC": "A", "GCA": "A", "GCG": "A",
            "GAU": "D", "GAC": "D", "GAA": "E", "GAG": "E", "GGU": "G", "GGC": "G", "GGA": "G", "GGG": "G",
        }

        # Ensure the sequence length is divisible by 3
        if len(sequence) % 3 != 0:
            log_entry = f"CDS not divisible by 3: {header}\n"
            self.log_file.write(log_entry)
            raise ValueError("Sequence length must be a multiple of 3")

        protein_sequence = ""
        for i in range(0, len(sequence), 3):
            codon = sequence[i:i+3]
            if codon in codon_table:
                amino_acid = codon_table[codon]
                protein_sequence += amino_acid
            else:
                log_entry = f"Invalid Codon: {header}\n"
                self.log_file.write(log_entry)
                raise NameError("Invalid codon: " + codon)

        return protein_sequence

    @staticmethod
    def is_valid_sequence(s):
        valid = {'a', 'c', 't', 'g', 'u'}
        return all(letter in valid for letter in s)

    def is_bad_sequence(self, s, header):
        hyphen_count = s.count('-')
        total_length = len(s)
        hyphen_percentage = (hyphen_count / total_length) * 100 if total_length > 0 else 0

        if hyphen_percentage > 95:
            log_entry = f"Bad sequence, too few nucleotides: {header}\n"
            self.log_file.write(log_entry)
            return True

        return False

    def reinsert_insertions(self, aligned_header, aligned_fasta, intein, dna_insertions_file, total_insertions):

        row = dna_insertions_file.loc[dna_insertions_file['strain'] == aligned_header.replace(">", "")]
        if row.empty:
            return aligned_fasta, 0

        row_dict = {key: value for i, (key, value) in enumerate(row.to_dict(orient='records')[0].items()) if i != 0}

        intein_insertions = 0
        for insertion, nucleotides in row_dict.items():

            pos = int(insertion[insertion.index("pos ") + len("pos "):])

            if pd.notna(nucleotides):

                nucleotides = nucleotides.replace("T", "U").replace("\n", "")
                n_nucleotides = len(nucleotides)

                if pos == intein["start_pos"] - 1:
                    pos, nucleotides, n_nucleotides = (
                        self.check_start_pos(pos, nucleotides, n_nucleotides, aligned_fasta))

                if pos == intein["end_pos"] - 1:
                    pos, nucleotides, n_nucleotides = self.check_end_pos(pos, nucleotides, aligned_fasta)

                if intein["start_pos"] - 1 <= pos <= intein["end_pos"] - 1:
                    aligned_fasta = (aligned_fasta[:pos + intein_insertions + total_insertions]
                                     + nucleotides +
                                     aligned_fasta[pos + intein_insertions + total_insertions:])
                    intein_insertions += n_nucleotides

        return aligned_fasta, intein_insertions

    @staticmethod
    def check_start_pos(pos, nucleotides, n_nucleotides, check_fasta):
        start_codon = "AUG"
        start_codon_index = nucleotides.find(start_codon)
        if start_codon_index == -1 or check_fasta[:3] == "AUG":
            return -1, "", 0  # Ignore insertion, cause it doesn't have start codon
        return pos, nucleotides[start_codon_index:], n_nucleotides - start_codon_index

    @staticmethod
    def check_end_pos(pos, nucleotides, check_fasta):

        stop_codons = ["UAA", "UAG", "UGA"]
        min_stop_codon_index = -1
        for stop_codon in stop_codons:
            stop_codon_index = nucleotides.find(stop_codon)
            if stop_codon_index != -1:
                if min_stop_codon_index == -1 or stop_codon_index < min_stop_codon_index:
                    min_stop_codon_index = stop_codon_index

        if min_stop_codon_index == -1 or check_fasta[-3:] in ["UAA", "UAG", "UGA"]:
            return -1, "", 0  # Ignore insertion, because it doesn't have a stop codon

        return pos, nucleotides[:min_stop_codon_index + 3], min_stop_codon_index + 3

    @staticmethod
    def correct_start_end_deletions(reference, target):

        # Count the number of '-' at theHost start and end of the target string
        start_dashes = len(target) - len(target.lstrip('-'))
        end_dashes = len(target) - len(target.rstrip('-'))

        # Replace the start '-' sequence with the corresponding characters from the start of the reference
        if start_dashes > 0:
            target = reference[:start_dashes] + target[start_dashes:]

        # Replace the end '-' sequence with the corresponding characters from the end of the reference
        if end_dashes > 0:
            target = target[:-end_dashes] + reference[-end_dashes:]

        return target


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-fasta', type=str, required=False)
    parser.add_argument('-metadata', type=str, required=False)

    # Parse the command-line arguments
    args = parser.parse_args()
       
    fasta = args.fasta
    meta = args.metadata
    MutationDatabaseHandler(meta, fasta)
