CREATE TABLE `Marker` (
  `pos` int,
  `allele` string,
  `annotation_id` int,
  `marker_id` int
);

CREATE TABLE `SegmentMarkersView` (
  `segment_id` int,
  `marker_id` int
);

CREATE TABLE `SegmentData` (
  `segment_id` int,
  `annotation_id` int,
  `sequence` string
);

CREATE TABLE `Location` (
  `location_id` integer,
  `region` string,
  `state` string,
  `city` string
);

CREATE TABLE `Isolate` (
  `isolate_id` integer,
  `isolate_epi` string,
  `serotype_id` integer,
  `host` string,
  `collection_date` date,
  `location_id` integer
);

CREATE TABLE `Segment` (
  `segment_id` integer,
  `isolate_id` integer,
  `segment_type` string,
  `segment_epi` string,
  `virus_name` string,
  `epi_virus_name` string
);

CREATE TABLE `ReferenceSegment` (
  `reference_id` integer,
  `serotype_id` integer,
  `segment_type` string,
  `dna_fasta` text,
  `protein_fasta` text
);

CREATE TABLE `Annotation` (
  `reference_id` integer,
  `annotation_id` integer,
  `annotation_name` string,
  `annotation_type` int,
  `start_pos` integer,
  `end_pos` integer
);

CREATE TABLE `Serotype` (
  `serotype_id` integer,
  `name` string
);

CREATE TABLE `Mutation` (
  `mutation_id` integer,
  `mutation_name` string,
  `serotype_name` string,
  `annotation_id` integer,
  `annotation_name` string,
  `position` integer,
  `ref` string,
  `alt` string
);

CREATE TABLE `SegmentMutations` (
  `segment_id` integer,
  `reference_id` integer,
  `mutation_id` integer
);

CREATE TABLE `MutationMarkerView` (
  `mutation_id` integer,
  `marker_id` integer
);

CREATE TABLE `Effect` (
  `effect_id` integer,
  `effect_type` string,
  `host` string,
  `drug` string,
  `effect_full` string
);

CREATE TABLE `Paper` (
  `paper_id` integer,
  `title` string,
  `authors` string,
  `year` integer,
  `journal` string,
  `address` string,
  `doi` string
);

CREATE TABLE `PaperAndEffectOfMarker` (
  `paper_effect_marker_id` integer,
  `marker_id` integer,
  `paper_id` integer,
  `effect_id` integer,
  `subtype` string,
  `in_vivo` integer,
  `in_vitro` integer
);

ALTER TABLE `SegmentMutations` ADD FOREIGN KEY (`segment_id`) REFERENCES `Segment` (`segment_id`);

ALTER TABLE `SegmentMutations` ADD FOREIGN KEY (`mutation_id`) REFERENCES `Mutation` (`mutation_id`);

ALTER TABLE `MutationMarkerView` ADD FOREIGN KEY (`mutation_id`) REFERENCES `Mutation` (`mutation_id`);

ALTER TABLE `PaperAndEffectOfMarker` ADD FOREIGN KEY (`effect_id`) REFERENCES `Effect` (`effect_id`);

ALTER TABLE `PaperAndEffectOfMarker` ADD FOREIGN KEY (`paper_id`) REFERENCES `Paper` (`paper_id`);

ALTER TABLE `SegmentMutations` ADD FOREIGN KEY (`reference_id`) REFERENCES `ReferenceSegment` (`reference_id`);

ALTER TABLE `ReferenceSegment` ADD FOREIGN KEY (`serotype_id`) REFERENCES `Serotype` (`serotype_id`);

ALTER TABLE `Isolate` ADD FOREIGN KEY (`location_id`) REFERENCES `Location` (`location_id`);

ALTER TABLE `Isolate` ADD FOREIGN KEY (`serotype_id`) REFERENCES `Serotype` (`serotype_id`);

ALTER TABLE `Annotation` ADD FOREIGN KEY (`reference_id`) REFERENCES `ReferenceSegment` (`reference_id`);

ALTER TABLE `Segment` ADD FOREIGN KEY (`isolate_id`) REFERENCES `Isolate` (`isolate_id`);

ALTER TABLE `Mutation` ADD FOREIGN KEY (`annotation_id`) REFERENCES `Annotation` (`annotation_id`);

ALTER TABLE `SegmentData` ADD FOREIGN KEY (`segment_id`) REFERENCES `Segment` (`segment_id`);

ALTER TABLE `SegmentMarkersView` ADD FOREIGN KEY (`segment_id`) REFERENCES `SegmentData` (`segment_id`);

ALTER TABLE `SegmentMarkersView` ADD FOREIGN KEY (`marker_id`) REFERENCES `Marker` (`marker_id`);

ALTER TABLE `Marker` ADD FOREIGN KEY (`annotation_id`) REFERENCES `Annotation` (`annotation_id`);

ALTER TABLE `MutationMarkerView` ADD FOREIGN KEY (`marker_id`) REFERENCES `Marker` (`marker_id`);

ALTER TABLE `PaperAndEffectOfMarker` ADD FOREIGN KEY (`marker_id`) REFERENCES `Marker` (`marker_id`);
