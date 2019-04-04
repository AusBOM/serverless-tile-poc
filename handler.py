from rio_tiler.utils import array_to_image, get_colormap
import numpy as np
from rio_tiler import main
import os
import boto3
from tile import create_tile
import rasterio
import base64


def handler(event, context): # pylint: disabl=unused-argument
  """Generate new tile"""

  with rasterio.open('s3://bom-csiro-serverless-test/abcout.tif') as src:
      print("This raster has {} bands".format(src.count))


  # Get x,y,z variables
  x_index = int(event['pathParameters']['x'])
  y_index = int(event['pathParameters']['y'].strip('.png'))
  zoom_index = int(event['pathParameters']['z'])

  bucket = "bom-csiro-serverless-test"
  try:
    tile = create_tile("s3://{bucket}/abcout.tif".format(bucket=bucket), x_index, y_index, zoom_index)
  except:
    # Create empty 1x1 transparent is png
    tile_init = np.full((1,1,1), 0, dtype=np.uint8)
    mask = np.full((1,1), 0, dtype=np.uint8)
    tile = array_to_image(tile_init, mask=mask)

  output_file = "tiles/{z}/{x}/{y}.png".format(x=x_index,y=y_index,z=zoom_index)

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
