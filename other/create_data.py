import random
import string
import sqlite3
from datetime import datetime, timedelta

# Connect to SQLite database (creates a new file if not exist)
conn = sqlite3.connect('thesis.db')
cursor = conn.cursor()

# COMMON DATA
serotypes = ['H5N1', 'H5N2', 'H5N5', 'H1N1']
proteins = ["HA", "NA", "PB2", "PB1", "M1", "M2"]
aminoacids = {
    'F': ["Phe", ["UUU", "UUC"]],
    'L': ["Leu", ["UUA", "UUG", "CUU", "CUC", "CUA", "CUG"]],
    'I': ["Ile", ["AUU", "AUC", "AUA"]],
    'M': ["Met", ["AUG"]],
    'V': ["Val", ["GUU", "GUC", "GUA", "GUG"]],
    'S': ["Ser", ["UCU", "UCC", "UCA", "UCG", "AGU", "AGC"]],
    'P': ["Pro", ["CCU", "CCC", "CCA", "CCG"]],
    'T': ["Thr", ["ACU", "ACC", "ACA", "ACG"]],
    'A': ["Ala", ["GCU", "GCC", "GCA", "GCG"]],
    'Y': ["Tyr", ["UAU", "UAC"]],
    'H': ["His", ["CAU", "CAC"]],
    'Q': ["Gln", ["CAA", "CAG"]],
    'N': ["Asn", ["AAU", "AAC"]],
    'K': ["Lys", ["AAA", "AAG"]],
    'D': ["Asp", ["GAU", "GAC"]],
    'E': ["Glu", ["GAA", "GAG"]],
    'C': ["Cys", ["UGU", "UGC"]],
    'W': ["Trp", ["UGG"]],
    'R': ["Arg", ["CGU", "CGC", "CGA", "CGG", "AGA", "AGG"]],
    'G': ["Gly", ["GGU", "GGC", "GGA", "GGG"]],
    'U': ["Sec", ["UGA"]],
    'O': ["Pyl", ["UAG"]],
}

# OTHER COMMON DATA
location_number = 50
reference_number = 100
genes_number = 100
proteins_number = len(proteins) - 1
papers_number = 100
effects_number = 100
markers_number = 100
groups = 50
places = ["Honk Kong", "Hokkaido", "NY", "Guangdong", "MN", "Italy"]
isolates_ids = []
mutations_ids = []

# Define SQL statements for creating tables


# Location table
create_location_table = """ 
CREATE TABLE IF NOT EXISTS Location (
    id INTEGER PRIMARY KEY, region TEXT, state TEXT, city TEXT);"""

# Isolate table
create_isolate_table = """ 
CREATE TABLE IF NOT EXISTS Isolate (
    id TEXT PRIMARY KEY, isolate_id TEXT, isolate_name TEXT, serotype_id INTEGER,
    metadata_id INTEGER, host TEXT, collection_date DATE, location_id INTEGER, 
    FOREIGN KEY (serotype_id) REFERENCES Serotype(id),
    FOREIGN KEY (metadata_id) REFERENCES MutationMetadata(id),
    FOREIGN KEY (location_id) REFERENCES Location(id));"""

# Segment table
create_segment_table = """ 
CREATE TABLE IF NOT EXISTS Segment (
    id INTEGER PRIMARY KEY, reference_id INTEGER, isolate_id TEXT, type INTEGER, name TEXT,
    FOREIGN KEY (reference_id) REFERENCES ReferenceSegment(id),
    FOREIGN KEY (isolate_id) REFERENCES Isolate(id));"""

# ReferenceSegment table
create_reference_segment_table = """
CREATE TABLE IF NOT EXISTS ReferenceSegment (
    id INTEGER PRIMARY KEY, serotype_id INTEGER,
    name TEXT, fasta TEXT,
    FOREIGN KEY (serotype_id) REFERENCES Serotype(id)
);
"""

# Gene table
create_gene_table = """
CREATE TABLE IF NOT EXISTS Gene (
    id INTEGER PRIMARY KEY, reference_id INTEGER, protein_id INTEGER,
    start_pos INTEGER, end_pos INTEGER,
    FOREIGN KEY (reference_id) REFERENCES ReferenceSegment(id),
    FOREIGN KEY (protein_id) REFERENCES Protein(id)
);
"""

# Protein table
create_protein_table = """
CREATE TABLE IF NOT EXISTS Protein (
    id INTEGER PRIMARY KEY, gene_id INTEGER, name TEXT,
    FOREIGN KEY (gene_id) REFERENCES Gene(id)
);
"""

# Serotype table
create_serotype_table = """
CREATE TABLE IF NOT EXISTS Serotype (
    id INTEGER PRIMARY KEY, name TEXT
);
"""

# Mutation table
create_mutation_table = """
CREATE TABLE IF NOT EXISTS Mutation (
    id TEXT PRIMARY KEY, protein_id INTEGER, serotype TEXT,
    protein_name TEXT, type INTEGER, 
    position INTEGER, previous_AA TEXT, resulting_AA TEXT,
    FOREIGN KEY (protein_id) REFERENCES Protein(id)
);
"""

# MutationMetadata table
create_mutation_metadata_table = """
CREATE TABLE IF NOT EXISTS MutationMetadata (
    mutation_id TEXT, id INTEGER PRIMARY KEY, total_count INTEGER,
    FOREIGN KEY (mutation_id) REFERENCES Mutation(id)
);
"""

# SegmentMutations table
create_segment_mutations_table = """
CREATE TABLE IF NOT EXISTS SegmentMutations (
    segment_id INTEGER, mutation_id TEXT,
    FOREIGN KEY (segment_id) REFERENCES Segment(id),
    FOREIGN KEY (mutation_id) REFERENCES Mutation(id),
    PRIMARY KEY (segment_id, mutation_id)
);
"""

# MutationGroup table
create_mutation_group_table = """
CREATE TABLE IF NOT EXISTS MutationGroup (
    id INTEGER PRIMARY KEY, name TEXT
);
"""

# MutationToGroup table
create_mutation_to_group_table = """
CREATE TABLE IF NOT EXISTS MutationToGroup (
    mutation_id TEXT, mutation_group_id INTEGER,
    FOREIGN KEY (mutation_id) REFERENCES Mutation(id),
    FOREIGN KEY (mutation_group_id) REFERENCES MutationGroup(id),
    PRIMARY KEY (mutation_id, mutation_group_id)
);
"""

# Marker table
create_marker_table = """
CREATE TABLE IF NOT EXISTS Marker (
    id INTEGER PRIMARY KEY, notes TEXT, mutation_group_id INTEGER,
    FOREIGN KEY (mutation_group_id) REFERENCES MutationGroup(id)
);
"""

# Effect table
create_effect_table = """
CREATE TABLE IF NOT EXISTS Effect (
    id INTEGER PRIMARY KEY,
    name TEXT, host TEXT, drug TEXT
);
"""

# Paper table
create_paper_table = """
CREATE TABLE IF NOT EXISTS Paper (
    id INTEGER PRIMARY KEY,
    title TEXT, authors TEXT, year INTEGER,
    journal TEXT, address TEXT, doi TEXT
);
"""

# PaperAndEffectOfMarker table
create_paper_effect_marker_table = """
CREATE TABLE IF NOT EXISTS PaperAndEffectOfMarker (
    id INTEGER PRIMARY KEY,
    marker_id INTEGER, paper_id INTEGER, effect_id INTEGER,
    subtype TEXT, in_vivo INTEGER, in_vitro INTEGER,
    FOREIGN KEY (marker_id) REFERENCES Marker(id),
    FOREIGN KEY (paper_id) REFERENCES Paper(id),
    FOREIGN KEY (effect_id) REFERENCES Effect(id)
);
"""

# Execute all create table statements
create_table_statements = [
    create_location_table,
    create_isolate_table,
    create_segment_table,
    create_reference_segment_table,
    create_gene_table,
    create_protein_table,
    create_serotype_table,
    create_mutation_table,
    create_mutation_metadata_table,
    create_segment_mutations_table,
    create_mutation_group_table,
    create_mutation_to_group_table,
    create_marker_table,
    create_effect_table,
    create_paper_table,
    create_paper_effect_marker_table,
]

for create_statement in create_table_statements:
    cursor.execute(create_statement)


# CREATE ALL FILL FUNCTIONS

# Function to generate random date
def random_date(start_date, end_date):
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)


# Function to generate random location data
def generate_random_location():
    region = random.choice(['North', 'South', 'East', 'West'])
    state = random.choice(['State1', 'State2', 'State3'])
    city = random.choice(['City1', 'City2', 'City3'])
    return None, region, state, city


# Function to generate random isolate data
def generate_random_isolate():
    serotype_id = random.randint(1, len(serotypes))
    host = random.choice(['Human', 'Avian'])

    isolate_id = "EPI_ISL_" + str(random.randint(1, 10000))
    code = ''.join(random.choice(string.printable) for _ in range(random.randint(3, 6)))
    isolate_name = f"A{host}/{random.choice(places)}/{code}/2000"
    composite_id = isolate_id + isolate_name
    isolates_ids.append(composite_id)

    metadata_id = random.randint(1, 100)
    collection_date = random_date(datetime(2010, 1, 1), datetime.now())
    location_id = random.randint(0, location_number)
    return composite_id, isolate_id, isolate_name, serotype_id, metadata_id, host, collection_date, location_id


# Function to generate random segment data
def generate_random_segment():
    reference_id = random.randint(0, reference_number)
    isolate_id = random.choice(isolates_ids)
    segment_type = random.randint(1, 3)
    segment_name = f'Segment_{random.randint(1, 100)}'
    return None, reference_id, isolate_id, segment_type, segment_name


# Function to generate random reference segment data
def generate_random_reference_segment():
    serotype_id = random.randint(1, len(serotypes))
    name = f'ReferenceSegment_{random.randint(1, 100000)}'
    fasta = 'AGCTGCTAGCTAGCTA'  # Example FASTA sequence
    return None, serotype_id, name, fasta


# Function to generate random gene data
def generate_random_gene():
    reference_id = random.randint(0, reference_number)
    protein_id = random.randint(0, proteins_number)  # TODO?
    start_pos = random.randint(1, 1000)
    end_pos = random.randint(start_pos, 1000) + start_pos
    return None, reference_id, protein_id, start_pos, end_pos


# Function to generate random protein data
def generate_random_protein():
    gene_id = random.randint(0, genes_number)
    name = random.choice(proteins)
    return None, gene_id, name


# Function to generate random serotype data
# NOT NECESSARY


# Function to generate random mutation data
def generate_random_mutation():
    protein_id = random.randint(0, proteins_number)
    serotype = random.choice(serotypes)
    protein_name = proteins[protein_id]
    mutation_type = random.randint(1, 5)
    position = random.randint(1, 500)
    previous_AA = random.choice(list(aminoacids.keys()))
    resulting_AA = random.choice(list(aminoacids.keys()))
    mutation_id = f"{serotype}:{protein_name}:{previous_AA}{position}{resulting_AA}"
    mutations_ids.append(mutation_id)
    return mutation_id, protein_id, serotype, protein_name, mutation_type, position, previous_AA, resulting_AA


# Function to generate random connections between segments and mutations
# NOT NECESSARY


# Function to generate random mutation groups
# NOT NECESSARY

# Function to generate random connections between group of mutations
# NOT NECESSARY

# Function to generate random marker data
def generate_random_marker():
    notes = ''.join(random.choices(string.ascii_uppercase + string.digits, k=200))
    group_id = random.randint(0, groups)
    return None, notes, group_id


# Function to generate random effect data
def generate_random_effect():
    name = f'Effect_{random.randint(1, 100)}'
    host = random.choice(['Human', 'Avian'])
    drug = random.choice(['DrugA', 'DrugB', 'DrugC'])
    return None, name, host, drug


# Function to generate random paper data
def generate_random_paper():
    title = f'Paper_{random.randint(1, 10000)}'
    authors = 'AuthorA, AuthorB'
    year = random.randint(2010, 2023)
    journal = 'Journal of Virology'
    address = 'Somewhere'
    doi = 'doi1234567890'
    return None, title, authors, year, journal, address, doi


# Function to generate random paper and effect of marker data
def generate_random_paper_effect_marker():
    marker_id = random.randint(0, markers_number)
    paper_id = random.randint(0, papers_number)
    effect_id = random.randint(0, effects_number)
    subtype = 'SubtypeA'
    in_vivo = random.randint(0, 1)
    in_vitro = 1 - in_vivo
    return None, marker_id, paper_id, effect_id, subtype, in_vivo, in_vitro


# Generate fake data for each table
# Generate and insert location data
for _ in range(50):  # Generate 50 locations
    location_data = generate_random_location()
    cursor.execute('INSERT INTO Location VALUES (?, ?, ?, ?)', location_data)

# Generate and insert isolate data
for _ in range(100):  # Generate 100 isolates
    isolate_data = generate_random_isolate()
    cursor.execute('INSERT INTO Isolate VALUES (?, ?, ?, ?, ?, ?, ?, ?)', isolate_data)

# Generate and insert segment data
for _ in range(200):  # Generate 200 segments
    segment_data = generate_random_segment()
    cursor.execute('INSERT INTO Segment VALUES (?, ?, ?, ?, ?)', segment_data)

# Generate and insert reference segment data
for _ in range(reference_number):
    reference_data = generate_random_reference_segment()
    cursor.execute('INSERT INTO ReferenceSegment VALUES (?, ?, ?, ?)', reference_data)

# Generate and insert gene data
for _ in range(genes_number):
    gene_data = generate_random_gene()
    cursor.execute('INSERT INTO Gene VALUES (?, ?, ?, ?, ?)', gene_data)

# Generate and insert protein data
for _ in range(proteins_number):
    protein_data = generate_random_protein()
    cursor.execute('INSERT INTO Protein VALUES (?, ?, ?)', protein_data)

# Insert serotype data
for sero_index in range(len(serotypes)):
    cursor.execute('INSERT INTO Serotype VALUES (?, ?)', (sero_index, serotypes[sero_index]))

# Generate and insert mutation data
for _ in range(100):
    mutation_data = generate_random_mutation()
    cursor.execute('INSERT INTO Mutation VALUES (?, ?, ?, ?, ?, ?, ?, ?)', mutation_data)

# Generate random mutations for segments
for _ in range(1000):
    mutation_id = random.choice(mutations_ids)
    segment_id = random.randint(0, 200)
    cursor.execute('INSERT OR REPLACE INTO SegmentMutations VALUES (?, ?)', (segment_id, mutation_id))

# Generate random mutation groups
for g_id in range(groups):
    name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))
    cursor.execute('INSERT INTO MutationGroup VALUES (?, ?)', (g_id, name))

# Generate random mutations for mutation groups
for _ in range(200):
    mutation_id = random.choice(mutations_ids)
    group_id = random.randint(0, groups)
    cursor.execute('INSERT OR REPLACE INTO MutationToGroup VALUES (?, ?)', (mutation_id, group_id))

# Generate random markers for segments
for _ in range(markers_number):
    marker_data = generate_random_marker()
    cursor.execute('INSERT INTO Marker VALUES (?, ?, ?)', marker_data)

# Generate and insert effect data
for _ in range(effects_number):
    effect_data = generate_random_effect()
    cursor.execute('INSERT INTO Effect VALUES (?, ?, ?, ?)', effect_data)

# Generate and insert paper data
for _ in range(papers_number):
    paper_data = generate_random_paper()
    cursor.execute('INSERT INTO Paper VALUES (?, ?, ?, ?, ?, ?, ?)', paper_data)

# Generate and insert paper and effect of marker data
for _ in range(1000):
    paper_effect_marker = generate_random_paper_effect_marker()
    cursor.execute('INSERT INTO PaperAndEffectOfMarker VALUES (?, ?, ?, ?, ?, ?, ?)', paper_effect_marker)

# Commit changes and close connection
conn.commit()
conn.close()
