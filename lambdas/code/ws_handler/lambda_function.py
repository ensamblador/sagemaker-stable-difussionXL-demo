## process whatsApp Cloud API message
## Updated to Whatsapp API v14
import json
import os
import boto3


dynamodb = boto3.resource("dynamodb")

def store_connection(connetionId):
    if not(connetionId): return
    table_name = os.environ['CONNECTIONS_TABLE']

    table = dynamodb.Table(table_name)
    try:
        # Put the item into the table
        response = table.put_item(Item={"connectionId": connetionId})
        print(f'Item inserted successfully on {table_name}:', response)
    except Exception as e:
        print(f'Error inserting item on {table_name}:', str(e))


def delete_connection(connetionId):
    if not(connetionId): return
    table_name = os.environ['CONNECTIONS_TABLE']

    table = dynamodb.Table(table_name)
    try:
        # Put the item into the table
        response = table.delete_item(Key={"connectionId": connetionId})
        print(f'Item deleted successfully on {table_name}:', response)
    except Exception as e:
        print(f'Error deleting item on {table_name}:', str(e))

def lambda_handler(event, context):
    print(event)
    request_context = event.get("requestContext")
    if not(request_context):  return build_response(200, json.dumps("No request contextt"))

    route_key = request_context.get("routeKey")
    if route_key == "$connect": 
        store_connection(request_context.get("connectionId"))
        build_response(200, json.dumps("Connected"))

    if route_key == "$disconnect": 
        delete_connection(request_context.get("connectionId"))
        build_response(200, json.dumps("Connected"))
    
    
    return {
        "statusCode": 200,
        "body": "OK",
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
