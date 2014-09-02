﻿CREATE EXTERNAL TABLE wiki(
page_title STRING,
real_page_title STRING,
page_id STRING,
user_id STRING,
counter STRING)

ROW FORMAT SERDE 'org.apache.hadoop.hive.contrib.serde2.RegexSerDe'
WITH SERDEPROPERTIES (
 "input.regex" = "(.*),WR_CL_DL,(.*),WR_CL_DL,([0-9]+),WR_CL_DL,([0-9]+),WR_CL_DL,([0-9]+)"
) 
stored as textfile
location '/user/cloudera/wiki/';
