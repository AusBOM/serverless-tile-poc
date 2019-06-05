"""Functions for generating a custom colour map."""

import numpy as np
import spectra

def make_colour_map(colours, indexes=None, size=256):
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

    Returns
    -------
    numpy : numpy ndarray(256,3) of float
        The derived colour map.
    """

    if not indexes:
        # If indexes is not set, return an even continuous distribution.
        colour_array = spectra.range(colours, size)
        # Convert of Color objects to 2D numpy array of rgb and return
        return np.asarray([c.rgb for c in colour_array])*255

    # Otherwise, align the colour map to the indexes
    # Find the colours between the first and second index.
    colour_run = spectra.range([colours[0], colours[1]], indexes[1] - indexes[0] + 1)
    colour_map = np.asarray([c.rgb for c in colour_run])*255
    # Find the remaining colours values and concatenate into one array.
    for run in range(1, len(indexes) - 1):
        colour_run = spectra.range(
            [colours[run], colours[run+1]],
            indexes[run+1] - indexes[run] + 1)
        crt = np.asarray([c.rgb for c in colour_run])*255
        # Note: To avoid overlap we cut off the last value from the current colour map
        colour_map = np.concatenate((colour_map[:-1, :], crt), axis=0)

    return colour_map
