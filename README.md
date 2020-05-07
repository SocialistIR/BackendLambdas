# Backend Lambdas
AWS Lambda functions and layers for Mock Social Media Application

## Overview
These are AWS Lambda functions meant to be used in conjunction with Amazon API Gateway and Amazon RDS to create a publically accessible backend API for a mock social media web application based off Reddit.

The code is written in python 3, and uses mySQL (although postgreSQL is a viable alternative if psycopg2 is added to the layer instead). It may also require an Amazon S3 bucket for storing and returning images if required.

## Table Layout

You will need to create an Amazon RDS with the preferred DB type (this code supports mySQL by default). You will then need to set up AWS Secrets Manager to manage your Amazon RDS credentials - our function layers will query AWS Secrets Manager to connect to the database. You will then need to manually create the tables to match the following:

**All Tables**
```
mysql> SHOW TABLES;
+-------------------+
| Tables_in_backend |
+-------------------+
| ChannelUsers      |
| Channels          |
| Comments          |
| Posts             |
| TokenBlacklist    |
| Users             |
+-------------------+
6 rows in set (0.25 sec)
```
**ChannelUsers**
```
mysql> DESCRIBE ChannelUsers;
+-----------+-------------+------+-----+---------+----------------+
| Field     | Type        | Null | Key | Default | Extra          |
+-----------+-------------+------+-----+---------+----------------+
| rowID     | int(12)     | NO   | PRI | NULL    | auto_increment |
| channelID | varchar(64) | NO   | UNI | NULL    |                |
| userID    | varchar(64) | NO   |     | NULL    |                |
+-----------+-------------+------+-----+---------+----------------+
3 rows in set (0.26 sec)
```
**Channels**
```
mysql> DESCRIBE Channels;
+-----------+-------------+------+-----+---------+----------------+
| Field     | Type        | Null | Key | Default | Extra          |
+-----------+-------------+------+-----+---------+----------------+
| channelID | int(12)     | NO   | PRI | NULL    | auto_increment |
| title     | varchar(64) | NO   | UNI | NULL    |                |
| userID    | varchar(64) | NO   |     | NULL    |                |
+-----------+-------------+------+-----+---------+----------------+
3 rows in set (0.25 sec)
```
**Comments**
```
mysql> DESCRIBE Comments;
+-------------+----------------+------+-----+-------------------+-------+
| Field       | Type           | Null | Key | Default           | Extra |
+-------------+----------------+------+-----+-------------------+-------+
| commentID   | varchar(64)    | NO   | PRI | NULL              |       |
| postID      | varchar(64)    | NO   |     | NULL              |       |
| comment     | varchar(10000) | NO   |     | NULL              |       |
| parentID    | varchar(64)    | YES  |     | NULL              |       |
| userID      | varchar(64)    | NO   |     | NULL              |       |
| time_posted | timestamp      | YES  |     | CURRENT_TIMESTAMP |       |
+-------------+----------------+------+-----+-------------------+-------+
6 rows in set (0.25 sec)
```
**Posts**
```
mysql> DESCRIBE Posts;
+-------------+----------------+------+-----+-------------------+-------+
| Field       | Type           | Null | Key | Default           | Extra |
+-------------+----------------+------+-----+-------------------+-------+
| postID      | varchar(64)    | NO   | PRI | NULL              |       |
| channelID   | varchar(64)    | NO   |     | NULL              |       |
| userID      | varchar(64)    | NO   |     | NULL              |       |
| title       | varchar(200)   | NO   |     | NULL              |       |
| text        | varchar(40000) | NO   |     | NULL              |       |
| time_posted | timestamp      | YES  |     | CURRENT_TIMESTAMP |       |
+-------------+----------------+------+-----+-------------------+-------+
6 rows in set (0.25 sec)
```
**TokenBlacklist**
```
mysql> DESCRIBE TokenBlacklist;
+--------------+--------------+------+-----+-------------------+-------+
| Field        | Type         | Null | Key | Default           | Extra |
+--------------+--------------+------+-----+-------------------+-------+
| token        | varchar(512) | NO   |     | NULL              |       |
| blacklist_ts | timestamp    | YES  |     | CURRENT_TIMESTAMP |       |
+--------------+--------------+------+-----+-------------------+-------+
2 rows in set (0.26 sec)
```
**Users**
```
mysql> DESCRIBE Users;
+----------+--------------+------+-----+---------+-------+
| Field    | Type         | Null | Key | Default | Extra |
+----------+--------------+------+-----+---------+-------+
| userID   | varchar(64)  | NO   | PRI | NULL    |       |
| username | varchar(64)  | NO   | UNI | NULL    |       |
| password | varchar(64)  | NO   |     | NULL    |       |
| email    | varchar(100) | NO   | UNI | NULL    |       |
| salt     | varchar(20)  | NO   |     | NULL    |       |
+----------+--------------+------+-----+---------+-------+
5 rows in set (0.26 sec)
```
## Lambdas

Titles of the Lambdas should be pretty self explanatory. You can link them to a REST API Gateway, with the Integration Request for each method being of type LAMBDA_PROXY. All Lambdas should have the layer(s) in the Layer folder added to them for JWT and mySQL support. Lambdas should have a role which is inclusive of the managed policy 'AWSLambdaVPCAccessExecutionRole'. Image upload/download Lambdas also need S3 read/write permissions. Lambdas should be in the same VPC as the RDS.

## Limitations

 - **SECURITY** Currently, the secret used to encode and decode JWT tokens is stored in the layer. This is bad practice and should preferably moved to something like Secrets Manager.
 - **OPTIMISATION** Currently TokenBlacklist is being cleaned up everytime the Logout Lambda is being called. It is better practice to schedule a CloudWatch event to regularly trigger a Lambda to clean up the TokenBlacklist table instead.

## User Discretion

The following variables should be checked at and changed as per user's discretion-
- secret_name: (Layers/secretmanager.py) MySQL backend
- region_name: (Layers/secretmanager.py) Deployment Region
- GLOBAL_SECRET: (Layers/jwtvalidation.py) Secret for JWT Validation

## Roadmap

- Get IaC working (CloudFormation/CDK) to integrate API Gateway, Secrets Manager and RDS
- Create initial script to populate database with tables.
- Refactor code to remove JWT secret from layer
- Better support/documentation for image upload/download
- Use Foreign Keys in Database Tables (https://docs.aws.amazon.com/redshift/latest/dg/c_best-practices-defining-constraints.html)
