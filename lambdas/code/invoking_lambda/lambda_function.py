## process whatsApp Cloud API message
## Updated to Whatsapp API v14
import json
import os
import base64

import boto3
s3_client = boto3.client('s3')
sm_runtime = boto3.client('sagemaker-runtime')

def get_file_contents(bucket_name, file_key):

    # Create an S3 client

    try:
        # Retrieve the file from S3 as bytes
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        file_bytes = response['Body'].read()

        # Return the file as bytes
        return file_bytes

    except Exception as e:
        print(f"Error retrieving file: {e}")
        return False


def convert_img2payload(img_contents, prompt=""):
    

    encoded_image = base64.b64encode(bytearray(img_contents)).decode()

    payload = {
        "prompt": prompt,
        "image": encoded_image,
        "num_inference_steps": 75,
        "guidance_scale": 9.0,
        "noise_level": 20
    }

    
    return payload


def upload_json_to_s3(json_data, bucket_name, file_key, content_type):

    try:
        # Convert the JSON data to bytes
        file_bytes = json.dumps(json_data).encode('utf-8')

        # Upload the JSON file to S3
        response = s3_client.put_object(Body=file_bytes, Bucket=bucket_name, Key=file_key, ContentType=content_type)

        print(f"JSON data uploaded to S3: {bucket_name}/{file_key}")

        return f"s3://{bucket_name}/{file_key}"

    except Exception as e:
        print(f"Error uploading JSON data to S3: {e}")
        raise

def lambda_handler(event, context):
    print (event)
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_key = event['Records'][0]['s3']['object']['key']
    file_name = file_key.split('/')[-1]

    input_bucket = os.environ['BUCKET']
    payload_prefix = os.environ['PAYLOAD_PREFIX']
    endpoint_name = os.environ['SM_ENDPOINT']

    file_contents = get_file_contents(bucket_name, file_key)

    if not(file_contents):  
        print('Archivo Vacío')
        return build_response (200,json.dumps('Vacío!'))

    # Usar el prompt de la imagen original, tal vez escribirla en la metadata del Objeto
    payload = convert_img2payload(file_contents)
    s3_location  =  upload_json_to_s3(payload,input_bucket, f"{payload_prefix}/{file_name}.payload", 'application/json;jpeg')
    response = sm_runtime.invoke_endpoint_async(EndpointName=endpoint_name, InputLocation=s3_location, Accept='application/json;jpeg')
    print (response)


    return build_response (200,json.dumps(response))



def build_response(status_code, json_content):
        return {
        'statusCode': status_code,
        "headers": {
            "Content-Type": "text/html;charset=UTF-8",
            "charset": "UTF-8",
            "Access-Control-Allow-Origin": "*"
        },
        'body': json_content
    }