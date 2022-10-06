import os
from tokenize import PlainToken
from urllib import response
import boto3

from dynamodb_encryption_sdk.encrypted import CryptoConfig

# from boto3.dynamodb.conditions import Key
# from dynamodb_encryption_sdk.encrypted.resource import EncryptedResource
# from dynamodb_encryption_sdk.encrypted.item import (
#     encrypt_python_item,
#     decrypt_python_item,
# )
from dynamodb_encryption_sdk.encrypted.client import EncryptedClient
from .constants import TYPE_MAPPING
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


class DynamoDBEncryptDecrypt:
    def __init__(self, aws_cmp_id, primary_key=None) -> None:
        self._aws_cmp_id = aws_cmp_id
        self.table_name = os.getenv("EZYPASS_TABLE_NAME")
        self.primary_key = primary_key

    def _pre_config(self):

        self.table = boto3.client("dynamodb")
        # self.table = self.db_table.Table(self.table_name)
        table_info = TableInfo(name=self.table_name)
        table_info.refresh_indexed_attributes(self.table)

        self.aws_kms_cmp = AwsKmsCryptographicMaterialsProvider(key_id=self._aws_cmp_id)

        encryption_context = EncryptionContext(
            table_name=self.table_name,
            partition_key_name=table_info.primary_index.partition,
            attributes=dict_to_ddb(self.primary_key),
        )

        actions = AttributeActions(
            default_action=CryptoAction.DO_NOTHING,
            attribute_actions={"password": CryptoAction.ENCRYPT_AND_SIGN},
        )
        actions.set_index_keys(*table_info.protected_index_keys())

        self.crypto_config = CryptoConfig(
            materials_provider=self.aws_kms_cmp,
            encryption_context=encryption_context,
            attribute_actions=actions,
        )

        self.encrypt_client = EncryptedClient(
            client=self.table, materials_provider=self.aws_kms_cmp
        )
        # self.encrypted_table = EncryptedTable(
        #     table=self.table, materials_provider=self.aws_kms_cmp
        # )
        return self.crypto_config

    def encrypt(self, plain_item):
        """This function encrypts the password present in the given plaintext item, no other items will be encrypted

        Args:
            plain_item (dict): A dictionary containing all the given items

        """
        crypto_config = self._pre_config()
        # This below line should be used only when you are trying to add the element directly
        # encrypted_item = encrypt_python_item(plain_item, crypto_config)

        self.encrypt_client.put_item(
            TableName=self.table_name, Item=plain_item, crypto_config=crypto_config
        )
        # self.encrypted_table.put_item(Item=plain_item)
        # self.table.put_item(TableName=self.table_name,Item=encrypted_item)

    def query_item(self, index):
        crypto_config = self._pre_config()
        return self.encrypt_client.query(
            TableName=self.table_name,
            IndexName="byEzyUser",
            KeyConditionExpression="ezyUser = :user",
            ExpressionAttributeValues={":user": {"S": index}},
            crypto_config=crypto_config,
        )

    def get_item(self):
        crypto_config = self._pre_config()
        response = self.encrypt_client.get_item(
            TableName=self.table_name, Key=self.primary_key, crypto_config=crypto_config
        )

        return response

    def update_item(self, update_item):
        response = self.get_item()["Item"]
        existing_record = {key: list(val.values())[0] for key, val in response.items()}
        existing_record |= update_item

        # Constructing the data format in like {'website': {'S': 'ezypass.com'}
        prepared_data = {
            key: {TYPE_MAPPING[type(val)]: val} for key, val in existing_record.items()
        }

        self.encrypt(plain_item=prepared_data)

    def delete_item(self):
        print("////////////////////////////", self.primary_key)
       
        try:
            self.table.delete_item(
                TableName=self.table_name,
                Key=self.primary_key
            )
        except Exception as e:
            raise e

        # self.encrypt(plain_item=item)

    # def decrypt(self, index):  # sourcery skip: inline-immediately-returned-variable

    #     crypto_config = self._pre_config()
    #     encrypt_client = EncryptedClient(
    #         client=self.table, materials_provider=self.aws_kms_cmp
    #     )

    #     response = encrypt_client.query(
    #         TableName=self.table_name,
    #         IndexName="byEzyUser",
    #         KeyConditionExpression="ezyUser = :user",
    #         ExpressionAttributeValues={":user": {"S": index}},
    #         crypto_config=crypto_config,
    #     )

    # resource = EncryptedResource(
    #     resource=self.db_table,
    #     materials_provider=self.aws_kms_cmp
    # )
    # response = resource.batch_get_item(
    #     RequestItems={
    #         self.table_name:{
    #             'Keys':[{'email':'tahir@codeops.tech','website':'konfhub.com'}]
    #         }
    #     },
    #     crypto_config=crypto_config
    # )

    # return response
