import json
import sys
import logging
import pymysql
import os
import hashlib
import jwt
import datetime
import base64
from secretmanager import get_db_vars
from jwtvalidation import is_valid_jwt

#rds settings
rds_host, name, password, db_name = get_db_vars()

logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
except pymysql.MySQLError as e:
    logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
    logger.error(e)
    sys.exit()

logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")

def lambda_handler(event, context):
    """
    This function fetches content from MySQL RDS instance
    """
    try:
        try:
            params = json.loads(event['body'])
        except:
            params = json.loads(base64.b64decode(event['body']))
        query_token = params["token"]
        print(f"Token: {query_token}")
    except:
        return {
            'statusCode': 200,
            'headers' : {
                "Access-Control-Allow-Origin": "*"
            },
            'body': json.dumps({
                'status' : 400,
                'error' : "Malformed Request"
            })
        }

    
    with conn.cursor() as cur:
        # Delete expired tokens, as even if revalidated 'exp' means jwt token is expired
        week_ago = int((datetime.datetime.now() + datetime.timedelta(days=-7)).timestamp())
        print(week_ago)
        # cur.execute("create table TokenBlacklist (token varchar(256) NOT NULL, blacklist_ts timestamp default current_timestamp)")")
        cur.execute("delete from TokenBlacklist where blacklist_ts<%s", (week_ago))
        is_valid, validation_data = is_valid_jwt(query_token, cur)
        if not is_valid:
            return {
                'statusCode': 200,
                'headers' : {
                    "Access-Control-Allow-Origin": "*"
                },
                'body': json.dumps({
                    'status' : 401,
                    'error' : f"Unauthorised: {validation_data}"
                })
            }
        cur.execute("insert into TokenBlacklist(token) values(%s)", (query_token))
        conn.commit()
    
    return {
        'statusCode': 200,
        'headers' : {
            "Access-Control-Allow-Origin": "*"
        },
        'body':json.dumps({
            'status': 200
        })
    }
    
