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

hasMoreResults = True
while hasMoreResults:
    for i in cdn_response['DistributionList']['Items']:
        if 'Items' in i['Aliases']:
            aliases = i['Aliases']['Items']
            cdn_domains = cdn_domains + aliases
    hasMoreResults = cdn_response['DistributionList']['IsTruncated']
    if hasMoreResults:
        cdn_response = cdn.list_distributions(
            Marker=cdn_response['DistributionList']['NextMarker']
        )

print(json.dumps(cdn_domains))
