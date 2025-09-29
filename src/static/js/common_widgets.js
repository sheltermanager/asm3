/*global $, console, jQuery, CodeMirror, Mousetrap, tinymce */
/*global asm, common, config, dlgfx, edit_header, format, html, header, log, schema, tableform, validate, _, escape, unescape */
/*global MASK_VALUE: true */

"use strict";

// String shown in asm-mask fields instead of the value
const MASK_VALUE = "****************";

/**
 * asm_widget: Lightweight stateless ASM widget
 * 
 * This uses the JQuery fn mechanism instead of the
 * JQuery UI widget factory. Using widget factory turned out to have terrible
 * performance once there are stateful widget wrappers around every input field. 
 * 
 * This allows you to write code that mostly looks and works like $.widget, but 
 * is instead stateless. It also has no dependency on jquery.ui.widget.js or
 * JQuery UI in general and can be used to wrap Bootstrap or any other HTML UI toolkit.
 * 
 * To store and load arbitrary state data, use jQuery's data() method on the DOM element.
 * 
 * The function dispatcher sets "this" to the widget class/object (nb: this is a singleton) 
 * and passes the DOM element that the widget is wrapping as the first argument t.
 * The remaining arguments are passed in order after that (max of 2)
 * 
 * Eg: 
 * $.fn.textbox = asm_widget({ 
 *     _create: function(t) {
 *          // called with $("#id").textbox() or textbox("_create")
 *          t.data("arbitrary", "some value");
 *     },
 *     value: function(t, newval) {
 *         if (newval === undefined) { return t.val(); }
 *         t.val(newval);
 *     }
 * });
 */
const asm_widget = function(obj) {
    return function(method, arg1, arg2) {
        let rv = null;
        this.each(function() {
            // Dispatch the constructor (no args)
            if (method === undefined) {
                rv = obj._create.call(obj, $(this), obj.options);
            }
            // Dispatch the constructor (create explicitly called)
            else if (method === "create") {
                rv = obj._create.call(obj, $(this), obj.options);
            }
            // Dispatch the constructor (method is an object containing options, 
            // merge these options with obj.options and pass them as the second arg to _create)
            else if (typeof(method) === "object") {
                let opts = common.copy_object(obj.options, method);
                rv = obj._create.call(obj, $(this), opts);
            }
            // Dispatch the method call
            else if (obj.hasOwnProperty(method)) {
                rv = obj[method].call(obj, $(this), arg1, arg2);
            }
            else {
                throw new Error("method '" + method + "' does not exist");
            }
        });
        return rv;
    };
};

// Disables autocomplete on the given JQuery node t
const disable_autocomplete = function(t) {
    // Only disable it if autocomplete hasn't already been
    // set by the markup (eg: for password fields that are textbox)
    if (!t.attr("autocomplete")) {
        t.prop("autocomplete", "off");
        //t.prop("autocomplete", "disable" + new Date().getTime());
    }
};

// Generates a javascript object of parameters by looking
// at the data attribute of all items matching the
// selector
$.fn.toJSON = function() {
    let params = {};
    this.each(function() {
        let t = $(this);
        if (t.attr("type") == "checkbox" && t.attr("data")) {
            if (t.is(":checked")) {
                params[t.attr("data")] = "checked";
            }
        }
        else if (t.attr("data") && t.val()) {
            params[t.attr("data")] = t.val();
        }
    });
    return params;
};

// Populates fields matching the selector by looking up their
// data-json attribute 
$.fn.fromJSON = function(row) {
    this.each(function() {
        let n = $(this);
        let f = $(this).attr("data-json");
        if (f === undefined || f == null || f == "") { return; }
        if (n.hasClass("asm-animalchooser")) {
            n.animalchooser().animalchooser("loadbyid", row[f]);
        }
        else if (n.hasClass("asm-personchooser")) {
            n.personchooser().personchooser("loadbyid", row[f]);
        }
        else if (n.hasClass("asm-currencybox")) {
            n.val(format.currency(row[f]));
        }
        else if (n.hasClass("asm-datebox")) {
            n.val(format.date(row[f]));
        }
        else if (n.hasClass("asm-timebox")) {
            n.val(format.time(row[f]));
        }
        else if (n.hasClass("asm-richtextarea")) {
            n.richtextarea("value", row[f]);
        }
        else if (n.is("textarea")) {
            n.textarea("value", row[f]);
        }
        else if (n.attr("type") == "checkbox") {
            n.prop("checked", row[f] == 1);
        }
        else if (n.hasClass("asm-bsmselect")) {
            n.children().prop("selected", false);
            $.each(String(row[f]).split(/[|,]+/), function(mi, mv) {
                if (!mv) { return; }
                n.find("[value='" + mv + "']").prop("selected", true);
            });
            n.change();
        }
        else {
            n.val(html.decode(row[f]));
        }
    });
};

// Generates a URL encoded form data string of parameters
// by looking at the data-post or data attribute of all items 
// matching the selector. 
// includeblanks: true if you want fields with empty values sent instead of omitted.
$.fn.toPOST = function(includeblanks) {
    let post = [];
    this.each(function() {
        let t = $(this);
        let pname = t.attr("data-post");
        if (!pname) { pname = t.attr("data"); }
        if (!pname) { return; }
        if (t.attr("type") == "checkbox") {
            if (t.is(":checked")) {
                post.push(pname + "=checked");
            }
            else {
                post.push(pname + "=off");
            }
        }
        else if (t.hasClass("asm-currencybox")) {
            post.push(pname + "=" + encodeURIComponent(t.currency("value")));
        }
        else if (t.hasClass("asm-richtextarea")) {
            post.push(pname + "=" + encodeURIComponent(t.richtextarea("value")));
        }
        else if (t.hasClass("asm-mask")) {
            if (t.val() && t.val() != MASK_VALUE) {
                post.push(pname + "=" + encodeURIComponent(t.val()));
            }
        }
        else if (t.val() || includeblanks) {
            post.push(pname + "=" + encodeURIComponent(t.val()));
        }
    });
    return post.join("&");
};

// Generates a comma separated list of the data attributes of
// every single checked checkbox in the selector
$.fn.tableCheckedData = function() {
    let ids = "";
    this.each(function() {
        if ($(this).attr("type") == "checkbox") {
            if ($(this).is(":checked")) {
                ids += $(this).attr("data") + ",";
            }
        }
    });
    return ids;
};

// Styles an HTML table with jquery stuff and adds sorting
$.fn.table = asm_widget({

    options: {
        css:        'asm-table',
        filter:     false,  // whether filters are available
        reflow:     config.bool("TablesReflow"),  // whether to reflow the table on portrait smartphones < 480px wide
        row_hover:  true,   // highlight the row being hovered over with a mouse
        row_select: true,   // allow selection with a checkbox in the first column
        sticky_header: true // keep headers at the top of the screen when scrolling
    },
    
    _create: function(t, options) {
        let tbl = t;
        tbl.addClass(options.css);
        if (options.row_hover) {
            tbl.on("mouseover", "tbody tr", function() {
                $(this).addClass("ui-state-hover");
            });
            tbl.on("mouseout", "tbody tr", function() {
                $(this).removeClass("ui-state-hover");
            });
        }
        if (options.row_select) {
            tbl.on("click", "input:checkbox", function() {
                if ($(this).is(":checked")) {
                    $(this).closest("tr").addClass("ui-state-highlight");
                }
                else {
                    $(this).closest("tr").removeClass("ui-state-highlight");
                }
            });
        }
        tbl.addClass("tablesorter");
        let tablewidgets = [ ];
        if (options.filter) { 
            tablewidgets.push("filter"); 
        }
        if (options.reflow) { 
            tbl.addClass("asm-table-reflow"); 
            tablewidgets.push("reflow");
            // Read the table headers and copy their text values to the
            // data-title attribute of every column/cell. This allows the
            // reflow widget to show the column name to the left of the
            // value when reflowed.
            let hd = tbl.find("thead th");
            for (let i=0; i < hd.length; i++) {
                // Look for a span.columntext value in the th. If it's not found, just use the whole th.
                let columntext = $(hd[i]).find("span").text();
                if (!columntext) { columntext = hd[i].innerText; } 
                if (columntext) { columntext += ":"; } else { columntext = " "; } // show text:, but if it was blank make it a space for layout
                tbl.find("tbody td:nth-child(" + (i+1) + ")").attr("data-title", columntext);
            }
        }
        if (options.sticky_header && config.bool("StickyTableHeaders")) { 
            //tablewidgets.push("stickyHeaders"); //Use native browser support via position: sticky instead
            tbl.find("th").addClass("asm-table-sticky-header");
        }
        tbl.tablesorter({
            sortColumn: options.sortColumn,
            sortList: options.sortList,
            widgets: tablewidgets,
            widgetOptions: {
                filter_childRows: false,
                filter_columnFilters: options.filter,
                filter_cssFilter: "tablesorter-filter",
                filter_ignoreCase: true,
                filter_searchDelay: 500,
                reflow_className: "ui-table-reflow",
                reflow_headerAttrib: "data-name",
                reflow_dataAttrib: "data-title"
            },
            textExtraction: function(node, table, cellIndex) {
                // this function controls how text is extracted from cells for
                // sorting purposes.
                let s = common.trim($(node).text()), h = $(node).html();
                // If there's a data-sort attribute somewhere in the cell, use that
                if (h.indexOf("data-sort") != -1) {
                    let fq = h.indexOf("data-sort");
                    fq = h.indexOf("\"", fq);
                    s = h.substring(fq+1, h.indexOf("\"", fq+1));
                    // Looks like an ISO date/time - strip the punctuation
                    if (s.indexOf(":") != -1) { s = s.replace(/[\-\:T]/g, ""); }
                }
                // If the text contains a date, turn it into YYYY-MM-DD for sorting
                // We use a char class of .-/ as any of these can be date separators.
                else if (s && s.length >= 10 && s.length <= 20 ) {
                    if (s.match(/\d+[\/\.\-]\d+[\/\.\-]\d+/)) {
                        s = format.date_iso(s);
                        if (!s) { return ""; }
                        s = s.replace(/[\-\:T]/g, "");
                    }
                }
                // If we have custom emblems in the text, throw away the first word as it will
                // be the letters of the emblems and skew any sorting.
                else if (h.indexOf("class=\"custom\"") != -1 && s.indexOf(" ") != -1) {
                    s = s.substring(s.indexOf(" ")+1);
                }
                log.trace("table.textExtraction: " + s);
                return s;
            }
        });
        // Loading the tablesorter will add the filter row. Add a data-title
        // attribute to each of the filters so that the reflow plugin
        // can show what you're filtering on when reflowed
        if (options.filter && options.reflow) { 
            let hd = tbl.find("thead th");
            for (let i=0; i < hd.length; i++) {
                // Look for a span.columntext value in the th. If it's not found, just use the whole th.
                let columntext = $(hd[i]).find("span").text();
                if (!columntext) { columntext = hd[i].innerText; } 
                if (columntext) { columntext += ":"; } else { columntext = " "; } // show text:, but if it was blank make it a space for layout
                tbl.find(".tablesorter-filter-row td:nth-child(" + (i+1) + ")").attr("data-title", columntext);
            }
        }

    },
    
    /** Loads and sets the table filters in the object filters */
    load_filters: function(t, filters) {
        if (filters && Object.keys(filters).length > 0) {
            $.each(filters, function(column, value) {
                t.find('.tablesorter-filter[data-column="' + column + '"]').each(function() {
                    $(this).val(value);
                    $(this).trigger("keyup");
                });
            });
        }
    },

    /** Returns an object containing the filter textbox values. Can be passed to load_filters to reload them */
    save_filters: function(t) {
        let filters = {};
        t.find('.tablesorter-filter').each(function() {
            let column = $(this).attr('data-column');
            let value = $(this).val();
            filters[column] = value;
        });
        return filters;
    }

});

/** 
 * Styles a tab strip consisting of a div with an unordered list of tabs 
 * This is mainly used by the edit_header functions in all base screens
 */
$.fn.asmtabs = asm_widget({

    _create: function(t) {
        t.addClass("ui-tabs ui-widget ui-widget-content ui-corner-all");
        t.find("ul.asm-tablist").addClass("ui-tabs-nav ui-helper-reset ui-helper-clearfix ui-widget-header ui-corner-all");
        t.find("ul.asm-tablist li").addClass("ui-state-default ui-corner-top");
        t.find("ul.asm-tablist a").addClass("ui-tabs-anchor");
        t.on("mouseover", "ul.asm-tablist li", function() {
            $(this).addClass("ui-state-hover");
        });
        t.on("mouseout", "ul.asm-tablist li", function() {
            $(this).removeClass("ui-state-hover");
        });
    }

});

// Wrapper/helper for JQuery autocomplete widget. 
// Expects a data-source attribute to contain the source for the dropdown.
$.fn.autotext = asm_widget({

    _create: function(t, source) {
        disable_autocomplete(t);
        let minlength = t.attr("data-minlength") || 1;
        let defaultsearch = t.attr("data-defaultsearch");
        let appendto = t.attr("data-appendto");
        let osource = tableform._unpack_ac_source(t.attr("data-source"));
        t.autocomplete({
            source: source || osource,
            autoFocus: true,
            minLength: minlength, // number of chars to enter before searching starts
            close: function() {
                // fire the change event when the dropdown closes (ie. something is selected) 
                t.change();
            }
        });
        if (defaultsearch) {
            t.focus(function() {
                t.autocomplete("search", defaultsearch); 
            });
        }
        if (appendto) {
            t.autocomplete("option", "appendTo", appendto);
        }
        else {
            // If we don't have an appendTo, fall back to manipulating the z-index
            t.autocomplete("widget").css("z-index", 9999);
        }
    },

    // Updates the source for the autotext widget
    // source can be either an array of strings, or an array of dicts with label/value properties
    // [ "item1", "item2" ] or [ { label: "item1", value: "value1" } ]
    source: function(t, source) {
        t.autocomplete("option", "source", source);
    }

});

/**
 * Used by all of our number widgets to initialise themselves and set events.
 * self: A jquery node/reference to the DOM widget  
 * allowed_chars: A regex indicating which chars are allowed in this widget
 *                eg: /[0-9\.\-]/;
 */
const number_widget = function(t, allowed_chars) {
    let omin = t.attr("data-min") || null;
    let omax = t.attr("data-max") || null;
    if (omin) {
        t.blur(function(e) {
            if (format.to_int(t.val()) < format.to_int(omin)) {
                t.val(omin);
            }
        });
    }
    if (omax) {
        t.blur(function(e) {
            if (format.to_int(t.val()) > format.to_int(omax)) {
                t.val(omax);
            }
        });
    }
    disable_autocomplete(t);
    t.keypress(function(e) {
        let k = e.charCode || e.keyCode;
        let ch = String.fromCharCode(k);
        // Backspace, tab, ctrl, delete, arrow keys ok
        if (k == 8 || k == 9 || k == 17 || k == 46 || (k >= 35 && k <= 40)) {
            return true;
        }
        if (!allowed_chars.test(ch)) {
            e.preventDefault();
        }
    });
};

// Textbox that should only contain numbers.
// data-min and data-max attributes can be used to contain the lower/upper bound
$.fn.number = asm_widget({
    _create: function(t) {
        number_widget(t, new RegExp("[0-9\.\-]"));
    }
});

// Textbox that should only contain numbers and letters (latin alphabet, no spaces, limited punctuation)
// data-min and data-max attributes can be used to contain the lower/upper bound
$.fn.alphanumber = asm_widget({
    _create: function(t) {
        number_widget(t, new RegExp("[0-9A-Za-z\\.\\*\\-]"));
    }
});

// Textbox that should only contain integer numbers
// data-min and data-max attributes can be used to contain the lower/upper bound
$.fn.intnumber = asm_widget({
    _create: function(t) {
        number_widget(t, new RegExp("[0-9\\-]"));
    }
});

// Textbox that should only contain CIDR IP subnets or IPv6 HEX/colon
$.fn.ipnumber = asm_widget({
    _create: function(t) {
        number_widget(t, new RegExp("[0-9\\.\\/\\:abcdef ]"));
    }
});

const PHONE_RULES = [
    { locale: "en", prefix: "", length: 10, elements: 3, extract: /^(\d{3})(\d{3})(\d{4})$/, display: "({1}) {2}-{3}" },
    { locale: "en_AU", prefix: "04", length: 10, elements: 3, extract: /^(\d{4})(\d{3})(\d{3})$/, display: "{1} {2} {3}" },
    { locale: "en_AU", prefix: "", length: 10, elements: 3, extract: /^(\d{2})(\d{4})(\d{4})$/, display: "{1} {2} {3}" },
    { locale: "en_CA", prefix: "", length: 10, elements: 3, extract: /^(\d{3})(\d{3})(\d{4})$/, display: "({1}) {2}-{3}" },
    { locale: "fr_CA", prefix: "", length: 10, elements: 3, extract: /^(\d{3})(\d{3})(\d{4})$/, display: "({1}) {2}-{3}" },
    { locale: "en_GB", prefix: "011", length: 11, elements: 2, extract: /^(\d{4})(\d{7})$/, display: "{1} {2}" },
    { locale: "en_GB", prefix: "", length: 11, elements: 2, extract: /^(\d{5})(\d{6})$/, display: "{1} {2}" }
];

// Textbox that can format phone numbers to the locale rules above
$.fn.phone = asm_widget({

    _create: function(t) {
        if (!config.bool("FormatPhoneNumbers")) { return; } 
        disable_autocomplete($(this));
        t.blur(function(e) {
            let t = $(this);
            let num = String(t.val()).replace(/\D/g, ''); // Throw away all but the numbers
            $.each(PHONE_RULES, function(i, rules) {
                if (rules.locale != asm.locale) { return; }
                if (rules.prefix && num.indexOf(rules.prefix) != 0) { return; }
                if (num.length != rules.length) { return; }
                let s = rules.display, m = num.match(rules.extract), x=1;
                for (x=1; x <= rules.elements; x++) {
                    s = s.replace("{" + x + "}", m[x]);
                }
                t.val(s);
                return false;
            });
        });
    }
});

// Datepicker/wrapper widget
$.fn.date = asm_widget({

    _create: function(t) {
        disable_autocomplete(t);
        let dayfilter = t.attr("data-onlydays");
        let nopast = t.attr("data-nopast");
        let nofuture = t.attr("data-nofuture");
        if (dayfilter || nopast || nofuture) {
            t.datepicker({ 
                changeMonth: true, 
                changeYear: true,
                firstDay: config.integer("FirstDayOfWeek"),
                yearRange: "-70:+10",
                beforeShowDay: function(a) {
                    let day = a.getDay();
                    let rv = false;
                    if (dayfilter) {
                        $.each(dayfilter.split(","), function(i, v) {
                            if (v == String(day)) {
                                rv = true;
                            }
                            return false;
                        });
                    }
                    else {
                        rv = true;
                    }
                    if (nopast && a < new Date()) { rv = false; }
                    if (nofuture && a > new Date()) { rv = false; }
                    return [rv, ""];
                }
            });
        }
        else {
            t.datepicker({ 
                changeMonth: true, 
                changeYear: true,
                yearRange: "-70:+10",
                firstDay: config.integer("FirstDayOfWeek")
            });
        }
        this.bind_keys(t);
    },

    bind_keys: function(t) {
        t.keydown(function(e) {
            let d = $(this);
            let adjust = function(v) {
                if (v == "t") {
                    d.datepicker("setDate", new Date());
                }
                else {
                    d.datepicker("setDate", v); 
                    d.change();
                }
                d.change();
            };
            if (e.keyCode == 84) { // t - today
                adjust("t");
            }
            if (e.keyCode == 68 && e.shiftKey == false) { // d, add a day
                adjust("c+1d");
            }
            if (e.keyCode == 68 && e.shiftKey == true) { // shift+d, remove a day
                adjust("c-1d");
            }
            if (e.keyCode == 87 && e.shiftKey == false) { // w, add a week
                adjust("c+1w");
            }
            if (e.keyCode == 87 && e.shiftKey == true) { // shift+w, remove a week
                adjust("c-1w");
            }
            if (e.keyCode == 77 && e.shiftKey == false) { // m, add a month
                adjust("c+1m");
            }
            if (e.keyCode == 77 && e.shiftKey == true) { // shift+w, remove a month
                adjust("c-1m");
            }
            if (e.keyCode == 89 && e.shiftKey == false) { // y, add a year
                adjust("c+1y");
            }
            if (e.keyCode == 89 && e.shiftKey == true) { // shift+y, remove a year
                adjust("c-1y");
            }
        });
    },

    today: function(t) {
        t.datepicker("setDate", new Date());
    },

    getDate: function(t) {
        return t.datepicker("getDate");
    },

    setDate: function(t, newval) {
        t.datepicker("setDate");
    }

});

// Textbox that should only contain a time (numbers and colon), wraps the timepicker widget
$.fn.time = asm_widget({

    _create: function(t) {
        const allowed = [ '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':' ];
        t.timepicker({
            hourText: _("Hours"),
            minuteText: _("Minutes"),
            amPmText: [ _("AM"), _("PM") ],
            nowButtonText: _("Now"),
            showNowButton: true,
            closeButtonText: _("Close"),
            showCloseButton: true,
            deselectButtonText: _("Deselect"),
            showDeselectButton: false
        });
        disable_autocomplete(t);
        t.keypress(function(e) {
            let k = e.charCode || e.keyCode;
            let ch = String.fromCharCode(k);
            // Fill in the time now if t or n are pressed
            if (ch == 'n' || ch == 't') {
                t.val(format.time(new Date()));
                e.preventDefault();
                return false;
            }
            // Backspace, tab, ctrl, delete, arrow keys ok
            if (k == 8 || k == 9 || k == 17 || k == 46 || (k >= 35 && k <= 40)) {
                return true;
            }
            if ($.inArray(ch, allowed) == -1) {
                e.preventDefault();
            }
        });
        t.blur(function(e) {
            // If the value in the box is not HH:MM try and coerce it
            // people frequently enter times like 0900, 900 or 09.00 for some reason
            let v = String($(this).val());
            // Empty value or 5 chars with : in the middle is correct, do nothing
            if (v.length == 0 || (v.length == 5 && v.indexOf(":") == 2)) { return; }
            // 8 chars with : in positions 2,5 00:00:00 is correct
            if (v.length == 8 && v.indexOf(":") == 2 && v.lastIndexOf(":") == 5) { return; }
            // If we've got 5 chars and a ., replace with a colon
            else if (v.length == 5 && v.indexOf(".") == 2) { $(this).val( v.replace(".", ":")); }
            // If we've got 4 chars and no colon, add one in the middle
            else if (v.length == 4 && v.indexOf(":") == -1) { $(this).val( v.substring(0,2) + ":" + v.substring(2)); }
            // If we've got 3 chars and no colon, add a leading zero and one in the middle
            else if (v.length == 3 && v.indexOf(":") == -1) { $(this).val( "0" + v.substring(0,1) + ":" + v.substring(1)); }
            // If we've got 1 or 2 chars, assume it's just the hour
            else if (v.length == 2) { $(this).val(v + ":00"); }
            else if (v.length == 1) { $(this).val("0" + v + ":00"); }
            else {
                $(this).val("");
                header.show_error(_("'{0}' is not a valid time").replace("{0}", v), 5000);
            }
        });
    }
});

// Select box wrapper
$.fn.select = asm_widget({

    _create: function(t) {
        if ( t.hasClass("asm-iconselectmenu") ) {
            t.iconselectmenu({
                change: function(event , ui) {
                    $(this).trigger("change");
                }
            });
            t.iconselectmenu("menuWidget").css("height", "200px");
        }
        if ( t.hasClass("asm-selectmenu") ) {
            t.selectmenu({
                change: function(event, ui) {
                    $(this).trigger("change");
                }
            });
            t.selectmenu("menuWidget").css("height", "200px");
        }
    },

    disable: function(t) {
        t.attr("disabled", "disabled");
    },

    enable: function(t) {
        t.removeAttr("disabled");
    },

    /** Sets the value to the first element in the options list */
    firstvalue: function(t) {
        t.val( t.find("option:first").val() );
    },

    /** Set the value to the first element in the list if nothing is selected */
    firstIfBlank: function(t) {
        if (t.val() == null) {
            t.val( t.find("option:first").val() );
        }
    },

    /** Return the label for the selected option value */
    label: function(t) {
        return t.find("option:selected").html();
    },

    /** Strip any options that have been retired based on the data-retired attribute */
    removeRetiredOptions: function(t, mode) {
        // If mode == all, then we remove all retired items
        // (behaviour you want when adding records)
        if (mode !== undefined && mode == "all") {
            t.find("option").each(function() {
                if ($(this).attr("data-retired") == "1") {
                    $(this).remove();
                }
            });
        }
        // mode isn't set - don't remove the selected item if it's retired
        // (behaviour you want when editing records)
        else {
            t.find("option").each(function() {
                if (!$(this).prop("selected") && $(this).attr("data-retired") == "1") {
                    $(this).remove();
                }
            });
        }
    },

    value: function(t, newval) {
        if (newval !== undefined) {
            t.val(newval);
            if (t.hasClass("asm-iconselectmenu")) {
                t.iconselectmenu("refresh");            
            }
            else if (t.hasClass("asm-selectmenu")) {
                t.selectmenu("refresh");
            }
        }
        else {
            return t.val();
        }
    }

});

/** 
 * JQuery UI select menu with custom rendering for icons
 */
$.widget( "asm.iconselectmenu", $.ui.selectmenu, {
    _renderItem: function( ul, item ) {
        let li = $( "<li>" ),
        wrapper = $( "<div>", { text: item.label } );
        if ( item.disabled ) {
            li.addClass( "ui-state-disabled" );
        }
        $( "<span>", {
            style: item.element.attr( "data-style" ),
            "class": "ui-icon " + item.element.attr( "data-class" )
        }).appendTo( wrapper );
        return li.append( wrapper ).appendTo( ul );
    }
});

/** Wraps an input that contains a lat/long geocode */
$.fn.latlong = asm_widget({
    _create: function(t) {
        let self = this;
        t.hide();
        t.after([
            '<input type="text" class="latlong-lat asm-halftextbox" />',
            '<input type="text" class="latlong-long asm-halftextbox" />',
            '<input type="hidden" class="latlong-hash" />'
        ]);
        t.data("lat", t.parent().find(".latlong-lat"));
        t.data("lng", t.parent().find(".latlong-long"));
        t.data("hash", t.parent().find(".latlong-hash"));
        t.data("lat").blur(function() { self.save(t); });
        t.data("lng").blur(function() { self.save(t); });
    },
    load: function(t) {
        // Reads the base element value and splits it into the boxes
        let bits = t.val().split(",");
        if (bits.length > 0) { t.data("lat").val(bits[0]); }
        if (bits.length > 1) { t.data("lng").val(bits[1]); }
        if (bits.length > 2) { t.data("hash").val(bits[2]); }
    },
    save: function(t) {
        // Store the entered values back in the base element value
        let v = t.data("lat").val() + "," +
            t.data("lng").val() + "," +
            t.data("hash").val();
        t.val(v);
    }
});

/**
 * Callout widget to allow a help bubble.
 * Eg:
 *     <span id="callout-something" class="asm-callout">This inner content can be HTML</span>
 * 
 * The popup div and cancel event are attached to #asm-content, so they will unload
 * with the current module without having to be explicitly destroyed.
 */
$.fn.callout = asm_widget({

    _create: function(t) {
        let self = this;
        let button = t;
        let popupid = t.attr("id") + "-popup";
        let icon = t.attr("data-icon");
        if (!icon) { icon = "callout"; }

        // Read the elements inner content then remove it
        let content = button.html();
        button.html("");

        // Style the button by adding an actual button with icon
        button.append(html.icon(icon));
        //button.append('<span class="ui-icon ui-icon-help bottomborder"></span>');

        // Create the callout
        $("#asm-content").append('<div id="' + popupid + '" class="popupshadow asm-callout-popup">' + html.info(content) + '</div>');
        let popup = $("#" + popupid);
        popup.css("display", "none");
        t.data("popup", popup);

        // Hide the callout if we click elsewhere
        $("#asm-content").click(function() {
            self.hide(t);
        });

        button.click(function(e) {
            popup.css({
                "position": "fixed",
                "left": e.clientX + "px",
                "top": e.clientY + "px",
                "z-index": "9999",
                "max-width": "500px"
            });
            popup.toggle();
            return false; // prevent bubbling up to our click/hide event
        });
    },

    hide: function(t) {
        t.data("popup").hide();
    },

    destroy: function(t) {
        try {
            t.data("popup").remove();
        } catch (err) {}
    }

});

/**
 * ASM menu widget (we have to use asmmenu so as not to clash
 * with the built in JQuery UI menu widget)
 */
$.fn.asmmenu = asm_widget({ 

    _create: function(t) {
        let self = this;
        let button = t;
        
        // Add display arrow span
        let n = "<span style=\"display: inline-block; width: 16px; height: 16px; vertical-align: middle\" class=\"ui-button-text ui-icon ui-icon-triangle-1-e\"></span>";
        t.append(n);
        
        // If the menu is empty, disable it
        let id = t.attr("id");
        let body = $("#" + id + "-body");
        t.data("menu", body);

        if (body.find(".asm-menu-item").length == 0) {
            button.addClass("ui-state-disabled").addClass("ui-button-disabled");
        }
        
        // Add JQuery widget styles to the menu container/body
        body.addClass("ui-widget ui-widget-content ui-corner-all menushadow");
        button
            .addClass("ui-widget ui-state-default ui-corner-all")
            .mouseover(function() { $(this).addClass("ui-state-hover").removeClass("ui-state-default"); })
            .mouseout(function() { $(this).addClass("ui-state-default").removeClass("ui-state-hover"); });

        // Attach hover styles to the menu items, but make sure they're never bold
        body.find(".asm-menu-item").css("font-weight", "normal");
        body.on("mouseover", ".asm-menu-item", function() {
            $(this).addClass("ui-state-hover");
        });
        body.on("mouseout", ".asm-menu-item", function() {
            $(this).removeClass("ui-state-hover");
        });
        
        // Attach click handler to the button
        if (!button.hasClass("ui-state-disabled")) {
            button.click(function() {
                self.toggle_menu(t, id);
            });
        }

        // Hide the menu/body
        body.hide();

        // Hide all menus if any form content is clicked, as long as it's
        // not a menu opening button/icon that was clicked anyway
        // make sure we only do this once
        if (!$("body").attr("data-menu-hide")) {
            $("body").attr("data-menu-hide", "true");
            $("body").click(function(e) {
                let t = $(e.target);
                if (t.hasClass("asm-menu-icon") || t.parent().hasClass("asm-menu-icon")) { return true; }
                if (t.hasClass("asm-menu-button") || t.parent().hasClass("asm-menu-button")) { return true; }
                if (t.hasClass("asm-menu-filter") || t.parent().hasClass("asm-menu-filter")) { return true; }
                if (t.closest(".asm-menu-accordion").length > 0) { return true; }
                if (e.target.offsetParent && e.target.offsetParent.classList &&
                    e.target.offsetParent.classList.contains("asm-menu-button")) { return true; }
                self.hide_all();
            });
        }
    },

    hide_all: function(t) {
        // Active
        $(".asm-menu-icon").removeClass("ui-state-active").addClass("ui-state-default");
        // Menus
        $(".asm-menu-body").css("z-index", 0).hide();
        // Set icons back to up
        $(".asm-menu-icon span.ui-button-text").removeClass("ui-icon-triangle-1-s").addClass("ui-icon-triangle-1-e");
    },

    toggle_menu: function(t, id) {
        // Get the menu body element, style it and position it below the button
        let button = "#" + id;
        let body = "#" + id + "-body";
        let topval = $(button).offset().top + $(button).height() + 14;
        let leftval = $(button).offset().left;

        // If the menu button is disabled, don't do anything
        if ($(button).hasClass("ui-state-disabled")) { return; }

        // If the left position puts it off screen, move it over until it fits
        if ((leftval + $(body).width()) > $(window).width()) {
            leftval = $(window).width() - $(body).width() - 15;
        }

        $(body).css({
            top: topval + "px",
            left: leftval + "px"
        });

        // If the width of the body is less than the button, then increase the
        // size to match, otherwise it just looks weird
        if ($(body).width() < $(button).width()) {
            $(body).css({
                width: String($(button).width() + 8) + "px"
            });
        }

        // If the menu was displayed previously, don't try and display it again
        let wasactive = $(body).css("display") != "none";
        
        // Slide up all existing menus
        this.hide_all();

        // Slide down our newly opened menu
        if (!wasactive) {
            $(button).removeClass("ui-state-default").addClass("ui-state-active");
            $(button + " span.ui-button-text").removeClass("ui-icon-triangle-1-e").addClass("ui-icon-triangle-1-s");
            $(body).css("z-index", "2 !important").slideDown(common.fx_speed);
        }
    }
});

$.fn.textbox = asm_widget({

    _create: function(t) {
        disable_autocomplete(t);
        t.on("keypress", function(e) {
            if (t.prop("disabled")) {
                e.preventDefault();
            }
        });
    },

    enable: function(t) {
        t.removeClass("asm-textbox-disabled");
        t.prop("disabled", false);
    },

    disable: function(t) {
        t.addClass("asm-textbox-disabled");
        t.prop("disabled", true);
    },

    toggleEnabled: function(t, enableOrDisable) {
        if (enableOrDisable) { 
            this.enable(); 
        }
        else {
            this.disable();
        }
    },

    value: function(t, newval) {
        if (newval === undefined) {
            return t.val();
        }
        else {
            t.val(newval);
        }
    }
});

// Textbox wrapper that should only contain currency
// The value passed in and out via the value method is in whole pence/cents/whatever the subdivision is
// (an integer value that we stored in the db for the value)
$.fn.currency = asm_widget({

    _create: function(t) {
        const allowed = [ '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', asm.currencyradix, '-' ];
        disable_autocomplete(t);
        t.keypress(function(e) {
            let k = e.charCode || e.keyCode;
            let ch = String.fromCharCode(k);
            // Backspace, tab, ctrl, delete, arrow keys ok
            if (k == 8 || k == 9 || k == 17 || k == 46 || (k >= 35 && k <= 40)) {
                return true;
            }
            if ($.inArray(ch, allowed) == -1) {
                e.preventDefault();
            }
        });
        t.blur(function(e) {
            // reformat the value when focus leaves the field
            let i = format.currency_to_int(t.val());
            t.val(format.currency(i));
        });
        this.reset(t);
    },

    reset: function(t) {
        // Shows the locale's currency symbol and default amount of 0
        if (t.val() == "") {
            t.val(format.currency(0));
        }
    },

    value: function(t, newval) {
        if (newval === undefined) {
            // Get the value
            let v = t.val();
            if (!v) { return 0; }
            return format.currency_to_int(v);
        }
        // We're setting the value
        t.val(format.currency(newval));
    }

});

/** This is necessary for the richtextarea below - it allows the tinymce dialogs
 *  to work inside a JQuery UI modal dialog. The class prefix (tox) has
 *  changed between major TinyMCE releases in the past */
$.widget("ui.dialog", $.ui.dialog, {
    _allowInteraction: function(event) {
        return !!$(event.target).closest(".tox").length || this._super( event );
    }
});

/** Wrapper for a TinyMCE widget */
$.fn.richtextarea = asm_widget({

    _create: function(t) {
        let self = this;
        // Override height, width and margin-top if they were set as attributes of the div
        if (t.attr("data-width")) {
            t.css("width", t.attr("data-width"));
        }
        if (t.attr("data-height")) {
            t.css("height", t.attr("data-height"));
        }
        if (t.attr("data-margin-top")) {
            t.css("margin-top", t.attr("data-margin-top"));
        }
        tinymce.init({
            selector: "#" + t.attr("id"),
            plugins: [
                "advlist autolink lists link image charmap code ",
                "hr anchor searchreplace visualblocks visualchars ",
                "insertdatetime media nonbreaking table directionality",
                "emoticons template paste"
                ],
            inline: true,
            menubar: false,
            statusbar: false, 
            add_unload_trigger: false,

            toolbar_items_size: "small",
            toolbar: "undo redo | fontselect fontsizeselect | bold italic underline forecolor backcolor | alignleft aligncenter alignright alignjustify | bullist numlist | link image | code",
            //contextmenu: "link image | cut copy paste",
            contextmenu: "", // allow the browser's default context menu

            // enable browser spellchecking
            gecko_spellcheck: true,
            browser_spellcheck: true,

            // stop tinymce stripping data url images
            paste_data_images: true,

            // Necessary for fontsizeselect to work
            convert_fonts_to_spans: true,
            fontsize_formats: "8pt 10pt 11pt 12pt 14pt 16pt 18pt 20pt 22pt 24pt 36pt 72pt",

            entity_encoding: "raw",

            setup: function(ed) {
                t.data("editor", ed);
                ed.on("init", function(ed) {
                    $(".tox-tinymce-inline").css({ "z-index": 101 }); // Prevent floating under dialogs
                });
            }

        });
    },

    destroy: function(t) {
        try {
            tinymce.get(t.attr("id")).remove();
        }
        catch (err) {} // uncaught exception can block module unload
    },

    value: function(t, newval) {
        if (newval === undefined) {
            return t.html();
        }
        if (!newval) { newval = ""; }
        t.html(newval);
    }

});

/** Wrapper widget for textarea, adds a zoom and the ability to include links to searches and media records */
$.fn.textarea = asm_widget({
    
    _create: function(t) {
        
        let buttonstyle = "margin-left: -56px; margin-top: -24px; height: 16px",
            self = this;

        if (t.attr("data-zoom")) { return; }
        if (!t.attr("id")) { return; }

        t.attr("data-zoom", "true");
        let zbid = t.attr("id") + "-zb";

        t.wrap("<span style='white-space: nowrap'></span>");
        t.after("<button id='" + zbid + "' style='" + buttonstyle + "'></button>");

        let tdid = t.attr("id") + "-td";
        $("#" + zbid).after("<div id='" + tdid + "' style='white-space: normal;margin-bottom: 3px;'></div>");

        // When zoom button is clicked
        $("#" + zbid).button({ text: false, icons: { primary: "ui-icon-zoomin" }}).click(function() {
            self.zoom(t);
            return false; // Prevent any textareas in form elements submitting the form
        });

        t.on('paste keyup', function() {
            self.process_links(t);
        });
    },

    process_links: function(t) {
        let tdid = t.attr("id") + "-td";
        $('#' + tdid).html("");
        let searchmatches = t.val().match(/#s:\w{1,}:?\w{1,}/g);
        if (searchmatches) {
            $.each(searchmatches, function(i, v) {
                v = v.replace("#s:", "");
                let linkiconclass = 'asm-icon-link';
                if (v.includes('a:')) {
                    linkiconclass = 'asm-icon-animal';
                } else if (v.includes('ac:')) {
                    linkiconclass = 'asm-icon-call';
                } else if (v.includes('p:')) {
                    linkiconclass = 'asm-icon-person';
                } else if (v.includes('wl:')) {
                    linkiconclass = 'asm-icon-waitinglist';
                } else if (v.includes('la:')) {
                    linkiconclass = 'asm-icon-animal-lost';
                } else if (v.includes('fa:')) {
                    linkiconclass = 'asm-icon-animal-found';
                } else if (v.includes('li:')) {
                    linkiconclass = 'asm-icon-licence';
                } else if (v.includes('co:')) {
                    linkiconclass = 'asm-icon-cost';
                } else if (v.includes('lo:')) {
                    linkiconclass = 'asm-icon-log';
                } else if (v.includes('vo:')) {
                    linkiconclass = 'asm-icon-transactions';
                } else if (v.includes('ci:')) {
                    linkiconclass = 'asm-icon-citation';
                }
                $('#' + tdid).append('<div class="asm-token-link"><span class="asm-icon ' + linkiconclass + '"></span><a href="/search?q=' + v + '" target="_blank">' + v + '</a></div> ');
            });
            $('#' + tdid).show();
        }
        let mediamatches = t.val().match(/#m:\w{1,}/g);
        if (mediamatches) {
            $.each(mediamatches, function(i, v) {
                v = v.replace("#m:", "");
                $('#' + tdid).append('<div class="asm-token-link"><span class="asm-icon asm-icon-media"></span>&nbsp;<a href="/media?id=' + v + '" target="_blank">' + v + '</a></div> ');
            });
            $('#' + tdid).show();
        }
        if (!searchmatches && !mediamatches) {
            $('#' + tdid).hide();
        }
    },

    zoom: function(t) {
        if (t.is(":disabled")) { return; }
        if (t.attr("maxlength") !== undefined) { $("#textarea-zoom-area").attr("maxlength", t.attr("maxlength")); }

        $("#textarea-zoom-id").val( t.attr("id") );
        $("#textarea-zoom-area").val( t.val() );
        $("#textarea-zoom-area").css({ "font-family": t.css("font-family") });

        let title = "";
        if (t.attr("title")) { title = String(t.attr("title")); }
        $("#dialog-textarea-zoom").dialog("option", "title", title);
        $("#dialog-textarea-zoom").dialog("open");

        return false;
    },

    value: function(t, newval) {
        if (newval === undefined) {
            return t.val();
        }
        if (!newval) { newval = ""; }
        //newval = common.replace_all(newval, "<", "&lt;");
        //newval = common.replace_all(newval, ">", "&gt;");
        t.val(html.decode(newval));
        this.process_links(t);
        t.trigger("change");
    }
});

/** Wraps a CodeMirror instance editing HTML */
$.fn.htmleditor = asm_widget({

    _create: function(t) {
        let self = this;
        setTimeout(function() {
            let editor = CodeMirror.fromTextArea(t[0], {
                lineNumbers: true,
                mode: "htmlmixed",
                matchBrackets: true,
                autofocus: false,
                //direction: (asm.locale == "ar" || asm.locale == "he") ? "rtl" : "ltr",
                extraKeys: {
                    "F11": function(cm) {
                        self.fullscreen(t, cm, !cm.getOption("fullScreen"));
                    },
                    "Shift-Ctrl-F": function(cm) {
                        self.fullscreen(t, cm, !cm.getOption("fullScreen"));
                    },
                    "Esc": function(cm) {
                        self.fullscreen(t, cm, false);
                    }
                }
            });
            t.data("editor", editor);
            // Override height and width if they were set as attributes of the text area
            if (t.attr("data-width")) {
                t.next().css("width", t.attr("data-width"));
            }
            if (t.attr("data-height")) {
                t.next().css("height", t.attr("data-height"));
            }
            // When the editor loses focus, update the original textarea element
            editor.on("blur", function() {
                self.change(t);
            });

        }, 1000);
    },

    append: function(t, s) {
        let e = t.data("editor");
        e.setValue(e.getValue() + s);
    },

    change: function(t) {
        let e = t.data("editor");
        t.val( e.getValue() );
    },

    destroy: function(t) {
        try {
            let e = t.data("editor");
            e.destroy();
        }
        catch (err) {}
    },

    fullscreen: function(t, cm, fs) {
        // FIX FOR CHROME: If this code editor is inside a jquery dialog, Chrome will not render
        // the portion of the editor that is outside the dialog when it goes fullscreen.
        // To work around this, we record the position, height and width of the dialog before
        // going into fullscreen, make the dialog fill the screen and then restore it 
        // when leaving fullscreen as a workaround.
        let dlg = t.closest("div.ui-dialog");
        if (dlg) {
            if (fs) {
                t.data("dlgheight",  dlg.height()); 
                t.data("dlgwidth", dlg.width()); 
                t.data("dlgtop", dlg.position().top); 
                t.data("dlgleft", dlg.position().left);
                dlg.height("100%"); dlg.width("100%"); dlg.css("top", 0); dlg.css("left", 0);
            }
            else {
                dlg.height(t.data("dlgheight")); 
                dlg.width(t.data("dlgwidth"));
                dlg.css("top", t.data("dlgtop")); 
                dlg.css("left", t.data("dlgleft"));
            }
        }
        // END CHROME FIX
        cm.setOption("fullScreen", fs);
    },

    refresh: function(t) {
        t.data("editor").refresh();
    },

    value: function(t, newval) {
        if (newval === undefined) {
            return t.data("editor").getValue();
        }
        if (!newval) { newval = ""; }
        t.data("editor").setValue(newval);
        t.data("editor").refresh();
        this.change(t);
    }

});

/** Wraps a CodeMirror instance editing SQL */
$.fn.sqleditor = asm_widget({

    _create: function(t) {
        let self = this;
        setTimeout(function() {
            let editor = CodeMirror.fromTextArea(t[0], {
                lineNumbers: true,
                mode: "text/x-sql",
                matchBrackets: true,
                autofocus: false,

                //direction: (asm.locale == "ar" || asm.locale == "he") ? "rtl" : "ltr",
                extraKeys: {
                    "F11": function(cm) {
                        self.fullscreen(t, cm, !cm.getOption("fullScreen"));
                    },
                    "Shift-Ctrl-F": function(cm) {
                        self.fullscreen(t, cm, !cm.getOption("fullScreen"));
                    },
                    "Esc": function(cm) {
                        self.fullscreen(t, cm, false);
                    }
                },
                hintOptions: { tables: schema }
            });
            t.data("editor", editor);
            // Override height and width if they were set as attributes of the text area
            if (t.attr("data-width")) {
                t.next().css("width", t.attr("data-width"));
            }
            if (t.attr("data-height")) {
                t.next().css("height", t.attr("data-height"));
            }
            // When the editor loses focus, update the original textarea element
            editor.on("blur", function() {
                self.change(t);
            });

        }, 1000);
    },

    append: function(t, s) {
        let e = t.data("editor");
        e.setValue(e.getValue() + s);
    },

    change: function(t) {
        let e = t.data("editor");
        t.val( e.getValue() );
    },

    destroy: function(t) {
        try {
            let e = t.data("editor");
            e.destroy();
        }
        catch (err) {}
    },

    fullscreen: function(t, cm, fs) {
        // FIX FOR CHROME: If this code editor is inside a jquery dialog, Chrome will not render
        // the portion of the editor that is outside the dialog when it goes fullscreen.
        // To work around this, we record the position, height and width of the dialog before
        // going into fullscreen, make the dialog fill the screen and then restore it 
        // when leaving fullscreen as a workaround.
        let dlg = t.closest("div.ui-dialog");
        if (dlg) {
            if (fs) {
                t.data("dlgheight",  dlg.height()); 
                t.data("dlgwidth", dlg.width()); 
                t.data("dlgtop", dlg.position().top); 
                t.data("dlgleft", dlg.position().left);
                dlg.height("100%"); dlg.width("100%"); dlg.css("top", 0); dlg.css("left", 0);
            }
            else {
                dlg.height(t.data("dlgheight")); 
                dlg.width(t.data("dlgwidth"));
                dlg.css("top", t.data("dlgtop")); 
                dlg.css("left", t.data("dlgleft"));
            }
        }
        // END CHROME FIX
        cm.setOption("fullScreen", fs);
    },

    refresh: function(t) {
        t.data("editor").refresh();
    },

    value: function(t, newval) {
        if (newval === undefined) {
            return t.data("editor").getValue();
        }
        if (!newval) { newval = ""; }
        t.data("editor").setValue(newval);
        t.data("editor").refresh();
        this.change(t);
    }

});

// Helper to disable jquery ui dialog buttons
$.fn.disable_dialog_buttons = function() {
    this.each(function() {
        $(this).parent().find(".ui-dialog-buttonset button").button("disable");
    });
};

// Helper to enable jquery ui dialog buttons
$.fn.enable_dialog_buttons = function() {
    this.each(function() {
        $(this).parent().find(".ui-dialog-buttonset button").button("enable");
    });
};

$.fn.asmcontent = function(type) {
    // Show the content
    this.each(function() {
        // criteria
        // results
        // newdata
        // report
        if (type == "main") {
            $(this).show("slide", {direction: 'up'}, common.fx_speed);
            return;
        }
        if (type == "formtab") {
            $(this).show("slide", {direction: 'right'}, common.fx_speed);
            return;
        }
        if (type == "book") {
            $(this).show("slide", {direction: 'down'}, common.fx_speed);
            return;
        }
        if (type == "options") {
            $(this).show("slide", {direction: 'up'}, common.fx_speed);
            return;
        }
        // default
        $(this).show("slide", {direction: 'left'}, common.fx_speed);
    });
};

/** Signature widget that wraps JQUI signature() for drawing a signature,
 *  and allows a text box for rendering a font/typed version of the signature.
 *  Can use bootstrap buttons. 
 *  The element target should be a div.
 */
$.fn.asmsignature = asm_widget({

    options: {
        guideline: false,
        bootstrap: false,
        value: "" // a data URI that contains an image of the signature for loading
    },

    _create: function(t, options) {
        let self = this;
        t.hide();
        let id = "asmsign-" + t[0].id;
        let guideline = options.guideline;
        t.after([
            '<div id=' + id + '>',
                '<div>', 
                    '<button class="button-asmsignchange" type="button" style="vertical-align: middle;margin-right: 10px;">' + _("Clear") + '</button>', 
                    '<span class="asmsigntools" style="display: none;">', 
                        '<label>' + _("Draw") + '<input class="asmsigndraw" name="asmsigntype" type="radio" checked></label> ', 
                        '<label>' + _("Text") + '<input class="asmsigntext" name="asmsigntype" type="radio"></label> ', 
                        '<input type="text" class="asmsigntextinput" placeholder="' + _("Signature text") + '" style="margin-left: 10px;display: none;">', 
                    '</span>', 
                '</div>',
                '<div class="asmsignimg"><img src="' + options.value + '" style="width: 500px; height: 200px;"></div>', 
                '<div style="width: 500px; max-height: 200px;">', 
                    '<canvas class="asmsigncanvas" style="width: 500px; height: 200px;display: none;"></canvas>', 
                '</div>', 
                '<div class="asmsignwidget" style="width: 500px; height: 200px;display: none;"></div>', 
            '</div>'
        ].join("\n"));
        $("#" + id + " .asmsignwidget").signature({ guideline: options.guideline });
        if (options.bootstrap) {
            $("#" + id + " .button-asmsignchange").addClass("btn btn-primary").html("<i class='bi-x'>" + _("Clear") + "</i>");
            $("#" + id + " input[name='asmsigntype']").addClass("m-1");
            $("#" + id + " label").addClass("form-check-label");
        } else {
            $("#" + id + " .button-asmsignchange").button({ icons: { primary: "ui-icon-pencil" }, text: false });
        }
        $("#" + id + " .button-asmsignchange")
            .click(function() {
                $("#" + id + " .asmsignwidget").signature("clear");
                let canvas = $("#" + id + " .asmsigncanvas")[0];
                let ctx = canvas.getContext("2d");
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                $("#" + id + " .asmsigntextinput").val("");
                $("#" + id + " .asmsignimg").hide();
                $("#" + id + " .asmsigncanvas").hide();
                $("#" + id + " .asmsigndraw").prop("checked", true);
                $("#" + id + " .asmsigntools").show();
                $("#" + id + " .asmsignwidget").show();
            });
        if (options.value == "") {
            $("#" + id + " .button-asmsignchange").click();
        }
        $("#" + id + " .asmsigndraw").change(function() {
            $("#" + id + " .asmsigntextinput").hide();
            $("#" + id + " .asmsignwidget").show();
            $("#" + id + " .asmsigncanvas").hide();
        });
        $("#" + id + " .asmsigntext").change(function() {
            $("#" + id + " .asmsigntextinput").show();
            $("#" + id + " .asmsignwidget").hide();
            let canvas = $("#" + id + " .asmsigncanvas")[0];
            let ctx = canvas.getContext("2d");
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = "white";
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            if (guideline) {
                ctx.beginPath();
                ctx.moveTo(6, 112);
                ctx.lineTo(294, 112);
                ctx.strokeStyle = "#a0a0a0";
                ctx.lineWidth = 1;
                ctx.stroke();
                ctx.closePath();
            }
            $("#" + id + " .asmsigncanvas").show();
            $("#" + id + " .asmsigntextinput").focus();
        });
        $("#" + id + " .asmsigntextinput").keyup(function() {
            let canvas = $("#" + id + " .asmsigncanvas")[0];
            let ctx = canvas.getContext("2d");
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = "white";
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            if (guideline) {
                ctx.beginPath();
                ctx.moveTo(6, 112);
                ctx.lineTo(294, 112);
                ctx.strokeStyle = "#a0a0a0";
                ctx.lineWidth = 1;
                ctx.stroke();
                ctx.closePath();
            }
            ctx.fillStyle = "black";
            let siglength = $("#" + id + " .asmsigntextinput").val().length;
            let fontsize = 60;
            if ( siglength > 20 ) { 
                fontsize = 26 - ( siglength * 0.33 );
            } else if ( siglength > 8 ) { 
                fontsize = 60 - ( siglength * 1.7 ) ;
            }
            ctx.font = fontsize + "px cursive";
            ctx.fillText($("#" + id + " .asmsigntextinput").val(),10,100,500);
        });
        
    },

    value: function(t) {
        let id = "asmsign-" + t[0].id;
        if ($("#" + id + " .asmsigntools").css("display") == "none") {
            return "";
        }
        let canvas = $("#" + id + " .asmsigncanvas");
        if ($("#" + id + " .asmsigndraw").prop("checked") == true ) {
            canvas = $("#" + id + " .asmsignwidget canvas");
        }
        return canvas.get(0).toDataURL("image/png");
    },

    isEmpty: function(t) {
        let id = "asmsign-" + t[0].id;
        if ($("#" + id + " .asmsigndraw").prop("checked") == true ) {
            return $("#" + id + " .asmsignwidget").signature("isEmpty");
        } else {
            if ($("#" + id + " .asmsigntextinput").val() == "") {
                return true;
            } else {
                return false;
            }
        }
    }

});
