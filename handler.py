from rio_tiler.utils import array_to_image, get_colormap
import numpy as np
from rio_tiler import main
import os
import boto3
from tile import create_tile
import rasterio
import base64
import json
from stac import get_stac

with open("data_config.json") as config_file:
  config = json.load(config_file)

def get_stac_config(data_id):
  """Get the config for the given data_id"""

  stac_config = get_stac(data_id)
  return_config = stac_config['properties']
  return_config['source'] = stac_config['assets']['source']['href']
  return_config.setdefault('output_prefix', 'tiles/' + data_id)
  return return_config


def handler(event, context, invoke_local=False): # pylint: disabl=unused-argument
  """Generate new tile"""

  # Get x,y,z variables
  data = event['pathParameters']['data']
  x_index = int(event['pathParameters']['x'])
  y_index = int(event['pathParameters']['y'].strip('.png'))
  zoom_index = int(event['pathParameters']['z'])

  data_config = get_stac_config(data)

  bucket = "bom-csiro-serverless-test"
  try:
    tile = create_tile(data_config['source'], x_index, y_index, zoom_index, config=data_config)
  except Exception as e:
    print(e)
    # Create empty 1x1 transparent is png
    tile_init = np.full((1,1,1), 0, dtype=np.uint8)
    mask = np.full((1,1), 0, dtype=np.uint8)
    tile = array_to_image(tile_init, mask=mask)

  output_file = "{prefix}/{z}/{x}/{y}.png".format(prefix=data_config['output_prefix'],x=x_index,y=y_index,z=zoom_index)


  if invoke_local == True:
    with open("data/{output_file}".format(output_file=output_file), "wb") as binary_png:
      binary_png.write(tile)
  else:
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
