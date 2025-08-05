#!/usr/bin/env bash

if [ "${UPDATE_ALSO_KNOWLEDGE}" = "true" ]; then
  python3 database/handler.py &
  python3 resources/domain_data/insert_domain.py &
  python3 resources/academic_data/insert_academic.py &
  python3 resources/academic_data/insert_markers.py &
fi

python3 insert_segments.py -fasta "${FASTA_FILE:-none}" -metadata "${METADATA_FILE:-none}" &
python3 insert_mutations.py -fasta "${FASTA_FILE:-none}" -metadata "${METADATA_FILE:-none}" &

# Wait for all background processes to complete
wait
