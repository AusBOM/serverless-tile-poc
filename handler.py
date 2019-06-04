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
from style import Style

with open("data_config.json") as config_file:
  config = json.load(config_file)

def get_stac_config(data_id):
  """Get the config for the given data_id"""

  stac_config = get_stac(data_id)
  return_config = stac_config['properties']
  return_config['source'] = stac_config['assets']['source']['href']
  return_config.setdefault('output_prefix', 'tiles/' + data_id)
  return return_config


def get_style(data_id, style_id, bucket, indexes=None):
  # check s3 bucket
  s3path = 'tiles/{data_id}/{style_id}.json'.format(data_id=data_id, style_id=style_id)
  print(s3path)
  s3 = boto3.resource('s3')
  try:
    style_config = s3.Object(bucket, s3path).get()
    json_content = json.loads(style_config['Body'].read().decode('utf-8'))
    print(json_content)
    return Style(**json_content)
  except:
    return Style(style_id, indexes)

def handler(event, context, invoke_local=False): # pylint: disabl=unused-argument
  """Generate new tile"""

  # Get x,y,z variables
  data = event['pathParameters']['data']
  x_index = int(event['pathParameters']['x'])
  y_index = int(event['pathParameters']['y'].strip('.png'))
  zoom_index = int(event['pathParameters']['z'])

  bucket = "bom-csiro-serverless-test"

  data_config = get_stac_config(data)

  if 'style' in event['pathParameters'] and event['pathParameters']['style'] != 'default':
    style = get_style(data, event['pathParameters']['style'], bucket, data_config['style_indexes'])
    output_file = "{prefix}/styles/{style}/{z}/{x}/{y}.png".format(prefix=data_config['output_prefix'],style=event['pathParameters']['style'],x=x_index,y=y_index,z=zoom_index)
  else:
    style = get_style(data, 'default', bucket)
    # style = get_style(data, '#0000ff-azure-aqua-blueviolet-burlywood-green-darkgreen-chartreuse-coral-darkorange-deeppink-dimgrey-darkviolet', bucket)
    output_file = "{prefix}/{z}/{x}/{y}.png".format(prefix=data_config['output_prefix'],x=x_index,y=y_index,z=zoom_index)

  bucket = "bom-csiro-serverless-test"
  try:
    # tile = create_tile(data_config['source'], x_index, y_index, zoom_index, config=data_config)
    print(data_config, data)
    tile = create_tile(data_config['source'], x_index, y_index, zoom_index, style, bands=data_config['band'])
    print('yo', tile)
  except Exception as e:
    print(e)
    # Create empty 1x1 transparent is png
    tile_init = np.full((1,1,1), 0, dtype=np.uint8)
    mask = np.full((1,1), 0, dtype=np.uint8)
    tile = array_to_image(tile_init, mask=mask)
  # print(tile)


  if invoke_local == True:
    filepath = "data/{output_file}".format(output_file=output_file)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "wb") as binary_png:
      print("Generated: {filepath}".format(filepath=filepath))
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
