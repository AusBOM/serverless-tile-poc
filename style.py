"""Class for holding style data."""


import json
import numpy as np
from colour_map import make_colour_map


# The resampling options available.
RESAMPLING_OPTIONS = [
    "nearest",
    "bilinear", # default
    "cubic",
    "average"
]

class Style:
    """A style definition used to describe the styling that should be applied to
    a tile.

    Attributes
    ----------
    id : string
        The id is used to identify the the style and should either be an alias
        or a representation of the styling itself.  The id is a hyphen separated
        list of the colours to use with the resampling method at the front.
        id = {resampling_method}-{colour1}-{colour2}-(...)-{colour-n}
    indexes : list of type 'int'
        A normalised list of the points in the data that notes a change in the
        colour transitioning.
        Note: Min and Max are the first and last values on this list
        respectively.
    """

    def __init__(self, id, indexes, resampling_method='bilinear',
                 scale_factor=1., hide_min=True, hide_max=False,
                 colour_map=None):
        """Define the style and if not set build the colour map.

        id : string
            The id is used to identify the the style and should either be an alias
            or a representation of the styling itself.  The id is a hyphen separated
            list of the colours to use with the resampling method at the front.
            id = {resampling_method}-{colour1}-{colour2}-(...)-{colour-n}
        indexes : list of type 'int'
            A normalised list of the points in the data that notes a change in the
            colour transitioning.
            Note: Min and Max are the first and last values on this list
            respectively.
        resampling_method : string
            The resampling method to use when generating the tile.
        scale_factor : float
            The scale factor that has been applied to the raw data.
            Used to normalise the indexes from real values to the values in the
            dataset.
        hide_min : bool
            Whether to hide values equal to (or below) the minimum.
            Defaults to true
        hide_max : bool
            Whether to hide values equal to (or above) the maximum.
            Defaults to false.

        """
        # TODO: Check for valid colours
        colours = id.split('-')

        if colours[0] in RESAMPLING_OPTIONS:
            self.resampling_method = colours.pop(0)
        else:
            self.resampling_method = resampling_method
        self.id = id
        self.min = indexes[0]
        self.max = indexes[-1]
        self.indexes = self.normalise_list([index / scale_factor for index in indexes])
        # TODO: Handle scenarios where index list and colour list are different sizes
        # Use colour map if provided otherwise generate colour map
        if colour_map:
            self.colour_map = colour_map
        else:
            self.colour_map = make_colour_map(colours, self.indexes)

        self.hide_min = hide_min
        self.hide_max = hide_max

    def json(self):
        """Returns the styling attributes as json"""

        return json.dumps({
            'id': self.id,
            'indexes': self.indexes,
            'hide_min': self.hide_min,
            'hide_max': self.hide_max,
            'resamplilng_method': self.resampling_method,
            'colour_map': self.colour_map.tolist()
        })

    def normalise_tile(self, tile):
        """Normalise the tile between 0 and 255 for alignment with the colour map.

        Parameters
        ----------
        tile : numpy ndarray of type float
            An array of value representing a tile.

        Returns
        -------
        numpy ndarray of type 'np.uint8' (8-bit unsigned int)
            This returns an array of the same size as the given tile normalised between
            0 and 255.
        """

        # Make all values below the minimum equal the minimum.
        tile[tile < self.min] = self.min
        # Make all values above the maximum equal the maximum.
        tile[tile > self.max] = self.max

        return ((tile-self.min)/(self.max-self.min)*255).astype(np.uint8)

    def normalise_list(self, value_list):
        """Normalises the values in a list to scale between 0 and 255.

        Parameters
        ----------
        value_list : list of type float
            An list of values to normalise.

        Returns
        -------
        list of type 'int' (8-bit unsigned int)
            This returns a list of the same size as the given tile normalised between
            0 and 255.
        """

        if value_list:
            return [round((value-self.min)/(self.max-self.min)*255) for value in value_list]

        return None


    def style_tile_mask(self, tile, mask):
        """Style the transparency mask to decide where areas are transparent.

        Parameters
        ----------

        tile : numpy ndarray of type float
            An array of value representing the tile.
        mask : numpy ndarray of type int
            An array representing the alpha value for pixel in the tile.

        Returns
        -------
        numpy ndarray of type 'int'
            The values of the transparency (alpha) for each value in the tile.
        """
        if self.hide_min:
            # Make all minumum values transparent.
            minimum_mask = (tile > self.min).astype(int)
            mask = mask * minimum_mask[0]
        if self.hide_max:
            # Make all
            maximum_mask = (tile < self.max).astype(int)
            mask = mask * maximum_mask[0]

        return mask

    def get_colour_map_array(self):
        """Get the colour map for this style.

        Returns
        -------
        numpy ndarray of type 'int'
            The array representing the colour map.
        """
        return np.array(self.colour_map)

    def get_resampling_method(self):
        """Get the resampling method to use for this style.

        Returns
        -------
        string
            The string identifying the resampling method to use with this
            style.
        """
        return self.resampling_method
