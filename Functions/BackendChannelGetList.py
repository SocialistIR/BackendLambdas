# Returns all channels for now...

import json
import sys
import logging
import pymysql
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
    # TODO implement
    '''
    try:
        try:
            params = json.loads(event['body'])
        except:
            params = json.loads(base64.b64decode(event['body']))
        #token = params['token']
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
    '''
    
    with conn.cursor() as cur:
        '''
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
        '''
        #cur.execute("select Channels.channelID, Channels.title from ChannelUsers left join Channels on ChannelUsers.channelID = Channels.channelID where ChannelUsers.userID=%s", (userID,))
        cur.execute("select channelID, title from Channels limit 100")
        conn.commit()
        toret = {}
        for row in cur.fetchall():
            print(row)
            (channelID, channelName,) = row
            toret[channelID] = {
                "channelName" : channelName
            }
        return {
            'statusCode': 200,
            'headers' : {
                "Access-Control-Allow-Origin": "*"
            },
            'body': json.dumps({
                'statusCode' : 200,
                'channels' : toret
            })
        }
            
        
