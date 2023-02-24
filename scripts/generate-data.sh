#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

ALLOWED_REQS=$("$SCRIPT_DIR"/get-waf-requests-count.sh allowed)
BLOCKED_REQS=$("$SCRIPT_DIR"/get-waf-requests-count.sh blocked)
TOTAL_SANDBOXES=$("$SCRIPT_DIR"/get-sandboxes-count.sh)
TOTAL_USERS=$("$SCRIPT_DIR"/get-users-count.sh)
TOTAL_APPS=$("$SCRIPT_DIR"/get-apps-count.sh)
TOTAL_DOMAIN_INSTANCES=$("$SCRIPT_DIR"/get-service-offering-instance-count.sh external-domain,cdn-route,custom-domain)

jq -nr \
  --argjson allowed_reqs "$ALLOWED_REQS" \
  --argjson blocked_reqs "$BLOCKED_REQS" \
  --argjson total_sandbox_orgs "$TOTAL_SANDBOXES" \
  --argjson total_users "$TOTAL_USERS" \
  --argjson total_apps "$TOTAL_APPS" \
  --argjson total_domain_instances "$TOTAL_DOMAIN_INSTANCES" \
  '$ARGS.named' > "$SCRIPT_DIR/../src/data2.json"