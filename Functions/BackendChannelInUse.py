import json
import sys
import logging
import pymysql
import 
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
        title = params['channel'].lower()
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
        # Check if channel is already in use
        cur.execute('select count(*) from Channels where title=%s', (title,))
        (numrows, ) = cur.fetchone()
        conn.commit()
        if numrows > 0:
            return {
                'statusCode': 200,
                'headers' : {
                    "Access-Control-Allow-Origin": "*"
                },
                'body': json.dumps({
                    'available' : False
                })
            }
        else:
            return {
                'statusCode': 200,
                'headers' : {
                    "Access-Control-Allow-Origin": "*"
                },
                'body': json.dumps({
                    'available' : True
                })
            }
        
