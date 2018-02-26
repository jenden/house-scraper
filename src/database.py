import boto3
from boto3.dynamodb.conditions import Key, Attr
import os

AWS_DIR = os.path.join(os.path.dirname(__file__), '../.aws/')

os.environ['AWS_CONFIG_FILE'] = os.path.join(AWS_DIR, 'config')
os.environ['AWS_SHARED_CREDENTIALS_FILE'] = os.path.join(AWS_DIR, 'credentials')

ddb = boto3.resource('dynamodb')
ListingTable = ddb.Table('listings')
ExtractTable = ddb.Table('extracts')


if __name__ == "__main__":

    # response = ExtractTable.get_item(Key={'ListingID':'R2233392'})
    # print(response)
    # item = response['Item']
    # print(item)

    # import gzip
    # data = response['Items'][0]['original_page']['data']
    # # data is a Binary type object with a wrapper
    # print(type(data.value))
    # print(gzip.decompress(data.value))

    import dateutil
    from datetime import datetime
    response = ListingTable.query(KeyConditionExpression=Key('ListingID').eq('R2233392'))
    print(response)
    if response['Count'] > 0:
        record_datetime = dateutil.parser.parse(response['Items'][-1]['DateTime'])
        print(datetime.date(record_datetime) == datetime.date(datetime.now()))