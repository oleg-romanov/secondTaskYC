import boto3
import io
import base64
import requests
import json


def handler(event, context):
    bucket_id = event['messages'][0]['details']['bucket_id']
    object_id = event['messages'][0]['details']['object_id']

    session = boto3.session.Session()
    s3 = session.client(
        aws_access_key_id="", #TODO set params
        aws_secret_access_key="", #TODO set params
        service_name='s3',
        endpoint_url='https://storage.yandexcloud.net'
    )
    img = io.BytesIO()
    s3.download_fileobj(bucket_id, object_id, img)

    encoded_img = base64.b64encode(img.getbuffer().tobytes())

    response = requests.post("https://vision.api.cloud.yandex.net/vision/v1/batchAnalyze",
                        data=json.dumps({
                                "folderId": "b1gpe6vpo4egarkpset4",
                                "analyze_specs": [{
                                    "content": encoded_img.decode("UTF-8"),
                                    "features": [{
                                        "type": "FACE_DETECTION"
                                    }]
                                }]
                            }
                        ), 
                        headers={
                            "Content-Type": "application/json",
                            "Authorization": "Bearer <IAM TOKEN>" #TODO set param 
                        })

    print(response)
    print('------')
    print(response.json())

    queue_client = boto3.client(
        aws_access_key_id="", #TODO set param
        aws_secret_access_key="", #TODO set param
        service_name='sqs',
        endpoint_url='https://message-queue.api.cloud.yandex.net',
        region_name='ru-central1'
    )
    queue_url = queue_client.get_queue_url(QueueName="vvot12-tasks")['QueueUrl']
    print('Created queue url is "{}"'.format(queue_url))

    for face in response.json()['results'][0]['results'][0]['faceDetection']['faces']:
            queue_client.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps({
                    'object_id': object_id,
                    'vertices': face['boundingBox']['vertices']
                })
            )
    messages = queue_client.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=10,
        VisibilityTimeout=60,
        WaitTimeSeconds=20
    ).get('Messages')
    for msg in messages:
        print('Received message: "{}"'.format(msg.get('Body')))


