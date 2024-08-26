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
  `segment_type` string,
  `dna_fasta` text,
  `protein_fasta` text
);

CREATE TABLE `Annotation` (
  `reference_id` integer,
  `annotation_id` integer,
  `annotation_name` string,
  `annotation_type` int
);

CREATE TABLE `Intein` (
  `intein_id` int,
  `annotation_id` integer,
  `start_pos` integer,
  `end_pos` integer
);

CREATE TABLE `ReferenceOfSerotype` (
  `reference_id` int,
  `subtype_id` int
);

CREATE TABLE `Subtype` (
  `subtype_id` integer,
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

CREATE TABLE `MarkerToGroup` (
  `marker_id` integer,
  `marker_group_id` integer
);

CREATE TABLE `MarkerGroupToSubtype` (
  `subtype_id` integer,
  `marker_group_id` integer,
  `notes` text
);

CREATE TABLE `MarkerGroup` (
  `marker_group_id` integer,
  `paper_id` integer,
  `effect_id` integer
);

ALTER TABLE `SegmentMutations` ADD FOREIGN KEY (`segment_id`) REFERENCES `Segment` (`segment_id`);

ALTER TABLE `SegmentMutations` ADD FOREIGN KEY (`mutation_id`) REFERENCES `Mutation` (`mutation_id`);

ALTER TABLE `MutationMarkerView` ADD FOREIGN KEY (`mutation_id`) REFERENCES `Mutation` (`mutation_id`);

ALTER TABLE `SegmentMutations` ADD FOREIGN KEY (`reference_id`) REFERENCES `ReferenceSegment` (`reference_id`);

ALTER TABLE `Isolate` ADD FOREIGN KEY (`location_id`) REFERENCES `Location` (`location_id`);

ALTER TABLE `Isolate` ADD FOREIGN KEY (`serotype_id`) REFERENCES `Subtype` (`subtype_id`);

ALTER TABLE `Annotation` ADD FOREIGN KEY (`reference_id`) REFERENCES `ReferenceSegment` (`reference_id`);

ALTER TABLE `Segment` ADD FOREIGN KEY (`isolate_id`) REFERENCES `Isolate` (`isolate_id`);

ALTER TABLE `Mutation` ADD FOREIGN KEY (`annotation_id`) REFERENCES `Annotation` (`annotation_id`);

ALTER TABLE `SegmentData` ADD FOREIGN KEY (`segment_id`) REFERENCES `Segment` (`segment_id`);

ALTER TABLE `SegmentMarkersView` ADD FOREIGN KEY (`segment_id`) REFERENCES `SegmentData` (`segment_id`);

CREATE TABLE `Marker_MarkerToGroup` (
  `Marker_marker_id` int,
  `MarkerToGroup_marker_id` integer,
  PRIMARY KEY (`Marker_marker_id`, `MarkerToGroup_marker_id`)
);

ALTER TABLE `Marker_MarkerToGroup` ADD FOREIGN KEY (`Marker_marker_id`) REFERENCES `Marker` (`marker_id`);

ALTER TABLE `Marker_MarkerToGroup` ADD FOREIGN KEY (`MarkerToGroup_marker_id`) REFERENCES `MarkerToGroup` (`marker_id`);


ALTER TABLE `SegmentMarkersView` ADD FOREIGN KEY (`marker_id`) REFERENCES `Marker` (`marker_id`);

ALTER TABLE `Marker` ADD FOREIGN KEY (`annotation_id`) REFERENCES `Annotation` (`annotation_id`);

ALTER TABLE `MutationMarkerView` ADD FOREIGN KEY (`marker_id`) REFERENCES `Marker` (`marker_id`);

ALTER TABLE `Intein` ADD FOREIGN KEY (`annotation_id`) REFERENCES `Annotation` (`annotation_id`);

CREATE TABLE `ReferenceOfSerotype_ReferenceSegment` (
  `ReferenceOfSerotype_reference_id` int,
  `ReferenceSegment_reference_id` integer,
  PRIMARY KEY (`ReferenceOfSerotype_reference_id`, `ReferenceSegment_reference_id`)
);

ALTER TABLE `ReferenceOfSerotype_ReferenceSegment` ADD FOREIGN KEY (`ReferenceOfSerotype_reference_id`) REFERENCES `ReferenceOfSerotype` (`reference_id`);

ALTER TABLE `ReferenceOfSerotype_ReferenceSegment` ADD FOREIGN KEY (`ReferenceSegment_reference_id`) REFERENCES `ReferenceSegment` (`reference_id`);


CREATE TABLE `ReferenceOfSerotype_Subtype` (
  `ReferenceOfSerotype_subtype_id` int,
  `Subtype_subtype_id` integer,
  PRIMARY KEY (`ReferenceOfSerotype_subtype_id`, `Subtype_subtype_id`)
);

ALTER TABLE `ReferenceOfSerotype_Subtype` ADD FOREIGN KEY (`ReferenceOfSerotype_subtype_id`) REFERENCES `ReferenceOfSerotype` (`subtype_id`);

ALTER TABLE `ReferenceOfSerotype_Subtype` ADD FOREIGN KEY (`Subtype_subtype_id`) REFERENCES `Subtype` (`subtype_id`);


CREATE TABLE `MarkerToGroup_MarkerGroup` (
  `MarkerToGroup_marker_group_id` integer,
  `MarkerGroup_marker_group_id` integer,
  PRIMARY KEY (`MarkerToGroup_marker_group_id`, `MarkerGroup_marker_group_id`)
);

ALTER TABLE `MarkerToGroup_MarkerGroup` ADD FOREIGN KEY (`MarkerToGroup_marker_group_id`) REFERENCES `MarkerToGroup` (`marker_group_id`);

ALTER TABLE `MarkerToGroup_MarkerGroup` ADD FOREIGN KEY (`MarkerGroup_marker_group_id`) REFERENCES `MarkerGroup` (`marker_group_id`);


CREATE TABLE `MarkerGroupToSubtype_MarkerGroup` (
  `MarkerGroupToSubtype_marker_group_id` integer,
  `MarkerGroup_marker_group_id` integer,
  PRIMARY KEY (`MarkerGroupToSubtype_marker_group_id`, `MarkerGroup_marker_group_id`)
);

ALTER TABLE `MarkerGroupToSubtype_MarkerGroup` ADD FOREIGN KEY (`MarkerGroupToSubtype_marker_group_id`) REFERENCES `MarkerGroupToSubtype` (`marker_group_id`);

ALTER TABLE `MarkerGroupToSubtype_MarkerGroup` ADD FOREIGN KEY (`MarkerGroup_marker_group_id`) REFERENCES `MarkerGroup` (`marker_group_id`);


CREATE TABLE `MarkerGroupToSubtype_Subtype` (
  `MarkerGroupToSubtype_subtype_id` integer,
  `Subtype_subtype_id` integer,
  PRIMARY KEY (`MarkerGroupToSubtype_subtype_id`, `Subtype_subtype_id`)
);

ALTER TABLE `MarkerGroupToSubtype_Subtype` ADD FOREIGN KEY (`MarkerGroupToSubtype_subtype_id`) REFERENCES `MarkerGroupToSubtype` (`subtype_id`);

ALTER TABLE `MarkerGroupToSubtype_Subtype` ADD FOREIGN KEY (`Subtype_subtype_id`) REFERENCES `Subtype` (`subtype_id`);


ALTER TABLE `MarkerGroup` ADD FOREIGN KEY (`effect_id`) REFERENCES `Effect` (`effect_id`);

ALTER TABLE `MarkerGroup` ADD FOREIGN KEY (`paper_id`) REFERENCES `Paper` (`paper_id`);
