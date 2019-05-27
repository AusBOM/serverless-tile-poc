import boto3
import json
from decimal import Decimal
from boto3.dynamodb.conditions import Key, Attr

# Helper class to convert a DynamoDB item to JSON.

def update_stac(item):

  dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')
  table = dynamodb.Table('stac_register')
  response = table.put_item(Item=item)
  print(response)


def handler(event, context):

    # with open("stac/{datatype}.json".format(datatype=data)) as stac_file:
    #   stac_config = json.load(stac_file)
    print(event)
    print(event['body'])
    stacs = json.loads(event['body'], parse_float=Decimal)

    for stac in stacs:
        update_stac(stac)
        body = get_collection(collection_id)
    
    return {
        'statusCode': "204",
        'headers': {},
        }


def get_stac(id):

    dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')
    table = dynamodb.Table('stac_register')
    response = table.get_item(
        Key={
        'id': id
        })
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