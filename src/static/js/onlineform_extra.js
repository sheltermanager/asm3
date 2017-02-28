/*jslint browser: true, forin: true, eqeq: true, plusplus: true, white: true, sloppy: true, vars: true, nomen: true, continue: true */
/*global $, jQuery, alert, DATE_FORMAT, IS_FORM */

// This file is included with all online forms and used to load
// widgets and implement validation behaviour, etc.

$(document).ready(function() {

    // If this script is not being loaded from the context of a form and
    // the IS_FORM variable is therefore not defined, do nothing
    // to prevent reference errors on globals like DATE_FORMAT
    if (typeof IS_FORM === "undefined") { return; }

    var is_safari = navigator.userAgent.indexOf("Safari") > -1 && navigator.userAgent.indexOf("Chrome") == -1;
    var is_ios = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
    // NB: None of this js will load for IE8 and older due to JQuery 2 being required
    var is_ie9 = navigator.appName.indexOf("Internet Explorer") !=-1 && navigator.appVersion.indexOf("MSIE 9")== -1;

    // Validates that all mandatory signature fields have something in them.
    // returns false for failure.
    var validate_signatures = function() {
        var rv = true;
        $(".asm-onlineform-signature").each(function() {
            try {
                var img = $(this).find("canvas").get(0).toDataURL("image/png");
                var fieldname = $(this).attr("data-name");
                $("input[name='" + fieldname + "']").val(img);
                if ($(this).signature("isEmpty") && $(this).parent().find(".asm-onlineform-required").length > 0) {
                    alert("Signature is required.");
                    rv = false;
                    return false;
                }
            }
            catch (exo) {
                if (window.console) { window.console.log(exo); }
            }
        });
        return rv;
    };

    // Validates that all mandatory multi-lookup fields have something in them.
    // returns false for failure.
    var validate_lookupmulti = function() {
        var rv = true;
        $(".asm-onlineform-lookupmulti").each(function() {
            var fieldname = $(this).attr("data-name"),
                v = $(this).val();
            $("input[name='" + fieldname + "']").val(v);
            if (!v && $(this).attr("data-required")) {
                alert("You must choose at least one option");
                rv = false;
                return false;
            }
        });
        return rv;
    };


    // Validate HTML5 required input fields 
    // (only does anything for iOS and IE9 where the required attribute is not supported)
    var validate_required = function() {
        var rv = true;
        if (is_ios || is_safari || is_ie9) {
            $(".asm-onlineform-date, .asm-onlineform-text, .asm-onlineform-lookup, .asm-onlineform-notes").each(function() {
                if ($(this).attr("required")) {
                    var v = $.trim(String($(this).val())); // Throw away whitespace before checking
                    if (!v) {
                        alert("This field cannot be blank");
                        rv = false;
                        $(this).focus();
                        return false;
                    }
                }
            });
        }
        return rv;
    };

    // Parses all of the query string parameters into the params dictionary
    var parse_params = function() {
        var qstr = window.location.search.substring(1);
        var query = {}, i = 0;
        var a = (qstr[0] === '?' ? qstr.substr(1) : qstr).split('&');
        for (i = 0; i < a.length; i++) {
            var b = a[i].split('=');
            query[decodeURIComponent(b[0])] = decodeURIComponent(b[1] || '');
        }
        return query;
    };

    // Load all date picker widgets
    $(".asm-onlineform-date").datepicker({ dateFormat: DATE_FORMAT });

    // Load all signature widgets and implement the clear button functionality
    try {
        $(".asm-onlineform-signature").signature({ guideline: true });
        $(".asm-onlineform-signature-clear").click(function() {
            var signame = $(this).attr("data-clear");
            $("div[data-name='" + signame + "']").signature("clear");
        });
    } catch (ex) {}

    // Load all multi-lookup widgets
    $(".asm-onlineform-lookupmulti").asmSelect({
        animate: true,
        sortable: true,
        removeLabel: '<strong>&times;</strong>',
        listClass: 'bsmList-custom',  
        listItemClass: 'bsmListItem-custom',
        listItemLabelClass: 'bsmListItemLabel-custom',
        removeClass: 'bsmListItemRemove-custom'
    });

    // Check for any querystring parameters given and see if we need to set
    // some of our fields to values passed 
    $.each(parse_params(), function(k, v) {
        $(".asm-onlineform-date, .asm-onlineform-text, .asm-onlineform-lookup, .asm-onlineform-notes, .asm-onlineform-check").each(function() {
            if ($(this).attr("name").indexOf(k) == 0) {
                $(this).val(v);
            }
        });
    });

    // Add additional behaviours to when the online form is submitted to validate 
    // components either not supported by HTML5 form validation, or for browsers
    // that do not support it.
    $("input[type='submit']").click(function() {
        if (!validate_signatures()) { return false; }
        if (!validate_lookupmulti()) { return false; }
        if (!validate_required()) { return false; }
    });

});

