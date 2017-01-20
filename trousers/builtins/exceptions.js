#!/usr/bin/env phantomjs

const page = require('webpage').create();
const system = require('system');
const uri = system.args[1];
const errors = [];

console.log("Exceptions for: " + uri);

page.onError = function(msg, trace) {

    var msgStack = ['ERROR: ' + msg];
    
    if (trace && trace.length) {
        msgStack.push('TRACE:');
        trace.forEach(function(t) {
            msgStack.push(' -> ' + (t.file || t.sourceURL) + ': ' + t.line + (t.function ? ' (in function ' + t.function +')' : ''));
        });
    }

    errors.push(msgStack);
    
};

page.open(uri, function (status) {

    const printResults = function() {

        if(errors.length === 0){
            console.log("No exceptions thrown. Good job!")
        }
        
        errors.forEach(function(stack){
            console.log("EXCEPTION");
            console.log("----------------");
            console.log(stack.join("\n"));
            console.log("\n");
        });
    };
    
    if (status !== 'success') {
        console.log('Failed to load uri');
        phantom.exit();
    } else {
        window.setTimeout(function () { printResults(); phantom.exit(); }, 9000);
    }

});
