"""Using AWS Lambda to generate tile from data source."""

import os

import base64
import json
import numpy as np
import boto3
from rio_tiler.utils import array_to_image
from tile import create_tile
from stac import get_stac
from style import Style


def get_stac_config(data_id):
    """Get the config for the given data_id

    Parameters
    ----------
    data_id : string
        The id representing the data.
    Returns:
        object
            An object representing the config taken from the STAC for the given
            data_id.
    """

    stac_config = get_stac(data_id)
    return_config = stac_config['properties']
    return_config['source'] = stac_config['assets']['source']['href']
    return_config.setdefault('output_prefix', 'tiles/' + data_id)
    return return_config

def get_style(data_id, style_id, bucket, indexes=None):
    """Load the style from the s3 data store or use id and indexes to generate the style.

    Parameters
    ----------
    data_id : string
        The id representing the data.
    style_id : string
        The id representing the style.
    bucket : string
        The bucket where to search for the style data.
    indexes : list of type 'float'
        Used to generate a new style from the id.
        Only needed if no style not specified in STAC.

    Returns
    -------
    Style object
        The style to use for this implementation.
    """
    
    s3path = 'tiles/{data_id}/{style_id}.json'.format(data_id=data_id, style_id=style_id)
    s3 = boto3.resource('s3')
    try:
        style_config = s3.Object(bucket, s3path).get()
        json_content = json.loads(style_config['Body'].read().decode('utf-8'))
        return Style(**json_content)
    except:
        return Style(style_id, indexes)

def handler(event, context, invoke_local=False): # pylint: disable=unused-argument
    """The lambda handler for generating a tile
    
    Parameters
    ----------
    event : object
        The event passed from the API Gateway to the lambda function.
    context : object
        The context passed from the API Gateway to the lambda function.
    invoke_local : bool
        A flag to tell whether this was invoked locally.

    Returns
    -------
    object
        A lambda response to api gateway.
    """

    # Get path parameters
    data = event['pathParameters']['data']
    x_index = int(event['pathParameters']['x'])
    y_index = int(event['pathParameters']['y'].strip('.png'))
    zoom_index = int(event['pathParameters']['z'])

    # TODO: get the bucket from environment variable
    bucket = "bom-csiro-serverless-test"

    data_config = get_stac_config(data)

    if 'style' in event['pathParameters'] and event['pathParameters']['style'] != 'default':
        style = get_style(data, event['pathParameters']['style'], bucket, data_config['style_indexes'])
        output_file = "{prefix}/styles/{style}/{z}/{x}/{y}.png".format(prefix=data_config['output_prefix'], style=event['pathParameters']['style'], x=x_index,y=y_index,z=zoom_index)
    else:
        style = get_style(data, 'default', bucket)
        # style = get_style(data, '#0000ff-azure-aqua-blueviolet-burlywood-green-darkgreen-chartreuse-coral-darkorange-deeppink-dimgrey-darkviolet', bucket)
        output_file = "{prefix}/{z}/{x}/{y}.png".format(prefix=data_config['output_prefix'],x=x_index, y=y_index, z=zoom_index)

    bucket = "bom-csiro-serverless-test"
    try:
        tile = create_tile(data_config['source'], x_index, y_index, zoom_index, style, bands=data_config['band'])
    except Exception as e:
        print(e)
        # Create empty 1x1 transparent is png
        tile_init = np.full((1, 1, 1), 0, dtype=np.uint8)
        mask = np.full((1, 1), 0, dtype=np.uint8)
        tile = array_to_image(tile_init, mask=mask)

    if invoke_local:
        # If localally invoked save the tile to disk
        filepath = "data/{output_file}".format(output_file=output_file)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as binary_png:
            print("Generated: {filepath}".format(filepath=filepath))
            binary_png.write(tile)
    else:
        # save the tile to s3
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
