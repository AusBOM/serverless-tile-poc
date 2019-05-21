import numpy as np

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

def get_colour_band(style_json, band_thresholds=None):

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
