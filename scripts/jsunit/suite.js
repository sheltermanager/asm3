var assert = require("assert");

// Some very crude unit tests for common javascript functions.
// This is an experiment more than anything and could be
// fleshed out with a proper unit test library at some point.

// Stubs
performance = {}

// jQuery Stubs, most of the functions we're testing should be 
// standalone with inputs/outputs.
function JQStub(s) { return s; }
jQuery = JQStub;
$ = JQStub;
$.fn = {};
$.ui = {};
$.each = function(o, f) { var i=0; for (i=0; i < o.length; i++) { f.call(i, o[i]); }  };
$.widget = function(name, obj, d) {};
function createDOMObject(attrs, classes, value) {
    return {
        "hasClass": function(s) { return classes.indexOf(s) != -1; },
        "attr": function(s) { return attrs[s]; },
        "val": function(s) {  return value; },
        "currency": function(s) { return value; }
    };
};
// ----------------------------------------------------------------


// -------- common.js ---------
require("../../src/static/js/common.js");
assert.ok( common.array_overlap( [ "test1", "test2" ], [ "test3", "test1" ]), "common.array_overlap missing overlap");
assert.ok( common.generate_uuid().length == 36, "common.generate_uuid invalid length");
assert.equal( common.url_param("key1=X&key2=Y&key3=Z", "key2"), "Y", "common.url_param bad value" )

// -------- common_widgets.js ---------
require("../../src/static/js/common_widgets.js");
objs = {
    "each": function(f) {
        f.call(createDOMObject({ "data": "key1", "data-post": "key1" }, "asm-currencybox", 1000));
        f.call(createDOMObject({ "data": "key2", "data-post": "key2" }, "asm-textbox", "test"));
    }
};
assert.ok($.fn.toPOST.call(objs).indexOf("key1=1000") != -1, "toPOST failure missing key");
assert.ok($.fn.toJSON.call(objs)["key1"] == 1000, "toJSON failure missing key");


