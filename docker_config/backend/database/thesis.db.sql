BEGIN TRANSACTION;

-- LITERATURE
CREATE TABLE IF NOT EXISTS "Marker" (
	"marker_id"	INTEGER,
    "annotation_id" INTEGER NOT NULL,
	"position" INTEGER NOT NULL,
    "allele" TEXT NOT NULL,
    "name" TEXT NOT NULL,  -- name = annotation_name + position + allele
	PRIMARY KEY("marker_id"),
	FOREIGN KEY("annotation_id") REFERENCES "Annotation"("annotation_id"),
    UNIQUE (annotation_id, position, allele)
);

CREATE TABLE IF NOT EXISTS `MarkerToGroup` (
    "marker_id" INTEGER,
    "marker_group_id" INTEGER,
	FOREIGN KEY("marker_id") REFERENCES "Marker"("marker_id"),
	PRIMARY KEY("marker_id", "marker_group_id"),
    UNIQUE ("marker_id", marker_group_id)
);

CREATE TABLE IF NOT EXISTS "Effect" (
	"effect_id"	INTEGER,
	"effect_type"	TEXT NOT NULL,
	"host"	TEXT,
	"drug"	TEXT,
	"effect_full"	TEXT UNIQUE NOT NULL,
	PRIMARY KEY("effect_id")
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

CREATE TABLE IF NOT EXISTS "MarkerGroupPaperAndEffect" (
    "marker_group_id" INTEGER,
    "paper_id" INTEGER,
    "effect_id" INTEGER,
	FOREIGN KEY("marker_group_id") REFERENCES "MarkerToGroup"("marker_group_id"),
	FOREIGN KEY("paper_id") REFERENCES "Paper"("paper_id"),
	FOREIGN KEY("effect_id") REFERENCES "Effect"("effect_id"),
    PRIMARY KEY (marker_group_id, paper_id, effect_id)
);

-- CONNECTIONS

CREATE TABLE IF NOT EXISTS "MarkerGroupToSubtype" (
    "subtype_id" INTEGER,
    "marker_group_id" INTEGER,
    "notes" TEXT,
    FOREIGN KEY("subtype_id") REFERENCES "Subtype"("subtype_id"),
    FOREIGN KEY("marker_group_id") REFERENCES "MarkerToGroup"("marker_group_id"),
    PRIMARY KEY("subtype_id", "marker_group_id"),
    UNIQUE ("subtype_id", marker_group_id)
);

-- DOMAIN

CREATE TABLE IF NOT EXISTS "ReferenceSegment" (
	"reference_seg_id"	INTEGER,
    "subtype_id" INTEGER,
	"segment_type"	TEXT,
	"dna_fasta"	TEXT,
	"protein_fasta"	TEXT,
    FOREIGN KEY("subtype_id") REFERENCES "Subtype"("subtype_id"),
	PRIMARY KEY("reference_seg_id")
);

CREATE TABLE IF NOT EXISTS "Annotation" (
	"annotation_id"	INTEGER,
    "segment_type" TEXT,
	"annotation_name"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("annotation_id")
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

CREATE TABLE IF NOT EXISTS "Isolate" (
	"isolate_id"	INTEGER,
	"isolate_epi"	TEXT NOT NULL,
	"subtype_id"	INTEGER,
	"host"	TEXT,
	"collection_date"	DATE,
	"location_id"	INTEGER,
	FOREIGN KEY("subtype_id") REFERENCES "Subtype"("subtype_id"),
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

CREATE TABLE IF NOT EXISTS "Segment" (
	"segment_id"	INTEGER,
	"isolate_epi"	TEXT,
	"segment_type"	TEXT,
	"segment_epi"	TEXT,
	"virus_name"	TEXT,
	"epi_virus_name"	TEXT UNIQUE NOT NULL,
	FOREIGN KEY("isolate_epi") REFERENCES "Isolate"("isolate_epi"),
	PRIMARY KEY("segment_id")
);

CREATE TABLE IF NOT EXISTS "SegmentData" (
    "segment_id" INTEGER,
    "annotation_id" INTEGER,
    "sequence" TEXT,
    FOREIGN KEY("segment_id") REFERENCES "Segment"("segment_id"),
    FOREIGN KEY("annotation_id") REFERENCES "Annotation"("annotation_id"),
    PRIMARY KEY ("segment_id", "annotation_id", "sequence")
);

CREATE TABLE IF NOT EXISTS "Mutation" (
	"mutation_id" INTEGER,
    "segment_cds_type" TEXT,
	"position" INTEGER,
	"ref" TEXT,
	"alt" TEXT,
	"name" TEXT UNIQUE NOT NULL,
	PRIMARY KEY("mutation_id")
);

CREATE TABLE IF NOT EXISTS "SegmentMutations" (
	"segment_id" INTEGER,
	"reference_seg_id" INTEGER,
	"mutation_id" INTEGER,
	FOREIGN KEY("segment_id") REFERENCES "Segment"("segment_id"),
	FOREIGN KEY("mutation_id") REFERENCES "Mutation"("mutation_id"),
	FOREIGN KEY("reference_seg_id") REFERENCES "ReferenceSegment"("reference_seg_id"),
	PRIMARY KEY("segment_id","mutation_id","reference_seg_id")
);

CREATE TABLE IF NOT EXISTS "Subtype" (
	"subtype_id" INTEGER,
	"name" TEXT UNIQUE,
	PRIMARY KEY("subtype_id")
);

-- VIEWS

CREATE VIEW IF NOT EXISTS SegmentMarkers AS
    SELECT segment.segment_id, marker.marker_id
    FROM SegmentData segment
    JOIN Marker marker
    ON segment.annotation_id = marker.annotation_id
    AND SUBSTRING(segment.sequence, marker.position, 1) = marker.allele;

COMMIT;
