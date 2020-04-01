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
from jwtvalidation import encode_jwt_payload

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

def randomStringDigits(stringLength=10):
    """Generate a random string of letters and digits """
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))
    
def lambda_handler(event, context):
    """
    This function fetches content from MySQL RDS instance
    """
    try:
        try:
            params = json.loads(event['body'])
        except:
            params = json.loads(base64.b64decode(event['body']))
        query_user = params['username']
        query_pass = params['password']
        if len(query_user) > 64:
            return {
                'statusCode': 200,
                'headers' : {
                    "Access-Control-Allow-Origin": "*"
                },
                'body': json.dumps({
                    'status' : 400,
                    'error' : "Username should be at most 64 characters"
                })
            }
        print(f"Username: {query_user}")
        print(f"Password (hashed): {query_pass}")
    except Exception as e: # Check error codes here!
        print(f"An error occurred: {e}")
        print(f"Event body: {event['body']}")
        return {
            'statusCode': 200,
            'headers' : {
                "Access-Control-Allow-Origin": "*"
            },
            'body': json.dumps({
                'status' : 400,
                'error' : f"Malformed Request"
            })
        }
        
    with conn.cursor() as cur:
        # cur.execute("create table Users (userID varchar(64) NOT NULL, username varchar(64) NOT NULL, password varchar(64) NOT NULL, email varchar(100), PRIMARY KEY (userID))")
        cur.execute("select salt, password, userID from Users where username=%s",(query_user))
        try:
            (salt,password,userID,) = cur.fetchone()
            query_pass = hashlib.sha256(f"{query_pass}{salt}".encode()).hexdigest()
            if password != query_pass:
                raise Exception
        except:
            return {
                'statusCode': 200,
                'headers' : {
                    "Access-Control-Allow-Origin": "*"
                },
                'body':json.dumps({
                    'status': 401,
                    'error': "Incorrect username or password"
                })
            }
    
    jwttoken = encode_jwt_payload({
        'session': randomStringDigits(10),
        'iat': datetime.datetime.now().timestamp(),
        'exp': (datetime.datetime.now() + datetime.timedelta(days=7)).timestamp(),
        'userID': userID
    })
    
    return {
        'statusCode': 200,
        'headers' : {
            "Access-Control-Allow-Origin": "*"
        },
        'body':json.dumps({
            'status': 200,
            'token': jwttoken
        })
    }
    
