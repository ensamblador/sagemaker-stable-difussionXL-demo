## process whatsApp Cloud API message
## Updated to Whatsapp API v14
import json
import decimal
import os
import boto3


dynamodb = boto3.resource("dynamodb")


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)
    

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

def split_low_high_res(images):
    high = []
    low = []
    for im in images:

        parts = im['location'].split("s3://")[1].split("/")
        bucket = parts[0]
        filename = parts[-1]
        path = parts[1:-1]

        if im['resolution'] == 'high':
            high.append({
                'bucket': bucket,
                'path': "/".join(path),
                'filename': filename,
                'resolution': 'high'
            })
        else:
            low.append({
                'bucket': bucket,
                'path': "/".join(path),
                'filename': filename,
                'resolution': 'low'
            })
    return high, low

def get_im_from_list(filename, list):
    for im in list:
        if im['filename'].split('.')[0] == filename:
            return im
    return None

def mix_images (high, low):
    images = []

    for lim in low:
        filename = lim['filename'].split('.')[0]
        hr_filename = f"{filename}x4"
        hr_image = get_im_from_list(hr_filename, high)
        if hr_image:
            images.append(hr_image)
            high.remove(hr_image)
        else:
            images.append(lim)

    for him in high:
        images.append(him)
    return images


def lambda_handler(event, context):
    table_name = os.environ['IMAGE_TABLE']
    cloudfront_dns = os.environ['DISTRUBUTION_NAME']
    items = scan_dynamodb_table(table_name)
    high, low = split_low_high_res(items)
    mixed_images = mix_images(high,[])# low)
    for im in mixed_images:
        path = im['path']
        filename = im['filename']
        url = f"https://{cloudfront_dns}/{path}/{filename}"
        im['url'] = url

    return build_response(200, json.dumps({"items":mixed_images}))



def build_response(status_code, json_content):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json;charset=UTF-8",
            "charset": "UTF-8",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json_content,
    }
