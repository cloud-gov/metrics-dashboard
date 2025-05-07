#! /usr/bin/env python3

import os
import sys
import boto3
import json

def fail(message):
    print(message)
    exit(1)

if not os.environ.get('AWS_REGION')=='us-east-1':
    fail("Run this against US Gov cloud: us-east-1")

cdn_domains = []
cdn = boto3.client('cloudfront')
paginator = cdn.get_paginator('list_distributions')
page_iterator = paginator.paginate()
for page in page_iterator:
     if "DistributionList" in page:
        for i in page['DistributionList']['Items']:
            if i["Aliases"]["Quantity"] > 0: 
                aliases = i['Aliases']['Items']
                cdn_domains = cdn_domains + aliases

print(json.dumps(cdn_domains))
