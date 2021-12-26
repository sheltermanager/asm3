/*global $, jQuery, alert, FileReader, DATE_FORMAT, IS_FORM */

// This file is included with all online forms and used to load
// widgets and implement validation behaviour, etc.

$(document).ready(function() {

    "use strict";

    const browser_is = {
        chrome: navigator.userAgent.match(/Chrome/i) != null,
        safari: navigator.userAgent.match(/Safari/i) != null,
        ios:    navigator.userAgent.match(/iPad|iPhone|iPod/i) != null,
        ie9:    navigator.userAgent.match(/MSIE 9/i) != null
    };

    const html5_required = !browser_is.ios && !browser_is.ie9;

    // Loads and scales an image into an image form field for upload
    const process_image = function(field) {

        let file = field[0].files[0];

        // Is this an image? If not, stop now
        if (!file.type.match('image.*')) { alert("File is not an image"); field.val(""); return; }

        let max_width = 640, max_height = 640;

        // Read the file to an image tag, then render it to
        // an HTML5 canvas to scale it
        let img = document.createElement("img");
        let filedata = null;
        let imreader = new FileReader();
        imreader.onload = function(e) { 
            filedata = e.target.result;
            img.src = filedata; 
        };
        img.onload = function() {
            // Calculate the new image dimensions based on our max
            let img_width = img.width, img_height = img.height;
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
            let canvas = document.createElement("canvas"),
                ctx = canvas.getContext("2d");
            canvas.height = img_height;
            canvas.width = img_width;
            ctx.drawImage(img, 0, 0, img_width, img_height);
            let datauri = canvas.toDataURL("image/jpeg");
            if (datauri.length > 384000) { alert("Scaled image is too large"); field.val(""); return; }
            $("input[name='" + field.attr("data-name") + "']").val( datauri );
        };
        imreader.readAsDataURL(file);
    };

    // Validates that all mandatory signature fields have something in them.
    // returns false for failure.
    const validate_signatures = function() {
        let rv = true;
        $(".asm-onlineform-signature").each(function() {
            try {
                let img = $(this).find("canvas").get(0).toDataURL("image/png");
                let fieldname = $(this).attr("data-name");
                $("input[name='" + fieldname + "']").val(img);
                if (!$(this).attr("data-required")) { return; }
                if (!$(this).parent().is(":visible")) { return; }
                if ($(this).signature("isEmpty")) {
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

    const validate_images = function() {
        let rv = true;
        $(".asm-onlineform-image").each(function() {
            if (!$(this).attr("data-required")) { return; }
            if (!$(this).parent().is(":visible")) { return; }
            let fieldname = $(this).attr("data-name"),
                v = $(this).val();
            if (!v) {
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
    const validate_lookupmulti = function() {
        let rv = true;
        $(".asm-onlineform-lookupmulti").each(function() {
            let fieldname = $(this).attr("data-name"),
                v = $(this).val();
            $("input[name='" + fieldname + "']").val(v);
            if (!$(this).attr("data-required")) { return; }
            if (!$(this).parent().is(":visible")) { return; }
            if (!v) {
                alert("You must choose at least one option");
                $(this).parent().find(".asmSelect").focus();
                rv = false;
                return false;
            }
        });
        return rv;
    };

    // Verifies that mandatory checkbox groups have something in them
    // as well as loading the values into the hidden field
    const validate_checkboxgroup = function() {
        let rv = true;
        $(".asm-onlineform-checkgroup").each(function() {
            let fieldname = $(this).attr("data-name"),
                v = [];
            $(this).find("input[type='checkbox']:checked").each(function() {
                v.push($(this).attr("data"));
            });
            $("input[name='" + fieldname + "']").val(v.join(","));
            if (!$(this).attr("data-required")) { return; }
            if (!$(this).parent().is(":visible")) { return; }
            if (v.length == 0) {
                alert("You must choose at least one option");
                $(this).find("input[type='checkbox']").focus();
                rv = false;
                return false;
            }
        });
        return rv;
    };

    const validate_dates = function() {
        let rv = true;
        $(".asm-onlineform-date").each(function() {
            // If this date has a value, make sure it conforms to DATE_FORMAT
            let v = $(this).val();
            if (v) {
                try {
                    $.datepicker.parseDate(DATE_FORMAT, v);
                }
                catch (e) {
                    alert("Date is not valid.");
                    $(this).focus();
                    rv = false;
                    return false;
                }
            }
        });
        return rv;
    };

    const validate_times = function() {
        let rv = true;
        $(".asm-onlineform-time").each(function() {
            // Times should be HH:MM
            let v = $(this).val();
            if (v) {
                if (!v.match(/^\d\d\:\d\d$/)) {
                    alert("Time is not valid.");
                    $(this).focus();
                    rv = false;
                    return false;
                }
            }
        });
        return rv;
    };

    const validate_email = function() {
        let rv = true;
        $(".asm-onlineform-email").each(function() {
            // Email should at least be x@y.z 
            let v = $(this).val();
            if (v) {
                if (!v.match(/\S+@\S+\.\S+/)) {
                    alert("Email address is not valid.");
                    $(this).focus();
                    rv = false;
                    return false;
                }
            }
        });
        return rv;
    };

    // Validate HTML5 required input fields 
    // (only does anything for browsers that don't support html5 required)
    const validate_required = function() {
        let rv = true;
        if (!html5_required) {
            $(".asm-onlineform-adoptableanimal, .asm-onlineform-date, .asm-onlineform-text, .asm-onlineform-lookup, .asm-onlineform-yesno, .asm-onlineform-notes").each(function() {
                if ($(this).attr("required")) {
                    let v = String($(this).val()).trim(); // Throw away whitespace before checking
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
    const parse_params = function() {
        let qstr = window.location.search.substring(1);
        let query = {}, i = 0;
        let a = (qstr[0] === '?' ? qstr.substr(1) : qstr).split('&');
        for (i = 0; i < a.length; i++) {
            let b = a[i].split('=');
            query[decodeURIComponent(b[0])] = decodeURIComponent(b[1] || '');
        }
        return query;
    };

    // Remove all hidden elements from the DOM. Useful to prevent visibleif 
    // hidden conditional fields from being posted to the backend.
    // Remove checkbox inputs from checkbox groups to prevent them posting 
    // individually (they have a name attribute for showif functionality)
    const remove_hidden = function() {
        $("tr:hidden").remove();
        $(".asm-onlineform-checkgroup input").remove();
    };

    // Find every visibleif rule and show/hide accordingly
    const show_visibleif = function() {
        $("tr").each(function() {
            let o = $(this), expr = o.attr("data-visibleif"), mode = "and";
            if (!expr) { return; } // no rule, do nothing
            if (expr.indexOf("|") != -1) { mode = "or"; }
            let clauses = (mode == "and" ? expr.split("&") : expr.split("|"));
            let andshow = true, orshow = false; // evaluate all clauses for or/and, only one can be used
            $.each(clauses, function(ci, cv) {
                // Separate condition into field, operator (=!<>), value
                let m = cv.trim().match(new RegExp("(.*)([=!<>])(.*)"));
                let field = "", cond = "=", value = "";
                if (m.length >= 2) { field = m[1]; }
                if (m.length >= 3) { cond = m[2]; }
                if (m.length >= 4) { value = m[3]; }
                // Find the field and apply the condition
                $("input, select").each(function() {
                    if ($(this).attr("name") && $(this).attr("name").indexOf(field + "_") == 0) {
                        let v = $(this).val();
                        // Checkboxes always return on for val(), if it's a checkbox, set on/off from checked
                        if ($(this).attr("type") && $(this).attr("type") == "checkbox") { v = $(this).is(":checked") ? "on" : "off"; }
                        // Radio buttons need reading differently to find the selected value
                        if ($(this).attr("type") && $(this).attr("type") == "radio") { v = $("[name='" + $(this).attr("name") + "']:checked").val(); }
                        if (cond == "=" && v != value) { andshow = false; }
                        else if (cond == "!" && v == value) { andshow = false; }
                        else if (cond == ">" && v <= value) { andshow = false; }
                        else if (cond == "<" && v >= value) { andshow = false; }
                        if (cond == "=" && v == value) { orshow = true; }
                        else if (cond == "!" && v != value) { orshow = true; }
                        else if (cond == ">" && v >= value) { orshow = true; }
                        else if (cond == "<" && v <= value) { orshow = true; }
                        return false; // stop iterating fields, we found it
                    }
                });
            });
            // Show or hide the field based on our final condition
            if (mode == "and") { o.toggle(andshow); }
            if (mode == "or") { o.toggle(orshow); }
            if (!o.is(":visible")) {
                // If we just hid a field that had the required attribute, 
                // remove it, otherwise the form won't submit
                o.find("input, select, textarea").prop("required", false);
            }
            else {
                // Restore the required attribute to the now visible field 
                // if the field had it previously. Deliberately avoid it on multiselects
                // so the select dropdown does not become required.
                if (o.find(".asm-onlineform-required").length > 0 && 
                    o.find(".asm-onlineform-lookupmulti").length == 0) {
                    o.find("input, select, textarea").prop("required", true);
                }
            }

        });
    };

    // Title case a string, james smith -> James Smith
    const title_case = function(s) {
        let o = [];
        for (let w of s.toLowerCase().split(" ")) {
            o.push(w.charAt(0).toUpperCase()+ w.slice(1));
        }
        return o.join(" ");
    };

    const upper_fields = [ "postcode", "zipcode", "areapostcode", "areazipcode", 
        "dropoffpostcode", "dropoffzipcode", "pickuppostcode", "pickupzipcode",
        "dispatchpostcode", "dispatchzipcode" ];
    const lower_fields = [ "emailaddress" ]; 
    const title_fields = [ "title", "initials", "forenames", "surname", 
        "firstname", "lastname", "address", "town", "county", "city", "state", "country", 
        "dispatchaddress", "dispatchtown", "dispatchcounty", "dispatchcity", "dispatchstate", 
        "pickupaddress", "pickuptown", "pickupcounty", "pickupcity", "pickupstate", "pickupcountry",
        "dropoffaddress", "dropofftown", "dropoffcounty", "dropoffcity", "dropoffstate", "dropoffcountry" ];
    const state_fields = [ "state", "dispatchstate", "pickupstate", "dropoffstate" ];

    // Called when a form field is changed. If we are dealing with some of our known
    // special fields, fix any bad character cases. 
    const fix_case_on_change = function() {
        if (typeof asm3_dont_fix_case !== 'undefined') { return; } // do nothing if global is declared
        var name = $(this).attr("name"), v = $(this).val();
        if (!name || !v) { return; }
        if (name.indexOf("_") != -1) { name = name.substring(0, name.indexOf("_")); }
        if (upper_fields.indexOf(name) != -1) {
            $(this).val( v.toUpperCase() );
        }
        if (lower_fields.indexOf(name) != -1) {
            $(this).val( v.toLowerCase() );
        }
        if (title_fields.indexOf(name) != -1) {
            $(this).val( title_case(v) );
        }
        if (state_fields.indexOf(name) != -1) {
            if (v.length <= 3) { $(this).val( v.toUpperCase() ); } // US or Aus state code
        }
    };

    // Load all date and time picker widgets
    $(".asm-onlineform-date").datepicker({ dateFormat: DATE_FORMAT, changeMonth: true, changeYear: true, yearRange: "-90:+3" });
    $(".asm-onlineform-time").timepicker();

    // Load all signature widgets and implement the clear button functionality
    try {
        $(".asm-onlineform-signature").each(function() {
            $(this).width( Math.min($(window).width()-20, 500 )); // max 500, min viewport width
            $(this).height(200);
        });
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

    // Watch text input fields for change so we can fix bad case/etc
    $("body").on("change", "input", fix_case_on_change);

    // Watch all fields for change and determine whether we need to hide or display rows
    $("body").on("change", "input, select", show_visibleif);
    show_visibleif(); // set initial state

    // Add additional behaviours to when the online form is submitted to validate 
    // components either not supported by HTML5 form validation, or for browsers
    // that do not support it.
    $("input[type='submit']").click(function(e) {
        const self = this;
        const enable = function() { $(self).prop("disabled", false); };
        $(this).prop("disabled", true); // Stop double submit by disabling the button
        if (!validate_signatures()) { enable(); return false; }
        if (!validate_lookupmulti()) { enable(); return false; }
        if (!validate_checkboxgroup()) { enable(); return false; }
        if (!validate_dates()) { enable(); return false; }
        if (!validate_times()) { enable(); return false; }
        if (!validate_email()) { enable(); return false; }
        if (!validate_required()) { enable(); return false; }
        if (!validate_images()) { enable(); return false; }
        if (html5_required && !$("form")[0].checkValidity()) { 
            enable(); // the default behaviour highlights the required fields so we need it to happen
        }
        else {
            e.preventDefault();
            remove_hidden(); // strip conditional fields that are not visible so they do not post
            if (typeof asm3_onlineform_submit !== 'undefined') { asm3_onlineform_submit(); }
            $("form").submit();
        }
    });

});

