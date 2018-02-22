import boto3
from boto3.dynamodb.conditions import Key, Attr
import os

os.environ['AWS_CONFIG_FILE'] = '../.aws/config'
os.environ['AWS_SHARED_CREDENTIALS_FILE'] = '../.aws/credentials'

ddb = boto3.resource('dynamodb')
ListingTable = ddb.Table('listings')
ExtractTable = ddb.Table('extracts')


if __name__ == "__main__":

    response = ExtractTable.query(KeyConditionExpression=Key('ListingID').eq('R2241950'))
    print(response)
    item = response['Item']
    print(item)

    # import gzip
    # data = response['Items'][0]['original_page']['data']
    # # data is a Binary type object with a wrapper
    # print(type(data.value))
    # print(gzip.decompress(data.value))
