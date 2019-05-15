/*jslint browser: true, forin: true, eqeq: true, plusplus: true, white: true, sloppy: true, vars: true, nomen: true, continue: true */
/*global $, jQuery, alert, FileReader, DATE_FORMAT, IS_FORM */

// This file is included with all online forms and used to load
// widgets and implement validation behaviour, etc.

$(document).ready(function() {

    var is_safari = navigator.userAgent.indexOf("Safari") > -1 && navigator.userAgent.indexOf("Chrome") == -1;
    var is_ios = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
    // NB: None of this js will load for IE8 and older due to JQuery 2 being required
    var is_ie9 = navigator.appName.indexOf("Internet Explorer") !=-1 && navigator.appVersion.indexOf("MSIE 9")== -1;

    // Loads and scales an image into an image form field for upload
    var process_image = function(field) {

        var file = field[0].files[0];

        // Is this an image? If not, stop now
        if (!file.type.match('image.*')) { alert("File is not an image"); field.val(""); return; }

        var max_width = 300, max_height = 300;

        // Read the file to an image tag, then render it to
        // an HTML5 canvas to scale it
        var img = document.createElement("img");
        var filedata = null;
        var imreader = new FileReader();
        imreader.onload = function(e) { 
            filedata = e.target.result;
            img.src = filedata; 
        };
        img.onload = function() {
            // Calculate the new image dimensions based on our max
            var img_width = img.width, img_height = img.height;
            if (img_width > img_height) {
                if (img_width > max_width) {
                    img_height *= max_width / img_width;
                    img_width = max_width;
                }
            }
            else {
                if (img_height > max_height) {
                    img_width *= max_height / img_height;
                    img_height = max_height;
                }
            }
            // Scale the image
            var canvas = document.createElement("canvas"),
                ctx = canvas.getContext("2d");
            canvas.height = img_height;
            canvas.width = img_width;
            ctx.drawImage(img, 0, 0, img_width, img_height);
            var datauri = canvas.toDataURL("image/jpeg");
            if (datauri.length > 75000) { alert("Scaled image is too large"); return; }
            $("input[name='" + field.attr("data-name") + "']").val( datauri );
        };
        imreader.readAsDataURL(file);
    };

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

    var validate_images = function() {
        var rv = true;
        $(".asm-onlineform-image").each(function() {
            var fieldname = $(this).attr("data-name"),
                v = $(this).val();
            if (!v && $(this).parent().find(".asm-onlineform-required").length > 0) {
                alert("You must attach an image");
                $(this).focus();
                rv = false;
                return false;
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
                $(this).parent().find(".asmSelect").focus();
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

    // Load all date and time picker widgets
    $(".asm-onlineform-date").datepicker({ dateFormat: DATE_FORMAT });
    $(".asm-onlineform-time").timepicker();

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

    // Attach event handlers to load images when they are selected
    $(".asm-onlineform-image").each(function() {
        $(this).change(function(e) {
            process_image($(this));
        });
    });

    // Check for any querystring parameters given and see if we need to set
    // some of our fields to values passed 
    $.each(parse_params(), function(k, v) {
        $(".asm-onlineform-date, .asm-onlineform-time, .asm-onlineform-text, .asm-onlineform-lookup, .asm-onlineform-notes, " +
            ".asm-onlineform-check, .asm-onlineform-radio, .asm-onlineform-adoptableanimal, .asm-onlineform-shelteranimal, " +
            ".asm-onlineform-breed, .asm-onlineform-colour, .asm-onlineform-species").each(function() {
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
        if (!validate_images()) { return false; }
    });

});

