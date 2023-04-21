#! /usr/bin/env python3

import os
import sys
import requests
import re
import datetime
import json
import getopt

# Get the command-line arguments, excluding the script name
alb_domain_file = cdn_domain_file = date = False
args = sys.argv[1:]
# Define the list of possible options and their arguments
opts, args = getopt.getopt(args, "ha:c:d:", ["help", "alb-domains", "cdn-domains", "date"])
for opt, arg in opts:
    if opt in ("-h", "--help"):
        help
    elif opt in ("-a", "--alb-domains"):
        alb_domain_file = str(arg)
    elif opt in ("-c", "--cdn-domains"):
        cdn_domain_file = str(arg)
    elif opt in ("-d", "--date"):
        date = str(arg)

def help():
   print("get-analytics.py [-h|--help] -a|--alb-domains=file -c|--cdn-domains=file -d|--date=date")
   print("Hint -- run all these:")
   print("    aws-vault exec com-prd-plat-auditor -- ./cdn-domains.py > cdn-domains.json")
   print("    aws-vault exec gov-prd-plat-auditor -- ./alb-domains.py > alb-domains.json")
   print("    ./get-analytics.py -a alb-domains.json -c cdn-domains.json -d YYYY-mm-dd")

   sys.exit(-1)

def fail(message):
    print(message)
    exit(1)

def usa_total(after,before):
    route = "reports/second-level-domain/data"
    payload = { 'api_key': api_key, 'after': after, 'before': before }
    api_url = api_root + "/" + route
    response = requests.get(api_url, params=payload)
    return sum(item['visits'] for item in response.json())

def domains_total(domains,after, before):
    N = 0
    for d in domains:
        if not d:
            continue
        else:
            route = f'domain/{d}/reports/domain/data'
            payload = { 'api_key': api_key, 'after': after, 'before': before }
            api_url = api_root + "/" + route
            response = requests.get(api_url, params=payload)
            for item in response.json():
                #if item['domain']:
                if item['report_agency']:
                    # print(N)
                    N = N + item['visits']
    return N

# MAIN
if not (alb_domain_file and cdn_domain_file and date):
    help()

api_key = os.environ.get('USA_API_KEY')
if not api_key:
    fail("Need to set env var USA_API_KEY")

with open(cdn_domain_file, 'r') as f:
  cdn_domains = json.load(f)
with open(alb_domain_file, 'r') as f:
  alb_domains = json.load(f)

after = datetime.datetime.strptime(date, '%Y-%m-%d')
before = after + datetime.timedelta(days=1)
api_root="https://api.gsa.gov/analytics/dap/v1.1"

print(f'-- Report for {date} --') 

usa_visits = usa_total(after,before)
print(f'USA total: {usa_visits}')

alb_visits = domains_total(alb_domains, after, before)
print("ALB visits (visits | percent): ", alb_visits, " | ", '{:.1%}'.format(alb_visits/usa_visits))

cdn_visits = domains_total(cdn_domains, after, before)
print("CDN visits (visits | percent): ", cdn_visits, " | ", '{:.1%}'.format(cdn_visits/usa_visits))

cloud_visits = alb_visits + cdn_visits
print("cloud.gov visits (visits | percent): ", cloud_visits, " | ", '{:.1%}'.format(cloud_visits/usa_visits))

