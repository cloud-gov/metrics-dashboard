#! /usr/bin/env python3

import os
import boto3
import json

def fail(message):
    print(message)
    exit(1)

if not os.environ.get('AWS_REGION')=='us-east-1':
    fail("Run this against US Gov cloud: us-east-1")

cdn_domains = []
cdn = boto3.client('cloudfront')
cdn_response = cdn.list_distributions()
for i in cdn_response['DistributionList']['Items']:
        aliases = i['Aliases']['Items']
        cdn_domains = cdn_domains + aliases

print(json.dumps(cdn_domains))