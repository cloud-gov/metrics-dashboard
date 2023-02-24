#!/bin/bash

if [[ -z $1 ]]; then
    echo "must specify \"allowed\" or \"blocked\" as first argument"
    exit 1;
fi

case $1 in
    "allowed")
        METRIC_NAME="AllowedRequests"
        ;;
    "blocked")
        METRIC_NAME="BlockedRequests"
        ;;
    *)
        echo "unexpected value: $1"
        exit 1
        ;;
esac

DATE_FORMAT="+%Y-%m-%dT%H:00:00"

UNAME=$(uname)
if [[ "$UNAME" == "Linux" ]]; then
    START_DATE=$(date -u -d "1 day ago" "$DATE_FORMAT")
else
    START_DATE=$(date -u -v -1d "$DATE_FORMAT")
fi

END_DATE=$(date -u "$DATE_FORMAT")
PERIOD=3600 # aggregate request count by the hour (3600 seconds)

aws cloudwatch get-metric-statistics \
    --metric-name "$METRIC_NAME" \
    --namespace AWS/WAFV2 \
    --statistics Sum \
    --period=$PERIOD \
    --start-time "$START_DATE" \
    --end-time "$END_DATE" \
    --dimensions Name=Region,Value=us-gov-west-1 \
    Name=WebACL,Value=production-cf-uaa-waf-core \
    Name=Rule,Value=ALL \
    | jq '.Datapoints | map(.Sum) | add'