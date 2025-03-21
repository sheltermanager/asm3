/*global $, console, jQuery, CodeMirror, Mousetrap, tinymce */
/*global asm, common, config, dlgfx, edit_header, format, html, header, log, schema, tableform, validate, _, escape, unescape */
/*global MASK_VALUE: true */

"use strict";

// String shown in asm-mask fields instead of the value
const MASK_VALUE = "****************";

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
            n.html(row[f]);
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
$.widget("asm.table", {
    
    options: {
        css:        'asm-table',
        filter:     false,  // whether filters are available
        reflow:     config.bool("TablesReflow"),  // whether to reflow the table on portrait smartphones < 480px wide
        row_hover:  true,   // highlight the row being hovered over with a mouse
        row_select: true,   // allow selection with a checkbox in the first column
        sticky_header: true // keep headers at the top of the screen when scrolling
    },

    _create: function() {
        let tbl = this.element, options = this.options;
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
    load_filters: function(filters) {
        let self = this;
        if (filters && Object.keys(filters).length > 0) {
            $.each(filters, function(column, value) {
                $(self.element).find('.tablesorter-filter[data-column="' + column + '"]').each(function() {
                    $(this).val(value);
                    $(this).trigger("keyup");
                });
            });
        }
    },

    /** Returns an object containing the filter textbox values. Can be passed to load_filters to reload them */
    save_filters: function() {
        let filters = {};
        $(this.element).find('.tablesorter-filter').each(function() {
            let column = $(this).attr('data-column');
            let value = $(this).val();
            filters[column] = value;
        });
        return filters;
    }

});

// Styles a tab strip consisting of a div with an unordered list of tabs
$.fn.asmtabs = function() {
    this.each(function() {
        $(this).addClass("ui-tabs ui-widget ui-widget-content ui-corner-all");
        $(this).find("ul.asm-tablist").addClass("ui-tabs-nav ui-helper-reset ui-helper-clearfix ui-widget-header ui-corner-all");
        $(this).find("ul.asm-tablist li").addClass("ui-state-default ui-corner-top");
        $(this).find("ul.asm-tablist a").addClass("ui-tabs-anchor");
        $(this).on("mouseover", "ul.asm-tablist li", function() {
            $(this).addClass("ui-state-hover");
        });
        $(this).on("mouseout", "ul.asm-tablist li", function() {
            $(this).removeClass("ui-state-hover");
        });
    });
};

// Wrapper/helper for JQuery autocomplete widget. 
// Expects a data-source attribute to contain the source for the dropdown.
$.fn.autotext = function(method, newval) {
    if (!method || method == "create") {
        this.each(function() {
            let self = $(this);
            disable_autocomplete(self);
            let minlength = self.attr("data-minlength") || 1;
            let defaultsearch = self.attr("data-defaultsearch");
            let appendto = self.attr("data-appendto");
            let source = tableform._unpack_ac_source(self.attr("data-source"));
            if (!appendto && $("#dialog-tableform").length > 0) { appendto = "#dialog-tableform"; }
            self.autocomplete({
                source: newval || source,
                minLength: minlength, // number of chars to enter before searching starts
                select: function() {
                    // fire the change event when something is selected from the dropdown
                    self.change();
                }
            });
            if (defaultsearch) {
                self.focus(function() {
                    self.autocomplete("search", defaultsearch); 
                });
            }
            if (appendto) {
                self.autocomplete("option", "appendTo", appendto);
            }
            else {
                // If we don't have an appendTo, fall back to manipulating the z-index
                self.autocomplete("widget").css("z-index", 1000);
            }
        });
    }
    else if (method == "source") {
        this.each(function() {
            let self = $(this);
            self.autocomplete("option", "source", newval);
        });
    }
};

// Textbox that should only contain numbers.
// data-min and data-max attributes can be used to contain the lower/upper bound
$.fn.number = function() {
    const allowed = /[0-9\.\-]/;
    this.each(function() {
        if ($(this).attr("data-min")) {
            $(this).blur(function(e) {
                if (format.to_int($(this).val()) < format.to_int($(this).attr("data-min"))) {
                    $(this).val($(this).attr("data-min"));
                }
            });
        }
        if ($(this).attr("data-max")) {
            $(this).blur(function(e) {
                if (format.to_int($(this).val()) > format.to_int($(this).attr("data-max"))) {
                    $(this).val($(this).attr("data-max"));
                }
            });
        }
        disable_autocomplete($(this));
        $(this).keypress(function(e) {
            let k = e.charCode || e.keyCode;
            let ch = String.fromCharCode(k);
            // Backspace, tab, ctrl, delete, arrow keys ok
            if (k == 8 || k == 9 || k == 17 || k == 46 || (k >= 35 && k <= 40)) {
                return true;
            }
            if (!allowed.test(ch)) {
                e.preventDefault();
            }
        });
    });
};

// Textbox that should only contain numbers and letters (numbers, latin alphabet, no spaces, limited punctuation)
$.fn.alphanumber = function() {
    const allowed = new RegExp("[0-9A-Za-z\\.\\*\\-]");
    this.each(function() {
        disable_autocomplete($(this));
        $(this).keypress(function(e) {
            let k = e.charCode || e.keyCode;
            let ch = String.fromCharCode(k);
            // Backspace, tab, ctrl, delete, arrow keys ok
            if (k == 8 || k == 9 || k == 17 || k == 46 || (k >= 35 && k <= 40)) {
                return true;
            }
            if (!allowed.test(ch)) {
                e.preventDefault();
            }
        });
    });
};

// Textbox that should only contain integer numbers
// data-min and data-max attributes can be used to contain the lower/upper bound
$.fn.intnumber = function() {
    const allowed = new RegExp("[0-9\\-]");
    this.each(function() {
        disable_autocomplete($(this));
        if ($(this).attr("data-min")) {
            $(this).blur(function(e) {
                if (format.to_int($(this).val()) < format.to_int($(this).attr("data-min"))) {
                    $(this).val($(this).attr("data-min"));
                }
            });
        }
        if ($(this).attr("data-max")) {
            $(this).blur(function(e) {
                if (format.to_int($(this).val()) > format.to_int($(this).attr("data-max"))) {
                    $(this).val($(this).attr("data-max"));
                }
            });
        }
        $(this).keypress(function(e) {
            let k = e.charCode || e.keyCode;
            let ch = String.fromCharCode(k);
            // Backspace, tab, ctrl, arrow keys ok
            // (note: little delete key is code 46, shared with decimal point
            //  so we do not allow it here)
            if (k == 8 || k == 9 || k == 17 || (k >= 35 && k <= 40)) {
                return true;
            }
            if (!allowed.test(ch)) {
                e.preventDefault();
            }
        });
    });
};

// Textbox that should only contain CIDR IP subnets or IPv6 HEX/colon
$.fn.ipnumber = function() {
    const allowed = new RegExp("[0-9\\.\\/\\:abcdef ]");
    this.each(function() {
        disable_autocomplete($(this));
        $(this).keypress(function(e) {
            let k = e.charCode || e.keyCode;
            let ch = String.fromCharCode(k);
            // Backspace, tab, ctrl, delete, arrow keys ok
            if (k == 8 || k == 9 || k == 17 || k == 46 || (k >= 35 && k <= 40)) {
                return true;
            }
            if (!allowed.test(ch)) {
                e.preventDefault();
            }
        });
    });
};

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
$.fn.phone = function() {
    this.each(function() {
        if (!config.bool("FormatPhoneNumbers")) { return; } 
        disable_autocomplete($(this));
        $(this).blur(function(e) {
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
    });
};

$.fn.date = function(method, newval) {
    if (!method || method == "create") {
        this.each(function() {
            disable_autocomplete($(this));
            let dayfilter = $(this).attr("data-onlydays");
            let nopast = $(this).attr("data-nopast");
            let nofuture = $(this).attr("data-nofuture");
            if (dayfilter || nopast || nofuture) {
                $(this).datepicker({ 
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
                $(this).datepicker({ 
                    changeMonth: true, 
                    changeYear: true,
                    yearRange: "-70:+10",
                    firstDay: config.integer("FirstDayOfWeek")
                });
            }
            $(this).keydown(function(e) {
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
        });
    }
    else if (method == "today") {
        this.each(function() {
            $(this).datepicker("setDate", new Date());
        });
    }
    else if (method == "getDate") {
        let rv = null;
        this.each(function() {
            rv = $(this).datepicker("getDate");
        });
        return rv;
    }
    else if (method == "setDate") {
        // Expects newval to contain a javascript Date object
        this.each(function() {
            $(this).datepicker("setDate", newval);
        });
    }
};

// Textbox that should only contain a time (numbers and colon)
$.fn.time = function() {
    const allowed = [ '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':' ];
    this.each(function() {
        let t = $(this);
        $(this).timepicker({
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
        disable_autocomplete($(this));
        $(this).keypress(function(e) {
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
        $(this).blur(function(e) {
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
    });
};

// Select box
$.fn.select = function(method, newval) {
    let rv = "", tv;
    if (!method || method == "create") {
        $(this).each(function() {
            if ( $(this).hasClass("asm-iconselectmenu") ) {
                $(this).iconselectmenu({
                    change: function(event , ui) {
                        $(this).trigger("change");
                    }
                });
                $(this).iconselectmenu("menuWidget").css("height", "200px");
            }
            if ( $(this).hasClass("asm-selectmenu") ) {
                $(this).selectmenu({
                    change: function(event, ui) {
                        $(this).trigger("change");
                    }
                });
                $(this).selectmenu("menuWidget").css("height", "200px");
            }
        });
    }
    else if (method == "firstvalue") {
        $(this).each(function() {
            $(this).val( $(this).find("option:first").val() );
        });
    }
    else if (method == "firstIfBlank") {
        $(this).each(function() {
            if ($(this).val() == null) {
                $(this).val( $(this).find("option:first").val() );
            }
        });
    }
    else if (method == "value") {
        $(this).each(function() {
            if (newval !== undefined) {
                $(this).val(newval);
                if ($(this).hasClass("asm-iconselectmenu")) {
                    $(this).iconselectmenu("refresh");
                }
                else if ($(this).hasClass("asm-selectmenu")) {
                    $(this).selectmenu("refresh");
                }
            }
            else {
                rv = $(this).val();
            }
        });
    }
    else if (method == "removeRetiredOptions") {
        $(this).each(function() {
            tv = $(this);
            // newval contains a "mode". If mode == all, then we remove all retired items
            // (behaviour you want when adding records)
            if (newval !== undefined && newval == "all") {
                tv.find("option").each(function() {
                    if ($(this).attr("data-retired") == "1") {
                        $(this).remove();
                    }
                });
            }
            // mode isn't set - don't remove the selected item if it's retired
            // (behaviour you want when editing records)
            else {
                tv.find("option").each(function() {
                    if (!$(this).prop("selected") && $(this).attr("data-retired") == "1") {
                        $(this).remove();
                    }
                });
            }
        });
    }
    else if (method == "label") {
        rv = "";
        $(this).each(function() {
            rv = $(this).find("option:selected").html();    
        });
    }
    else if (method == "disable") {
        $(this).each(function() {
            $(this).attr("disabled", "disabled");
        });
    }
    else if (method == "enable") {
        $(this).each(function() {
            $(this).removeAttr("disabled");
        });
    }
    return rv;
};

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

/**
 * Widget to create a payment dialog.
 * Target should be a div to contain the hidden dialog.
 */
$.widget("asm.createpayment", {
    options: {
        dialog: null
    },

    _create: function() {
        let dialog = this.element, self = this;
        this.options.dialog = dialog;
        this.element.append([
            '<div id="dialog-payment" style="display: none" title="' + html.title(_("Create Payment")) + '">',
            '<div>',
            '<input type="hidden" id="pm-animal" data="animal" class="asm-field" value="" />',
            '<input type="hidden" id="pm-person" data="person" class="asm-field" value="" />',
            '</div>',
            '<table width="100%">',
            '<tr>',
            '<td>', // LEFT TABLE
            '<table>',
            '<tr>',
            '<td><label for="pm-type">' + _("Type") + '</label></td>',
            '<td><select id="pm-type" data="type" class="asm-selectbox asm-field">',
            '</select></td>',
            '</tr>',
            '<tr>',
            '<td><label for="pm-method">' + _("Method") + '</label></td>',
            '<td><select id="pm-method" data="payment" class="asm-selectbox asm-field">',
            '</select></td>',
            '</tr>',
            '<tr>',
            '<td><label for="pm-due">' + _("Due") + '</label></td>',
            '<td><input id="pm-due" data="due" type="text" class="asm-textbox asm-datebox asm-field" /></td>',
            '</tr>',
            '<tr>',
            '<td><label for="pm-received">' + _("Received") + '</label></td>',
            '<td><input id="pm-received" data="received" type="text" class="asm-textbox asm-datebox asm-field" /></td>',
            '</tr>',
            '<tr>',
            '<td><label for="pm-amount">' + _("Amount") + '</label></td>',
            '<td><input id="pm-amount" data="amount" type="text" class="asm-textbox asm-currencybox asm-field" /></td>',
            '</tr>',
            '<tr>',
            '<td></td>',
            '<td><input id="pm-vat" data="vat" type="checkbox" class="asm-checkbox asm-field" /> <label for="pm-vat">' + _("Sales Tax") + '</label></td>',
            '</tr>',

            '<tr class="paymentsalestax">',
            '<td><label for="pm-vatratechoice">' + _("Tax Rate") + '</label></td>',
            '<td><select id="pm-vatratechoice" data="vatratechoice" class="asm-selectbox" /></select></td>',
            '</tr>',

            '<tr style="display: none;">',
            '<td><label for="pm-vatrate">' + _("Tax Rate %") + '</label></td>',
            '<td><input id="pm-vatrate" data="vatrate" type="text" class="asm-numberbox asm-field" /></td>',
            '</tr>',
            '<tr class="paymentsalestax">',
            '<td><label for="pm-vatamount">' + _("Tax Amount") + '</label></td>',
            '<td><input id="pm-vatamount" data="vatamount" type="text" class="asm-currencybox asm-textbox asm-field" /></td>',
            '</tr>',
            '</table>',
            '</td>',
            '<td>', // RIGHT TABLE
            '<table>',
            '<tr>',
            '<td><label for="pm-comments">' + _("Comments") + ' </label></td>',
            '<td><textarea id="pm-comments" data="comments" class="asm-textarea asm-field" rows="5"></textarea></td>',
            '</table>',
            '</td>',
            '</tr>',
            '</table>',
            '</div>'
        ].join("\n"));
        $("#pm-due, #pm-received").date();
        $("#pm-amount, #pm-vatamount").currency();
        let b = {}; 
        b[_("Create Payment")] = {
            text: _("Create Payment"),
            "class": "asm-dialog-actionbutton",
            click: function() {
                validate.reset("dialog-payment");
                if (!validate.notblank(["pm-due"])) { return; }
                let o = self.options.o;
                let formdata = "mode=create&";
                formdata += $("#dialog-payment .asm-field").toPOST();
                header.show_loading(_("Creating..."));
                common.ajax_post("donation", formdata, function(receipt) {
                    header.show_info( common.sub_arr(_("Payment {0} created for {1}"), 
                        [ receipt.split("|")[1], '<a href="person_donations?id=' + o.personid + '">' + o.personname + '</a>' ]) );
                    $("#dialog-payment").dialog("close");
                });
            }
        };
        b[_("Cancel")] = function() { $(this).dialog("close"); };
        $("#dialog-payment").dialog({
                autoOpen: false,
                resizable: false,
                modal: true,
                dialogClass: "dialogshadow",
                width: 650,
                show: dlgfx.add_show,
                hide: dlgfx.add_hide,
                buttons: b
        });
        $("#pm-vat").change(function() {
            if ($(this).is(":checked")) {
                if (!config.bool("VATExclusive")) {
                    $("#pm-vatamount").currency("value", common.tax_from_inclusive($("#pm-amount").currency("value"), $("#pm-vatrate").val()));
                }
                else {
                    $("#pm-vatamount").currency("value", common.tax_from_exclusive($("#pm-amount").currency("value"), $("#pm-vatrate").val()));
                    $("#pm-amount").currency("value", $("#pm-amount").currency("value") + $("#pm-vatamount").currency("value"));
                }
                $("#dialog-payment .paymentsalestax").fadeIn();
            } else {
                $("#pm-vatamount").currency("value", "0");
                $("#pm-vatrate").val("0"); 
                $("#dialog-payment .paymentsalestax").fadeOut();
            }
        });
        $("#pm-amount").change(function() {
            $("#pm-vat").change();
        });
        $("#pm-vatratechoice").change(function() {
            $("#pm-vatrate").val($("#pm-vatratechoice").val().split("|")[1]);
            $("#pm-vat").change();
        });
    },

    destroy: function() {
        common.widget_destroy("#dialog-payment", "dialog"); 
    },
    
    /**
     * Shows the create payment dialog.
     * title:      The dialog title (optional: Create Payment)
     * animalid:   Animal ID
     * personid:   Person ID
     * personname: Person name
     * donationtypes: The donationtypes lookup
     * paymentmethods: The paymentmethods lookup
     * chosentype: The default payment type to choose (optional, AFDefaultDonationType if not given)
     * chosenmethod: The default payment method to choose (optional, AFDefaultPaymentMethod if not given)
     * amount:     The amount of the payment (integer money expected)
     * vat:        (bool) whether we should have vat on or not
     * vatrate:    The vat rate (optional, configured amount used if not set)
     * vatamount:  The vat amount
     * comments:   Any comments for the payment
     *    Eg: show({ amount: 5000, vat: false })
     */
    show: function(o) {
        this.options.o = o;
        $("#dialog-payment").dialog("option", "title", o.title || _("Create Payment"));
        $("#pm-animal").val(o.animalid);
        $("#pm-person").val(o.personid);
        $("#pm-type").html( html.list_to_options(o.donationtypes, "ID", "DONATIONNAME") );
        $("#pm-type").select("removeRetiredOptions", "all");
        $("#pm-type").select("value", o.chosentype || config.integer("AFDefaultDonationType")); 
        $("#pm-method").html( html.list_to_options(o.paymentmethods, "ID", "PAYMENTNAME") );
        $("#pm-method").select("removeRetiredOptions", "all");
        $("#pm-method").select("value", o.chosenmethod || config.integer("AFDefaultPaymentMethod")); 
        $("#pm-amount").currency("value", o.amount || 0);
        $("#pm-vat").prop("checked", o.vat);
        $("#pm-vatrate").val( o.vatrate || config.number("VATRate") );
        $("#pm-vatamount").currency("value", o.vatamount || 0);
        $("#pm-comments").html( o.comments );
        $("#pm-due").date("today");
        $("#pm-vat").change();
        let vatrates = [];
        let defaulttaxrateval = "";
        $.each(controller.taxrates, function(taxratecount, taxrate) {
            let optval = taxrate.ID + "|" + taxrate.TAXRATE;
            if (taxrate.ID == config.integer("AFDefaultTaxRate")) {
                defaulttaxrateval = optval;
            }
            vatrates.push({ID: optval, TAXRATENAME: taxrate.TAXRATENAME});
        });
        let vatrateoptions = html.list_to_options(vatrates, "ID", "TAXRATENAME" );
        $("#pm-vatratechoice").html(vatrateoptions);
        if (defaulttaxrateval != "") {
            $("#pm-vatratechoice").val(defaulttaxrateval);
        }
        $("#pm-vat").change();
        $("#pm-vatratechoice").change();
        $("#dialog-payment").dialog("open");
        
    }
});

/**
 * Widget to manage a form that allows sending of email.
 * Target should be a div to contain the hidden dialog.
 */
$.widget("asm.emailform", {
    options: {
        dialog: null
    },

    _create: function() {
        let dialog = this.element, self = this;
        this.options.dialog = dialog;
        this.element.append([
            '<div id="dialog-email" style="display: none" title="' + html.title(_("Email person"))  + '">',
            '<table width="100%">',
            '<tr>',
            '<td><label for="em-from">' + _("From") + '</label></td>',
            '<td><input id="em-from" data="from" type="text" class="asm-doubletextbox" autocomplete="new-password" /></td>',
            '</tr>',
            '<tr>',
            '<td><label for="em-to">' + _("To") + '</label></td>',
            '<td><input id="em-to" data="to" type="text" class="asm-doubletextbox" autocomplete="new-password" /></td>',
            '</tr>',
            '<tr>',
            '<td><label for="em-cc">' + _("CC") + '</label></td>',
            '<td><input id="em-cc" data="cc" type="text" class="asm-doubletextbox" autocomplete="new-password" /></td>',
            '</tr>',
            '<tr>',
            '<td><label for="em-bcc">' + _("BCC") + '</label></td>',
            '<td><input id="em-bcc" data="bcc" type="text" class="asm-doubletextbox" autocomplete="new-password" /></td>',
            '</tr>',
            '<tr>',
            '<td><label for="em-subject">' + _("Subject") + '</label></td>',
            '<td><input id="em-subject" data="subject" type="text" class="asm-doubletextbox" /></td>',
            '</tr>',
            '<tr id="em-attachmentrow">',
            '<td><label for="em-attachments">' + _("Attachments") + '</label></td>',
            '<td><span id="em-attachments" data="attachments" type="text" class="strong"></span></td>',
            '</tr>',
            '<tr id="em-docreporow">',
            '<td><label for="em-docrepo">' + _("Document Repository") + '</label></td>',
            '<td>',
            '<select id="em-docrepo" data="docrepo" multiple="multiple" class="asm-bsmselect" title="' + _("Select") + '">',
            '</select>',
            '</td>',
            '</tr>',
            '<tr>',
            '<td></td>',
            '<td><input id="em-addtolog" data="addtolog" type="checkbox"',
            'title="' + html.title(_("Add details of this email to the log after sending")) + '" ',
            'class="asm-checkbox" /><label for="emailaddtolog">' + _("Add to log") + '</label>',
            '<select id="em-logtype" data="logtype" class="asm-selectbox">',
            '</select>',
            '</td>',
            '</tr>',
            '</table>',
            '<div id="em-body" data="body" data-margin-top="24px" data-height="300px" class="asm-richtextarea"></div>',
            '<p>',
            '<label for="em-template">' + _("Template") + '</label>',
            '<select id="em-template" class="asm-selectbox">',
            '<option value=""></option>',
            '</select>',
            '</p>',
            '</div>'
        ].join("\n"));
        if ( config.bool("AuditOnSendEmail"))
        $("#em-body").richtextarea();
        $("#em-docrepo").asmSelect({
            animate: true,
            sortable: true,
            removeLabel: '<strong>&times;</strong>',
            listClass: 'bsmList-custom',  
            listItemClass: 'bsmListItem-custom',
            listItemLabelClass: 'bsmListItemLabel-custom',
            removeClass: 'bsmListItemRemove-custom'
        });
        let b = {}; 
        b[_("Send")] = {
            text: _("Send"),
            "class": "asm-dialog-actionbutton",
            click: function() {
                validate.reset("dialog-email");
                if (!validate.notblank(["em-from", "em-to"])) { return; }
                if (!validate.validemail(["em-from", "em-to"])) { return; }
                if ($("#em-cc").val() != "" && !validate.validemail(["em-cc"])) { return; }
                if ($("#em-bcc").val() != "" && !validate.validemail(["em-bcc"])) { return; }
                let o = self.options.o;
                if (o.formdata) { o.formdata += "&"; }
                o.formdata += $("#dialog-email input, #dialog-email select, #dialog-email .asm-richtextarea").toPOST();
                header.show_loading(_("Sending..."));
                common.ajax_post(o.post, o.formdata, function() {
                    let recipients = $("#em-to").val();
                    if ($("#em-cc").val() != "") { recipients += ", " + $("#em-cc").val(); }
                    header.show_info(_("Message successfully sent to {0}").replace("{0}", recipients));
                    $("#dialog-email").dialog("close");
                });
            }
        };
        b[_("Cancel")] = function() { $(this).dialog("close"); };
        $("#dialog-email").dialog({
                autoOpen: false,
                resizable: false,
                modal: true,
                dialogClass: "dialogshadow",
                width: 640,
                show: dlgfx.add_show,
                hide: dlgfx.add_hide,
                buttons: b
        });
        $("#em-template").change(function() {
            let o = self.options.o;
            let formdata = "mode=emailtemplate&dtid=" + $("#em-template").val();
            if (o.animalcontrolid) { formdata += "&animalcontrolid=" + o.animalcontrolid; }
            if (o.licenceid) { formdata += "&licenceid=" + o.licenceid; }
            if (o.donationids) { formdata += "&donationids=" + o.donationids; }
            if (o.personid) { formdata += "&personid=" + o.personid; }
            if (o.animalid) { formdata += "&animalid=" + o.animalid; }
            header.show_loading(_("Loading..."));
            common.ajax_post("document_gen", formdata, function(response) {
                let j = jQuery.parseJSON(response);
                if (j.TO) { $("#em-to").val(j.TO); }
                if (j.SUBJECT) { $("#em-subject").val(j.SUBJECT); }
                if (j.FROM) { $("#em-from").val(j.FROM); }
                if (j.CC) { $("#em-cc").val(j.CC); }
                if (j.BCC) { $("#em-bcc").val(j.BCC); }
                $("#em-body").html(j.BODY); 
            });
        });

    },

    destroy: function() {
        common.widget_destroy("#dialog-email", "dialog"); 
        common.widget_destroy("#em-body", "richtextarea");
    },
    
    /**
     * Shows the email dialog.
     * title:      The dialog title (optional: Email person)
     * post:       The ajax post target
     * formdata:   The first portion of the formdata
     * name:       The name to show on the form (optional)
     * email:      The email(s) to show on the form (optional)
     * bccemail:   The bcc email(s) to show on the form (optional)
     * subject:    The default subject (optional)
     * message:    The default message (optional)
     * logtypes:   The logtypes to populate the attach as log box (optional)
     * templates:  The list of email document templates (optional)
     * personid:   A person to substitute tokens in templates for (optional)
     * animalid:   An animal to substitute tokens in templates for (optional)
     *    Eg: show({ post: "person", formdata: "mode=email&personid=52", name: "Bob Smith", email: "bob@smith.com" })
     */
    show: function(o) {
        this.options.o = o;
        $("#dialog-email").dialog("option", "title", o.title || _("Email person"));
        $("#dialog-email").dialog("open");
        if (o.logtypes) {
            $("#em-logtype").html( html.list_to_options(o.logtypes, "ID", "LOGTYPENAME") );
            $("#em-logtype").select("removeRetiredOptions", "all");
            $("#em-logtype").select("value", config.integer("AFDefaultLogType"));
        }
        else {
            $("#em-logtype").closest("tr").hide();
        }
        if (o.templates) {
            $("#em-template").html( edit_header.template_list_options(o.templates) );
        }
        else {
            $("#em-template").closest("tr").hide();
        }
        let fromaddresses = [], toaddresses = [];
        let conf_org = html.decode(config.str("Organisation").replace(",", ""));
        let conf_email = config.str("EmailAddress");
        let org_email = conf_org + " <" + conf_email + ">";
        let bcc_email = config.str("EmailBCC");
        $("#em-from").val(conf_email);
        fromaddresses.push(conf_email);
        fromaddresses.push(org_email);
        if (asm.useremail) {
            fromaddresses.push(asm.useremail);
            fromaddresses.push(html.decode(asm.userreal) + " <" + asm.useremail + ">");
            if (config.bool(asm.user + "_EmailDefault")) {
                $("#em-from").val(asm.useremail);
            }
        }
        if (bcc_email) {
            $("#em-bcc").val(bcc_email);
        }
        if (o.toaddresses) {
            toaddresses = toaddresses.concat(o.toaddresses);
        }
        if (o.attachments) {
            $("#em-attachments").html(o.attachments);
            $("#em-attachmentrow").show();
        }
        else {
            $("#em-attachmentrow").hide();
        }
        if (o.documentrepository) {
            $("#em-docrepo").html(html.list_to_options(o.documentrepository, "ID", "NAME"));
            $("#em-docrepo").change();
            $("#em-docreporow").show();
        }
        else {
            $("#em-docreporow").hide();
        }
        fromaddresses = fromaddresses.concat(config.str("EmailFromAddresses").split(","));
        toaddresses = toaddresses.concat(config.str("EmailToAddresses").split(","));
        const add_address = function(n, s) {
            // build a list of valid existing addresses in the textbox (n: node) so far, then add the new one (s: String)
            let existing = [], xs = String(n.val());
            $.each(xs.split(","), function(i, v) {
                if (validate.email(v) && common.trim(v) != s) { existing.push(common.trim(v)); }
            });
            existing.push(s);
            n.val(existing.join(", "));
        };
        $("#em-from").autocomplete({source: fromaddresses});
        $("#em-from").autocomplete("widget").css("z-index", 1000);
        $("#em-to").autocomplete({source: toaddresses});
        $("#em-to").autocomplete("widget").css("z-index", 1000);
        $("#em-to").on("autocompleteselect", function(event, ui) { add_address($("#em-to"), ui.item.value); return false; });
        $("#em-cc").autocomplete({source: toaddresses});
        $("#em-cc").autocomplete("widget").css("z-index", 1000);
        $("#em-cc").on("autocompleteselect", function(event, ui) { add_address($("#em-cc"), ui.item.value); return false; });
        $("#em-bcc").autocomplete({source: toaddresses});
        $("#em-bcc").autocomplete("widget").css("z-index", 1000);
        $("#em-bcc").on("autocompleteselect", function(event, ui) { add_address($("#em-bcc"), ui.item.value); return false; });
        $("#em-from, #em-to, #em-cc, #em-bcc").bind("focus", function() {
            $(this).autocomplete("search", "@");
        });
        if (o.email && o.email.indexOf(",") != -1) { 
            // If there's more than one email address, only output the comma separated emails
            $("#em-to").val(o.email); 
        }
        else if (o.email) { 
            // Otherwise, use RFC821
            $("#em-to").val(common.replace_all(html.decode(o.name), ",", "") + " <" + o.email + ">"); 
        }
        if (o.bccemail) {
            $("#em-bcc").val(o.bccemail);
        }
        let msg = config.str("EmailSignature");
        if (o.message) { msg = "<p>" + o.message + "</p>" + msg; }
        else { msg = "<p>&nbsp;</p>" + msg; }
        if (msg) {
            $("#em-body").richtextarea("value", msg);
        }
        if (o.subject) {
            $("#em-subject").val(o.subject); 
        }
        if (config.bool("LogEmailByDefault")) {
            $("#em-addtolog").prop("checked", true);
        } else {
            $("#em-addtolog").prop("checked", false);
        }
        // If a default email log type has been chosen and exists in the list, select it 
        if ($("#em-logtype option[value='" + config.integer("EmailLogType") + "']").length > 0) {
            $("#em-logtype").val(config.integer("EmailLogType"));
        }
        $("#em-subject").focus();
    }
});

$.widget("asm.latlong", {
    options: {
        lat: null,
        lng: null,
        hash: null
    },
    _create: function() {
        let self = this;
        this.element.hide();
        this.element.after([
            '<input type="text" class="latlong-lat asm-halftextbox" />',
            '<input type="text" class="latlong-long asm-halftextbox" />',
            '<input type="hidden" class="latlong-hash" />'
        ]);
        this.options.lat = this.element.parent().find(".latlong-lat");
        this.options.lng = this.element.parent().find(".latlong-long");
        this.options.hash = this.element.parent().find(".latlong-hash");
        this.options.lat.blur(function() { self.save.call(self); });
        this.options.lng.blur(function() { self.save.call(self); });
    },
    load: function() {
        // Reads the base element value and splits it into the boxes
        let bits = this.element.val().split(",");
        if (bits.length > 0) { this.options.lat.val(bits[0]); }
        if (bits.length > 1) { this.options.lng.val(bits[1]); }
        if (bits.length > 2) { this.options.hash.val(bits[2]); }
    },
    save: function() {
        // Store the entered values back in the base element value
        let v = this.options.lat.val() + "," +
            this.options.lng.val() + "," +
            this.options.hash.val();
        this.element.val(v);
    }
});

/**
 * Widget to take one or more payments.
 * Relies on controller.accounts, controller.paymentmethods and controller.donationtypes
 * target should be a container div
 */
$.widget("asm.payments", {
    options: {
        count: 0,
        controller: null,
        giftaid: false
    },
    _create: function() {
        let self = this;
        // If the user does not have permission to add payments, do nothing
        if (!common.has_permission("oaod")) { return; }
        this.element.append([
            html.content_header(_("Payment"), true),
            '<table class="asm-table-layout">',
            '<thead>',
            '<tr>',
            '<th>' + _("Type") + '</th>',
            '<th class="overridedates">' + _("Due") + '</th>',
            '<th class="overridedates">' + _("Received") + '</th>',
            '<th>' + _("Method") + '</th>',
            '<th>' + _("Check No") + '</th>',
            '<th class="quantities">' + _("Quantity") + '</th>',
            '<th class="quantities">' + _("Unit Price") + '</th>',
            '<th>' + _("Amount") + '</th>',
            '<th class="overrideaccount">' + _("Deposit Account") + '</th>',
            '<th class="giftaid">' + _("Gift Aid") + '</th>',
            '<th class="vat">' + _("Sales Tax") + '</th>',
            '<th>' + _("Comments") + '</th>',
            '</tr>',
            '</thead>',
            '<tbody id="paymentlines">',
            '</tbody>',
            '<tfoot id="paymenttotals">',
            '<tr>',
            '<td colspan="3"><button class="takepayment">' + _("Take another payment") + '</button>',
            '<a class="takepayment" href="#">' + _("Take another payment") + '</a></td>',
            '<td class="overridedates"></td>',
            '<td class="overridedates"></td>',
            //'<td></td>',
            //'<td></td>',
            '<td class="quantities"></td>',
            '<td class="quantities"></td>',
            '<td class="rightalign strong" id="totalamount"></td>',
            '<td class="overrideaccount"></td>',
            '<td class="giftaid"></td>',
            '<td class="vat rightalign strong" id="totalvat"></td>',
            '<td></td>',
            '</tr>',
            '</tfoot>',
            '</table>',
            html.content_footer()
        ].join("\n"));
        this.add_payment();
        $("button.takepayment")
            .button({ icons: { primary: "ui-icon-circle-plus" }, text: false })
            .click(function() {
            self.add_payment();
        });
        this.element.find("a.takepayment").click(function() {
            self.add_payment();
            return false;
        });
    },

    add_payment: function() {
        let h = [
            '<tr>',
            '<td>',
            '<select id="donationtype{i}" data="donationtype{i}" class="asm-selectbox asm-halfselectbox">',
            html.list_to_options(this.options.controller.donationtypes, "ID", "DONATIONNAME"),
            '</select>',
            '</td>',
            '<td class="overridedates">',
            '<input id="due{i}" data="due{i}" class="asm-datebox asm-textbox asm-halftextbox" />',
            '</td>',
            '<td class="overridedates">',
            '<input id="received{i}" data="received{i}" class="asm-datebox asm-textbox asm-halftextbox" />',
            '</td>',
            '<td>',
            '<select id="payment{i}" data="payment{i}" class="asm-halfselectbox">',
            html.list_to_options(this.options.controller.paymentmethods, "ID", "PAYMENTNAME"),
            '</select>',
            '</td>',
            '<td>',
            '<input id="chequenumber{i}" data="chequenumber{i}" class="asm-textbox asm-halftextbox" />',
            '</td>',
            '<td class="quantities">',
            '<input id="quantity{i}" data="quantity{i}" class="rightalign asm-numberbox asm-textbox asm-halftextbox" value="1" />',
            '</td>',
            '<td class="quantities">',
            '<input id="unitprice{i}" data="unitprice{i}" class="rightalign unitprice asm-currencybox asm-textbox asm-halftextbox" value="0" />',
            '</td>',
            '<td>',
            '<input id="amount{i}" data="amount{i}" class="rightalign amount asm-currencybox asm-textbox asm-halftextbox" />',
            '</td>',
            '<td class="overrideaccount">',
            '<select id="destaccount{i}" data="destaccount{i}" class="asm-selectbox asm-halfselectbox">',
            html.list_to_options(this.options.controller.accounts, "ID", "CODE"),
            '</select>',
            '</td>',
            '<td class="giftaid centered">',
            '<input id="giftaid{i}" data="giftaid{i}" type="checkbox" class="asm-checkbox"',
            (this.options.giftaid ? ' checked="checked"' : '') + ' />',
            '</td>',
            '<td class="vat centered nowrap">',
            '<input id="vat{i}" data="vat{i}" type="checkbox" class="asm-checkbox" />',
            '<span id="vatboxes{i}" style="display: none">',
            '<select id="vatratechoice{i}" data="destaccount{i}" class="asm-selectbox asm-halfselectbox">',
            html.list_to_options(this.options.controller.taxrates, "ID", "TAXRATENAME"),
            '</select>',
            '<input id="vatrate{i}" data="vatrate{i}" class="rightalign asm-textbox asm-halftextbox asm-numberbox" value="0" style="display: none;" />',
            '<input id="vatamount{i}" data="vatamount{i}" class="rightalign vatamount asm-textbox asm-halftextbox asm-currencybox" value="0" disabled="disabled" />',
            '</span>',
            '</td>',
            '<td>',
            '<input id="comments{i}" data="comments{i}" class="asm-textbox" />',
            '</td>',
            '</tr>'
        ];
        // Construct and add our new payment fields to the DOM
        this.options.count += 1;
        let i = this.options.count, self = this;
        this.element.find("#paymentlines").append(common.substitute(h.join("\n"), {
            i: this.options.count
        }));
        // Remove any retired payment types and methods
        $("#donationtype" + i).select("removeRetiredOptions", "all");
        $("#payment" + i).select("removeRetiredOptions", "all");
        // Change the default amount when the payment type changes
        $("#donationtype" + i).change(function() {
            let dc = common.get_field(self.options.controller.donationtypes, $("#donationtype" + i).select("value"), "DEFAULTCOST");
            let dv = common.get_field(self.options.controller.donationtypes, $("#donationtype" + i).select("value"), "ISVAT");
            $("#quantity" + i).val("1");
            $("#unitprice" + i).currency("value", dc);
            $("#amount" + i).currency("value", dc);
            $("#vat" + i).prop("checked", dv == 1);
            $("#vat" + i).change();
            self.update_totals();
        });
        // Recalculate when quantity or unit price changes
        $("#quantity" + i + ", #unitprice" + i).change(function() {
            let q = $("#quantity" + i).val(), u = $("#unitprice" + i).currency("value");
            $("#amount" + i).currency("value", q * u);
            self.update_totals();
        });
        // Recalculate when amount or VAT changes
        $("#amount" + i).change(function() {
            $("#vatratechoice" + i).change();
            //self.update_totals();
        });
        $("#vatratechoice" + i).change(function() {
            let taxrate = 0.0;
            taxrate = common.get_field(self.options.controller.taxrates, $("#vatratechoice" + i).val(), "TAXRATE");
            console.log("taxrate = " + taxrate);
            $("#vatrate" + i).val(taxrate);
            if (!config.bool("VATExclusive")) {
                $("#vatamount" + i).currency("value", common.tax_from_inclusive($("#amount" + i).currency("value"), $("#vatrate" + i).val()));
            }
            else {
                $("#vatamount" + i).currency("value", common.tax_from_exclusive($("#amount" + i).currency("value"), $("#vatrate" + i).val()));
            }
            self.update_totals();
        });
        // Clicking the VAT checkbox enables and disables the rate/amount fields with defaults
        $("#vat" + i).change(function() {
            if ($(this).is(":checked")) {
                
                $("#vatrate" + i).val(config.number("VATRate"));
                if (!config.bool("VATExclusive")) {
                    $("#vatamount" + i).currency("value", 
                        common.tax_from_inclusive($("#amount" + i).currency("value"), format.to_float($("#vatrate" + i).val())));
                }
                else {
                    $("#vatamount" + i).currency("value", 
                        common.tax_from_exclusive($("#amount" + i).currency("value"), format.to_float($("#vatrate" + i).val())));
                    $("#amount" + i).currency("value", $("#amount" + i).currency("value") + $("#vatamount" + i).currency("value"));
                }
                $("#vatratechoice" + i).val(config.number("AFDefaultTaxRate"));
                $("#vatboxes" + i).fadeIn();
            }
            else {
                $("#vatrate" + i + ", #vatamount" + i).val("0");
                $("#vatboxes" + i).fadeOut();
            }
            $("#vatratechoice" + i).change();
            self.update_totals();
        });
        // Set the default for our new payment type
        $("#donationtype" + i).val(config.str("AFDefaultDonationType")).change();
        $("#donationtype" + i).change();
        // Payment method
        $("#payment" + i).val(config.str("AFDefaultPaymentMethod"));
        // If we're creating accounting transactions and the override
        // option is set, allow override of the destination account
        if (config.bool("CreateDonationTrx") && config.bool("DonationTrxOverride")) {
            $(".overrideaccount").show();
            // Set it to the default account
            $("#destaccount" + i).val(config.str("DonationTargetAccount"));
        }
        else {
            $(".overrideaccount").hide();
        }
        // Gift aid only applies to the UK
        if (asm.locale != "en_GB") { $(".giftaid").hide(); }
        // Disable vat/tax if the option is off necessary
        if (!config.bool("VATEnabled")) { $(".vat").hide(); }
        // Disable quantity/unit price if the option is off
        if (!config.bool("DonationQuantities")) { $(".quantities").hide(); }
        // Disable dates if the option is off
        if (!config.bool("DonationDateOverride")) { 
            $(".overridedates").hide(); 
        }
        else {
            // Set due or received date to today if the date override is on
            if (config.bool("MovementDonationsDefaultDue")) {
                $("#due" + i).val(format.date(new Date()));
            }
            else {
                $("#received" + i).val(format.date(new Date()));
            }
            // Make sure the dates are turned into picker widgets
            $("#due" + i).date();
            $("#received" + i).date();
        }
    },

    update_totals: function() {
        let totalamt = 0, totalvat = 0, totalall = 0;
        $(".amount").each(function() {
            totalamt += $(this).currency("value");
        });
        $(".vatamount").each(function() {
            totalvat += $(this).currency("value");
        });
        $("#totalamount").html(format.currency(totalamt));
        $("#totalvat").html(format.currency(totalvat));
    },

    destroy: function() {
    }

});

/**
 * Callout widget to allow a help bubble.
 * Eg:
 *     <span id="callout-something" class="asm-callout">This inner content can be HTML</span>
 * 
 * The popup div and cancel event are attached to #asm-content, so they will unload
 * with the current form without having to be explicitly destroyed.
 */
$.widget("asm.callout", {
    options: {
        button: null,
        popup: null
    },

    _create: function() {
        let self = this;
        let button = this.element;
        this.options.button = this.element;
        let popupid = this.element.attr("id") + "-popup";
        let icon = this.element.attr("data-icon");
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
        this.options.popup = popup;
        popup.css("display", "none");

        // Hide the callout if we click elsewhere
        $("#asm-content").click(function() {
            self.hide();
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

    hide: function() {
        this.options.popup.hide();
    },

    destroy: function() {
        try {
            this.options.popup.remove();
        } catch (err) {}
    }

});


/**
 * ASM menu widget (we have to use asmmenu so as not to clash
 * with the built in JQuery UI menu widget)
 */
$.widget("asm.asmmenu", {
    options: {
        button: null,
        menu: null
    },

    _create: function() {
        let self = this;
        let button = this.element;
        this.options.button = button;
        
        // Add display arrow span
        let n = "<span style=\"display: inline-block; width: 16px; height: 16px; vertical-align: middle\" class=\"ui-button-text ui-icon ui-icon-triangle-1-e\"></span>";
        this.element.append(n);
        
        // If the menu is empty, disable it
        let id = this.element.attr("id");
        let body = $("#" + id + "-body");
        this.options.menu = body;
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
                self.toggle_menu(id);
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
                if (t.closest(".asm-menu-accordion").length > 0) { return true; }
                if (e.target.offsetParent && e.target.offsetParent.classList &&
                    e.target.offsetParent.classList.contains("asm-menu-button")) { return true; }
                self.hide_all();
            });
        }
    },

    hide_all: function() {
        // Active
        $(".asm-menu-icon").removeClass("ui-state-active").addClass("ui-state-default");
        // Menus
        $(".asm-menu-body").css("z-index", 0).hide();
        // Set icons back to up
        $(".asm-menu-icon span.ui-button-text").removeClass("ui-icon-triangle-1-s").addClass("ui-icon-triangle-1-e");
    },

    toggle_menu: function(id) {
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

$.widget("asm.textbox", {
    options: {
        disabled: false
    },

    _create: function() {
        let self = this;
        disable_autocomplete(this.element);
        this.element.on("keypress", function(e) {
            if (self.options.disabled) {
                e.preventDefault();
            }
        });
    },

    enable: function() {
        this.options.disabled = false;
        this.element.removeClass("asm-textbox-disabled");
        this.element.prop("disabled", false);
    },

    disable: function() {
        this.options.disabled = true;
        this.element.addClass("asm-textbox-disabled");
        this.element.prop("disabled", true);
    },

    toggleEnabled: function(enableOrDisable) {
        if (enableOrDisable) { 
            this.enable(); 
        }
        else {
            this.disable();
        }
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

$.widget("asm.richtextarea", {

    options: {
        editor: null
    },

    _create: function() {
        let self = this;
        // Override height, width and margin-top if they were set as attributes of the div
        if (self.element.attr("data-width")) {
            self.element.css("width", self.element.attr("data-width"));
        }
        if (self.element.attr("data-height")) {
            self.element.css("height", self.element.attr("data-height"));
        }
        if (self.element.attr("data-margin-top")) {
            self.element.css("margin-top", self.element.attr("data-margin-top"));
        }
        tinymce.init({
            selector: "#" + this.element.attr("id"),
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
                self.editor = ed;
                ed.on("init", function(ed) {
                    $(".tox-tinymce-inline").css({ "z-index": 101 }); // Prevent floating under dialogs
                });
            }

        });
    },

    destroy: function() {
        try {
            tinymce.get(this.element.attr("id")).remove();
        }
        catch (err) {} // uncaught exception can block module unload
    },

    value: function(newval) {
        if (newval === undefined) {
            return this.element.html();
        }
        if (!newval) { newval = ""; }
        this.element.html(newval);
    }

});

$.widget("asm.textarea", {
    
    options: {
        disabled: false
    },

    _create: function() {
        
        let buttonstyle = "margin-left: -56px; margin-top: -24px; height: 16px",
            fixmarginstyle = "margin-left: 32px; margin-top: 24px;",
            t = $(this.element[0]),
            self = this;

        if (t.attr("data-zoom")) { return; }
        if (!t.attr("id")) { return; }

        t.attr("data-zoom", "true");
        let zbid = t.attr("id") + "-zb";

        t.wrap("<span style='white-space: nowrap'></span>");
        t.after("<button id='" + zbid + "' style='" + buttonstyle + "'></button>" + "<span style='" + fixmarginstyle + "'></span>");

        // When zoom button is clicked
        $("#" + zbid).button({ text: false, icons: { primary: "ui-icon-zoomin" }}).click(function() {
            self.zoom();
            return false; // Prevent any textareas in form elements submitting the form
        });

    },

    zoom: function() {
        let t = $(this.element[0]);

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
    }
});

$.widget("asm.htmleditor", {
    options: {
        editor: null
    },

    _create: function() {
        let self = this;
        setTimeout(function() {
            self.options.editor = CodeMirror.fromTextArea(self.element[0], {
                lineNumbers: true,
                mode: "htmlmixed",
                matchBrackets: true,
                autofocus: false,
                //direction: (asm.locale == "ar" || asm.locale == "he") ? "rtl" : "ltr",
                extraKeys: {
                    "F11": function(cm) {
                        self.fullscreen(cm, !cm.getOption("fullScreen"));
                    },
                    "Shift-Ctrl-F": function(cm) {
                        self.fullscreen(cm, !cm.getOption("fullScreen"));
                    },
                    "Esc": function(cm) {
                        self.fullscreen(cm, false);
                    }
                }
            });
            // Override height and width if they were set as attributes of the text area
            if (self.element.attr("data-width")) {
                self.element.next().css("width", self.element.attr("data-width"));
            }
            if (self.element.attr("data-height")) {
                self.element.next().css("height", self.element.attr("data-height"));
            }
            // When the editor loses focus, update the original textarea element
            self.options.editor.on("blur", function() {
                self.change();
            });

        }, 1000);
    },

    append: function(s) {
        this.options.editor.setValue(this.options.editor.getValue() + s);
    },

    change: function() {
        this.element.val( this.options.editor.getValue() );
    },

    destroy: function() {
        try {
            this.options.editor.destroy();
        }
        catch (err) {}
    },

    fullscreen: function(cm, fs) {
        // FIX FOR CHROME: If this code editor is inside a jquery dialog, Chrome will not render
        // the portion of the editor that is outside the dialog when it goes fullscreen.
        // To work around this, we record the position, height and width of the dialog before
        // going into fullscreen, make the dialog fill the screen and then restore it 
        // when leaving fullscreen as a workaround.
        let dlg = this.element.closest("div.ui-dialog");
        if (dlg) {
            if (fs) {
                this.dlgheight = dlg.height(); this.dlgwidth = dlg.width(); this.dlgtop = dlg.position().top; this.dlgleft = dlg.position().left;
                dlg.height("100%"); dlg.width("100%"); dlg.css("top", 0); dlg.css("left", 0);
            }
            else {
                dlg.height(this.dlgheight); dlg.width(this.dlgwidth); dlg.css("top", this.dlgtop); dlg.css("left", this.dlgleft);
            }
        }
        // END CHROME FIX
        cm.setOption("fullScreen", fs);
    },

    refresh: function() {
        this.options.editor.refresh();
    },

    value: function(newval) {
        if (newval === undefined) {
            return this.options.editor.getValue();
        }
        if (!newval) { newval = ""; }
        this.options.editor.setValue(newval);
        this.options.editor.refresh();
        this.change();
    }

});


$.widget("asm.sqleditor", {
    options: {
        editor: null
    },

    _create: function() {
        let self = this;
        setTimeout(function() {
            self.options.editor = CodeMirror.fromTextArea(self.element[0], {
                lineNumbers: true,
                mode: "text/x-sql",
                matchBrackets: true,
                autofocus: false,
                //direction: (asm.locale == "ar" || asm.locale == "he") ? "rtl" : "ltr",
                extraKeys: {
                    "F11": function(cm) {
                        self.fullscreen(cm, !cm.getOption("fullScreen"));
                    },
                    "Shift-Ctrl-F": function(cm) {
                        self.fullscreen(cm, !cm.getOption("fullScreen"));
                    },
                    "Esc": function(cm) {
                        self.fullscreen(cm, false);
                    },
                    "Ctrl-Space": "autocomplete"
                },
                hintOptions: { tables: schema }
            });
            // Override height and width if they were set as attributes of the text area
            if (self.element.attr("data-width")) {
                self.element.next().css("width", self.element.attr("data-width"));
            }
            if (self.element.attr("data-height")) {
                self.element.next().css("height", self.element.attr("data-height"));
            }
            // When the editor loses focus, update the original textarea element
            self.options.editor.on("blur", function() {
                self.change();
            });

        }, 1000);
    },

    append: function(s) {
        this.options.editor.setValue(this.options.editor.getValue() + s);
    },

    change: function() {
        this.element.val( this.options.editor.getValue() );
    },

    destroy: function() {
        try {
            this.options.editor.destroy();
        }
        catch (err) {}
    },

    fullscreen: function(cm, fs) {
        // FIX FOR CHROME: If this code editor is inside a jquery dialog, Chrome will not render
        // the portion of the editor that is outside the dialog when it goes fullscreen.
        // To work around this, we record the position, height and width of the dialog before
        // going into fullscreen, make the dialog fill the screen and then restore it 
        // when leaving fullscreen as a workaround.
        let dlg = this.element.closest("div.ui-dialog");
        if (dlg.length > 0) {
            if (fs) {
                this.dlgheight = dlg.height(); this.dlgwidth = dlg.width(); this.dlgtop = dlg.position().top; this.dlgleft = dlg.position().left;
                dlg.height("100%"); dlg.width("100%"); dlg.css("top", 0); dlg.css("left", 0);
            }
            else {
                dlg.height(this.dlgheight); dlg.width(this.dlgwidth); dlg.css("top", this.dlgtop); dlg.css("left", this.dlgleft);
            }
        }
        // END CHROME FIX
        cm.setOption("fullScreen", fs);
    },

    refresh: function() {
        this.options.editor.refresh();
    },

    value: function(newval) {
        if (newval === undefined) {
            return this.options.editor.getValue();
        }
        if (!newval) { newval = ""; }
        this.options.editor.setValue(newval);
        this.options.editor.refresh();
        this.change();
    }

});


// Styles a textbox that should only contain currency
$.fn.currency = function(cmd, newval) {
    const reset = function(b) {
        // Show a currency symbol and default amount of 0
        if ($(b).val() == "") {
            $(b).val(format.currency(0));
        }
    };
    if (cmd === undefined) {
        const allowed = [ '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', asm.currencyradix, '-' ];
        this.each(function() {
            let t = $(this);
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
            reset(this);
        });
    }
    else if (cmd == "reset") {
        this.each(function() {
            reset(this);
        });
    }
    else if (cmd == "value") {
        if (newval === undefined) {
            // Get the value
            let v = this.val();
            if (!v) { return 0; }
            return format.currency_to_int(v);
        }
        // We're setting the value
        this.each(function() {
            $(this).val(format.currency(newval));
        });
    }
};

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
