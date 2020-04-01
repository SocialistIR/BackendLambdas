import json
import boto3
import base64

s3 = boto3.client('s3')
    
def lambda_handler(event, context):
    bucket = 'backend-image-storage'
    key = event['queryStringParameters']['image']
    try:
        data = s3.get_object(Bucket=bucket, Key=key)
    except Exception as e:
        return {
            'statusCode': 200,
            'headers' : {
                "Access-Control-Allow-Origin": "*"
            },
            'body': json.dumps({
                'status' : 404,
                'error' : "Could not find resource"
            })
        }

    return {
        'statusCode': 200,
        'headers' : {
            'Content-Type' : 'image/jpeg',
            "Access-Control-Allow-Origin": "*"
        },
        'body': base64.b64encode(data['Body'].read()).decode(),
        "isBase64Encoded": True
    }