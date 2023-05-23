## process whatsApp Cloud API message
## Updated to Whatsapp API v14
import json
import os
import boto3
from PIL import Image
from io import BytesIO
import base64

s3_client = boto3.client('s3')

out_bucket = os.environ['BUCKET']
out_prefix = os.environ['PREFIX']

def upload_file_to_s3(file_path, bucket_name, object_key):
    
    # Upload the file to S3
    with open(file_path, 'rb') as file:
        s3_client.upload_fileobj(file, bucket_name, object_key)
    
    print(f"File uploaded to s3://{bucket_name}/{object_key}")


def get_json_from_s3(bucket_name, object_key):

    # Retrieve the object from S3
    response = s3_client.get_object(Bucket=bucket_name, Key=object_key)

    # Read the object's contents as JSON
    json_data = response['Body'].read().decode('utf-8')
    json_object = json.loads(json_data)

    return json_object

def parse_response(query_response):
    """Parse response and return the generated images and prompt."""

    response_dict = json.loads(query_response)
    return response_dict["generated_images"], response_dict["prompt"]

def lambda_handler(event, context):
    print(event)

    records = event.get("Records")
    if not (records):
        print("Sin Records")
        return build_response(200, json.dumps("Sin records"))

    for rec in records:

        msg = json.loads(rec["Sns"]["Message"])
        print (msg)
        output_location = msg["responseParameters"]["outputLocation"]
        input_location = msg["requestParameters"]["inputLocation"]

        inference_id =  msg["inferenceId"]
        endpoint_name =  msg["requestParameters"]["endpointName"]
        
        output_location_parts = output_location.split('s3://')[1].split('/')
        output_location_bucket = output_location_parts[0]
        output_location_key = '/'.join(output_location_parts[1:])
        
        
        file_name_orig = input_location.split('/')[-1].split('.')[0]
        file_name = f'{file_name_orig}x4.jpg'

        output = get_json_from_s3(output_location_bucket,output_location_key )
        generated_images, prompt = output["generated_images"], output["prompt"] #parse_response(output)
        scaled_image = generated_images[0]
        scaled_image_decoded = BytesIO(base64.b64decode(scaled_image.encode()))

        scaled_image_rgb = Image.open(scaled_image_decoded).convert("RGB")
        scaled_image_rgb.save(f'/tmp/{file_name}')

        upload_file_to_s3(f'/tmp/{file_name}', out_bucket, f"{out_prefix}/{file_name}")

    return build_response(200, json.dumps("All good!"))

    message = {
        "awsRegion": "us-east-1",
        "eventTime":    "2023-05-23T03:23:21.814Z",
        "receivedTime": "2023-05-23T03:23:09.588Z",
        "invocationStatus": "Completed",
        "requestParameters": {
            "accept": "application/json;jpeg",
            "endpointName": "EEndpoint1CBD216E-N0iXvhsBov7n",
            "inputLocation": "s3://sdx4upscaler-b08e7c7af-vc56motqrwj5/payload_imagescat128.png.payload",
        },
        "responseParameters": {
            "contentType": "application/json;jpeg",
            "outputLocation": "s3://sdx4upscaler-b08e7c7af-vc56motqrwj5/inferences/output/2f4dcf85-01b8-418c-8c93-2b30fcdd1ab8.out",
        },
        "inferenceId": "8a80ed4e-1ff9-4c2b-bf16-31bdd5d17835",
        "eventVersion": "1.0",
        "eventSource": "aws:sagemaker",
        "eventName": "InferenceResult",
    }

    event = {
        "Records": [
            {
                "EventSource": "aws:sns",
                "EventVersion": "1.0",
                "EventSubscriptionArn": "arn:aws:sns:us-east-1:844626608976:SDx4Upscaler-SNS7073F6E6-k2qlB4XgaoSq:1710c1a3-6cdd-45c6-8524-a0e269b91585",
                "Sns": {
                    "Type": "Notification",
                    "MessageId": "c9cafd57-db5c-5f85-9c8f-a1b1e8b5a527",
                    "TopicArn": "arn:aws:sns:us-east-1:844626608976:SDx4Upscaler-SNS7073F6E6-k2qlB4XgaoSq",
                    "Subject": null,
                    "Message": '{"awsRegion":"us-east-1","eventTime":"2023-05-23T03:23:21.814Z","receivedTime":"2023-05-23T03:23:09.588Z","invocationStatus":"Completed","requestParameters":{"accept":"application/json;jpeg","endpointName":"EEndpoint1CBD216E-N0iXvhsBov7n","inputLocation":"s3://sdx4upscaler-b08e7c7af-vc56motqrwj5/payload_imagescat128.png.payload"},"responseParameters":{"contentType":"application/json;jpeg","outputLocation":"s3://sdx4upscaler-b08e7c7af-vc56motqrwj5/inferences/output/2f4dcf85-01b8-418c-8c93-2b30fcdd1ab8.out"},"inferenceId":"8a80ed4e-1ff9-4c2b-bf16-31bdd5d17835","eventVersion":"1.0","eventSource":"aws:sagemaker","eventName":"InferenceResult"}',
                    "Timestamp": "2023-05-23T03:23:21.961Z",
                    "SignatureVersion": "1",
                    "Signature": "PYpWtLPK2jL1SDWPX2M0BS1YSu9lk0um9KC/ZW+UeS+0ET5NcoumtmIkfg1lbYA4eoiLaO7DJfLxcOHmoHfJzjReYthpmD3PvMgDu/A834FtGdUvRpztgSvzY7qJxs7shwjgkUWNaeAF8S21NZdhxpm4fvn4f6MbUoRQKBXiws8EF0gdY7bQcqZGsAKq4TAyrqShWaLM1MPAG1SZm91mJzdUzAPVOyiKr6WAddHSwBckTMWkhpasnFodJc2zMkAfzYJyGzA+uQHhRFAbaI4qPcffqbhZSJTZTblGOQwEAwxdfkcUbTWwinyrtIJOAXn8DHXB7liv3qgbsSR5hH7oYA==",
                    "SigningCertUrl": "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-01d088a6f77103d0fe307c0069e40ed6.pem",
                    "UnsubscribeUrl": "https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-1:844626608976:SDx4Upscaler-SNS7073F6E6-k2qlB4XgaoSq:1710c1a3-6cdd-45c6-8524-a0e269b91585",
                    "MessageAttributes": {},
                },
            }
        ]
    }



def build_response(status_code, json_content):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "text/html;charset=UTF-8",
            "charset": "UTF-8",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json_content,
    }
