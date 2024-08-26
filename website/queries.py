# GENERAL QUERIES


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
#       - The Serotype the Effect was found in
#       - The Paper mentioning the Effect
#
# --------------------------------------------------------------

get_markers_literature = \
 (f"WITH SelectedMarkersIds AS ("
  f"SELECT marker_id FROM Marker "
  f"WHERE name IN ({', '.join(':placeholder' for _ in selected_markers)})) "
  f""
  f"WITH SelectedMarkerGroupsIds AS ("
  f"SELECT DISTINCT marker_group_id FROM MarkerToGroup MTG "
  f"JOIN SelectedMarkersIds SMI ON MTG.marker_id = SMI.marker_id "
  f"GROUP BY MTG.marker_group_id "
  f"HAVING COUNT(DISTINCT MTG.marker_id) = (SELECT COUNT(*) FROM SelectedMarkersIds)) "
  f""
  f"SELECT GROUP_CONCAT(DISTINCT marker.name) AS 'Marker Group', "
  f"effect.effect_full AS 'Effect', effect.host AS 'Host', effect.drug AS 'Drug' "
  f"paper.doi AS 'DOI' "
  f"FROM MarkerGroup markerGroup "
  f"JOIN MarkerToGroup MTG ON markerGroup.marker_group_id = MTG.marker_group_id "
  f"JOIN Marker marker ON MTG.marker_id = marker.marker_id "
  f"JOIN Effect effect ON markerGroup.effect_id = effect.effect_id "
  f"JOIN Paper paper ON markerGroup.paper_id = paper.paper_id "
  f"GROUP BY markerGroup.marker_group_id ")


# --------------------------------------------------------------
# QUERY 2: Get Markers ordered by % human hosts, divided by serotype and segment
# --------------------------------------------------------------
# Description:
#   TODO
#
# Inputs:
#   - (Optional) serotype: Serotype
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
  "JOIN Isolate isolate ON segment.isolate_id = isolate.isolate_id "
  "WHERE isolate.host = 'Human' "
  "AND (segment.segment_type == :segment_type OR :segment_type IS NULL) "
  "AND (isolate.subtype_id == :serotype OR :serotype IS NULL)), "
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
  "SELECT marker.marker_id, COALESCE(HMC.human_marker_count, 0), TMC.total_marker_count, "
  "ROUND(COALESCE(HMC.human_marker_count, 0) * 100.0 / TMC.total_marker_count, 2) AS Percentage "
  "FROM Marker marker "
  "JOIN HumanMarkerCount HMC ON marker.marker_id = HMC.marker_id "
  "JOIN TotalMarkerCount TMC ON marker.marker_id = TMC.marker_id "
  "WHERE :min_perc <= Percentage <= :max_perc "
  "AND TMC.total_marker_count >= :min_n_instances "
  "GROUP BY marker.marker_id "
  "LIMIT :limit) "
  ""
  "SELECT marker1.name AS 'Marker', GROUP_CONCAT(DISTINCT marker2.name, ', ') AS marker_group,"
  "COALESCE(HMC.human_marker_count, 0) as 'Human Instances', TMC.total_marker_count AS 'Total Instances', "
  "ROUND(COALESCE(HMC.human_marker_count, 0) * 100.0 / TMC.total_marker_count, 2) AS Percentage "
  "FROM Marker AS marker1 "
  "JOIN SelectedMarkers selectedMarkers ON marker1.marker_id = selectedMarkers.marker_id "
  "JOIN MarkerToGroup MTG1 ON marker1.marker_id = MTG1.marker_id "
  "JOIN MarkerToGroup MTG2 ON MTG1.marker_group_id = MTG2.marker_group_id "
  "JOIN Marker marker2 ON marker1.marker_id = marker2.marker_id "
  "GROUP BY marker1.name, MTG1.marker_id "
  "ORDER BY Percentage DESC")


# TODO: Query 3
# --------------------------------------------------------------
# QUERY 3: Given a (Group of) Marker count the instances divided by host
# GRAPH
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
#   - For each Marker Group that contains the given makers:
#       - Total number of instances of the Marker Group
#       - Subdivision by host of the instances
#
# --------------------------------------------------------------
# NOTE: view SegmentMarker(segment_id, marker_id), tells whether a marker is found in a given segment

get_group_of_marker_by_n_of_hosts = \
 ("")


# TODO: Query 4
# --------------------------------------------------------------
# QUERY 4: Given a (Group of) Marker count the instances divided by location (normalized)
# GRAPH
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
#   - For each Marker Group that contains the given makers:
#       - Total number of instances of the Marker Group
#       - Subdivision by location of the instances (normalized) by location
#
# --------------------------------------------------------------
# NOTE: view SegmentMarker(segment_id, marker_id), tells whether a marker is found in a given segment

get_group_of_marker_by_n_of_locations = \
 ("")

# --------------------------------------------------------------
# QUERY 5: Get the most common Marker for the selected serotype and segment type with filters
# --------------------------------------------------------------
# Description:
#   TODO
#
# Inputs:
#   - (Optional) serotype: A Serotype
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
  "JOIN Isolate isolate ON segment.isolate_id = isolate.isolate_id "
  "JOIN Location location ON isolate.location_id = location.location_id "
  "WHERE (isolate.host = :host OR :host IS NULL) "
  "AND (location.region = :region OR :region IS NULL) "
  "AND (location.state = :state OR :state IS NULL) "
  "AND (segment.segment_type == :segment_type OR :segment_type IS NULL) "
  "AND (isolate.subtype_id == :serotype OR :serotype IS NULL)), "
  ""
  "SelectedMarkers AS ("
  "SELECT marker_id, COUNT(*) AS selected_marker_count FROM SegmentMarkers "
  "WHERE segment_id IN SelectedSegmentsIds "
  "GROUP BY marker_id ) "
  ""
  "SELECT marker1.name AS 'Marker', GROUP_CONCAT(DISTINCT marker2.name, ', ') AS marker_group, "
  "selected_marker_count AS 'Times Found' "
  "FROM Marker AS marker1 "
  "JOIN SelectedMarkers selectedMarkers ON marker1.marker_id = selectedMarkers.marker_id "
  "JOIN MarkerToGroup MTG1 ON marker1.marker_id = MTG1.marker_id "
  "JOIN MarkerToGroup MTG2 ON MTG1.marker_group_id = MTG2.marker_group_id "
  "JOIN Marker marker2 ON marker1.marker_id = marker2.marker_id "
  "GROUP BY marker1.name, MTG1.marker_id "
  "ORDER BY selected_marker_count DESC ")


# TODO: subqueries where the filter is in the group by, so that I can put data in graphs?
# --------------------------------------------------------------
# QUERY 6: Get N. of instances of distinct Markers for each host
# GRAPH
# --------------------------------------------------------------
# Description:
#   TODO
#
# Inputs:
#   - (Optional) serotype: A Serotype
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
  "JOIN Isolate isolate ON segment.isolate_id = isolate.isolate_id "
  "WHERE (segment.segment_type == :segment_type OR :segment_type IS NULL) "
  "AND (isolate.subtype_id == :serotype OR :serotype IS NULL)) "
  ""
  "SELECT selectedSegments.host AS 'Host', "
  "COUNT(DISTINCT segmentMarkers.marker_id) AS selected_marker_count "
  "FROM SelectedSegments selectedSegments "
  "JOIN SegmentMarkers segmentMarkers ON selectedSegments.segment_id = segmentMarkers.segment_id "
  "GROUP BY selectedSegments.host "
  "ORDER BY selected_marker_count DESC ")

# TODO: Query 7: For each mutation get the number of segments that exhibit it, and the percentage over the total number of segments

# --------------------------------------------------------------
# QUERY 8: Given a Segment Type find the Most Mutable Zones
# GRAPH
# --------------------------------------------------------------
# Description:
#   TODO
#
# Inputs:
#   - segment_type: Segment to be analyzed
#   - serotype: Serotype to be analyzed
#   - reference: Which reference to take into account for the mutations
#   - list of bins: List of (start, end) of interests
#   OR
#   - bin_size: Uniform size for the bins
#
# Outputs:
#   - Bins, ordered by average number of mutations in them (?), and how much they have mutated
#
# --------------------------------------------------------------

get_segment_mutability_zones = \
 ("")


# --------------------------------------------------------------
# QUERY 9: TODO
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

x = \
 ("")


# QUERIES ONTOLOGY

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
#       - The Serotype the Effect was found in
#       - The Paper mentioning the Effect
#
# --------------------------------------------------------------

get_group_of_marker = \
 ("SELECT marker1.name AS 'Marker', GROUP_CONCAT(DISTINCT marker2.name, ', ') AS 'Group', "
  "effect.effect_full AS 'Effect', effect.host AS 'Host', effect.drug AS 'Drug', "
  "paper.doi AS 'DOI' "
  "FROM Marker marker1 "
  "JOIN MarkerToGroup MTG1 ON marker1.marker_id = MTG1.marker_id "
  "JOIN MarkerToGroup MTG2 ON MTG1.marker_group_id = MTG2.marker_group_id "
  "JOIN Marker marker2 ON marker1.marker_id = marker2.marker_id "
  "JOIN MarkerGroup markerGroup ON MTG1.marker_group_id = markerGroup.marker_group_id "
  "JOIN Effect effect ON markerGroup.effect_id = effect.effect_id "
  "JOIN Paper paper ON markerGroup.paper_id = paper.paper_id ")


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
 ("SELECT GROUP_CONCAT(DISTINCT marker.name, ', ') AS 'Group', "
  "paper.doi AS 'DOI' "
  "FROM Effect effect "
  "JOIN MarkerGroup markerGroup ON effect.effect_id = markerGroup.effect_id "
  "JOIN Paper paper ON markerGroup.paper_id = paper.paper_id "
  "JOIN MarkerToGroup MTG ON markerGroup.marker_group_id = MTG.marker_group_id "
  "JOIN Marker marker ON MTG.marker_id = marker.marker_id "
  "GROUP BY markerGroup.marker_group_id ")