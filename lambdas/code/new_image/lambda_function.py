## process whatsApp Cloud API message
## Updated to Whatsapp API v14
import json
import os
import boto3



dynamodb = boto3.resource("dynamodb")

def scan_dynamodb_table(table_name):

    table = dynamodb.Table(table_name)
    
    items = []
    response = table.scan()
    
    while 'Items' in response:
        items.extend(response['Items'])
        
        if 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        else:
            break

    return items


def process_images(images):
    processed = []
    cloudfront_dns = os.environ['DISTRUBUTION_NAME']
    for im in images:
        parts = im['location'].split("s3://")[1].split("/")
        bucket = parts[0]
        filename = parts[-1]
        path = "/".join(parts[1:-1])
        url = f"https://{cloudfront_dns}/{path}/{filename}"

        processed.append({
            'bucket': bucket,
            'path': path,
            'filename': filename,
            'resolution': im['resolution'],
            'url': url
        })
    return processed

def convert_records_to_json(records):
    deserializer = boto3.dynamodb.types.TypeDeserializer()
    json_records = []
    
    for record in records:
        # Extract the DynamoDB record data
        if 'NewImage' in record['dynamodb']:
            data = record['dynamodb']['NewImage']
        elif 'OldImage' in record['dynamodb']:
            data = record['dynamodb']['OldImage']
        else: 
            continue
        
        # Convert the record data to JSON using TypeDeserializer
        json_data = {}
        for key, value in data.items():
            json_data[key] = deserializer.deserialize(value)
        
        # Append the JSON record to the list
        json_records.append(json_data)
    
    return json_records


def lambda_handler(event, context):
    print (event)
    if not(event.get('Records')):
        return build_response(200, json.dumps("No records"))


    json_records = convert_records_to_json(event.get('Records'))
    items = process_images(json_records)
    ws_endpoint = os.environ['WS_ENDPOINT']
    client = boto3.client('apigatewaymanagementapi', endpoint_url = ws_endpoint)
    
    table_name = os.environ['CONNECTIONS_TABLE']
    connections = scan_dynamodb_table(table_name)
    
    
    for con in connections:
        print ("connection:", con)
        if len(items)>0:

            try:
                response = client.post_to_connection(
                    Data=json.dumps(items[0]),
                    ConnectionId=con['connectionId'])
        
            except Exception as e:
                print(f"Error : {e}")
                




    #endpoint_url='https://{api-id}.execute-api.{your-aws-region}.amazonaws.com/{stage}')

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
