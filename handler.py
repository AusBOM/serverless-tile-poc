from rio_tiler.utils import array_to_image, get_colormap
import numpy as np
from rio_tiler import main
import os
import boto3
from tile import create_tile
import rasterio
import base64
import json

with open("data_config.json") as config_file:
  config = json.load(config_file)

print(config)

def get_config(data):
  """Reads the config in for test."""
  source_bucket = "bom-csiro-serverless-test"


  config[data].setdefault("source", "s3://{bucket}/{file}".format(bucket=source_bucket, file=config[data]['datasource_file'])),
  config[data].setdefault("output_prefix", "tiles/{data}".format(data=data))

  return config[data]


def handler(event, context): # pylint: disabl=unused-argument
  """Generate new tile"""

  # with rasterio.open('s3://bom-csiro-serverless-test/abcout.tif') as src:
  #     print("This raster has {} bands".format(src.count))

  # Get x,y,z variables
  data = event['pathParameters']['data']
  x_index = int(event['pathParameters']['x'])
  y_index = int(event['pathParameters']['y'].strip('.png'))
  zoom_index = int(event['pathParameters']['z'])

  data_config = get_config(data)
  # print(data_config)

  bucket = "bom-csiro-serverless-test"
  try:
    tile = create_tile(data_config['source'], x_index, y_index, zoom_index, config=data_config)
  except Exception as e:
    # Create empty 1x1 transparent is png
    tile_init = np.full((1,1,1), 0, dtype=np.uint8)
    mask = np.full((1,1), 0, dtype=np.uint8)
    tile = array_to_image(tile_init, mask=mask)

  # print(tile)
  output_file = "{prefix}/{z}/{x}/{y}.png".format(prefix=data_config['output_prefix'],x=x_index,y=y_index,z=zoom_index)

  # with open('whack.png', "wb") as binary_png:
  #   binary_png.write(tile)


  s3 = boto3.resource('s3')
  s3object = s3.Object(bucket, output_file)
  s3object.put(Body=tile)

  return {
    'statusCode': "200",
    'headers': {
      'Content-Type': 'image/png'
    },
    'body': base64.b64encode(tile).decode('utf-8'),
    'isBase64Encoded': True
  }

# event = {
#   'pathParameters': {
#     'data': 'rainrate', 
#     'x': 914,
#     # 'y': 548,
#     'y': '549.png',
#     'z': 10
#   }
# }


# event = {
#   'pathParameters': {
#     'data': 'rainrate', 
#     'x': 3661,
#     # 'y': 548,
#     'y': '2192.png',
#     'z': 12
#   }
# }

# handler(event, None)