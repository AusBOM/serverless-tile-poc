import numpy as np
import spectra

def genarate_range(start, end, size):
  if start == end:
    return np.full(size, start, dtype=np.uint8)
  
  return np.arange(start, end, (end - start) / size).astype(int)

def generate_colour_mapping(start_style, end_style, size=256):

  red = genarate_range(start_style['red'], end_style['red'], size)
  green = genarate_range(start_style['green'], end_style['green'], size)
  blue = genarate_range(start_style['blue'], end_style['blue'], size)
  return np.stack((red, green, blue), axis=-1)

def get_colour_map(style):

  style_runs = len(style) - 1
  run_size, overflow = divmod(256, style_runs)
  print(style_runs, run_size, overflow)
  colour_map = np.empty([0,3], dtype=np.uint8)
  
  for i in (1, style_runs):
    
    style_run_map = generate_colour_mapping(style[i-1], style[i], run_size)
    colour_map = np.concatenate((colour_map, style_run_map), axis=0)
  return colour_map

def make_colour_map(colours, indexes=None, size=256):
    print(indexes)
    if not indexes:
      # If indexes is falsy, return an even distribution.
      color_array = spectra.range(colours, 256)
      return np.asarray([c.rgb for c in color_array])*255
    else:
      # If indexes is not falsy, make the distribution in parts
      
      # TODO: match indexes and colours
      
    
    #   colour_map = np.empty([0,3], dtype=np.uint8)
    #   colour_map = np.array([[0,0,0]])
        colour_run = spectra.range([colours[0], colours[1]], indexes[1] - indexes[0] + 1)
        colour_map = np.asarray([c.rgb for c in colour_run])*255
        print(colour_map, colour_map[:-1])
        for x in range(1, len(indexes) - 1):
            print(colours[x], colours[x+1], indexes[x], indexes[x+1])
            # print(spectra.range([colours[x], colours[x+1]], indexes[x+1] - indexes[x]))
            colour_run = spectra.range([colours[x], colours[x+1]], indexes[x+1] - indexes[x] + 1)
            crt = np.asarray([c.rgb for c in colour_run])*255
            print(colour_map.shape, crt.shape, type(crt))
            # print(colour_map)
            # print(colour_map[:-1,:])
            # Note: To avoid overlap we cut off the last value from the current colour map
            colour_map = np.concatenate((colour_map[:-1,:], crt), axis=0)
      

        return colour_map

# def make_colour_map(start_colour, end_colour, size=256):
#     color_array = spectra.range(['red', 'green', 'blue'], 256)
#     j = np.asarray([c.rgb for c in color_array])*255
  

def get_style_colour_map(style_id):
  # Check to see if style is in s3
  # Otherwise check if style is in s3
  pass

def get_colour_band(style_json, band_thresholds=None):


  return make_colour_map(['#0000ff', 'purple', 'green', 'blue'], indexes=[0, 4, 10, 255])
  calibration_array = np.arange(0, 412)
  # print(calibration_array.astype(np.uint8))  

  style_runs = len(style_json) - 1
  run_size, overflow = divmod(256, style_runs)
  # print(style_runs, run_size, overflow)
  colour_map = np.empty([0,3], dtype=np.uint8)

  overflow_count = 0


  if not band_thresholds:
    for x in range(1, style_runs + 1):
      if overflow_count >= style_runs:
        size = run_size + 1
        overflow_count -= style_runs
      else:
        size = run_size
      overflow_count += overflow
      print(x, style_json[x-1], style_json[x])
      style_run_map = generate_colour_mapping(style_json[x-1]['rgb'], style_json[x]['rgb'], size)
      print(style_run_map)
      colour_map = np.concatenate((colour_map, style_run_map), axis=0)
      print(x, colour_map.shape)
      # print(colour_map)
    colour_map = np.concatenate((colour_map, np.array([[0,0,0]])), axis=0)
    print(colour_map)
    return colour_map
  else:
    x = 0
    for i,j in zip(band_thresholds, band_thresholds[1:]):
      # print(i,j)
      style_run_map = generate_colour_mapping(style_json[x]['rgb'], style_json[x+1]['rgb'], j-i)
      colour_map = np.concatenate((colour_map, style_run_map), axis=0)
      x += 1
    
    # print(colour_map)
    color_array = spectra.range(['red', 'green', 'blue'], 256)
    j = np.asarray([c.rgb for c in color_array])*255
    return j
    return colour_map


  # if band_thresholds:
  #   for x in range(1, style_runs + 1):
  #     if overflow_count >= style_runs:
  #       size = run_size + 1
  #       overflow_count -= style_runs
  #     else:
  #       size = run_size
  #     overflow_count += overflow
  #     print(x, style_json[x-1], style_json[x])
  #     style_run_map = generate_colour_mapping(style_json[x-1]['rgb'], style_json[x]['rgb'], size)
  #     print(style_run_map)
  #     colour_map = np.concatenate((colour_map, style_run_map), axis=0)
  #     print(x, colour_map.shape)
  #     # print(colour_map)
  #   colour_map = np.concatenate((colour_map, np.array([[0,0,0]])), axis=0)
  #   print(colour_map)
  #   return colour_map
  # else:
  #   x = 0
  #   for i,j in zip(band_thresholds, band_thresholds[1:]):
  #     style_run_map = generate_colour_mapping(style_json[x]['rgb'], style_json[x+1]['rgb'], j-i)
  #     colour_map = np.concatenate((colour_map, style_run_map), axis=0)
  #     x += 1
