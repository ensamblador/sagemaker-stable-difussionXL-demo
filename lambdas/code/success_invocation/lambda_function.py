## process whatsApp Cloud API message
## Updated to Whatsapp API v14
import json
import os
import boto3
from PIL import Image
from io import BytesIO
import base64
from datetime import datetime
from decimal import Decimal

s3_client = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

out_bucket = os.environ["BUCKET"]
out_prefix = os.environ["PREFIX"]




def upload_file_to_s3(file_path, bucket_name, object_key):
    # Upload the file to S3
    with open(file_path, "rb") as file:
        s3_client.upload_fileobj(file, bucket_name, object_key)

    print(f"File uploaded to s3://{bucket_name}/{object_key}")


def get_json_from_s3(bucket_name, object_key):
    # Retrieve the object from S3
    response = s3_client.get_object(Bucket=bucket_name, Key=object_key)

    # Read the object's contents as JSON
    json_data = response["Body"].read().decode("utf-8")
    json_object = json.loads(json_data)

    return json_object


def get_invocation_by_id(InvocationId):
    table = dynamodb.Table(os.environ["TABLE_NAME"])

    response = table.query(
        IndexName="InferenceId-index",
        KeyConditionExpression="InferenceId = :id",
        ExpressionAttributeValues={":id": InvocationId},
    )

    items = response.get("Items")
    if items:
        return items[0]

    return None

def save_image_data(invocation_data):
    table_name = os.environ['IMAGE_TABLE']
    table = dynamodb.Table(table_name)

    item = {
        "location": invocation_data["outputFile"],
        "ts": Decimal(int(datetime.now().timestamp())),
        "resolution": "high"
    }

    try:
        # Put the item into the table
        response = table.put_item(Item=item)
    except Exception as e:
        print(f'Error inserting item on {table_name}:', str(e))

def save_invocation_data(msg):
    table = dynamodb.Table(os.environ["TABLE_NAME"])
    item = get_invocation_by_id(msg["inferenceId"])

    if not (item):
        print("No hay Item")
        return

    end_time = int(datetime.now().timestamp())
    delta_time = end_time - int(item["startTime"])

    response = table.update_item(
        Key={"endpointName": item["endpointName"], "startTime": item["startTime"]},
        UpdateExpression="SET #item1 = :newState1, #item2 = :newState2, #item3 = :newState3, #item4 = :newState4,#item5 = :newState5",
        ExpressionAttributeNames={
            "#item1": "invocationStatus",
            "#item2": "endTime",
            "#item3": "seconds",
            "#item4": "outputFile",
            "#item5": "intermediateFiles"
        },
        ExpressionAttributeValues={
            ":newState1": msg["invocationStatus"],
            ":newState2": end_time,
            ":newState3": delta_time,
            ":newState4": msg["outputFile"],
            ":newState5": json.dumps(
                {
                    "in": msg["requestParameters"]["inputLocation"],
                    "out": msg["responseParameters"]["outputLocation"],
                }
            ),
        },
        ReturnValues="UPDATED_NEW",
    )


def lambda_handler(event, context):
    print(event)

    records = event.get("Records")
    if not (records):
        print("Sin Records")
        return build_response(200, json.dumps("Sin records"))

    for rec in records:
        msg = json.loads(rec["Sns"]["Message"])
        print(msg)
        output_location = msg["responseParameters"]["outputLocation"]
        input_location = msg["requestParameters"]["inputLocation"]

        inference_id = msg["inferenceId"]
        endpoint_name = msg["requestParameters"]["endpointName"]

        output_location_parts = output_location.split("s3://")[1].split("/")
        output_location_bucket = output_location_parts[0]
        output_location_key = "/".join(output_location_parts[1:])

        file_name_orig = input_location.split("/")[-1].split(".")[0]
        file_name = f"{file_name_orig}x4.jpg"

        output = get_json_from_s3(output_location_bucket, output_location_key)
        generated_images, prompt = output["generated_images"], output["prompt"]
        scaled_image = generated_images[0]
        scaled_image_decoded = BytesIO(base64.b64decode(scaled_image.encode()))

        scaled_image_rgb = Image.open(scaled_image_decoded).convert("RGB")
        scaled_image_rgb.save(f"/tmp/{file_name}")

        upload_file_to_s3(f"/tmp/{file_name}", out_bucket, f"{out_prefix}/{file_name}")

        msg["outputFile"] = f"s3://{out_bucket}/{out_prefix}/{file_name}"
        save_invocation_data(msg)
        save_image_data(msg)

    return build_response(200, json.dumps("All good!"))



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
