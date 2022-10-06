import os
import json
from common.dbb_crypto_service import DynamoDBEncryptDecrypt


cmp_key_id=os.environ["AWS_CMP_ID"]
dynamo_db = DynamoDBEncryptDecrypt(aws_cmp_id=cmp_key_id)

def encryption_handler(event, context):
    
    event = event["body"]
    primary_key = {"email": event["email"], "website": event["website"]}

    # Merging the dictionaries, we need
    plain_item = {
        "email": event["email"],
        "password": event["password"],
        "ezyUser": event["ezyUser"],
        "description": event["description"],
    } | primary_key

    dynamo_db.primary_key = primary_key
    dynamo_db.encrypt(plain_item=plain_item)
    
    body = {"message": "succesfully added the data"}

    return {"statusCode": 200, "body": json.dumps(body)}
