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
opts, args = getopt.getopt(args, "ha:c:s:n:", ["help", 
                            "alb-domains", "cdn-domains", 
                            "starting-date", "number-of-days"])
for opt, arg in opts:
    if opt in ("-h", "--help"):
        help
    elif opt in ("-a", "--alb-domains"):
        alb_domain_file = str(arg)
    elif opt in ("-c", "--cdn-domains"):
        cdn_domain_file = str(arg)
    elif opt in ("-s", "--starting-date"):
        date = str(arg)
    elif opt in ("-n", "--number-of-days"):
        n_days = int(arg)

print(f'alb: {alb_domain_file}')
print(f'cdn: {cdn_domain_file}')
print(f'date: {date}')
print(f'number of days {n_days}')

def help():
   print("get-analytics.py [-h|--help] -a|--alb-domains=file ",
      "-c|--cdn-domains=file -s|--starting-date=date -n|--number-of-days")
   print("Hint -- run all these:")
   print("    aws-vault exec com-prd-plat-auditor -- ./cdn-domains.py > cdn-domains.json")
   print("    aws-vault exec gov-prd-plat-auditor -- ./alb-domains.py > alb-domains.json")
   print("    ./get-analytics.py -a alb-domains.json -c cdn-domains.json -s YYYY-mm-dd -n 90")

   sys.exit(-1)

def fail(message):
    print(message)
    exit(1)

def usa_total(after,before):
    visits_by_date = {}
    route = "reports/second-level-domain/data"
    payload = { 'api_key': api_key, 'after': after, 'before': before }
    api_url = api_root + "/" + route
    response = requests.get(api_url, params=payload)
    for item in response.json():
#        print(item)
        current_value = visits_by_date.get(item['date'])
        if current_value:
            visits_by_date[item['date']] += item['visits'] 
        else:
            visits_by_date[item['date']] = item['visits'] 
#        print(f'date: {item["date"]}, total_visits: {visits_by_date[item["date"]]}')
    print("USA visits counted", file=sys.stderr)
    return visits_by_date

def domains_total(domains,after, before):
    status_report_interval = 20
    visits_by_date = {}
    nd = 0
    for d in domains:
        nd += 1
        print(f'... {nd} domains processed...') if nd % 20
        else:
            route = f'domain/{d}/reports/domain/data'
            payload = { 'api_key': api_key, 'after': after, 'before': before }
            api_url = api_root + "/" + route
#            print(f'api_url: {api_url}')
            response = requests.get(api_url, params=payload)
            for item in response.json():
                if item['report_agency']:
                    current_value = visits_by_date.get(item['date'])
                    if current_value:
                        visits_by_date[item['date']] += item['visits'] 
                    else:
                        visits_by_date[item['date']] = item['visits'] 
#                    print(f'date: {item["date"]}, total_visits: {visits_by_date[item["date"]]}')

    return visits_by_date 

# MAIN
if not (alb_domain_file and cdn_domain_file and date and n_days):
    help()

api_key = os.environ.get('USA_API_KEY')
if not api_key:
    fail("Need to set env var USA_API_KEY")

with open(cdn_domain_file, 'r') as f:
  cdn_domains = json.load(f)
with open(alb_domain_file, 'r') as f:
  alb_domains = json.load(f)

after = datetime.datetime.strptime(date, '%Y-%m-%d')
before = after + datetime.timedelta(days=n_days)
api_root="https://api.gsa.gov/analytics/dap/v1.1"

usa_visits = usa_total(after,before)

#alb_visits = domains_total(alb_domains, after, before)
#print("ALB visits (visits | percent): ", alb_visits, " | ", '{:.1%}'.format(alb_visits/usa_visits))

cdn_visits = domains_total(cdn_domains, after, before)
print(f'-- Report starting from {date} --') 
for date_key in cdn_visits.keys():
   print("CDN visits for ", date_key, " -- (visits | percent): ", cdn_visits[date_key], " | ", '{:.1%}'.format(cdn_visits[date_key]/usa_visits[date_key]))


#cloud_visits = alb_visits + cdn_visits
#print("cloud.gov visits (visits | percent): ", cloud_visits, " | ", '{:.1%}'.format(cloud_visits/usa_visits))

