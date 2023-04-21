#!/bin/bash

npm install

# copy data generated in previous step into place
cp ../data/data.json src

# compile CSS
npx gulp compile

# generate HTML
npm run generate-html
