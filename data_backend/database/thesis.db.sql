BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "Annotation" (
	"annotation_id"	INTEGER,
	"annotation_name"	TEXT NOT NULL,
	"annotation_type"	INTEGER,
	"reference_id"	INTEGER NOT NULL,
	FOREIGN KEY("reference_id") REFERENCES "ReferenceSegment"("reference_id"),
	PRIMARY KEY("annotation_id"),
    UNIQUE (annotation_name, reference_id)
);
CREATE TABLE IF NOT EXISTS "Effect" (
	"effect_id"	INTEGER,
	"effect_type"	TEXT NOT NULL,
	"host"	TEXT,
	"drug"	TEXT,
	"effect_full"	TEXT UNIQUE NOT NULL,
	PRIMARY KEY("effect_id")
);
CREATE TABLE IF NOT EXISTS "Isolate" (
	"isolate_id"	INTEGER,
	"isolate_epi"	TEXT NOT NULL,
	"serotype_id"	INTEGER,
	"host"	TEXT,
	"collection_date"	DATE,
	"location_id"	INTEGER,
	FOREIGN KEY("serotype_id") REFERENCES "Serotype"("serotype_id"),
	FOREIGN KEY("location_id") REFERENCES "Location"("location_id"),
	PRIMARY KEY("isolate_id"),
    UNIQUE (isolate_epi)
);
CREATE TABLE IF NOT EXISTS "Location" (
	"location_id"	INTEGER,
	"region"	TEXT NOT NULL,
	"state"	TEXT,
	"city"	TEXT,
	PRIMARY KEY("location_id"),
    UNIQUE (region, state, city)
);
CREATE TABLE IF NOT EXISTS "Marker" (
	"marker_id"	INTEGER,
    "annotation_id" INTEGER NOT NULL,
	"position" INTEGER NOT NULL,
    "allele" TEXT NOT NULL,
	PRIMARY KEY("marker_id"),
	FOREIGN KEY("annotation_id") REFERENCES "Annotation"("annotation_id"),
    UNIQUE (annotation_id, position, allele)
);
CREATE TABLE IF NOT EXISTS "Mutation" (
	"mutation_id"	INTEGER,
	"mutation_name"	TEXT UNIQUE NOT NULL,
	"serotype_name"	TEXT,
	"annotation_id"	,
	"annotation_name"	TEXT,
	"position"	INTEGER,
	"ref"	TEXT,
	"alt"	TEXT,
	FOREIGN KEY("annotation_id") REFERENCES "Annotation"("annotation_id"),
	PRIMARY KEY("mutation_id")
);
CREATE TABLE IF NOT EXISTS "Paper" (
	"paper_id"	INTEGER,
	"title"	TEXT,
	"authors"	TEXT,
	"year"	INTEGER,
	"journal"	TEXT,
	"address"	TEXT,
	"doi"	TEXT UNIQUE NOT NULL,
	PRIMARY KEY("paper_id")
);
CREATE TABLE IF NOT EXISTS "PaperAndEffectOfMarker" (
	"paper_effect_marker_id"	INTEGER,
	"marker_id"	INTEGER NOT NULL,
	"paper_id"	INTEGER NOT NULL,
	"effect_id"	INTEGER NOT NULL,
	"subtype"	TEXT,
	"in_vivo"	INTEGER,
	"in_vitro"	INTEGER,
	FOREIGN KEY("marker_id") REFERENCES "Marker"("marker_id"),
	FOREIGN KEY("paper_id") REFERENCES "Paper"("paper_id"),
	FOREIGN KEY("effect_id") REFERENCES "Effect"("effect_id"),
	PRIMARY KEY("paper_effect_marker_id"),
    UNIQUE (marker_id, paper_id, effect_id)
);
CREATE TABLE IF NOT EXISTS "ReferenceSegment" (
	"reference_id"	INTEGER,
	"segment_type"	TEXT,
	"dna_fasta"	TEXT,
	"protein_fasta"	TEXT,
	PRIMARY KEY("reference_id")
);
CREATE TABLE IF NOT EXISTS "Segment" (
	"segment_id"	INTEGER,
	"isolate_id"	INTEGER,
	"segment_type"	TEXT,
	"segment_epi"	TEXT,
	"virus_name"	TEXT,
	"epi_virus_name"	TEXT UNIQUE NOT NULL,
	FOREIGN KEY("isolate_id") REFERENCES "Isolate"("isolate_id"),
	PRIMARY KEY("segment_id")
);
CREATE TABLE IF NOT EXISTS "SegmentMutations" (
	"segment_id"	INTEGER,
	"reference_id"	INTEGER,
	"mutation_id"	INTEGER,
	FOREIGN KEY("segment_id") REFERENCES "Segment"("segment_id"),
	FOREIGN KEY("mutation_id") REFERENCES "Mutation"("mutation_id"),
	FOREIGN KEY("reference_id") REFERENCES "ReferenceSegment"("reference_id"),
	PRIMARY KEY("segment_id","mutation_id","reference_id")
);
CREATE TABLE IF NOT EXISTS "Serotype" (
	"serotype_id"	INTEGER,
	"name"	TEXT,
	PRIMARY KEY("serotype_id")
);
CREATE TABLE IF NOT EXISTS "Intein" (
    "intein_id" INTEGER,
    "annotation_id" INTEGER NOT NULL,
    "start_pos" INTEGER NOT NULL,
    "end_pos" INTEGER NOT NULL,
    FOREIGN KEY("annotation_id") REFERENCES "Annotation"("annotation_id"),
    PRIMARY KEY("intein_id"),
    UNIQUE (annotation_id, start_pos, end_pos)
);
CREATE TABLE IF NOT EXISTS "SegmentData" (
    "segment_id" INTEGER,
    "sequence" TEXT,
    FOREIGN KEY("segment_id") REFERENCES "Segment"("segment_id"),
    PRIMARY KEY ("segment_id", "sequence")
);
CREATE TABLE IF NOT EXISTS "ReferenceOfSerotype" (
    "reference_id" INTEGER,
    "serotype_id" TEXT,
    FOREIGN KEY("reference_id") REFERENCES "ReferenceSegment"("reference_id"),
    FOREIGN KEY("serotype_id") REFERENCES "Serotype"("serotype_id"),
    PRIMARY KEY ("reference_id", "serotype_id")
);

CREATE VIEW IF NOT EXISTS MutationsMarkers AS
SELECT mutation.mutation_id, marker.marker_id
FROM Mutation mutation
JOIN Marker marker
ON mutation.annotation_id = marker.annotation_id
AND mutation.position = marker.position
AND mutation.alt = marker.allele;

CREATE VIEW IF NOT EXISTS SegmentMarkers AS
SELECT segment.segment_id, marker.marker_id
FROM SegmentData segment
JOIN Marker marker
ON segment.annotation_id = marker.annotation_id
AND SUBSTRING(segment.sequence, marker.position, 1) = marker.allele;
COMMIT;
