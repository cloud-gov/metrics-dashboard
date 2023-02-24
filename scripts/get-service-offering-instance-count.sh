#!/bin/bash

function usage {
  echo -e "
  Usage
  ./$( basename "$0" ) service-offering-names
  
  Examples:
  ./$( basename "$0" ) external-domain,cdn-route

  Get the total count of service instances for the given service offerings.
  "
}

if [[ -z $1 ]]; then
    echo "service offering name(s) are required as first argument"
    usage
    exit 1;
fi

OFFERINGS=$1
PLAN_NAMES=$(cf curl "/v3/service_plans?service_offering_names=$OFFERINGS" | jq -r '.resources | map(.name) | join(",")')
cf curl "/v3/service_instances?service_plan_names=${PLAN_NAMES}" | jq -r '.pagination.total_results'
