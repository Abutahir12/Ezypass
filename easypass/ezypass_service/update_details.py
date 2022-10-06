import os
from common.dbb_crypto_service import DynamoDBEncryptDecrypt

cmp_key_id = os.environ["AWS_CMP_ID"]
table_name = os.environ["EZYPASS_TABLE_NAME"]


def update_details(event, context):

    mandatory_fields = ["email", "website"]
    event = event["body"]

    primary_key = {
        "email": {"S": event.get("email")},
        "website": {"S": event.get("website")},
    }

    #TODO : REVISIT THIS VALIDATION. THIS VALIDATION ALWAYS PASSES
    for key in primary_key:
        if key not in mandatory_fields:
            return {"statusCode": 400, "body": "missing mandatory fields"}

    # result = get_item(key=primary_key, index="Abutahir")['Items']
    ddb_crypto_service = DynamoDBEncryptDecrypt(
        aws_cmp_id=cmp_key_id, primary_key=primary_key
    )
    try:
        ddb_crypto_service.update_item(update_item=event)
    except Exception as e:
        return {"statusCode":400}
    # print("////", response)
    # record_list = []
    # for record in response:
    #     d = {key: list(val.values())[0] for key, val in record.items()}
    #     record_list.append(d)

    return {"statusCode": 200, "Message":" Succesfully updated the data"}
