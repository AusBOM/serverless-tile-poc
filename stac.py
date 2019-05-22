import boto3
import json
from decimal import Decimal

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

def get_stac(id):
  print('hi')
  
  dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')
  table = dynamodb.Table('stac_register')
  response = table.get_item(
    Key={
      'id': id
    })
  # return json.dumps("[{  \"type\": \"Feature\",  \"id\" : \"RAINRATE\",  \"bbox\": [140.7495166666666666, -13.823025, 143.09648333333333332,  -11.5096694444444444],  \"geometry\": {    \"type\": \"Polygon\",    \"coordinates\": [      [        [140.7495166666666666,  -13.823025],        [140.7495166666666666, 143.09648333333333332],        [143.09648333333333332, 143.09648333333333332],        [143.09648333333333332,  -13.823025],        [140.7495166666666666,  -13.823025]      ]    ]  },  \"properties\": {    \"datetime\": \"2018-06-26T00:00:0.000Z\",    \"min\": 0,    \"max\": 1200,    \"mask_min\": \"true\",    \"scale_factor\": 0.05,    \"style_thresholds\": [0, 4, 10, 30, 50, 80, 120, 200, 300, 400, 700, 1200]  },  \"collection\": \"RAINRATE\",  \"links\": [  ],  \"assets\": {    \"source\": {      \"href\": \"s3://bom-csiro-serverless-test/abcout.tif\",      \"title\": \"uv\",      \"product\": \"this\"    }  }}]")
  print(response['Item'], type(response['Item']))
  # item = response['Item']
  # print(item)
  # return item
  return replace_decimals(response['Item'])
  # return response['Item']

# get_stac('RAINRATE')

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