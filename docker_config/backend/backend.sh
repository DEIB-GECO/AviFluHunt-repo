#!/usr/bin/env bash

exec python3 database/handler.py & 
exec python3 resources/domain_data/insert_domain.py &  # may need files for ref and subtypes
exec python3 resources/academic_data/insert_academic.py &  # may need files for effects, markers and papers
exec python3 resources/academic_data/insert_markers.py &
exec python3 insert_segments.py & # needs files (fasta + metadata)
#exec python3 insert_mutations.py  # needs files