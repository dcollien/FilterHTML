var fs = require('fs');
var FilterHTML = require('../FilterHTML');
var test1 = require('./test1');

var html, html_out, result;

console.log(test1.SPEC);

html = fs.readFileSync('test1.html').toString();
html_out = fs.readFileSync('test1.out.html').toString();
result = FilterHTML.filter_html(html, test1.SPEC);

if (result.trim() !== html_out.trim()) {
    console.log("Test1 Failed");
} else {
	console.log("Test1 Passed");
}
