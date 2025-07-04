/*global $, jQuery, alert, FileReader, DATE_FORMAT, IS_FORM */

// This file is included with all online forms and used to load
// widgets and implement validation behaviour, etc.

const PHONE_RULES = [
    { locale: "en", prefix: "", length: 10, elements: 3, extract: /^(\d{3})(\d{3})(\d{4})$/, display: "({1}) {2}-{3}", placeholder: "(NNN) NNN-NNNN" },
    { locale: "en", prefix: "1", length: 11, elements: 3, extract: /(?<=1)(\d{3})(\d{3})(\d{4})/, display: "({1}) {2}-{3}", placeholder: "(NNN) NNN-NNNN" },
    { locale: "en_AU", prefix: "04", length: 10, elements: 3, extract: /^(\d{4})(\d{3})(\d{3})$/, display: "{1} {2} {3}", placeholder: "NNNN NNN NNN" },
    { locale: "en_AU", prefix: "", length: 10, elements: 3, extract: /^(\d{2})(\d{4})(\d{4})$/, display: "{1} {2} {3}", placeholder: "NN NNNN NNNN" },
    { locale: "en_AU", prefix: "61", length: 11, elements: 3, extract: /(?<=61)(\d{1})(\d{4})(\d{4})/, display: "0{1} {2} {3}", placeholder: "NN NNNN NNNN" },
    { locale: "en_CA", prefix: "", length: 10, elements: 3, extract: /^(\d{3})(\d{3})(\d{4})$/, display: "({1}) {2}-{3}", placeholder: "(NNN) NNN-NNNN" },
    { locale: "en_CA", prefix: "1", length: 11, elements: 3, extract: /(?<=1)(\d{3})(\d{3})(\d{4})/, display: "({1}) {2}-{3}", placeholder: "(NNN) NNN-NNNN" },
    { locale: "fr_CA", prefix: "", length: 10, elements: 3, extract: /^(\d{3})(\d{3})(\d{4})$/, display: "({1}) {2}-{3}", placeholder: "(NNN) NNN-NNNN" },
    { locale: "fr_CA", prefix: "1", length: 11, elements: 3, extract: /(?<=1)(\d{3})(\d{3})(\d{4})/, display: "({1}) {2}-{3}", placeholder: "(NNN) NNN-NNNN" },
    { locale: "en_GB", prefix: "011", length: 11, elements: 2, extract: /^(\d{4})(\d{7})$/, display: "{1} {2}", placeholder: "NNNNN NNNNNN" },
    { locale: "en_GB", prefix: "44", length: 12 , elements: 2, extract: /(?<=44)(\d{4})(\d{6})/, display: "0{1} {2}", placeholder: "NNNNN NNNNNN" },
    { locale: "en_GB", prefix: "", length: 11, elements: 2, extract: /^(\d{5})(\d{6})$/, display: "{1} {2}", placeholder: "NNNNN NNNNNN" },
    { locale: "en_IE", prefix: "01", length: 9, elements: 3, extract: /^(\d{2})(\d{3})(\d{4})$/, display: "{1} {2} {3}", placeholder: "NN NNN NNNN" },
    { locale: "en_IE", prefix: "08", length: 10, elements: 3, extract: /^(\d{3})(\d{3})(\d{4})$/, display: "{1} {2} {3}", placeholder: "NNN NNN NNNN" },
    { locale: "en_IE", prefix: "", length: 10, elements: 3, extract: /^(\d{3})(\d{3})(\d{4})$/, display: "{1} {2} {3}", placeholder: "NNN NNN NNNN" },
    { locale: "en_IE", prefix: "", length: 9, elements: 3, extract: /^(\d{3})(\d{3})(\d{3})$/, display: "{1} {2} {3}", placeholder: "NNN NNN NNN" },
    { locale: "en_IE", prefix: "", length: 8, elements: 2, extract: /^(\d{3})(\d{5})$/, display: "{1} {2}", placeholder: "NNN NNNNN" },
    { locale: "en_IE", prefix: "", length: 7, elements: 2, extract: /^(\d{3})(\d{4})$/, display: "{1} {2}", placeholder: "NNN NNNN" },
    { locale: "en_IE", prefix: "+353", length: 13, elements: 3,extract: /(?<=353)(\d{3})(\d{3})(\d{4})/, display: "0{1} {2} {3}", placeholder: "NNN NNN NNNN" },
    { locale: "en_IE", prefix: "+353", length: 12, elements: 3,extract: /(?<=353)(\d{3})(\d{3})(\d{3})/, display: "0{1} {2} {3}", placeholder: "NNN NNN NNN" },
    { locale: "en_IE", prefix: "+353", length: 11, elements: 2,extract: /(?<=353)(\d{3})(\d{5})/, display: "0{1} {2}", placeholder: "NNN NNNNN" },
    { locale: "en_IE", prefix: "+353", length: 10, elements: 2,extract: /(?<=353)(\d{3})(\d{4})/, display: "0{1} {2}", placeholder: "NNN NNNN" },
    { locale: "es", prefix: "", length: 9, elements: 3,extract: /^(\d{3})(\d{3})(\d{3})$/, display: "{1} {2} {3}", placeholder: "NNN NNN NNN" },
    { locale: "es", prefix: "34", length: 11, elements: 3,extract: /(?<=34)(\d{3})(\d{3})(\d{3})/, display: "{1} {2} {3}", placeholder: "NNN NNN NNN" },
    { locale: "en_ES", prefix: "", length: 9, elements: 3,extract: /^(\d{3})(\d{3})(\d{3})$/, display: "{1} {2} {3}", placeholder: "NNN NNN NNN" },
    { locale: "en_ES", prefix: "34", length: 11, elements: 3,extract: /(?<=34)(\d{3})(\d{3})(\d{3})/, display: "{1} {2} {3}", placeholder: "NNN NNN NNN" }
];

$(document).ready(function() {

    "use strict";

    const browser_is = {
        chrome: navigator.userAgent.match(/Chrome/i) != null,
        safari: navigator.userAgent.match(/Safari/i) != null,
        ios:    navigator.userAgent.match(/iPad|iPhone|iPod/i) != null,
        ie9:    navigator.userAgent.match(/MSIE 9/i) != null,
        mobileff: navigator.userAgent.match(/Firefox/i) != null && navigator.userAgent.match(/Mobile/i) != null
    };

    const html5_required = !browser_is.ie9 && !browser_is.mobileff;

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
                    let date = $.datepicker.parseDate(DATE_FORMAT, v);
                    let today = new Date();
                    if ( $(this).hasClass("nopast") && date < today ) {
                        alert("Date cannot be in the past.");
                        $(this).focus();
                        rv = false;
                        return false;
                    }
                    if ( $(this).hasClass("nofuture") && date > today ) {
                        alert("Date cannot be in the future.");
                        $(this).focus();
                        rv = false;
                        return false;
                    }
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
            let vid = $(this).attr("ID");
            if ( !vid.includes("verify") ) {
                let vnode = $("#" + vid + "verify");
                if (vnode.length > 0) {
                    let v2 = vnode.val();
                    if (v != v2) {
                        alert("Email addresses do not match.");
                        $(this).focus();
                        rv = false;
                        return false;
                    }
                }
            }
        });
        return rv;
    };

    const validate_number = function() {
        let rv = true;
        $(".asm-onlineform-number").each(function() {
            let v = $(this).val();
            if (v) {
                if (isNaN(v) || isNaN(parseFloat(v))) {
                    alert("Number is not valid.");
                    $(this).focus();
                    rv = false;
                    return false;
                }
            }
        });
        return rv;
    };

    const validate_phone = function() {
        let rv = true;
        $(".asm-onlineform-phone").each(function() {
            let v = $(this).val();
            if (v) {
                if (v.replace(/\D/g, '').length < 6) {
                    alert("Telephone number is not valid.");
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
            $(".asm-onlineform-adoptableanimal, .asm-onlineform-date, .asm-onlineform-email, .asm-onlineform-text, .asm-onlineform-lookup, .asm-onlineform-yesno, .asm-onlineform-notes").each(function() {
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
                // Separate condition into field, operator (=!<>*^), value
                let m = cv.trim().match(new RegExp("(.*)([=!<>\*\^])(.*)"));
                let field = "", cond = "=", value = "";
                if (!m) { return; } // The condition does not match our regex and is invalid, skip
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
                        else if (cond == "*" && String(v).indexOf(value) == -1) { andshow = false; }
                        else if (cond == "^" && String(v).indexOf(value) != -1) { andshow = false; }
                        if (cond == "=" && v == value) { orshow = true; }
                        else if (cond == "!" && v != value) { orshow = true; }
                        else if (cond == ">" && v >= value) { orshow = true; }
                        else if (cond == "<" && v <= value) { orshow = true; }
                        else if (cond == "*" && String(v).indexOf(value) != -1) { orshow = true; }
                        else if (cond == "^" && String(v).indexOf(value) == -1) { orshow = true; }
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
                // if the field had it previously. 
                // Deliberately avoid it on multiselect elements so the inner fields do not become required.
                if (o.find(".asm-onlineform-required").length > 0 && 
                    o.find(".asm-onlineform-lookupmulti, .asm-onlineform-checkgroup, .asm-onlineform-radiogroup").length == 0) {
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

    // Updates the thumbnail image when changing an adoptable animal dropdown
    const update_thumbnail = function(n) {
        let aid = n.find("option:selected").attr("data-id");
        let im = n.parent().find("img");
        if (!aid) { im.hide(); return; }
        let url = $("form").attr("action") + "?method=animal_image&account=" + $("input[name='account']").val() + "&animalid=" + aid;
        im.prop("src", url);
        im.show();
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
    $(".asm-onlineform-date").each(function() {
        let nopast = $(this).hasClass("nopast");
        let nofuture = $(this).hasClass("nofuture");
        if (nopast || nofuture) {
            $(this).datepicker({ 
                dateFormat: DATE_FORMAT,
                changeMonth: true, 
                changeYear: true,
                firstDay: $(this).attr("data-firstday"),
                yearRange: "-90:+3",
                beforeShowDay: function(a) {
                    let rv = true;
                    if (nopast && a < new Date()) { rv = false; }
                    if (nofuture && a > new Date()) { rv = false; }
                    return [rv, ""];
                }
            });
        } else {
            $(this).datepicker({ 
                dateFormat: DATE_FORMAT,
                changeMonth: true, 
                changeYear: true,
                yearRange: "-90:+3",
                firstDay: $(this).prop("data-firstday")
            });
        }
    });

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

    // Insert phone number input placeholders
    $.each($(".asm-onlineform-phone"), function(i, phoneinput) {
        let inputlocale = $(this).attr("data-locale");
        $.each(PHONE_RULES, function(i, rule) {
            if (rule.locale == inputlocale) {
                phoneinput.placeholder = rule.placeholder;
                return false;
            }
        });
    });

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

    // Show a thumbnail for adoptable animals
    $(".asm-onlineform-adoptableanimal").each(function() {
       $(this).change(function(e) {
            update_thumbnail($(this));
       });
    });

    // Check for any querystring parameters given and see if we need to set
    // some of our fields to values passed 
    $.each(parse_params(), function(k, v) {
        $(".asm-onlineform-date, .asm-onlineform-time, .asm-onlineform-text, .asm-onlineform-lookup, .asm-onlineform-notes, " +
            ".asm-onlineform-check, .asm-onlineform-radio, .asm-onlineform-breed, .asm-onlineform-colour, " +
            ".asm-onlineform-species").each(function() {
            if ($(this).attr("name").indexOf(k) == 0) {
                $(this).val(v);
            }
        });
        // Use a pattern match for animal dropdowns instead of an exact match
        // so that the name or the sheltercode can be passed
        $(".asm-onlineform-adoptableanimal, .asm-onlineform-shelteranimal").each(function() {
            if ($(this).attr("name").indexOf(k) == 0) {
                var dd = $(this);
                $(this).find("option").each(function() {
                    if ($(this).prop("value").indexOf(v) >= 0) {
                        $(this).prop("selected", true);
                        update_thumbnail(dd);
                        return false;
                    }
                });
                return false;
            }
        });
    });

    // Watch text input fields for change so we can fix bad case/etc
    $("body").on("change", "input", fix_case_on_change);

    // Watch phone input fields for change so they can be formatted according to locale
    $(".asm-onlineform-phone").on("blur", function() {
        if ( $(this).attr("data-locale") ) {
            let locale = $(this).attr("data-locale");
            let t = $(this);
            let num = String(t.val()).replace(/\D/g, ''); // Throw away all but the numbers
            $.each(PHONE_RULES, function(i, rules) {
                if (rules.locale != locale) { return; }
                if (rules.prefix && num.indexOf(rules.prefix) != 0) { return; }
                if (num.length != rules.length) { return; }
                let s = rules.display, m = num.match(rules.extract), x=1;
                for (x=1; x <= rules.elements; x++) {
                    s = s.replace("{" + x + "}", m[x]);
                }
                t.val(s);
                return false;
            });
        }
    });

    // Multi-lookup fields should copy their values into the corresponding hidden field when changed
    // so that showif pattern matching on them still works
    $("body").on("change", ".asm-onlineform-lookupmulti", function() {
        $("input[name='" + $(this).attr("data-name") + "']").val($(this).val());
    });

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
        if (!validate_number()) { enable(); return false; }
        if (!validate_required()) { enable(); return false; }
        if (!validate_images()) { enable(); return false; }
        if (!validate_phone()) { enable(); return false; }
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

