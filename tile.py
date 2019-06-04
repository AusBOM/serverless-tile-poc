""" Use settings and rio-tiler to generate a tile."""
import sys
import traceback
import json
import numpy as np
from rio_tiler import main
from rio_tiler.utils import array_to_image
from colour_map import get_colour_map, get_colour_band

# default_style = [{
#   'red': 0,
#   'green': 0,
#   'blue': 0
# }, {
#   'red': 0,
#   'green': 0,
#   'blue': 224
# }, {
#   'red': 224,
#   'green': 0,
#   'blue': 0
# }
# ]

# default_style = [{
#     'red': 0,
#     'green': 0,
#     'blue': 0
# }, {
#     'red': 0,
#     'green': 0,
#     'blue': 224
# }, {
#     'red': 206,
#     'green': 13,
#     'blue': 206
# }]

def normalise_tile(tile, min_value, max_value):
    """ Normalises the tile to scale between 0 and 255."""
    tile[tile < min_value] = min_value
    tile[tile > max_value] = max_value

    return ((tile-min_value)/(max_value-min_value)*255).astype(np.uint8)

def normalise_list(value_list, min_value, max_value):
    """ Normalises the values in a list to scale between 0 and 255."""
    if value_list:
        return [round((value-min_value)/(max_value-min_value)*255) for value in value_list]

    return None

def create_tile(src, x, y, z, style, bands=None):

    try:
        # returns the tile at the point as well as a mask to for the undefined values
        # src = "/home/mbell/netcdf-test/abcout.tif"
        # src = "/home/mbell/netcdf-test/uv1.tif"
        # src = "warped.tif"
        # src = "out.warp.tif"
        # src = "rf2/IDR00010.201905150548.tif"
        # src = "/home/mbell/netcdf-test/uv-mod.tif/uv-mod.tif.0.tif"
        # print(src)
        # tile, alpha = main.tile(src, x, y, z, resampling_method="nearest")
        # indexes = config.get('band')
        indexes = bands
        tile, alpha = main.tile(src, x, y, z, indexes=indexes, resampling_method=style.get_resampling_method())
        alpha = style.style_tile_mask(tile, alpha)
        png_tile = style.style_tile(tile)
        # print(style.get)


        # print(tile)
        # print(tile.shape)
        # tile_min = config.get('min', np.amin(tile))
        # tile_max = config.get('max', np.amax(tile))
        # scale_factor = config.get('scale_factor', 1)
        # mask_min = config.get('mask_min', False)
        # mask_max = config.get('mask_max', False)
        # band_thresholds = normalise_list(config.get('style_thresholds', None), tile_min, tile_max)
        # # tile_min = 0
        # # tile_max = 255
        # # band_thresholds = normalise_list([0, 1, 3, 8, 13, 20, 30, 50, 75, 100, 175, 255], tile_min, tile_max)
        # # band_thresholds = normalise_list([0, 1, 2, 3, 4, 5, 6, 7, 8, 100, 175, 255], tile_min, tile_max)
        # # print(band_thresholds)


        # # tile = normalise_tile()
        # if mask_min:
        #     minimum_mask = (tile > tile_min).astype(int)
        #     alpha = alpha * minimum_mask[0]
        # if mask_max:
        #     maximum_mask = (tile > tile_min).astype(int)
        #     alpha = alpha * minimum_mask[0]


        # # colour_map = get_colour_map(default_style)
        # colour_map = np.empty([256, 3])
        # with open('styles.json') as styles_json:
        #     styles = json.load(styles_json)

        # colour_map = get_colour_band(styles['carla-special'], band_thresholds)
        # print(colour_map, colour_map.shape)
        # png_tile = normalise_tile(tile, tile_min, tile_max)

    except Exception as e:
        print('tile generation exception')
        print(e)
        traceback.print_exc(file=sys.stdout)
        # raise e
        png_tile = np.full(256, 3)
    # print(png_tile.shape, png_tile)

    # print(colour_map)
    colour_map = style.get_colour_map_array()

    print('array to image', png_tile.shape, colour_map.shape)
    # print(png_tile)
    # print(colour_map)
    
    return array_to_image(png_tile, color_map=colour_map, mask=alpha)


# def generate_tile(src, x, y, z):
#   tile, mask = main.tile(src, x, y, z)
#   png_tile = tile.astype(np.uint8)

#   return array_to_image(png_tile, color_map=colour_map, mask=mask, nodata=nodata)

# tile = create_tile('/home/mbell/test-geo/crc-si/COG-Conversion-master/abcout.tif', 13, 8, 4)
# tile = create_tile('/home/mbell/netcdf-test/abcout.tif', 914, 548, 10)
# with open('tile_check.png', "wb") as binary_png:
#   binary_png.write(tile)

# get_colour_map(default_style)
