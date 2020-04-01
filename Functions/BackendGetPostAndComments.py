import json
import sys
import logging
import pymysql
import os
import datetime
import base64
from secretmanager import get_db_vars

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
    # TODO implement
    
    try:
        try:
            params = json.loads(event['body'])
        except:
            params = json.loads(base64.b64decode(event['body']))
        postID=params['postID']
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
        cur.execute('select postID, title, text, time_posted from Posts where postID=%s', (postID,))
        try:
            (postID, title, text, time_posted) = cur.fetchone()
            postData = {
                "title" : title,
                "text" : text,
                "time_posted" : time_posted.timestamp()
            }
        except:
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
        
        cur.execute('select commentID, userID, comment, parentID, time_posted from Comments where postID=%s order by time_posted asc', (postID))
        comments_resp = {}
        for row in cur.fetchall():
            (commentID, userID, comment, parentID, time_posted) = row
            comments_resp[commentID] = {
                "userID" : userID,
                "comment" : comment,
                "time_posted" : time_posted.timestamp(),
                "parentID" : parentID
            }
        
    return {
        'statusCode': 200,
        'headers' : {
            "Access-Control-Allow-Origin": "*"
        },
        'body': json.dumps({
            'statusCode' : 200,
            'post' : {
                postID : postData
            },
            'comments' : comments_resp
        })
    }