import boto3
import json
from decimal import Decimal
from boto3.dynamodb.conditions import Key, Attr
from style import Style
# Helper class to convert a DynamoDB item to JSON.

def update_stac(item):

    dynamodb = boto3.resource('dynamodb'  , region_name='ap-southeast-2')
    table = dynamodb.Table('stac_register')
    print(item, 'wassup')
    print(item, item['id'])
    response = table.put_item(Item=item)
    print(response)


def create_style_from_stac(style_data, indexes, bucket=None, dataname=None, default=False):
    style_id = style_data['id']
    style_indexes = indexes
    resampling_method = style_data.get('resampling_method', 'bilinear')
    hide_min = style_data.get('hide_min', True)
    hide_max = style_data.get('hide_max', False)
    gradient = style_data.get('gradient', True)
    if 'colours' in style_data:
        colours = '-'.join(style_Data.colours)
    else:
        colours = style_id

    style = Style(style_id, style_indexes, resampling_method=resampling_method, hide_min=hide_min, hide_max=hide_max, gradient=gradient)
    
    # save the style to s3
    if bucket and dataname:
        s3 = boto3.resource('s3')
        s3filename = "tiles/{data}/{id}.json".format(data=dataname, id=style_id)
        s3object = s3.Object(bucket, s3filename)
        s3object.put(
            Body=(bytes(style.json().encode('UTF-8')))
        )
        print(default)
        if default:
            s3filename = "tiles/{data}/default.json".format(data=dataname, id=style_id)
            s3object = s3.Object(bucket, s3filename)
            s3object.put(
                Body=(bytes(style.json().encode('UTF-8')))
            )


    return style

def handler(event, context):

    # with open("stac/{datatype}.json".format(datatype=data)) as stac_file:
    #   stac_config = json.load(stac_file)
    print(event)
    print(event['body'])
    stacs = json.loads(event['body'], parse_float=Decimal)

    for stac in stacs:
        # print(stac)
        update_stac(stac)
        # body = get_collection(collection_id)
        print(stac['properties'])
        # print(stac['indexes'])
        if 'styles' in stac['properties'] and 'style_indexes' in stac['properties']:
            bucket = "bom-csiro-serverless-test"
            for style in stac['properties']['styles']:
                default = False
                print(stac['properties']['default_style'], stac['id'])
                if 'default_style' in stac['properties'] and stac['properties']['default_style'] == style['id']:
                    default = True
                create_style_from_stac(style, stac['properties'] ['style_indexes'], bucket, stac['id'], default=default)
    
    return {
        'statusCode': "204",
        'headers': {},
        }


def get_stac(id):

    dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')
    table = dynamodb.Table('stac_register')
    print(id)
    response = table.get_item(
        Key={
        'id': id
        })
    print(response)
    return replace_decimals(response['Item'])


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
