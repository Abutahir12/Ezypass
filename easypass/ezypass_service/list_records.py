import os
from common.dbb_crypto_service import DynamoDBEncryptDecrypt

cmp_key_id = os.environ["AWS_CMP_ID"]
table_name = os.environ["EZYPASS_TABLE_NAME"]


def list_details(event, context):

    mandatory_fields = ["email", "website"]

    if event["fetch_one"]:
        mandatory_fields.extend(["ezy_user"])

    index = event.get("ezy_user")

    primary_key = {
        "email": {"S": event.get("email")},
        "website": {"S": event.get("website")},
    }

    missing_fields = list(set(mandatory_fields) - set(event.keys()))
    if len(missing_fields):
        return {"statusCode": 400, "Message": "Missing mandatory fields"}

    ddb_crypto_service = DynamoDBEncryptDecrypt(
        aws_cmp_id=cmp_key_id, primary_key=primary_key
    )
    try:
        if not event["fetch_one"]:
            response = ddb_crypto_service.query_item(index=index)["Items"]
            result = []
            for record in response:
                d = {key: list(val.values())[0] for key, val in record.items()}
                result.append(d)
        else:
            response = ddb_crypto_service.get_item()["Item"]
            result = {key: list(val.values())[0] for key, val in response.items()}
    except Exception as e:
        return {"statusCode": 400, "Message": e}

    return {"statusCode": 200, "Data": result}
