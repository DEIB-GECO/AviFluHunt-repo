# GENERAL QUERIES
get_hosts = \
 ("SELECT DISTINCT host "
  "FROM Isolate")

get_markers = \
 ("SELECT DISTINCT name "
  "FROM Marker")

get_subtypes = \
 ("SELECT DISTINCT subtype_id, name "
  "FROM Subtype")

get_segments = \
 ("SELECT DISTINCT segment_type "
  "FROM ReferenceSegment")

get_regions = \
 ("SELECT DISTINCT region "
  "FROM Location")

get_states = \
 ("SELECT DISTINCT region, state "
  "FROM Location")

# QUERIES
# --------------------------------------------------------------
# QUERY TODO: TODO
# --------------------------------------------------------------
# Description:
#   TODO
#
# Inputs:
#   - TODO (type): TODO
#
# Outputs:
#   - TODO (type): TODO
#
# --------------------------------------------------------------

# CHECKED
# --------------------------------------------------------------
# QUERY 1: Select the literature data associated to a group of Markers
# --------------------------------------------------------------
# Description:
#   TODO
#
# Inputs:
#   - A list of Markers
#       - After the first on is selected only Markers in group with the selected ones can be
#         further selected
#
# Outputs:
#   - A list of all Markers groups that contain the input Markers, and for each:
#       - The associated Effect
#       - The subtype the Effect was found in
#       - The Paper mentioning the Effect
#
# EXAMPLE: HA1:156A
# --------------------------------------------------------------

get_markers_literature = \
    (f"WITH SelectedMarkersIds AS ("
     f"SELECT marker_id FROM Marker "
     f"WHERE name IN (placeholder)), "
     f""
     f"SelectedMarkerGroupsIds AS ("
     f"SELECT DISTINCT marker_group_id FROM MarkerToGroup MTG "
     f"JOIN SelectedMarkersIds SMI ON MTG.marker_id = SMI.marker_id "
     f"GROUP BY MTG.marker_group_id "
     f"HAVING COUNT(DISTINCT MTG.marker_id) = (SELECT COUNT(*) FROM SelectedMarkersIds)), "
     f""
     f"MarkerGroupsNames AS ( "
     f"SELECT marker_group_id, GROUP_CONCAT(marker.name, ', ') AS group_names "
     f"FROM Marker marker "
     f"JOIN MarkerToGroup MTG ON marker.marker_id = MTG.marker_id "
     f"WHERE marker_group_id IN SelectedMarkerGroupsIds "
     f"GROUP BY marker_group_id) "
     ""
     f"SELECT group_names AS 'Marker Group', "
     f"effect.effect_full AS 'Effect', effect.host AS 'Host', effect.drug AS 'Drug', "
     f"paper.doi AS 'DOI' "
     f"FROM MarkerGroupsNames MGN "
     f"JOIN MarkerGroupPaperAndEffect MGPAE ON MGN.marker_group_id = MGPAE.marker_group_id "
     f"JOIN Effect effect ON MGPAE.effect_id = effect.effect_id "
     f"JOIN Paper paper ON MGPAE.paper_id = paper.paper_id "
     f"GROUP BY MGPAE.marker_group_id ")

# CHECKED
# --------------------------------------------------------------
# QUERY 2: Get Markers ordered by % human hosts, divided by subtype and segment
# --------------------------------------------------------------
# Description:
#   TODO
#
# Inputs:
#   - (Optional) subtype: subtype
#   - (Optional) segment_type: Segment type
#   - (Optional Filter) min_perc, max_perc: Percentage range (default = (0, 100))
#   - (Optional Filter) limit: Limit in the number of results (default = 10000)
#   - (Optional Filter) min_n_instance: Min number of Segments that must contain the Marker (default = 1)
#
# Outputs:
#   - A list of all Markers ordered by percentage of human hosts in the given range, and for each:
#       - The Groups it belongs to
#
# --------------------------------------------------------------
# NOTE: view SegmentMarker(segment_id, marker_id), tells whether a marker is found in a given segment

get_markers_by_human_percentage = \
    ("WITH SelectedSegmentsIds AS ("
     "SELECT DISTINCT segment.segment_id "
     "FROM Segment segment "
     "JOIN Isolate isolate ON segment.isolate_id = isolate.isolate_epi "
     "JOIN Subtype subtype ON isolate.subtype_id = subtype.subtype_id "
     "WHERE isolate.host = 'Human' "
     "AND (segment.segment_type == :segment_type OR :segment_type IS NULL) "
     "AND (subtype.name == :subtype OR :subtype IS NULL)), "
     ""
     "HumanMarkerCount AS ("
     "SELECT marker_id, COUNT(*) AS human_marker_count FROM SegmentMarkers "
     "WHERE segment_id IN SelectedSegmentsIds "
     "GROUP BY marker_id), "
     ""
     "TotalMarkerCount AS ("
     "SELECT marker_id, COUNT(*) AS total_marker_count FROM SegmentMarkers "
     "GROUP BY marker_id), "
     ""
     "SelectedMarkers AS ("
     "SELECT marker.marker_id, COALESCE(HMC.human_marker_count, 0) as human_marker_count, "
     "TMC.total_marker_count as total_marker_count,"
     "ROUND(COALESCE(HMC.human_marker_count, 0) * 100.0 / TMC.total_marker_count, 2) AS percentage "
     "FROM Marker marker "
     "JOIN HumanMarkerCount HMC ON marker.marker_id = HMC.marker_id "
     "JOIN TotalMarkerCount TMC ON marker.marker_id = TMC.marker_id "
     "WHERE ROUND(COALESCE(HMC.human_marker_count, 0) * 100.0 / TMC.total_marker_count, 2) "
     "BETWEEN :min_perc AND :max_perc "
     "AND TMC.total_marker_count >= :min_n_instances "
     "GROUP BY marker.marker_id "
     "LIMIT :limit), "
     ""
     "MarkerGroupsNames AS ("
     "SELECT marker_group_id, GROUP_CONCAT(marker.name, ', ') AS group_names "
     "FROM Marker marker "
     "JOIN MarkerToGroup MTG ON marker.marker_id = MTG.marker_id "
     "GROUP BY marker_group_id) "
     ""
     "SELECT marker.name AS 'Marker', "
     "GROUP_CONCAT(CONCAT('(', "
     "(SELECT group_names "
     "FROM MarkerGroupsNames "
     "WHERE marker_group_id = MTG.marker_group_id), ')'), ' ') as 'Groups', "
     "COALESCE(selectedMarkers.human_marker_count, 0) as 'Human Instances', "
     "selectedMarkers.total_marker_count AS 'Total Instances', "
     "selectedMarkers.percentage AS Percentage "
     "FROM Marker AS marker "
     "JOIN SelectedMarkers selectedMarkers ON marker.marker_id = selectedMarkers.marker_id "
     "JOIN MarkerToGroup MTG ON marker.marker_id = MTG.marker_id "
     "GROUP BY marker.marker_id "
     "ORDER BY Percentage DESC")

# CHECKED
# --------------------------------------------------------------
# QUERY 3: Get markers by difference in relative presence in hosts
# GRAPH
# --------------------------------------------------------------
# Description:
#   TODO
#
# Inputs:
#   - (Optional) host1: The first host to consider for the analysis
#       - host2: The second host to be compared with host1
#
# Outputs:
#   - For each Marker its relative presence in any host type, sorted by the difference in presence
#     between host1 and host 2
#
# --------------------------------------------------------------
# NOTE: view SegmentMarker(segment_id, marker_id), tells whether a marker is found in a given segment
# ATTENTION: This query only returns (marker, host%), to aggregate data python is necessary!

get_markers_id_by_host_relative_presence = \
    ("WITH SegmentsByHost AS ("
     "SELECT DISTINCT segment.segment_id, isolate.host "
     "FROM Segment segment "
     "JOIN Isolate isolate ON segment.isolate_id = isolate.isolate_epi "
     "WHERE host in (hosts)), "
     ""
     "MarkerCountByHost AS ( "
     "SELECT segmentMarkers.marker_id, SBH.host, COUNT(DISTINCT segmentMarkers.segment_id) AS marker_host_count "
     "FROM SegmentMarkers segmentMarkers "
     "JOIN SegmentsByHost SBH ON segmentMarkers.segment_id = SBH.segment_id "
     "GROUP BY segmentMarkers.marker_id, SBH.host), "
     ""
     "TotalSegmentCountByHost AS ( "
     "SELECT host, COUNT(DISTINCT segment_id) AS host_count "
     "FROM SegmentsByHost "
     "GROUP BY host ) "
     ""
     "SELECT distinct marker.name as 'Marker', MCbH.host, "
     "ROUND(MCbH.marker_host_count * 100.0 / TSCbH.host_count, 2) AS 'percentage' "
     "FROM MarkerCountByHost MCbH "
     "JOIN TotalSegmentCountByHost TSCbH  ON MCbH.host = TSCbH.host "
     "JOIN Marker marker ON MCbH.marker_id = marker.marker_id")

# TODO: Query 4
# --------------------------------------------------------------
# QUERY 4:
# GRAPH
# --------------------------------------------------------------
# Description:
#   TODO
#
# Inputs:
#   -
#
# Outputs:
#   -
#
# --------------------------------------------------------------
# NOTE: view SegmentMarker(segment_id, marker_id), tells whether a marker is found in a given segment

get_markers_by_location_relative_presence = \
    ("")

# CHECKED
# --------------------------------------------------------------
# QUERY 5: Get the most common Marker for the selected subtype and segment type with filters
# --------------------------------------------------------------
# Description:
#   TODO
#
# Inputs:
#   - (Optional) subtype: A subtype
#   - (Optional) segment_type: A Segment type
#   - (Optional Filter) host: Host type
#   - (Optional Filter) region: Geographical Region
#   - (Optional Filter) state: State in the Region Selected
#
# Outputs:
#   - A list of all Markers ordered by their prevalence given the filters:
#       - The Groups it belongs to
#       - The N. of times it was found
#
# --------------------------------------------------------------
# NOTE: view SegmentMarker(segment_id, marker_id), tells whether a marker is found in a given segment

get_most_common_markers_by_filters = \
    ("WITH SelectedSegmentsIds AS ("
     "SELECT DISTINCT segment.segment_id "
     "FROM Segment segment "
     "JOIN Isolate isolate ON segment.isolate_id = isolate.isolate_epi "
     "JOIN Location location ON isolate.location_id = location.location_id "
     "JOIN Subtype subtype ON isolate.subtype_id = subtype.subtype_id "
     "WHERE (isolate.host = :host OR :host IS NULL) "
     "AND (location.region = :region OR :region IS NULL) "
     "AND (location.state = :state OR :state IS NULL) "
     "AND (segment.segment_type == :segment_type OR :segment_type IS NULL) "
     "AND (subtype.name == :subtype OR :subtype IS NULL)), "
     ""
     "SelectedMarkers AS ( "
     "SELECT marker_id, COUNT(*) AS selected_marker_count FROM SegmentMarkers "
     "WHERE segment_id IN SelectedSegmentsIds "
     "GROUP BY marker_id ), "
     ""
     "MarkerGroupsNames AS ( "
     "SELECT marker_group_id, GROUP_CONCAT(marker.name, ', ') AS group_names "
     "FROM Marker marker "
     "JOIN MarkerToGroup MTG ON marker.marker_id = MTG.marker_id "
     "GROUP BY marker_group_id) "
     ""
     "SELECT marker.name AS 'Marker', "
     "selected_marker_count AS 'Times Found', "
     "GROUP_CONCAT( "
     "CONCAT('(', "
     "(SELECT group_names "
     "FROM MarkerGroupsNames "
     "WHERE marker_group_id = MTG.marker_group_id), ')'), ' ') as 'Groups' "
     "FROM Marker AS marker "
     "JOIN SelectedMarkers selectedMarkers ON marker.marker_id = selectedMarkers.marker_id "
     "JOIN MarkerToGroup MTG ON marker.marker_id = MTG.marker_id "
     "GROUP BY marker.marker_id "
     "ORDER BY selected_marker_count DESC")

# TODO: subqueries where the filter is in the group by, so that I can put data in graphs?
# CHECKED
# --------------------------------------------------------------
# QUERY 6: Get N. of instances of distinct Markers for each host
# GRAPH
# --------------------------------------------------------------
# Description:
#   TODO
#
# Inputs:
#   - (Optional) subtype: A subtype
#   - (Optional) segment_type: A Segment type
#
# Outputs:
#   - A list of the Hosts with the number of DISTINCT Markers found in that host
#
# --------------------------------------------------------------
# NOTE: view SegmentMarker(segment_id, marker_id), tells whether a marker is found in a given segment

get_host_by_n_of_markers = \
    ("WITH SelectedSegments AS ("
     "SELECT DISTINCT segment.segment_id, isolate.host "
     "FROM Segment segment "
     "JOIN Isolate isolate ON segment.isolate_id = isolate.isolate_epi "
     "JOIN Subtype subtype ON isolate.subtype_id = subtype.subtype_id "
     "WHERE (segment.segment_type == :segment_type OR :segment_type IS NULL) "
     "AND (subtype.name == :subtype OR :subtype IS NULL)) "
     ""
     "SELECT selectedSegments.host AS 'Host', "
     "COUNT(DISTINCT segmentMarkers.marker_id) AS 'Distinct Markers Per Host' "
     "FROM SelectedSegments selectedSegments "
     "JOIN SegmentMarkers segmentMarkers ON selectedSegments.segment_id = segmentMarkers.segment_id "
     "GROUP BY selectedSegments.host "
     "ORDER BY COUNT(DISTINCT segmentMarkers.marker_id) DESC ")

# CHECKED
# --------------------------------------------------------------
# QUERY 7: Get how common is each Marker
# GRAPH
# --------------------------------------------------------------
# Description:
#   TODO
#
# Inputs:
#   - (Optional Filter) min_perc, max_perc: Percentage range (default = (0, 100))
#   - (Optional Filter) limit: Limit in the number of results (default = 10000)
#
# Outputs:
#   - Markers and percentage of appearance sorted
#
# --------------------------------------------------------------

get_markers_by_relevance = \
    ("WITH MarkerCount AS ( "
     "SELECT marker_id, COUNT(DISTINCT segment_id) AS marker_count "
     "FROM SegmentMarkers "
     "GROUP BY marker_id), "
     ""
     "TotalCount AS ("
     "SELECT COUNT(DISTINCT segment_id) AS total_count "
     "FROM SegmentMarkers) "
     ""
     "SELECT marker.name AS 'Marker', "
     "ROUND((markerCount.marker_count * 100.0) / totalCount.total_count, 2) AS 'Percentage' "
     "FROM Marker marker "
     "JOIN MarkerCount markerCount ON marker.marker_id = markerCount.marker_id "
     "CROSS JOIN TotalCount totalCount "
     "WHERE (markerCount.marker_count * 100.0) / totalCount.total_count BETWEEN :min_perc AND :max_perc "
     "ORDER BY ROUND((markerCount.marker_count * 100.0) / totalCount.total_count, 2) DESC "
     "LIMIT :limit")

# --------------------------------------------------------------
# QUERY 8: Given a Segment Type find the Most Mutable Zones
# GRAPH
# --------------------------------------------------------------
# Description:
#   TODO
#
# Inputs:
#   - segment_type: Segment to be analyzed
#   - subtype: subtype to be analyzed
#   - reference: Which reference to take into account for the mutations
#   - list of bins: List of (start, end) of interests
#   OR
#   - bin_size: Uniform size for the bins
#
# Outputs:
#   - Bins, ordered by average number of mutations in them (?), and how much they have mutated
#
# --------------------------------------------------------------
# IDEA: select only mutations that are markers?

bins = []
get_segment_mutability_zones = \
    ("WITH SelectedSegments AS ("
     "SELECT DISTINCT segment.segment_id, isolate.host "
     "FROM Segment segment "
     "JOIN Isolate isolate ON segment.isolate_id = isolate.isolate_epi "
     "WHERE (segment.segment_type == :segment_type OR :segment_type IS NULL) "
     "AND (isolate.subtype_id == :subtype OR :subtype IS NULL)), "
     ""
     "CountPerBin AS ("
     "SELECT start_range, end_range, COUNT(DISTINCT mutation.mutation_id) AS bin_count "
     "FROM Mutation mutation "
     f"JOIN (VALUES {', '.join([f"({start}, {end})" for start, end in bins])}) "
     "AS Bins (start_range, end_range) "
     "ON Mutation.position BEWTWEEN Bins.start_range AND Bins.end_range "
     "JOIN SegmentMutations segmentMutations ON mutation.mutation_id = segmentMutations.mutation_id "
     "JOIN SelectedSegments selectedSegments ON segmentMutations.segment_id = selectedSegments.segment_id "
     "WHERE (segmentMutations.reference_id = :reference_id OR :reference_id IS NULL) "
     "GROUP BY Bins.start_range, Bins.end_range "
     "ORDER BY distinct_id_count DESC) "
     ""
     "SELECT start_range AS 'From', end_range AS 'To', bin_count FROM CountPerBin AS 'Total Mutations'")

# QUERIES ONTOLOGY

# CHECKED
# --------------------------------------------------------------
# QUERY ???: Retrieve the Marker Groups that contain a specific Marker
# --------------------------------------------------------------
# Description:
#   TODO
#
# Inputs:
#   - marker: A Marker
#
# Outputs:
#   - A list of all Marker Groups that contain that Marker and, for each group:
#       - The associated Effect
#       - The subtype the Effect was found in
#       - The Paper mentioning the Effect
#
# --------------------------------------------------------------

get_group_of_marker = \
    ("WITH MarkerGroupsNames AS ( "
     "SELECT marker_group_id, GROUP_CONCAT(marker.name, ', ') AS group_names "
     "FROM Marker marker "
     "JOIN MarkerToGroup MTG ON marker.marker_id = MTG.marker_id "
     "GROUP BY marker_group_id) "
     ""
     "SELECT group_names AS 'Group',"
     "effect.effect_full AS 'Effect', "
     "paper.doi AS 'DOI' "
     "FROM MarkerGroupsNames MGN "
     "JOIN MarkerGroupPaperAndEffect MGPAE ON MGN.marker_group_id = MGPAE.marker_group_id "
     "JOIN Effect effect ON MGPAE.effect_id = effect.effect_id "
     "JOIN Paper paper ON MGPAE.paper_id = paper.paper_id "
     "WHERE MGN.marker_group_id IN ( "
     "SELECT marker_group_id FROM MarkerToGroup WHERE marker_id = "
     "(SELECT marker_id FROM Marker WHERE name = :marker_name))")


# CHECKED
# --------------------------------------------------------------
# QUERY ???: Retrieve the Effects associated to Host/Drug
# --------------------------------------------------------------
# Description:
#   TODO
#
# Inputs:
#   - (Optional) host: A Host type
#   - (Optional) drug: A Drug type
#
# Outputs:
#   - A list of all Effects associated to the given Host and/or Drug
#
# --------------------------------------------------------------

get_effects_by_effect_metadata = \
    ("SELECT effect_full AS 'Effect', effect_type AS 'Type', "
     "host AS 'Host', drug AS 'Drug' "
     "FROM Effect effect "
     "WHERE (host = :host OR :host IS NULL) "
     "AND (drug = :drug OR :drug IS NULL)")


# CHECKED
# --------------------------------------------------------------
# QUERY ???: Retrieve the Groups associated to a particular Effect
# --------------------------------------------------------------
# Description:
#   TODO
#
# Inputs:
#   - (Optional) effect: Effect
#
# Outputs:
#   - A list of Marker Groups associated with the effect and the doi of the paper where they were found
#
# --------------------------------------------------------------

get_marker_groups_by_effect = \
    ("WITH MarkerGroupsNames AS ( "
     "SELECT marker_group_id, GROUP_CONCAT(marker.name, ', ') AS group_names "
     "FROM Marker marker "
     "JOIN MarkerToGroup MTG ON marker.marker_id = MTG.marker_id "
     "GROUP BY marker_group_id) "
     ""
     "SELECT group_names AS 'Group', "
     "paper.doi AS 'DOI' "
     "FROM Effect effect "
     "JOIN MarkerGroupPaperAndEffect MGPAE ON MGPAE.effect_id = effect.effect_id "
     "JOIN MarkerGroupsNames MGN ON MGPAE.marker_group_id = MGN.marker_group_id "
     "JOIN Paper paper ON MGPAE.paper_id = paper.paper_id "
     "WHERE effect.effect_full = :effect_full ")
