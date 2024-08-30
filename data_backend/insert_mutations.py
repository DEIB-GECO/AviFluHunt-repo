import gc
import os
import sys
import shutil
import pandas as pd

sys.path.append('helpers')
import excel_extractor
import variant_calling

sys.path.append('database')
import handler


class MutationDatabaseHandler:

    def __init__(self, metadata_file, fasta_file):

        gc.enable()  # Enable garbage collection

        try:
            shutil.rmtree("tmp_mutations")
        except FileNotFoundError:
            pass

        try:
            os.mkdir("tmp_mutations")
            os.mkdir("tmp_mutations/protein")
        except FileExistsError:
            pass

        self.log_file = open("tmp_mutations/bad_sequences.log", "w")

        self.fasta_file = None
        self.metadata_file = None
        self.database_handler = handler.DatabaseHandler()
        self.protein_fasta_by_ref = {}

        self.organize_files(metadata_file, fasta_file)
        self.execute_data_flow()

    def __del__(self):
        self.log_file.close()

    def execute_data_flow(self):

        for key in self.protein_fasta_by_ref.keys():

            subtype_name, segment_type = key.split('_', 1)
            reference = self.get_reference(subtype_name, segment_type)
            dna_reference = reference["dna_fasta"]
            protein_reference = self.dna2aminoacid(dna_reference.upper().replace("T", "U").replace("\n", ""),
                                                   f"{key} Reference")

            if protein_reference is None:
                continue

            aligned_protein_fastas, protein_insertions_file = (
                self.align_sequences("tmp_mutations/protein/", f"{key}",
                                     protein_reference, "".join(self.protein_fasta_by_ref[key])))

            for aligned_protein_header, aligned_protein_fasta in aligned_protein_fastas.items():

                header_dict = self.get_header_dict(aligned_protein_header)
                segment_id = self.get_segment(header_dict)

                if segment_id is None: continue

                mutations = self.get_mutations(aligned_protein_header, aligned_protein_fasta,
                                               protein_reference, protein_insertions_file)

                for mutation in mutations:
                    mut_id = self.create_mutation(header_dict['segment_subtype'], segment_type, mutation)
                    self.create_segment_mutation(segment_id, reference["reference_seg_id"], mut_id)

                self.database_handler.commit_changes()

        self.database_handler.commit_changes()

    """ --- EXECUTION FUNCTIONS --- """
    def organize_protein_fasta_by_reference(self):
        header, dna_sequence = None, ""
        for line in self.fasta_file.readlines():
            if line.startswith('>'):
                if header:
                    self.add_to_protein_fasta_by_ref_dict(header, dna_sequence)
                header = line.strip()
                dna_sequence = ""
            else:
                dna_sequence += line.strip()

        if header:
            self.add_to_protein_fasta_by_ref_dict(header, dna_sequence)

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

    @staticmethod
    def get_mutations(aminoacid_header, aminoacid_aligned, reference_aminoacid_fasta, insertion_file_path):
        variant_caller = variant_calling.VariantCaller(reference_aminoacid_fasta,
                                                       insertions_file_path=insertion_file_path)
        alignment_changes = variant_caller.call_variants(name=aminoacid_header, aligned=aminoacid_aligned,
                                                         aggregate_close_changes=False, one_based=False)
        return alignment_changes.subs + alignment_changes.dels + alignment_changes.ins

    """ --- FILE HANDLING FUNCTIONS --- """
    def organize_files(self, metadata_file, fasta_file):
        self.read_fasta_and_metadata(metadata_file, fasta_file)
        self.organize_protein_fasta_by_reference()
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
    def create_mutation(self, subtype_name, segment_type, mutation):

        position = int(mutation[:mutation.find('_')]) + 1
        ref = mutation[mutation.find('|') - 1:mutation.find('|')]
        alt = mutation[mutation.find('|') + 1:]
        mutation_name = f"{subtype_name}:{segment_type}:{ref}{position}{alt}"

        mutations_in_db = self.database_handler.get_rows("Mutation", ["name"], (mutation_name,))
        if mutations_in_db:
            return mutations_in_db[0]["mutation_id"]

        return self.database_handler.insert_row("Mutation",
                                                ["segment_type", "position", "ref", "alt", "name"],
                                                (segment_type, position, ref, alt, mutation_name, ), commit=True)

    def create_segment_mutation(self, segment_id, reference_id, mutation_id):
        self.database_handler.insert_row("SegmentMutations",
                                         ["segment_id", "reference_seg_id", "mutation_id"],
                                         (segment_id, reference_id, mutation_id,))

    """ GET FUNCTIONS """
    def get_subtype(self, subtype_name):
        subtypes = self.database_handler.get_rows("subtype", ["name"], (subtype_name,))
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

    def get_segment(self, header_dict):
        epi_virus_name = header_dict["segment_id"]
        segments_in_db = self.database_handler.get_rows("Segment", ["epi_virus_name"], (epi_virus_name,))
        if segments_in_db:
            return segments_in_db[0]["segment_id"]
        return None

    """ --- HELPER FUNCTIONS --- """
    def add_to_protein_fasta_by_ref_dict(self, header, dna_sequence):
        segment = header.split("|")[1]
        subtype = header.split("|")[5][-4:]

        protein_sequence = self.dna2aminoacid(dna_sequence.upper().replace("T", "U").replace("\n", ""), header)
        key = f"{subtype}_{segment}"
        entry = f"{header}\n{protein_sequence}\n"

        if protein_sequence is not None:
            if key in self.protein_fasta_by_ref:
                self.protein_fasta_by_ref[key] += entry
            else:
                self.protein_fasta_by_ref[key] = entry

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
            return None

        protein_sequence = ""
        for i in range(0, len(sequence), 3):
            codon = sequence[i:i+3]
            if codon in codon_table:
                amino_acid = codon_table[codon]
                protein_sequence += amino_acid
            else:
                log_entry = f"Invalid Codon: {header}\n"
                self.log_file.write(log_entry)
                return None

        return protein_sequence


if __name__ == "__main__":
    fasta = "resources/segments_data/H5/H5N1/H5N1_Fasta.fasta"
    meta = "resources/segments_data/H5/H5N1/H5N1_Metadata.xls"
    MutationDatabaseHandler(meta, fasta)
