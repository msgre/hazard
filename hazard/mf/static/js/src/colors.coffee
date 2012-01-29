###
Funkce pro vypocet interpolovanych barev mezi dvema zadanymi body.
###

hex = (v) ->
    out = v.toString(16)
    if out.length == 1
        out = '0' + out
    out

convert_to_hex = (rgb) ->
    '#' + hex(rgb[0]) + hex(rgb[1]) + hex(rgb[2])

trim = (s) ->
    return if s.charAt(0) == '#' then s.substring(1, 7) else s

convert_to_rgb = (hex) ->
    color = [
        parseInt(trim(hex).substring(0, 2), 16)
        parseInt(trim(hex).substring(2, 4), 16)
        parseInt(trim(hex).substring(4, 6), 16)
    ]

interpolate_color = (start_color, end_color, value) ->
    start = convert_to_rgb(start_color)
    end = convert_to_rgb(end_color)
    c = [
        Math.round((end[0] - start[0]) * value + start[0])
        Math.round((end[1] - start[1]) * value + start[1])
        Math.round((end[2] - start[2]) * value + start[2])
    ]
    convert_to_hex(c)

get_color = (type, value) ->
    if type == 'hells'
        color = interpolate_color('#FFD700', '#EE0000', value)
    else
        color = interpolate_color('#00FFFF', '#0028FF', value)
    return color
