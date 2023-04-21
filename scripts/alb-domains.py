#! /usr/bin/env python3

import os
import re
import boto3
import json
import datetime
import pytz
from cryptography import x509

utc=pytz.UTC

def fail(message):
    print(message)
    print('Usage: alb-domains')
    exit(1)

def show_cert_cn(cert, upload_cutoff):
    now  = datetime.datetime.now()
    now = utc.localize(now)
    if cert['UploadDate'] > upload_cutoff:
        full_cert = iam.get_server_certificate(ServerCertificateName=cert['ServerCertificateName'])
        cert_body=full_cert['ServerCertificate']['CertificateBody']
        x509_cert = x509.load_pem_x509_certificate(cert_body.encode('utf-8'))
        if x509_cert.not_valid_after > datetime.datetime.now():
            domain_name = re.match(rf'<Name\(CN=(.*)\)\>', str(x509_cert.subject))
            if domain_name:
                return domain_name.group(1)

if not os.environ.get('AWS_REGION')=='us-gov-west-1':
  fail("Run this against US Gov cloud: us-gov-west-1")

# Create IAM client
iam = boto3.client('iam')
paginator = iam.get_paginator('list_server_certificates')

# Iterate over all the production ALB paths, get their certs, and pull out the 
# currently valid domains
alb_domains = []
ninety_days_ago = datetime.datetime.now() - datetime.timedelta(days=91)
ninety_days_ago = utc.localize(ninety_days_ago)
for path in ['/domains/production', '/lets-encrypt/production', '/alb/external-domains-production']:
    page_iterator = paginator.paginate( PathPrefix = path )
    for page in page_iterator:
        for cert in (page['ServerCertificateMetadataList']):
            cn = show_cert_cn(cert, ninety_days_ago)
            if cn in alb_domains:
                continue
            elif cn is None:
                continue
            elif re.match(rf'\*', cn):
                continue
            else:
                alb_domains.append(cn)

print (json.dumps(alb_domains))