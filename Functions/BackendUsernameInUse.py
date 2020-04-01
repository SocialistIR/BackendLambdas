import json
import sys
import logging
import pymysql
import os
import base64
from secretmanager import get_db_vars

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
    """
    This function fetches content from MySQL RDS instance
    """
    try:
        try:
            params = json.loads(event['body'])
        except:
            params = json.loads(base64.b64decode(event['body']))
        query_user = params['username']
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
        print(f"Username (check if valid): {query_user}")
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
                    'available': False
                })
            }
        # Query returned no rows
        except:
            return {
                'statusCode': 200,
                'headers' : {
                    "Access-Control-Allow-Origin": "*"
                },
                'body':json.dumps({
                    'available': True
                })
            }
    
