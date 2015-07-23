/*jslint browser: true, forin: true, eqeq: true, plusplus: true, white: true, regexp: true, sloppy: true, vars: true, nomen: true */
/*global $, console, jQuery */
/*global asm, common, config, dlgfx, format, html, header, validate, _, escape, unescape */

(function($) {

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
    // matching the selector
    $.fn.toPOST = function(includeblanks) {
        var post = "";
        this.each(function() {
            var t = $(this);
            var pname = t.attr("data-post");
            if (!pname) { pname = t.attr("data"); }
            if (!pname) { return; }
            if (t.attr("type") == "checkbox") {
                if (post != "") { post += "&"; }
                if (t.is(":checked")) {
                    post += pname + "=checked";   
                }
                else {
                    post += pname + "=off";
                }
            }
            else if (t.hasClass("asm-currencybox")) {
                if (post != "") { post += "&"; }
                post += pname + "=" + encodeURIComponent(t.currency("value"));
            }
            else if (t.val()) {
                if (post != "") { post += "&"; }
                post += pname + "=" + encodeURIComponent(t.val());
            }
            else if (includeblanks) {
                if (post != "") { post += "&"; }
                post += pname + "=" + encodeURIComponent(t.val());
            }
        });
        return post;
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
                textExtraction: function(node) {
                    // custom extraction function turns display dates 
                    // into iso dates behind the scenes for 
                    // alphanumeric sorting
                    var s = $(node).text();
                    if (s.split("/").length == 3) {
                        var rv = format.date_iso(s);
                        if (!rv) { return ""; }
                        rv = rv.replace(/\-/g, "").replace(/\:/g, "").replace("T", "");
                        return rv;
                    }
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

    // Textbox that should only contain numbers
    $.fn.number = function() {
        var allowed = [ '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.' ];
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
        var allowed = [ '0', '1', '2', '3', '4', '5', '6', '7', '8', '9' ];
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

    // Textbox that should only contain CIDR IP subnets
    $.fn.ipnumber = function() {
        var allowed = [ '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', '/', ' ' ];
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
                    firstDay: 1,
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
                    firstDay: 1
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
        var rv = "";
        if (method === undefined) {
            method = "create";
        }
        if (method == "create") {
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
        if (method == "firstvalue") {
            $(this).each(function() {
                $(this).val( $(this).find("option:first").val() );
            });
        }
        if (method == "value") {
            rv = "";
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
                    return;
                }
            });
            return rv;
        }
        if (method == "label") {
            rv = "";
            $(this).each(function() {
                rv = $(this).find("option:selected").html();    
            });
            return rv;
        }
        if (method == "disable") {
            $(this).each(function() {
                $(this).attr("disabled", "disabled");
            });
        }
        if (method == "enable") {
            $(this).each(function() {
                $(this).removeAttr("disabled");
            });
        }
    };

    /** 
     * JQuery UI select menu with custom rendering for icons
     */
    $.widget( "asm.iconselectmenu", $.ui.selectmenu, {
        _renderItem: function( ul, item ) {
            var li = $( "<li>", { text: item.label } );
            if ( item.disabled ) {
                li.addClass( "ui-state-disabled" );
            }
            $( "<span>", {
                "style": item.element.attr( "data-style" ),
                "class": "ui-icon asm-icon asm-icon-" + item.element.attr( "data-class" )
            }).appendTo( li );
            return li.appendTo( ul );
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
            var dialog = this.element;
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
                '<td><label for="emailsubject">' + _("Subject") + '</label></td>',
                '<td><input id="emailsubject" data="subject" type="text" class="asm-doubletextbox" /></td>',
                '</tr>',
                '<tr>',
                '<td></td>',
                '<td><input id="emailhtml" data="html" type="checkbox"',
                'title="' + html.title(_("Set the email content-type header to text/html")) + '" ',
                'class="asm-checkbox" /><label for="emailhtml">' + _("HTML") + '</label></td>',
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
                '<textarea id="emailbody" data="body" rows="15" class="asm-textarea"></textarea>',
                '</div>'
            ].join("\n"));
        },

        destroy: function() {
            common.widget_destroy("#dialog-email", "dialog"); 
        },
        
        /**
         * Shows the email dialog.
         * post:       The ajax post target
         * formdata:   The first portion of the formdata
         * name:       The name to show on the form
         * email:      The email to show on the form
         * logtypes:   The logtypes to populate the attach as log box
         *    Eg: show({ post: "person", formdata: "mode=email&personid=52", name: "Bob Smith", email: "bob@smith.com" })
         */
        show: function(o) {
            var b = {}; 
            b[_("Send")] = function() { 
                if (o.formdata) { o.formdata += "&"; }
                o.formdata += $("#dialog-email input, #dialog-email select, #dialog-email textarea").toPOST();
                common.ajax_post(o.post, o.formdata, function() { 
                    header.show_info(_("Message successfully sent"));
                    $("#dialog-email").dialog("close");
                });
            };
            b[_("Cancel")] = function() { $(this).dialog("close"); };
            $("#dialog-email").dialog({
                 resizable: false,
                 modal: true,
                 dialogClass: "dialogshadow",
                 width: 640,
                 show: dlgfx.add_show,
                 hide: dlgfx.add_hide,
                 buttons: b
            });
            if (o.logtypes) {
                $("#emaillogtype").append( html.list_to_options(o.logtypes, "ID", "LOGTYPENAME") );
            }
            var mailaddresses = [];
            var conf_org = html.decode(config.str("Organisation").replace(",", ""));
            var conf_email = config.str("EmailAddress");
            var org_email = conf_org + " <" + conf_email + ">";
            mailaddresses.push(org_email);
            $("#emailfrom").val(org_email);
            if (asm.useremail) {
                mailaddresses.push(html.decode(asm.userreal) + " <" + asm.useremail + ">");
            }
            $("#emailfrom").autocomplete({source: mailaddresses});
            $("#emailfrom").autocomplete("widget").css("z-index", 1000);
            $("#emailto").val(html.decode(o.name) + " <" + o.email + ">");
            var sig = config.str("EmailSignature");
            if (sig != "") {
                $("#emailbody").val(html.decode("\n--\n" + sig));
            }
            $("#emailsubject").focus();
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
            var n = "<span style=\"display: inline\" class=\"ui-button-text ui-icon ui-icon-triangle-1-e\">&nbsp;&nbsp;&nbsp;</span>";
            this.element.append(n);
            
            // If the menu is empty, disable it
            var id = this.element.attr("id");
            var body = $("#" + id + "-body");
            this.options.menu = body;
            if (body.find(".asm-menu-item").size() == 0) {
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
                $(body).css("z-index", "2 !important").slideDown();
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

    $.fn.textarea = function() {
        var pos = "left: -32px; top: -8px;";
        if (common.is_msie()) { pos = "left: -36px;"; }
        this.each(function() {
            var t = $(this);
            if (t.attr("data-zoom")) { return; }
            t.attr("data-zoom", "true");
            var zbid = t.attr("id") + "-zb";
            t.wrap("<span style='white-space: nowrap'></span>");
            t.after("<a style='position: relative; " + pos + " ' id='" + zbid + "' href='#'><span class='asm-icon asm-icon-edit'></span></a>");
            $("#" + zbid).click(function() {
                // If the textarea is disabled, don't do anything
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
            });
        });
    };

    // Styles a textbox that should only contain currency
    $.fn.currency = function(cmd, newval) {
        var reset = function(b) {
            // Show a currency symbol and default amount of 0
            if ($(b).val() == "") {
                $(b).val(format.currency(0));
            }
        };
        if (cmd === undefined) {
            var allowed = [ '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', '-' ];
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
            if (newval == undefined) {
                // Get the value
                var v = this.val(), f;
                if (!v) {
                    return 0;
                }
                // Extract only the numbers, sign and decimal point
                v = v.replace(/[^0123456789\-\.]/g, '');
                v = $.trim(v);
                f = parseFloat(v);
                f *= 100;
                // Adding 0.5 corrects IEEE rounding errors 
                if (f > 0) { f += 0.5; }
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
            $(this).parent().find("button").button("disable");
        });
    };

    // Helper to enable jquery ui dialog buttons
    $.fn.enable_dialog_buttons = function() {
        this.each(function() {
            $(this).parent().find("button").button("enable");
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
                $(this).delay(1).show("slide", {direction: 'up'});
                return;
            }
            if (type == "formtab") {
                $(this).delay(1).show("slide", {direction: 'right'});
                return;
            }
            if (type == "book") {
                $(this).delay(1).show("slide", {direction: 'down'});
                return;
            }
            if (type == "options") {
                $(this).delay(1).show("slide", {direction: 'up'});
                return;
            }
            // default
            $(this).delay(1).show("slide", {direction: 'left'});
        });
    };

} (jQuery));
