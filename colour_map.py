"""Functions for generating a custom colour map."""

import numpy as np
import spectra

def make_colour_map(colours, indexes=None, size=256, gradient=True):
    """Make a colour map for a list of colours aligned to indexes.

    Parameters
    ----------
    colours : list of (spectra color objects or strings)
        The list can contain spectra color objects or strings containing namded
        colors or hexcodes.
    indexes : list of ints
        The index placements to tell when to move from one colour to the next
    size : int
        The size of the colour map.
    gradient : bool
        Whether to trasition between colours as a gradient (True) or jump
        between at the indexes. (False)

    Returns
    -------
    numpy ndarray(size,3) of float
        The derived colour map.
    """

    if not indexes:
        # If indexes is not set, return an even continuous distribution.
        colour_array = spectra.range(colours, size)
        # Convert of Color objects to 2D numpy array of rgb and return
        return np.asarray([c.rgb for c in colour_array])*255

    # Otherwise, align the colour map to the indexes
    # Find the colours between the first and second index.
    run_size = indexes[1] - indexes[0] + 1
    if gradient:
        colour_run = spectra.range([colours[0], colours[1]], run_size)
        colour_map = np.asarray([c.rgb for c in colour_run])*255
    else:
        colour_map = np.tile(np.asarray(spectra.html(colours[0]).rgb), (run_size, 1))*255
    # Find the remaining colours values and concatenate into one array.
    for run in range(1, len(indexes) - 1):
        run_size = indexes[run+1] - indexes[run] + 1
        if gradient:
            colour_run = spectra.range([colours[run], colours[run+1]], run_size)
            crt = np.asarray([c.rgb for c in colour_run])*255
        else:
            crt = np.tile(np.asarray(spectra.html(colours[run]).rgb), (run_size, 1))*255
        # Note: To avoid overlap we cut off the last value from the current colour map
        colour_map = np.concatenate((colour_map[:-1, :], crt), axis=0)
    return colour_map

def split_colours(colours_list, colours_required):
    """Takes a list of colours and returns the list with required number of
    colours instead.

    Parameters
    ----------
    colours_list : list of type 'string' or type spectra.color object.
        The list of colours to create the range.
    colours_required : int
        The number of colours to be put in the returned list.

    Returns
    -------
    list of type 'string'
        A list with the appropriated number of colours created from the range
        given by the colours_list.
    """
    colour_range = spectra.range(colours_list, colours_required)
    return [colour.hexcode for colour in colour_range]
