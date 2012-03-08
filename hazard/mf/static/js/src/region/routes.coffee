class Workspace extends Backbone.Router

    routes:
        "/:region/:district/:town/kampane/mf/": "town1"
        ":region/:district/:town/kampane/mf/":  "town2"
        "/:region/:district/kampane/mf/":       "district1"
        "/:region/:district/kampane/mf/":       "district2"
        "/:region/kampane/mf/":                 "region1"
        "/:region/kampane/mf/":                 "region2"

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
