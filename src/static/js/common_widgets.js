/*global $, console, jQuery, CodeMirror, Mousetrap, tinymce */
/*global asm, common, config, dlgfx, edit_header, format, html, header, log, schema, validate, _, escape, unescape */
/*global MASK_VALUE: true */

"use strict";

// String shown in asm-mask fields instead of the value
const MASK_VALUE = "****************";

// Generates a javascript object of parameters by looking
// at the data attribute of all items matching the
// selector
$.fn.toJSON = function() {
    var params = {};
    this.each(function() {
        var t = $(this);
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
        var n = $(this);
        var f = $(this).attr("data-json");
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
        else if (n.is("textarea")) {
            n.html(row[f]);
        }
        else if (n.attr("type") == "checkbox") {
            n.prop("checked", row[f] == 1);
        }
        else if (n.hasClass("asm-bsmselect")) {
            n.children().prop("selected", false);
            $.each(String(row[f]).split(/[|,]+/), function(mi, mv) {
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
    var post = [];
    this.each(function() {
        var t = $(this);
        var pname = t.attr("data-post");
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
    var ids = "";
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
$.fn.table = function(options) {
    var defaults = {
        css:        'asm-table',
        filter:     false,
        style_td:   true,
        row_hover:  true,
        row_select: true,
        sticky_header: true
    };
    options = $.extend(defaults, options);
    return this.each(function () {
        var input = $(this);
        input.addClass(options.css);
        if (options.row_hover) {
            input.on("mouseover", "tr", function() {
                $(this).children("td").addClass("ui-state-hover");
            });
            input.on("mouseout", "tr", function() {
                $(this).children("td").removeClass("ui-state-hover");
            });
        }
        if (options.row_select) {
            input.on("click", "input:checkbox", function() {
                if ($(this).is(":checked")) {
                    $(this).closest("tr").find("td").addClass("ui-state-highlight");
                }
                else {
                    $(this).closest("tr").find("td").removeClass("ui-state-highlight");
                }
            });
        }
        input.find("th").addClass("ui-state-default");
        if (options.style_td) {
            input.prop("data-style-td", "true");
            input.find("td").addClass("ui-widget-content");
        }
        input.addClass("tablesorter");
        var tablewidgets = [];
        if (options.filter) { tablewidgets.push("filter"); }
        if (options.sticky_header && config.bool("StickyTableHeaders")) { tablewidgets.push("stickyHeaders"); }
        input.tablesorter({
            sortColumn: options.sortColumn,
            sortList: options.sortList,
            widgets: tablewidgets,
            filter_columnFilters: options.filter,
            filter_cssFilter: "tablesorter-filter",
            filter_ignoreCase: true,
            textExtraction: function(node, table, cellIndex) {
                // this function controls how text is extracted from cells for
                // sorting purposes.
                var s = common.trim($(node).text()), h = $(node).html();
                // If there's a data-sort attribute somewhere in the cell, use that
                if (h.indexOf("data-sort") != -1) {
                    var fq = h.indexOf("data-sort");
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
    });
};

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

// Textbox that should only contain numbers.
// data-min and data-max attributes can be used to contain the lower/upper bound
$.fn.number = function() {
    var allowed = [ '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', '-' ];
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
        $(this).keypress(function(e) {
            var k = e.charCode || e.keyCode;
            var ch = String.fromCharCode(k);
            // Backspace, tab, ctrl, delete, arrow keys ok
            if (k == 8 || k == 9 || k == 17 || k == 46 || (k >= 35 && k <= 40)) {
                return true;
            }
            if ($.inArray(ch, allowed) == -1) {
                e.preventDefault();
            }
        });
    });
};

// Textbox that should only contain numbers and letters (no spaces or punctuation)
$.fn.alphanumber = function() {
    this.each(function() {
        $(this).keydown(function(e) {
            if (!(e.keyCode == 8 // backspace
                || e.keyCode == 9 // tab
                || e.keyCode == 17 // ctrl
                || e.keyCode == 46 // delete
                || e.keyCode == 190 // point
                || e.keyCode == 110 // point
                || (e.keyCode >= 65 && e.keyCode <= 90) // capitals
                || (e.keyCode >= 97 && e.keyCode <= 122) // lower case
                || (e.keyCode >= 35 && e.keyCode <= 40) // arrow keys/home
                || (!e.shiftKey && e.keyCode >= 48 && e.keyCode <= 57) // numbers on keyboard
                || (e.keyCode >= 96 && e.keyCode <= 105) // numbers on keypad
            )) {
                e.preventDefault();
            }
        });
    });
};

// Textbox that should only contain integer numbers
$.fn.intnumber = function() {
    var allowed = [ '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '-' ];
    this.each(function() {
        $(this).keypress(function(e) {
            var k = e.charCode || e.keyCode;
            var ch = String.fromCharCode(k);
            // Backspace, tab, ctrl, arrow keys ok
            // (note: little delete key is code 46, shared with decimal point
            //  so we do not allow it here)
            if (k == 8 || k == 9 || k == 17 || (k >= 35 && k <= 40)) {
                return true;
            }
            if ($.inArray(ch, allowed) == -1) {
                e.preventDefault();
            }
        });
    });
};

// Textbox that should only contain CIDR IP subnets or IPv6 HEX/colon
$.fn.ipnumber = function() {
    var allowed = [ '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', '/', ' ', 'a', 'b', 'c', 'd', 'e', 'f', ':' ];
    this.each(function() {
        $(this).keypress(function(e) {
            var k = e.charCode || e.keyCode;
            var ch = String.fromCharCode(k);
            // Backspace, tab, ctrl, delete, arrow keys ok
            if (k == 8 || k == 9 || k == 17 || k == 46 || (k >= 35 && k <= 40)) {
                return true;
            }
            if ($.inArray(ch, allowed) == -1) {
                e.preventDefault();
            }
        });
    });
};

$.fn.date = function() {
    this.each(function() {
        var dayfilter = $(this).attr("data-onlydays");
        var nopast = $(this).attr("data-nopast");
        if (dayfilter) {
            $(this).datepicker({ 
                changeMonth: true, 
                changeYear: true,
                firstDay: config.integer("FirstDayOfWeek"),
                yearRange: "-30:+10",
                beforeShowDay: function(a) {
                    var day = a.getDay();
                    var rv = false;
                    $.each(dayfilter.split(","), function(i, v) {
                        if (v == String(day)) {
                            rv = true;
                        }
                        return false;
                    });
                    if (nopast && a < new Date()) { rv = false; }
                    return [rv, ""];
                }
            });
        }
        else {
            $(this).datepicker({ 
                changeMonth: true, 
                changeYear: true,
                yearRange: "-30:+10",
                firstDay: config.integer("FirstDayOfWeek")
            });
        }
        $(this).keydown(function(e) {
            var d = $(this);
            var adjust = function(v) {
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
};

// Textbox that should only contain a time (numbers and colon)
$.fn.time = function() {
    var allowed = [ '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':' ];
    this.each(function() {
        var t = $(this);
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
        $(this).keypress(function(e) {
            var k = e.charCode || e.keyCode;
            var ch = String.fromCharCode(k);
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
    });
};

// Select box
$.fn.select = function(method, newval) {
    var rv = "", tv;
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
        var li = $( "<li>" ),
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
            '<td><label for="emailfrom">' + _("From") + '</label></td>',
            '<td><input id="emailfrom" data="from" type="text" class="asm-doubletextbox" /></td>',
            '</tr>',
            '<tr>',
            '<td><label for="emailto">' + _("To") + '</label></td>',
            '<td><input id="emailto" data="to" type="text" class="asm-doubletextbox" /></td>',
            '</tr>',
            '<tr>',
            '<td><label for="emailcc">' + _("CC") + '</label></td>',
            '<td><input id="emailcc" data="cc" type="text" class="asm-doubletextbox" /></td>',
            '</tr>',
            '<tr>',
            '<td><label for="emailbcc">' + _("BCC") + '</label></td>',
            '<td><input id="emailbcc" data="bcc" type="text" class="asm-doubletextbox" /></td>',
            '</tr>',
            '<tr>',
            '<td><label for="emailsubject">' + _("Subject") + '</label></td>',
            '<td><input id="emailsubject" data="subject" type="text" class="asm-doubletextbox" /></td>',
            '</tr>',
            '<tr>',
            '<td></td>',
            '<td><input id="emailaddtolog" data="addtolog" type="checkbox"',
            'title="' + html.title(_("Add details of this email to the log after sending")) + '" ',
            'class="asm-checkbox" /><label for="emailaddtolog">' + _("Add to log") + '</label>',
            '<select id="emaillogtype" data="logtype" class="asm-selectbox">',
            '</select>',
            '</td>',
            '</tr>',
            '</table>',
            '<div id="emailbody" data="body" data-margin-top="24px" data-height="300px" class="asm-richtextarea"></div>',
            '<p>',
            '<label for="emailtemplate">' + _("Template") + '</label>',
            '<select id="emailtemplate" class="asm-selectbox">',
            '<option value=""></option>',
            '</select>',
            '</p>',
            '</div>'
        ].join("\n"));
        $("#emailbody").richtextarea();
        var b = {}; 
        b[_("Send")] = {
            text: _("Send"),
            "class": "asm-dialog-actionbutton",
            click: function() { 
                if (!validate.email($("#emailfrom").val())) { return; }
                if (!validate.email($("#emailto").val())) { return; }
                if ($("#emailcc").val() != "" && !validate.email($("#emailcc").val())) { return; }
                if ($("#emailbcc").val() != "" && !validate.email($("#emailbcc").val())) { return; }
                let o = self.options.o;
                if (o.formdata) { o.formdata += "&"; }
                o.formdata += $("#dialog-email input, #dialog-email select, #dialog-email .asm-richtextarea").toPOST();
                header.show_loading(_("Sending..."));
                common.ajax_post(o.post, o.formdata, function() {
                    var recipients = $("#emailto").val();
                    if ($("#emailcc").val() != "") { recipients += ", " + $("#emailcc").val(); }
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
        $("#emailtemplate").change(function() {
            let o = self.options.o;
            let formdata = "mode=emailtemplate&dtid=" + $("#emailtemplate").val();
            if (o.donationids) { formdata += "&donationids=" + o.donationids; }
            if (o.personid) { formdata += "&personid=" + o.personid; }
            if (o.animalid) { formdata += "&animalid=" + o.animalid; }
            header.show_loading(_("Loading..."));
            common.ajax_post("document_gen", formdata, function(result) {
                $("#emailbody").html(result); 
            });
        });

    },

    destroy: function() {
        common.widget_destroy("#dialog-email", "dialog"); 
        common.widget_destroy("#emailbody", "richtextarea");
    },
    
    /**
     * Shows the email dialog.
     * title:      The dialog title (optional: Email person)
     * post:       The ajax post target
     * formdata:   The first portion of the formdata
     * name:       The name to show on the form (optional)
     * email:      The email to show on the form (optional)
     * subject:    The default subject (optional)
     * message:    The default message (otpional)
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
            $("#emaillogtype").append( html.list_to_options(o.logtypes, "ID", "LOGTYPENAME") );
            $("#emaillogtype").select("value", config.integer("AFDefaultLogType"));
        }
        else {
            $("#emaillogtype").closest("tr").hide();
        }
        if (o.templates) {
            $("#emailtemplate").html( edit_header.template_list_options(o.templates) );
        }
        else {
            $("#emailtemplate").closest("tr").hide();
        }
        let fromaddresses = [], toaddresses = [];
        let conf_org = html.decode(config.str("Organisation").replace(",", ""));
        let conf_email = config.str("EmailAddress");
        let org_email = conf_org + " <" + conf_email + ">";
        $("#emailfrom").val(conf_email);
        fromaddresses.push(conf_email);
        fromaddresses.push(org_email);
        if (asm.useremail) {
            fromaddresses.push(asm.useremail);
            fromaddresses.push(html.decode(asm.userreal) + " <" + asm.useremail + ">");
        }
        fromaddresses.push(config.str("EmailFromAddresses").split(","));
        toaddresses = config.str("EmailToAddresses").split(",");
        $("#emailfrom").autocomplete({source: fromaddresses});
        $("#emailfrom").autocomplete("widget").css("z-index", 1000);
        $("#emailto").autocomplete({source: toaddresses});
        $("#emailto").autocomplete("widget").css("z-index", 1000);
        $("#emailcc").autocomplete({source: toaddresses});
        $("#emailcc").autocomplete("widget").css("z-index", 1000);
        $("#emailbcc").autocomplete({source: toaddresses});
        $("#emailbcc").autocomplete("widget").css("z-index", 1000);
        $("#emailfrom, #emailto, #emailcc, #emailbcc").bind("focus", function() {
            $(this).autocomplete("search", "@");
        });
        if (o.email && o.email.indexOf(",") != -1) { 
            // If there's more than one email address, only output the comma separated emails
            $("#emailto").val(o.email); 
        }
        else if (o.email) { 
            // Otherwise, use RFC821
            $("#emailto").val(common.replace_all(html.decode(o.name), ",", "") + " <" + o.email + ">"); 
        }
        let msg = config.str("EmailSignature");
        if (o.message) { msg = "<p>" + o.message + "</p>" + msg; }
        else { msg = "<p>&nbsp;</p>" + msg; }
        if (msg) {
            $("#emailbody").richtextarea("value", msg);
        }
        if (o.subject) {
            $("#emailsubject").val(o.subject); 
        }
        $("#emailaddtolog").prop("checked", true);
        $("#emailsubject").focus();
    }
});

$.widget("asm.latlong", {
    options: {
        lat: null,
        lng: null,
        hash: null
    },
    _create: function() {
        var self = this;
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
        var bits = this.element.val().split(",");
        if (bits.length > 0) { this.options.lat.val(bits[0]); }
        if (bits.length > 1) { this.options.lng.val(bits[1]); }
        if (bits.length > 2) { this.options.hash.val(bits[2]); }
    },
    save: function() {
        // Store the entered values back in the base element value
        var v = this.options.lat.val() + "," +
            this.options.lng.val() + "," +
            this.options.hash.val();
        this.element.val(v);
    }
});

/**
 * Widget to take one or more payments.
 * Relies on controller.accounts, controller.paymenttypes and controller.donationtypes
 * target should be a container div
 */
$.widget("asm.payments", {
    options: {
        count: 0,
        controller: null,
        giftaid: false
    },
    _create: function() {
        var self = this;
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
            '<td><button class="takepayment">' + _("Take another payment") + '</button>',
            '<a class="takepayment" href="#">' + _("Take another payment") + '</a></td>',
            '<td class="overridedates"></td>',
            '<td class="overridedates"></td>',
            '<td></td>',
            '<td></td>',
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
        var h = [
            '<tr>',
            '<td>',
            '<select id="donationtype{i}" data="donationtype{i}" class="asm-selectbox">',
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
            html.list_to_options(this.options.controller.paymenttypes, "ID", "PAYMENTNAME"),
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
            '<select id="destaccount{i}" data="destaccount{i}" class="asm-selectbox">',
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
            '<input id="vatrate{i}" data="vatrate{i}" class="rightalign asm-textbox asm-halftextbox asm-numberbox" value="0" /> %',
            '<input id="vatamount{i}" data="vatamount{i}" class="rightalign vatamount asm-textbox asm-halftextbox asm-currencybox" value="0" />',
            '</span>',
            '</td>',
            '<td>',
            '<input id="comments{i}" data="comments{i}" class="asm-textbox" />',
            '</td>',
            '</tr>'
        ];
        // Construct and add our new payment fields to the DOM
        this.options.count += 1;
        var i = this.options.count, self = this;
        this.element.find("#paymentlines").append(common.substitute(h.join("\n"), {
            i: this.options.count
        }));
        // Remove any retired payment types and methods
        $("#donationtype" + i).select("removeRetiredOptions", "all");
        $("#payment" + i).select("removeRetiredOptions", "all");
        // Change the default amount when the payment type changes
        $("#donationtype" + i).change(function() {
            var dc = common.get_field(self.options.controller.donationtypes, $("#donationtype" + i).select("value"), "DEFAULTCOST");
            var dv = common.get_field(self.options.controller.donationtypes, $("#donationtype" + i).select("value"), "ISVAT");
            $("#quantity" + i).val("1");
            $("#unitprice" + i).currency("value", dc);
            $("#amount" + i).currency("value", dc);
            $("#vat" + i).prop("checked", dv == 1);
            $("#vat" + i).change();
            self.update_totals();
        });
        // Recalculate when quantity or unit price changes
        $("#quantity" + i + ", #unitprice" + i).change(function() {
            var q = $("#quantity" + i).val(), u = $("#unitprice" + i).currency("value");
            $("#amount" + i).currency("value", q * u);
            self.update_totals();
        });
        // Recalculate when amount or VAT changes
        $("#amount" + i + ", #vatamount" + i).change(function() {
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
                $("#vatboxes" + i).fadeIn();
            }
            else {
                $("#vatrate" + i + ", #vatamount" + i).val("0");
                $("#vatboxes" + i).fadeOut();
            }
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
        var totalamt = 0, totalvat = 0, totalall = 0;
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
        var self = this;
        var button = this.element;
        this.options.button = this.element;
        var popupid = this.element.attr("id") + "-popup";

        // Read the elements inner content then remove it
        var content = button.html();
        button.html("");

        // Style the button by adding an actual button with icon
        button.append(html.icon("callout"));

        // Create the callout
        $("#asm-content").append('<div id="' + popupid + '">' + html.info(content) + '</div>');
        var popup = $("#" + popupid);
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
        this.options.popup.remove();
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
        var self = this;
        var button = this.element;
        this.options.button = button;
        
        // Add display arrow span
        var n = "<span style=\"display: inline-block; width: 16px; height: 16px; vertical-align: middle\" class=\"ui-button-text ui-icon ui-icon-triangle-1-e\"></span>";
        this.element.append(n);
        
        // If the menu is empty, disable it
        var id = this.element.attr("id");
        var body = $("#" + id + "-body");
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
                var t = $(e.target);
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
        var button = "#" + id;
        var body = "#" + id + "-body";
        var topval = $(button).offset().top + $(button).height() + 14;
        var leftval = $(button).offset().left;

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
        var wasactive = $(body).css("display") != "none";
        
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
        var self = this;
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
 *  to work inside a JQuery UI dialog */
$.widget("ui.dialog", $.ui.dialog, {
    _allowInteraction: function(event) {
        return !!$(event.target).closest(".mce-container").length || this._super( event );
    }
});

$.widget("asm.richtextarea", {

    options: {
        editor: null
    },

    _create: function() {
        var self = this;
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
                "insertdatetime media nonbreaking table contextmenu directionality",
                "emoticons template paste textcolor"
                ],
            theme: "modern",
            inline: true,
            menubar: false,
            statusbar: false, 
            add_unload_trigger: false,

            toolbar_items_size: "small",
            toolbar: "undo redo | fontselect fontsizeselect | bold italic underline forecolor backcolor | alignleft aligncenter alignright alignjustify | bullist numlist | link image | code",

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
            }

        });
    },

    destroy: function() {
        tinymce.get(this.element.attr("id")).remove();
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
        
        var buttonstyle = "margin-left: -56px; margin-top: -24px; height: 16px",
            fixmarginstyle = "margin-left: 32px; margin-top: 24px;",
            t = $(this.element[0]),
            self = this;

        if (t.attr("data-zoom")) { return; }
        if (!t.attr("id")) { return; }

        t.attr("data-zoom", "true");
        var zbid = t.attr("id") + "-zb";

        t.wrap("<span style='white-space: nowrap'></span>");
        t.after("<button id='" + zbid + "' style='" + buttonstyle + "'></button>" + "<span style='" + fixmarginstyle + "'></span>");

        // When zoom button is clicked
        $("#" + zbid).button({ text: false, icons: { primary: "ui-icon-zoomin" }}).click(function() {
            self.zoom();
            return false; // Prevent any textareas in form elements submitting the form
        });

    },

    zoom: function() {
        var t = $(this.element[0]);

        if (t.is(":disabled")) { return; }
        if (t.attr("maxlength") !== undefined) { $("#textarea-zoom-area").attr("maxlength", t.attr("maxlength")); }

        $("#textarea-zoom-id").val( t.attr("id") );
        $("#textarea-zoom-area").val( t.val() );
        $("#textarea-zoom-area").css({ "font-family": t.css("font-family") });

        var title = "";
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
        var self = this;
        setTimeout(function() {
            self.options.editor = CodeMirror.fromTextArea(self.element[0], {
                lineNumbers: true,
                mode: "htmlmixed",
                matchBrackets: true,
                autofocus: false,
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
        this.options.editor.destroy();
    },

    fullscreen: function(cm, fs) {
        // FIX FOR CHROME: If this code editor is inside a jquery dialog, Chrome will not render
        // the portion of the editor that is outside the dialog when it goes fullscreen.
        // To work around this, we record the position, height and width of the dialog before
        // going into fullscreen, make the dialog fill the screen and then restore it 
        // when leaving fullscreen as a workaround.
        var dlg = this.element.closest("div.ui-dialog");
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
        var self = this;
        setTimeout(function() {
            self.options.editor = CodeMirror.fromTextArea(self.element[0], {
                lineNumbers: true,
                mode: "text/x-sql",
                matchBrackets: true,
                autofocus: false,
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
        this.options.editor.destroy();
    },

    fullscreen: function(cm, fs) {
        // FIX FOR CHROME: If this code editor is inside a jquery dialog, Chrome will not render
        // the portion of the editor that is outside the dialog when it goes fullscreen.
        // To work around this, we record the position, height and width of the dialog before
        // going into fullscreen, make the dialog fill the screen and then restore it 
        // when leaving fullscreen as a workaround.
        var dlg = this.element.closest("div.ui-dialog");
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
    var reset = function(b) {
        // Show a currency symbol and default amount of 0
        if ($(b).val() == "") {
            $(b).val(format.currency(0));
        }
    };
    if (cmd === undefined) {
        var allowed = [ '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', asm.currencyradix, '-' ];
        this.each(function() {
            $(this).keypress(function(e) {
                var k = e.charCode || e.keyCode;
                var ch = String.fromCharCode(k);
                // Backspace, tab, ctrl, delete, arrow keys ok
                if (k == 8 || k == 9 || k == 17 || k == 46 || (k >= 35 && k <= 40)) {
                    return true;
                }
                if ($.inArray(ch, allowed) == -1) {
                    e.preventDefault();
                }
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
            var v = this.val(), f;
            if (!v) {
                return 0;
            }
            // Extract only the numbers, sign and decimal point
            f = format.currency_to_float(v) * 100;
            // Adding 0.5 corrects IEEE rounding errors in multiplication
            if (f > 0) { f += 0.5; }
            if (f < 0) { f -= 0.5; }
            return parseInt(f, 10);
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

