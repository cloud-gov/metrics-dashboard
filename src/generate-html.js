const fs = require('fs');
const Mustache = require('mustache');

const staticData = require('./static.json');
const data = require('./data.json');
const view = Object.assign({}, staticData, data)

const template = fs.readFileSync( __dirname + '/index.html.mustache', 'utf-8');
const output = Mustache.render(template, view);

fs.writeFileSync( __dirname + '/index.html', output);
