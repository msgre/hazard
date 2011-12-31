# TODO: aktualnejsi kod je v mf.coffee

# convert_to_hex = (rgb) ->
#     parseInt(rgb[0], 16) + parseInt(rgb[1], 16) + parseInt(rgb[2], 16)
#
# trim = (s) ->
#     return if s.charAt(0) == '#' then s.substring(1, 7) else s
#
# convert_to_rgb = (hex) ->
#     color = [
#         parseInt ((trim(hex)).substring (0, 2), 16)
#         parseInt ((trim(hex)).substring (2, 4), 16)
#         parseInt ((trim(hex)).substring (4, 6), 16)
#     ]
#
# interpolate_color = (start_color, end_color, value) ->
#     start = convert_to_rgb(start_color)
#     end = convert_to_rgb(end_color)
#     c = [
#         (end[0] - start[0]) * value + start[0]
#         (end[1] - start[1]) * value + start[1]
#         (end[2] - start[2]) * value + start[2]
#     ]
#     convert_to_hex(c)
