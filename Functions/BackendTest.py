import json

def lambda_handler(event, context):
    # TODO implement
    return {
        'statusCode': 200,
        'headers' : {
            "Access-Control-Allow-Origin": "*"
        },
        'body': json.dumps('Hello from Lambda!')
    }
