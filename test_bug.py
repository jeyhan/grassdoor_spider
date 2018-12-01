#!/usr/bin/python
# -*- coding: UTF-8 -*-

from bs4 import BeautifulSoup
import re
import requests

import sys

reload(sys)
sys.setdefaultencoding("utf-8")

import pymongo
import json
from bson import json_util

myclient = pymongo.MongoClient("mongodb://admin:password123@ds151393.mlab.com:51393/grassdoor_job_data")
mydb = myclient["grassdoor_job_data"]
print mydb

mycollection = mydb["jobs"]

i=0
for doc in mycollection.find():
    i+=1
    #print json.dumps(doc, sort_keys=True, indent=4, default=json_util.default)

print i
