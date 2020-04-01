import json
import sys
import logging
import pymysql
import os
import hashlib
import jwt
import string
import random
import datetime
import re
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
        query_email = params['email']
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
        if len(query_email) > 100:
            return {
                'statusCode': 200,
                'headers' : {
                    "Access-Control-Allow-Origin": "*"
                },
                'body': json.dumps({
                    'status' : 400,
                    'error' : "Email should be at most 100 characters"
                })
            }
        regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
        if not re.search(regex, query_email):
            return {
                'statusCode': 200,
                'headers' : {
                    "Access-Control-Allow-Origin": "*"
                },
                'body': json.dumps({
                    'status' : 400,
                    'error' : "Invalid Email"
                })
            }
        print(f"Username: {query_user}")
        print(f"Password (hashed): {query_pass}")
        print(f"Email: {query_email}")
    except Exception as e: # Check error codes here!
        print(f"Error: {e}")
        logging.error(f"Event body: {event['body']}")
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
        cur.execute("select userID from Users where username=%s",(query_user))
        try:
            (userID,) = cur.fetchone()
            return {
                'statusCode': 200,
                'headers' : {
                    "Access-Control-Allow-Origin": "*"
                },
                'body':json.dumps({
                    'status': 401,
                    'error': "Username already in use"
                })
            }
        except:
            pass
        
        cur.execute("select userID from Users where email=%s",(query_email))
        try:
            (userID,) = cur.fetchone()
            return {
                'statusCode': 2,
                'headers' : {
                    "Access-Control-Allow-Origin": "*"
                },
                'body':json.dumps({
                    'status': 401,
                    'error': "Email already in use"
                })
            }
        except:
            pass
        
        salt = randomStringDigits(20)
        query_pass = hashlib.sha256(f"{query_pass}{salt}".encode()).hexdigest()
        userID = hashlib.sha256(f"{query_user}{query_pass}".encode()).hexdigest()
        cur.execute("insert into Users(userID, username, password, email, salt) values(%s, %s, %s, %s, %s)", (userID, query_user, query_pass, query_email, salt))
        conn.commit()
        
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
    
