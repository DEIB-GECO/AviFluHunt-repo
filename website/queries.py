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
  f"SELECT GROUP_CONCAT(DISTINCT marker.name) AS 'Full Marker Group', "
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
#   - (Optional Filter) limit: Limit in the number of results (default = no limit)
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
  "AND (isolate.serotype_id == :serotype OR :serotype IS NULL)), "
  ""
  "HumanMarkerCount AS ("
  "SELECT marker_id, COUNT(*) human_marker_count FROM SegmentMarkers "
  "WHERE segment_id IN SelectedSegmentsIds "
  "GROUP BY marker_id), "
  ""
  "TotalMarkerCount AS ("
  "SELECT marker_id, COUNT(*) as total_marker_count FROM SegmentMarkers "
  "GROUP BY marker_id), "
  ""
  "SelectedMarkers AS ("
  "SELECT marker.marker_id, COALESCE(HMC.human_marker_count, 0), TMC.total_marker_count, "
  "ROUND(COALESCE(HMC.human_marker_count, 0) * 100.0 / TMC.total_marker_count, 2) AS Percentage "
  "FROM Marker marker "
  "JOIN HumanMarkerCount HMC ON marker.marker_id = HMC.marker_id "
  "JOIN TotalMarkerCount TMC ON marker.marker_id = TMC.marker_id "
  "GROUP BY marker.marker_id) "
  ""
  ""  # ATTENTION: the following query returns the results SEPARATED
  "SELECT marker1.name AS 'Marker', GROUP_CONCAT(DISTINCT marker2.name, ', ') AS marker_group "
  "FROM Marker AS marker1 "
  "JOIN MarkerToGroup MTG1 ON marker1.marker_id = MTG1.marker_id "
  "JOIN MarkerToGroup MTG2 ON MTG1.marker_group_id = MTG2.marker_group_id "
  "JOIN Marker marker2 ON marker1.marker_id = marker2.marker_id "
  "WHERE marker1.name IN SelectedMarkers "
  "GROUP BY marker1.name, MTG1.marker_id ")


# TODO: Query 3
# --------------------------------------------------------------
# QUERY 3: Get Markers ordered by % human hosts, divided by serotype and segment
# --------------------------------------------------------------
# Description:
#   TODO
#
# Inputs:
#   - (Optional) serotype: Serotype
#   - (Optional) segment_type: Segment type
#   - (Optional Filter) min_perc, max_perc: Percentage range (default = (0, 100))
#   - (Optional Filter) limit: Limit in the number of results (default = no limit)
#   - (Optional Filter) min_n_instance: Min number of Segments that must contain the Marker (default = 1)
#
# Outputs:
#   - A list of all Markers ordered by percentage of human hosts in the given range, and for each:
#       - The Groups it belongs to
#
# --------------------------------------------------------------
# NOTE: view SegmentMarker(segment_id, marker_id), tells whether a marker is found in a given segment



# TODO: Query 4

# --------------------------------------------------------------
# QUERY 5: Get the most common Marker for the selected serotype and segment type with filters
# --------------------------------------------------------------
# Description:
#   TODO
#
# Inputs:
#   - (Optional) A Serotype
#   - (Optional) A Segment type
#   - (Optional Filter) Host type
#
# Outputs:
#   - A list of all Markers ordered by their prevalence given the filters:
#       - The Groups it belongs to TODO
#       - The Effect associated to each group TODO
#       - The doi of the Paper the group was found in TODO
#       - The number of instances found
#
# --------------------------------------------------------------
# NOTE: view SegmentMarker(segment_id, marker_id), tells whether a marker is found in a given segment

# TODO: check better
get_markers_by_prevalence = \
    ("WITH FilteredMarkers AS ("
     "SELECT segmentMarkers.marker_id "
     "FROM SegmentMarkers segmentMarkers "
     "JOIN Segment segment ON segmentMarkers.segment_id = segment.segment_id "
     "JOIN Isolate isolate ON segment.isolate_id = isolate.isolate_id "
     "WHERE segment.segment_type = :segment_type "
     "AND isolate.serotype_id = :serotype_id "
     "AND isolate.host = :host OR :host IS NULL "
     "GROUP BY segmentMarkers.segment_id )"
     ""
     "SELECT count(*) "  # TODO: Group, effect, paper doi
     "FROM Marker marker "
     "JOIN FilteredMarkers filteredMarkers ON marker.marker_id = filteredMarkers.marker_id ")


# TODO: Query 6: For each mutation get the number of segments that exhibit it, and the percentage over the total number of segments


# QUERIES ONTOLOGY

# --------------------------------------------------------------
# QUERY ???: Retrieve the Marker Groups that contain a specific Marker
# --------------------------------------------------------------
# Description:
#   TODO
#
# Inputs:
#   - A Marker
#
# Outputs:
#   - A list of all Marker Groups that contain that Marker
#
# --------------------------------------------------------------

# TODO