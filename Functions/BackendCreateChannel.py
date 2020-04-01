import json
import sys
import logging
import pymysql
import os
import hashlib
import string
import random
import datetime
import re
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

def lambda_handler(event, context):
    # TODO implement
    
    try:
        try:
            params = json.loads(event['body'])
        except:
            params = json.loads(base64.b64decode(event['body']))
        token = params['token']
        title = params['title'].lower()
        
        
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
    
    with conn.cursor() as cur:
        is_valid, validation_data = is_valid_jwt(token, cur)
        if not is_valid:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'statusCode' : 401,
                    'error' : f'Unauthorized: {validation_data}'
                })
            }
        userID = validation_data['userID']
        # Check if channel is already in use
        cur.execute('select count(*) from Channels where title=%s', (title,))
        (numrows, ) = cur.fetchone()
        if numrows > 0:
            return {
                'statusCode': 200,
                'headers' : {
                    "Access-Control-Allow-Origin": "*"
                },
                'body': json.dumps({
                    'statusCode' : 400,
                    'error' : f'Channel name already in use'
                })
            }
        cur.execute('insert into Channels(title, userID) values (%s, %s)',(title, userID))
        cur.execute('select channelID from Channels where title=%s', (title, ))
        (channelID, ) = cur.fetchone()
        cur.execute('insert into ChannelUsers(channelID, userID) values (%s,%s)', (channelID, userID))
        conn.commit()
    
    return {
        'statusCode': 200,
        'headers' : {
            "Access-Control-Allow-Origin": "*"
        },
        'body': json.dumps({
            'statusCode' : 200,
            'channelID' : channelID
        })
    }
