import numpy as np
from rio_tiler import main
from rio_tiler.utils import array_to_image
from colour_map import get_colour_map, get_colour_band
from data_normaliser import DataNormaliser
# import cv2

import json
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

default_style = [{
  'red': 0,
  'green': 0,
  'blue': 0
}, {
  'red': 0,
  'green': 0,
  'blue': 224
}, {
  'red': 206,
  'green': 13,
  'blue': 206
} 
]

def create_tile(src, x, y, z, style_config=None):
  
  mask_below = 0
  tile, mask = main.tile(src, x, y, z)
  b = (tile > 0).astype(int)
  mask = mask * b[0]
  # colour_map = get_colour_map(default_style)
  colour_map = np.empty([256,3])
  with open('styles.json') as styles_json:
    styles = json.load(styles_json)
    # pprint(styles)
    colour_map = get_colour_band(styles['carla-special'])
    # dn = DataNormaliser(111)
    # dn.normalise_data(tile, styles['carla-special'])

  # png_tile = tile.astype(np.uint8)
  # png_tile = np.zeros(shape= (256,3))
  # type(tile)
  # cv2.normalize(tile, png_tile, 0, 255, cv2.NORM_MINMAX)
  # print(png_tile)

  print(tile)
  print(tile/1200*255)
  print((tile/1200*255).astype(np.uint8))
  png_tile = (tile/1200*255).astype(np.uint8)

  # calibration = np.empty((12,), dtype=np.int16)
  # inputs = np.array([0, 4, 10, 30, 50, 80, 120, 200, 300, 400, 700, 1200])
  # print(inputs, calibrat  ion)
  # cv2.normalize(inputs, calibration, 0, 255, cv2.NORM_MINMAX)
  # print(calibration)

  # img = np.array([2000, -150, 11], dtype=np.int16)
  # img = np.array([0, 4, 10, 30, 50, 80, 120, 200, 300, 400, 700, 1200], dtype=np.int16)
  # # print(np.uint8(img))
  # # print(img.shape)
  # out = np.empty((12,), dtype=np.int16)
  # print(cv2.normalize(img, out, 0 ,255, cv2.NORM_MINMAX))
  # print(out)

  return array_to_image(png_tile, color_map=colour_map, mask=mask)


def generate_tile(src, x, y, z):
  
  # colour_map = get_colour_map(format='gdal')
  tile, mask = main.tile(src, x, y, z)
  png_tile = tile.astype(np.uint8)

  return array_to_image(png_tile, color_map=colour_map, mask=mask, nodata=nodata)


# tile = create_tile('/home/mbell/test-geo/crc-si/COG-Conversion-master/abcout.tif', 13, 8, 4)
# tile = create_tile('/home/mbell/netcdf-test/abcout.tif', 914, 548, 10)
# with open('tile_check.png', "wb") as binary_png:
#   binary_png.write(tile)

# get_colour_map(default_style)