#!/bin/bash

npm install

# copy data generated in previous step into place
cp ../data/data.json src

npm run generate-html