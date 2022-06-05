import json
import os
import boto3
from boto3.dynamodb.types import Binary
from dynamodb_encryption_sdk.encrypted import CryptoConfig
from dynamodb_encryption_sdk.encrypted.item import (
    encrypt_python_item,
    decrypt_python_item,
)
from dynamodb_encryption_sdk.identifiers import CryptoAction
from dynamodb_encryption_sdk.material_providers.aws_kms import (
    AwsKmsCryptographicMaterialsProvider,
)
from dynamodb_encryption_sdk.structures import (
    TableInfo,
    AttributeActions,
    EncryptionContext,
)
from dynamodb_encryption_sdk.transform import dict_to_ddb


table_name = os.environ["EZYPASS_TABLE_NAME"]


def encrypt(event, context):

    """Demonstrate use of EncryptedTable to transparently encrypt an item."""

    index_key = {"ezy_user": event["ezy_user"]}

    plaintext_item = {
        "website": event["website"],
        "description": event["description"],  # We want to ignore this attribute
        "email": event["email"],
        "password": event["password"],
    }

    # Add the index pairs to the item.
    plaintext_item.update(index_key)

    table = boto3.resource("dynamodb").Table(table_name)

    table_info = TableInfo(name=table_name)
    table_info.refresh_indexed_attributes(table.meta.client)

    aws_cmp_id = "57921ecf-f4c9-4bf6-8c27-d4b05a59869d"
    aws_kms_cmp = AwsKmsCryptographicMaterialsProvider(key_id=aws_cmp_id)

    encryption_context = EncryptionContext(
        table_name=table_name,
        partition_key_name=table_info.primary_index.partition,
        attributes=dict_to_ddb(index_key),
    )

    actions = AttributeActions(
        default_action=CryptoAction.DO_NOTHING,
        attribute_actions={
            "password": CryptoAction.ENCRYPT_AND_SIGN
        },
    )
    actions.set_index_keys(*table_info.protected_index_keys())

    crypto_config = CryptoConfig(
        materials_provider=aws_kms_cmp,
        encryption_context=encryption_context,
        attribute_actions=actions,
    )

    encrypted_item = encrypt_python_item(plaintext_item, crypto_config)

    table.put_item(Item=encrypted_item)
    # result = table.update_item(
    #     Key = index_key,
    #     UpdateExpression  = 'set website_username.testuser1 = :password',
    #     ExpressionAttributeValues = {
    #         ":password":"mypass"
    #     }
    # )

    decrypted_item = decrypt_python_item(encrypted_item, crypto_config)

    body = {"message": decrypted_item}

    return {"statusCode": 200, "body": json.dumps(body)}
