#!/usr/bin/env bash

if [ ! "${UPDATE_ALSO_KNOWLEDGE}" ]; then
  exec python3 database/handler.py & 
  exec python3 resources/domain_data/insert_domain.py & 
  exec python3 resources/academic_data/insert_academic.py & 
  exec python3 resources/academic_data/insert_markers.py
fi  &
exec python3 insert_segments.py -fasta "${FASTA_FILE:none}" -metadata "${METADATA_FILE:none}" &
exec python3 insert_mutations.py  -fasta "${FASTA_FILE:none}" -metadata "${METADATA_FILE:none}"