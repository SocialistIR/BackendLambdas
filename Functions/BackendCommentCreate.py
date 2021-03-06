import json
import sys
import logging
import pymysql
import os
import hashlib
import string
import random
import datetime
import base64
from secretmanager import get_db_vars
from jwtvalidation import is_valid_jwt

#rds settings
rds_host, name, password, db_name = get_db_vars()

logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=10)
except pymysql.MySQLError as e:
    logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
    logger.error(e)
    sys.exit()

logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")

def randomStringDigits(stringLength=45):
    """Generate a random string of letters and digits """
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))

def lambda_handler(event, context):
    # TODO implement
    
    try:
        try:
            params = json.loads(event['body'])
        except:
            params = json.loads(base64.b64decode(event['body']))
        token = params['token']
        postID=params['postID']
        comment=params['comment']
        logger.info(params)
        print(params)
    except Exception as e:
        logger.error(e)
        return {
            'statusCode': 200,
            'headers' : {
                "Access-Control-Allow-Origin": "*"
            },
            'body': json.dumps({
                'status': 400,
                'error': "Malformed request"
            })
        }
    
    try:
        parentID = params['parentID']
    except:
        parentID = None
    
    with conn.cursor() as cur:
        is_valid, validation_data = is_valid_jwt(token, cur)
        if not is_valid:
            return {
                'statusCode': 200,
                'headers' : {
                    "Access-Control-Allow-Origin": "*"
                },
                'body': json.dumps({
                    'statusCode' : 401,
                    'error' : f'Unauthorized: {validation_data}'
                })
            }
        userID = validation_data['userID']
        cur.execute('select count(*) from Posts where postID=%s', (postID,))
        (numrows, ) = cur.fetchone()
        if numrows <= 0:
            return {
                'statusCode': 200,
                'headers' : {
                    "Access-Control-Allow-Origin": "*"
                },
                'body': json.dumps({
                    'statusCode' : 400,
                    'error' : 'Invalid postID'
                })
            }
        # check if parent id is valid
        if parentID is not None:
            cur.execute('select count(*) from Comments where postID=%s and commentID=%s', (postID, parentID, ))
            (numrows, ) = cur.fetchone()
            if numrows <= 0:
                return {
                    'statusCode': 200,
                    'headers' : {
                        "Access-Control-Allow-Origin": "*"
                    },
                    'body': json.dumps({
                        'statusCode' : 400,
                        'error' : 'Invalid parentID'
                    })
                }
        commentID = f"{int(datetime.datetime.now().timestamp())}_{randomStringDigits()}"
        cur.execute('insert into Comments(commentID, postID, comment, userID, parentID) values (%s, %s, %s, %s, %s)',(commentID, postID, comment, userID, parentID))
        conn.commit()
    
    return {
        'statusCode': 200,
        'headers' : {
            "Access-Control-Allow-Origin": "*"
        },
        'body': json.dumps({
            'statusCode' : 200,
            'commentID' : commentID
        })
    }
