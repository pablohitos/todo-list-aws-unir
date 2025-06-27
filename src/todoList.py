import os
import boto3
import time
import uuid
import json
import functools
from botocore.exceptions import ClientError


def get_table(dynamodb=None):
    if not dynamodb:
        URL = os.environ['ENDPOINT_OVERRIDE']
        if URL:
            print('URL dynamoDB:' + URL)
            boto3.client = functools.partial(boto3.client, endpoint_url=URL)
            boto3.resource = functools.partial(boto3.resource, endpoint_url=URL)
        dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    return table


def get_item(key, dynamodb=None):
    table = get_table(dynamodb)
    try:
        result = table.get_item(Key={'id': key})
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print('Result getItem:' + str(result))
        if 'Item' in result:
            return result['Item']


def get_items(dynamodb=None):
    table = get_table(dynamodb)
    result = table.scan()
    return result['Items']


def put_item(text, dynamodb=None):
    if not text:
        raise Exception("El parámetro 'text' no puede estar vacío")

    table = get_table(dynamodb)
    timestamp = str(time.time())
    print('Table name:' + table.name)
    item = {
        'id': str(uuid.uuid1()),
        'text': text,
        'checked': False,
        'createdAt': timestamp,
        'updatedAt': timestamp,
    }
    try:
        table.put_item(Item=item)
        response = {
            "statusCode": 200,
            "body": json.dumps(item)
        }
    except ClientError as e:
        print(e.response['Error']['Message'])
        raise
    else:
        return response


def update_item(key, text, checked, dynamodb=None):
    if not key:
        raise TypeError("El parámetro 'key' no puede estar vacío")
    if not text:
        raise Exception("El parámetro 'text' no puede estar vacío")
    if not checked:
        raise Exception("El parámetro 'checked' no puede estar vacío")

    table = get_table(dynamodb)
    timestamp = int(time.time() * 1000)

    try:
        result = table.update_item(
            Key={'id': key},
            ExpressionAttributeNames={'#todo_text': 'text'},
            ExpressionAttributeValues={
                ':text': text,
                ':checked': checked,
                ':updatedAt': timestamp,
            },
            UpdateExpression='SET #todo_text = :text, checked = :checked, updatedAt = :updatedAt',
            ReturnValues='ALL_NEW',
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
        raise
    else:
        return result['Attributes']


def delete_item(key, dynamodb=None):
    if not key:
        raise TypeError("El parámetro 'key' no puede estar vacío")

    table = get_table(dynamodb)
    try:
        table.delete_item(Key={'id': key})
    except ClientError as e:
        print(e.response['Error']['Message'])
        raise
    else:
        return


def create_todo_table(dynamodb):
    tableName = os.environ['DYNAMODB_TABLE']
    print('Creating Table with name:' + tableName)
    table = dynamodb.create_table(
        TableName=tableName,
        KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
        ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
    )

    table.meta.client.get_waiter('table_exists').wait(TableName=tableName)
    if table.table_status != 'ACTIVE':
        raise AssertionError()

    return table