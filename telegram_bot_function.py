import os
import ydb
import json
import time
import boto3
import os
import ydb
from io import BytesIO
import base64

print("started")
global_id = ""
global_name = ""
get_query = None
find_by_name_sql = None
driver = ydb.Driver(endpoint=os.getenv('YDB_ENDPOINT'), database=os.getenv('YDB_DATABASE'))
driver.wait(fail_fast=True, timeout=10)
pool = ydb.SessionPool(driver)
print("driver configuring done")
boto_session = None
storage_client = None


def handler(event, context):
    print("handler started work")
    body = json.loads(event['body'])
    print(body)
    try:
        if ("/start" in body['message']['text']):
            print('Hello!')
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'method': 'sendMessage',
                    'chat_id': body['message']['chat']['id'],
                    'text': 'Hello!'
                }),
                'isBase64Encoded': False
            }
        elif ("/getface" in body['message']['text']):
            print("getfaces start")
            photo_url, photo_name = getUnsignedPhoto()
            print("done")
            print({
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'method': 'sendPhoto',
                    'chat_id': body['message']['chat']['id'],
                    'photo': photo_url,
                    'caption': photo_name
                }),
                'isBase64Encoded': False
            })
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'method': 'sendPhoto',
                    'chat_id': body['message']['chat']['id'],
                    'photo': photo_url,
                    'caption': photo_name
                }),
                'isBase64Encoded': False
            }
        elif ("/find" in body['message']['text']):
            print("find started")
            name = str(body['message']['text'].split(" ")[1])
            new_sql = "SELECT * FROM cloudlab WHERE name='" + name + "';"
            edit_sql_get_photo(new_sql)
            result = pool.retry_operation_sync(get_photo_by_name)
            print("find command result")
            return send_photos(result[0].rows, body)

        elif (body['message']['reply_to_message'] != None):
            edit_global_id(str(body['message']['reply_to_message']['caption']))
            edit_global_name(str(body['message']['text']))
            update_name()
            print('Name was updated')
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'method': 'sendMessage',
                    'chat_id': body['message']['chat']['id'],
                    'text': 'name setted'
                }),
                'isBase64Encoded': False
            }

    except Exception as error:
        print(error)
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'method': 'sendMessage',
            'chat_id': body['message']['chat']['id'],
            'text': 'Хорошо'
        }),
        'isBase64Encoded': False
    }

def send_photos(photos_db_rows, body):
    list_photos = []
    for photo_row in photos_db_rows:
        print('PHOTO ROW:::::::   ' + photo_row['photo'])
        photo_url = "https://d5dr9732gbkg19immv4d.apigw.yandexcloud.net/orig_photo/" + photo_row['photo']
        list_photos.append({'type': 'photo', 'media': photo_url, 'caption': body['message']['text'].split(" ")[1]})

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'method': 'sendMediaGroup',
            'chat_id': body['message']['chat']['id'],
            'media': list_photos
        }),
        'isBase64Encoded': False
    }




def get_photo_by_name(session):
    tmp_result = session.transaction().execute(
        find_by_name_sql,
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    )
    return tmp_result


def getUnsignedPhoto():
    print("finding result for getface")
    result = pool.retry_operation_sync(execute_unsigned_photo_query)
    print("result result[0].rows")
    print(result[0].rows)
    print("object_id")
    print(result[0].rows[0]['face'])
    object_id = result[0].rows[0]['face']
    print('Name photo:    ' + object_id)
    url_photo = 'https://d5dr9732gbkg19immv4d.apigw.yandexcloud.net/static/' + object_id
    print('Url photo:    ' + url_photo)
    return [url_photo, object_id]


def update_name():
    print("Updating name")
    result = pool.retry_operation_sync(execute_query_get_bd_id)
    execute_update_photo(result[0].rows[0]['id'])
    return 'OK'


def execute_unsigned_photo_query(session):
    # Create the transaction and execute query.
    return session.transaction().execute(
        "select * from cloudlab where name like '' LIMIT 1;",
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    )


def execute_query_get_bd_id(session):
    get_db_id_query = "select * from cloudlab where face like '" + global_id + "' LIMIT 1;"
    return session.transaction().execute(
        get_db_id_query,
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    )


def execute_update_photo(db_id):
    object_id = global_id
    print('DB_ID ::::::::     ' + str(db_id))

    # create ydb client
    session = boto3.session.Session(region_name='ru-central1')

    ydb_client = session.client('vvot38-db-photo-face',
                                endpoint_url='https://docapi.serverless.yandexcloud.net/ru-central1/b1g71e95h51okii30p25/etnmgkku88n8f44mdgq4',
                                aws_access_key_id='',
                                aws_secret_access_key=''
                                )

    ydb_client.update_item(TableName='cloudlab',
                           Key={
                               'id': {
                                   'S': db_id
                               }
                           },
                           AttributeUpdates={
                               'name': {
                                   'Value': {
                                       'S': global_name
                                   },
                                   'Action': 'PUT'
                               }
                           }

                           )


def edit_global_id(new_id):
    global global_id
    if (new_id != None):
        global_id = new_id


def edit_global_name(new_name):
    global global_name
    if (new_name != None):
        global_name = new_name


def edit_sql_get_photo(new_sql):
    global find_by_name_sql
    if (new_sql != None):
        find_by_name_sql = new_sql

