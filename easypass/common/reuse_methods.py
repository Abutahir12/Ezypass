from typing import Dict
from urllib import response
import boto3
import os
from .dbb_crypto_service import DynamoDBEncryptDecrypt
from boto3.dynamodb.conditions import Key

cmp_key_id=os.environ["AWS_CMP_ID"]
ddb_crypto_service = DynamoDBEncryptDecrypt(aws_cmp_id=cmp_key_id)
table_name = os.environ["EZYPASS_TABLE_NAME"]

ddb_table = boto3.resource("dynamodb").Table(table_name)

def put_item(item: Dict) -> None:
    ddb_table.put_item(Item=item)

def get_item(key: Dict, index):

    
    return ddb_crypto_service.decrypt(index)
  

def update_item():
    pass

def delete_item():
    pass