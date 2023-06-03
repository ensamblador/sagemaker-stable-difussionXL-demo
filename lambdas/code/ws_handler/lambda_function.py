## process whatsApp Cloud API message
## Updated to Whatsapp API v14
import json
import os
import boto3


dynamodb = boto3.resource("dynamodb")



def lambda_handler(event, context):
    print(event)
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
