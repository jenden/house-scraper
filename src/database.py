import boto3
from boto3.dynamodb.conditions import Key, Attr
import os

os.environ['AWS_CONFIG_FILE'] = '../.aws/config'
os.environ['AWS_SHARED_CREDENTIALS_FILE'] = '../.aws/credentials'

ddb = boto3.resource('dynamodb')
ListingTable = ddb.Table('listings')
ExtractTable = ddb.Table('extracts')

# table.put_item(Item={'ListingID':'R26','LinkDate':'2018-02-18 18:24:11','Area':'VANCOUVER-BC', 'ExtractID':123582301})

# response = table.get_item(
#     Key={
#         'ListingID': 'R24',
#         'LinkDate':'2018-02-18 18:24:11'
#     }
# )
# print(response)
# item = response['Item']
# print(item)

# response = table.query(KeyConditionExpression=Key('ListingID').eq('R24'))
# response = table.query(AttrConditionExpression=Attr('LinkDate').eq('2018-02-18 18:24:11'))
#
# print(response)

ExtractTable.put_item(Item={'ListingID':'R2225079', 'Table':[{'Something':'S', 'N':'Nothing'},{'More':10, 'Less':2}]})
