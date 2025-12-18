#!/bin/bash

if [[ -z $1 ]]; then
    echo "must specify \"allowed\" or \"blocked\" as first argument"
    exit 1;
fi

NAMESPACE="$1"
METRIC_NAME="$2"
DIMENSIONS="$3"
START_DATE="$5"
END_DATE="$5"
PERIOD="$6"

DATE_FORMAT="+%Y-%m-%dT%H:00:00"

if [[ -z $START_DATE ]]; then
    UNAME=$(uname)
    if [[ "$UNAME" == "Linux" ]]; then
        START_DATE=$(date -u -d "1 day ago" "$DATE_FORMAT")
    else
        START_DATE=$(date -u -v -1d "$DATE_FORMAT")
    fi
fi

if [[ -z $END_DATE ]]; then
    END_DATE=$(date -u "$DATE_FORMAT")
fi

if [[ -z $PERIOD ]]; then
    PERIOD=3600 # aggregate request count by the hour (3600 seconds)
fi

args=(
    --metric-name "$METRIC_NAME"
    --namespace "$NAMESPACE"
    --statistics Sum
    --period=$PERIOD
    --start-time "$START_DATE"
    --end-time "$END_DATE"
)

if [[ -n $DIMENSIONS ]]; then
    args+=(--dimensions $DIMENSIONS)
fi

aws cloudwatch get-metric-statistics "${args[@]}" | jq '.Datapoints | map(.Sum) | add'
