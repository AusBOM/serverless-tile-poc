""" Use style and rio-tiler to generate a tile."""
import sys
import traceback
import numpy as np
from rio_tiler import main
from rio_tiler.utils import array_to_image


def create_tile(src, x, y, z, style, bands=None):
    """Create the tile for x,y,z

    Parameters
    ----------
    src : string
        The connection to the source data.
        Accepted protocols are s3, https and local files.
    x : int
        Mercator tile X index.
    y : int
        Mercator tile Y index.
    z : int
        Mecator tile zoom level.
    style : Style object
        Used to style the tile.
    bands : int or list of type 'int'
        When querying a source with multiple bands, selects the band to use.

    Returns
    -------
    bytes
        The png image as bytes.
    """

    try:
        # returns the tile at the point as well as a mask to for the undefined values
        indexes = bands
        resample = style.get_resampling_method()
        tile, alpha = main.tile(src, x, y, z, indexes=indexes, resampling_method=resample)
        alpha = style.style_tile_mask(tile, alpha)
        png_tile = style.normalise_tile(tile)

    except Exception as exception:
        print('tile generation exception')
        print(exception)
        traceback.print_exc(file=sys.stdout)
        # Return empty tile
        png_tile = np.full(256, 3)

    colour_map = style.get_colour_map_array()

    return array_to_image(png_tile, color_map=colour_map, mask=alpha)
