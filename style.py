import json
import numpy as np
from colour_map import make_colour_map


def normalise_tile(tile, min_value, max_value, scale_factor = 1):
    """ Normalises the tile to scale between 0 and 255."""
    tile[tile < min_value] = min_value
    tile[tile > max_value] = max_value

    return ((tile-min_value)/(max_value-min_value)*255).astype(np.uint8)

def normalise_list(value_list, min_value, max_value):
    """ Normalises the values in a list to scale between 0 and 255."""
    if value_list:
        return [round((value-min_value)/(max_value-min_value)*255) for value in value_list]

    return None

resampling_options = [
    "nearest",
    "bilinear", # default
    "cubic",
    "average"
]

class Style:

    def __init__(self, id, indexes, **kwargs):

        # TODO: Check for local style

        # TODO: Check for valid colours
        print(id)
        colours = id.split('-')
        self.resampling_method = 'bilinear'
        if colours[0] in resampling_options:
            self.resampling_method = colours.pop(0)
        self.id = id
        self.scale_factor = kwargs.get('scale_factor', 1)
        self.min = indexes[0]
        self.max = indexes[-1]
        self.indexes = [index / self.scale_factor for index in indexes]
        
        if 'colour_map' in kwargs:
            self.colour_map = kwargs['colour_map']
        else:
            self.colour_map = make_colour_map(colours, indexes=kwargs.get('indexes'))

        # print(self.colour_map)
        self.hide_min = kwargs.get('hide_min', True)
        self.hide_max = kwargs.get('hide_max', False)
        self.scale_factor = kwargs.get('scale_factor')

    def json(self,):

        return json.dumps({
            'id': self.id,
            'indexes': self.indexes,
            'hide_min': self.hide_min,
            'hide_max': self.hide_max,
            'colour_map': self.colour_map.tolist()
        })
    

    def style_tile(self, tile):

        # colour_map = get_colour_band(styles['carla-special'], band_thresholds)
        # print(colour_map, colour_map.shape)
        return normalise_tile(tile, self.min, self.max)


    def style_tile_mask(self, tile, mask):
        if self.hide_min:
            minimum_mask = (tile > self.min).astype(int)
            mask = mask * minimum_mask[0]
        if self.hide_max:
            maximum_mask = (tile < self.max).astype(int)
            mask = mask * maximum_mask[0]

        return mask

    def get_colour_map_array(self):

        return np.array(self.colour_map)

    def get_resampling_method(self):

        return self.resampling_method

print(Style('red-blue-green', indexes=[0, 10, 255]).json())