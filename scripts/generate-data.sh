#!/bin/bash

cf target > /dev/null
if [ $? -eq 1 ]; then
  cf login -a "$CF_API_URL" \
    -u "$CF_API_USER" \
    -p "$CF_API_PASSWORD" \
    -o "$CF_ORG" \
    -s "$CF_SPACE"
fi

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

ALLOWED_REQS=$("$SCRIPT_DIR"/get-waf-requests-count.sh allowed)
BLOCKED_REQS=$("$SCRIPT_DIR"/get-waf-requests-count.sh blocked)
TOTAL_SANDBOXES=$("$SCRIPT_DIR"/get-sandboxes-count.sh)
TOTAL_USERS=$("$SCRIPT_DIR"/get-users-count.sh)
TOTAL_APPS=$("$SCRIPT_DIR"/get-apps-count.sh)
# Get domains from external-domain-broker and old cdn-broker and custom-domain-broker
TOTAL_DOMAIN_INSTANCES=$("$SCRIPT_DIR"/get-service-offering-instance-count.sh external-domain,cdn-route,custom-domain)
TOTAL_DATABASE_INSTANCES=$("$SCRIPT_DIR"/get-service-offering-instance-count.sh aws-rds)
TOTAL_ES_INSTANCES=$("$SCRIPT_DIR"/get-service-offering-instance-count.sh aws-elasticsearch)
TOTAL_REDIS_INSTANCES=$("$SCRIPT_DIR"/get-service-offering-instance-count.sh aws-elasticache-redis)
# Platform and Pages S3 service instances
TOTAL_S3_INSTANCES=$("$SCRIPT_DIR"/get-service-offering-instance-count.sh s3,federalist-s3)
agencies_with_agreement=$("$SCRIPT_DIR"/get-agency-customers-count.sh)

jq -n -r \
  --argjson allowed_reqs "$ALLOWED_REQS" \
  --argjson blocked_reqs "$BLOCKED_REQS" \
  --argjson total_sandbox_orgs "$TOTAL_SANDBOXES" \
  --argjson total_users "$TOTAL_USERS" \
  --argjson total_apps "$TOTAL_APPS" \
  --argjson total_domain_instances "$TOTAL_DOMAIN_INSTANCES" \
  --argjson total_database_instances "$TOTAL_DATABASE_INSTANCES" \
  --argjson total_es_instances "$TOTAL_ES_INSTANCES" \
  --argjson total_redis_instances "$TOTAL_REDIS_INSTANCES" \
  --argjson total_s3_instances "$TOTAL_S3_INSTANCES" \
  --argjson agencies_with_agreement "$agencies_with_agreement" \
  '$ARGS.named' > "$SCRIPT_DIR/../src/data.json"
