"""Handle STAC related functions."""

import json
import os
from decimal import Decimal
import boto3
from boto3.dynamodb.conditions import Key, Attr
from style import Style
# Helper class to convert a DynamoDB item to JSON.

STAC_TABLE = os.environ['stacTable']
dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')
table = dynamodb.Table(STAC_TABLE)

def update_stac(item):
    """Writes the STAC item to dynamodb

    Parameters
    ----------
    item: object
        The STAC item to write to dynamodb.
    """
      
    response = table.put_item(Item=item)


def create_style_from_stac(style_data, indexes, bucket=None, dataname=None, default=False):
    """Read the data from the STAC file to create a style.

    Parameters
    ----------
    style_data : dict
        The styling data from the STAC.
    indexes: list of type 'float' or type 'int'
        The indexes for aligning the colours in the style.
    bucket : string
        If set, saves the style to given bucket.
    dataname : string
        The id of the dataset this style applies to.
    default : string
        Flag to identify if this is the default style for this data.
    """
    style_id = style_data['id']
    style_indexes = indexes
    resampling_method = style_data.get('resampling_method', 'bilinear')
    hide_min = style_data.get('hide_min', True)
    hide_max = style_data.get('hide_max', False)
    gradient = style_data.get('gradient', True)
    # if 'colours' in style_data:
    #     colours = '-'.join(style_data['colours'])
    #     style = Style(style_id, style_indexes, resampling_method=resampling_method, hide_min=hide_min, hide_max=hide_max, colours=colours)
    # else:
    style = Style(style_id, style_indexes, resampling_method=resampling_method, hide_min=hide_min, hide_max=hide_max, gradient=gradient)

    # save the style to s3
    if bucket and dataname:
        s3 = boto3.resource('s3')
        s3filename = f"tiles/{dataname}/{style_id}.json"
        s3object = s3.Object(bucket, s3filename)
        s3object.put(
            Body=(bytes(style.json().encode('UTF-8')))
        )
        # save default style as default.
        if default:
            s3filename = f"tiles/{dataname}/default.json"
            s3object = s3.Object(bucket, s3filename)
            s3object.put(
                Body=(bytes(style.json().encode('UTF-8')))
            )

    return style

def handler(event, context):
    """The handler for the lambda endpoint for adding/updating a new STAC.

    Parameters
    ----------
    event : object
        The event passed from the API Gateway to the lambda function.
    context : object
        The context passed from the API Gateway to the lambda function.

    Returns
    -------
    object
        A lambda response to API Gateway.
    """
    stacs = json.loads(event['body'], parse_float=Decimal)

    for stac in stacs:
        update_stac(stac)
        if 'styles' in stac['properties'] and 'style_indexes' in stac['properties']:
            bucket = os.environ['tileBucket']
            for style in stac['properties']['styles']:
                # Check if this style is the default.
                default = False
                if 'default_style' in stac['properties'] and stac['properties']['default_style'] == style['id']:
                    default = True
                # Create the style
                create_style_from_stac(style, stac['properties']['style_indexes'], bucket, stac['id'], default=default)

    # return empty response
    return {
        'statusCode': "204",
        'headers': {},
        }

def get_stac(id):
    """Return STAC from id.

    Parameters
    ----------
    id: string
        The id of the STAC.

    Returns
    -------
    dict
        The STAC item.
    """
    # dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')
    # table = dynamodb.Table('stac_register')
    response = table.get_item(
        Key={
            'id': id
        })
    return replace_decimals(response['Item'])

""" Not yet implemented.
def collection_items_handler(event, context):
    body = get_collection(event['pathParameters']['collection_id'])
    return {
    'statusCode': "200",
    'headers': {
      'Content-Type': 'application/json'
    },
    'body': body,
  }

def get_collection(collection_id):
    dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')
    table = dynamodb.Table('stac_register')
    filter_expression = Key('collection').eq(collection_id)
    response = table.scan(
        FilterExpression=filter_expression,
    )
    return replace_decimals(response['Items'])
"""

# https://github.com/boto/boto3/issues/369
def replace_decimals(obj):
    if isinstance(obj, list):
        for i in range(len(obj)):
            obj[i] = replace_decimals(obj[i])
        return obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            obj[k] = replace_decimals(v)
        return obj
    elif isinstance(obj, Decimal):
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    else:
        return obj
