from PIL import Image
import requests
from io import BytesIO
import boto3
import json
import os
import ydb
from sanic import Sanic
from sanic.response import text
import sanic.response as response

app = Sanic(__name__)


@app.after_server_start
async def after_server_start(app, loop):
    print(f"App listening at port {os.environ['PORT']}")


@app.route("", methods=['GET', 'POST'])
async def hello(request):
    bucket = 'itis-2022-2023-vvot38-photos'
    new_bucket = 'itis-2022-2023-vvot38-faces'
    ip = request.headers["X-Forwarded-For"]

    json_msg = json.loads(request.json['messages'][0]['details']['message']['body'])
    photo = json_msg['object_id']


    x1 = int(json_msg['vertices'][0]['x'])
    y1 = int(json_msg['vertices'][0]['y'])
    x2 = int(json_msg['vertices'][2]['x'])
    y2 = int(json_msg['vertices'][2]['y'])

    url = 'https://storage.yandexcloud.net/' + bucket + '/' + photo
    r = requests.get(url)
    im = Image.open(BytesIO(r.content))
    im.crop((x1, y1, x2, y2)).save(photo, quality=95)
    session = boto3.session.Session(region_name='ru-central1')
    s3 = session.client(
        aws_access_key_id='',
        aws_secret_access_key='',
        service_name='s3',
        endpoint_url='https://storage.yandexcloud.net',
        region_name='ru-central1'
    )
    face = str(request.json['messages'][0]['details']['message']['message_id']) + str(photo)
    s3.upload_file(photo, new_bucket, face)
    #Write to ydb
    ydb_client = session.client('dynamodb', endpoint_url='/ru-central1/b1g71e95h51okii30p25/etnmgkku88n8f44mdgq4', aws_access_key_id='', aws_secret_access_key='')

    ydb_client.put_item(TableName='cloudlab', Item={
        'id': {
            'S': str(request.json['messages'][0]['details']['message']['message_id']) },
        'name': { 
                 'S': ''},
        'photo': {
            'S': photo},
        'face': {
            'S': face}
                                 })


    return response.json(
        {'message': "Handled."},
        status=200
    )


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ['PORT']), motd=False, access_log=False)
