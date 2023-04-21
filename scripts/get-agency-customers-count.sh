#!/bin/bash

cf orgs \
  | tail -n +4 \
  | grep -v 'sandbox\|arsalan-haider\|mark-boyd\|3pao\|test-\|system\|david-anderson\|cf\|cloud-gov\|tech-talk' \
  | cut -d - -f 1 \
  | sort \
  | uniq -c \
  | wc -l \
  | jq -r
