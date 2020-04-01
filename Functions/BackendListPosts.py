import json
import logging
import pymysql
import datetime
import base64

from secretmanager import get_db_vars
from jwtvalidation import is_valid_jwt


logger = logging.getLogger()
logger.setLevel(logging.INFO)

rds_host, name, password, db_name = get_db_vars()

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
        channelID=params['channelID']
        
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
        
    resp = {}
    
    with conn.cursor() as cur:
        cur.execute('Select postID, channelID, userID, title, text, time_posted from Posts where channelID=%s order by time_posted limit 5', (channelID))
        (results ) = cur.fetchall()
        
        # print(channelIDs)
        
        for result in results:
            resp[result[0]] = {
                "channelID" : result[1],
                "userID" : result[2],
                "title" : result[3],
                "textbody" : result[4],
                "time_posted" : result[5].timestamp()
            }
            
        
    return {
        'statusCode': 200,
        'headers' : {
            "Access-Control-Allow-Origin": "*"
        },
        'body': json.dumps({
            "status" : 200,
            "posts" : resp
        })
    }


