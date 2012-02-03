class Workspace extends Backbone.Router

    routes:
        "/:region/:district/:town/kampan/mf/": "town1"
        ":region/:district/:town/kampan/mf/":  "town2"
        "/:region/:district/kampan/mf/":       "district1"
        "/:region/:district/kampan/mf/":       "district2"
        "/:region/kampan/mf/":                 "region1"
        "/:region/kampan/mf/":                 "region2"

    town1: (region, district, town) ->
        console.log "town1: #{region} / #{district} / #{town}"

    town2: (region, district, town) ->
        console.log "town2: #{region} / #{district} / #{town}"

    district1: (region, district) ->
        console.log "district1: #{region} / #{district}"

    district2: (region, district) ->
        console.log "district2: #{region} / #{district}"

    region1: (region) ->
        console.log "region1: #{region}"

    region2: (region) ->
        console.log "region2: #{region}"
