/*jslint browser: true, forin: true, eqeq: true, plusplus: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, console, jQuery, Mousetrap, Path */
/*global asm, header, _, escape, unescape */
/*global common: true, config: true, controller: true, dlgfx: true, format: true, html: true, tableform: true, validate: true */

(function($) {

    common = {

        substitute: function(str, sub) {
            /*jslint regexp: true */
            return str.replace(/\{(.+?)\}/g, function($0, $1) {
                return sub.hasOwnProperty($1) ? sub[$1] : $0;
            });
        },

        /**
         * Returns true if any element of array1 is present in array2
         */
        array_overlap: function(array1, array2) {
            var overlap = false;
            $.each(array1, function(i1, v1) {
                $.each(array2, function(i2, v2) {
                    if (v2 == v1) {
                        overlap = true;
                    }
                });
            });
            return overlap;
        },

        /**
         * Translates a phrase that deals with a number of
         * something so the correct plural can be used.
         * number: The number of items
         * translations: A list of translations for each plural form
         */
        ntranslate: function(number, translations) {
            // english
            var pluralfun = function(n) { if (n == 1) { return 0; } return 1; };
            // slavic languages
            if (asm.locale == "ru") {
                pluralfun = function(n) {
                    if (n % 10 == 1 && n % 100 != 11) { return 0; }
                    if (n % 10 >= 2 && n % 10 <= 4 && 
                        (n % 100 < 10 || n % 100 >= 20)) { return 1; }
                    return 2;
                };
            }
            var text = translations[pluralfun(number)];
            text = text.replace("{plural0}", number);
            text = text.replace("{plural1}", number);
            text = text.replace("{plural2}", number);
            text = text.replace("{plural3}", number);
            text = text.replace("{plural4}", number);
            return text;
        },

        console_log: function(str) {
            if (window.console) {
                console.log(str);
            }
        },

        cookie_set: function(name, value, days) {
            var expires = "";
            if (days) {
                var date = new Date();
                date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
                expires = "; expires=" + date.toGMTString();
            } 
            document.cookie = escape(name) + "=" + escape(value) + expires + "; path=/";
        },

        cookie_get: function(name) {
            var nameEQ = escape(name) + "=",
                ca = document.cookie.split(';'),
                i = 0;
            for (i = 0; i < ca.length; i++) {
                var c = ca[i];
                while (c.charAt(0) == ' ') {
                    c = c.substring(1, c.length);
                }
                if (c.indexOf(nameEQ) == 0) {
                    return unescape(c.substring(nameEQ.length, c.length));
                }
            }
            return null;
        },

        cookie_delete: function(name) {
            this.cookie_set(name, "", -1);
        },

        current_url: function() {
            return String(window.location);
        },

        /**
         * Returns a querystring parameter value from the current url
         * or empty string if not present.
         */
        querystring_param: function(param) {
            return common.url_param(common.current_url(), param);
        },

        url_param: function(s, param) {
            var p = s.indexOf(param + "=");
            if (p == -1) { return ""; }
            var e = s.indexOf("&", p);
            if (e == -1) { e = s.length; }
            return s.substring(p + param.length + 1, e);
        },

        /**
         * Get a value from HTML5 local storage. Returns empty string
         * if the value is not set or local storage not available.
         */
        local_get: function(name) {
            if (typeof(Storage) === "undefined") { return ""; }
            if (localStorage[name]) { return localStorage[name]; }
            return "";
        },

        /**
         * Sets a value in HTML5 local storage. Value must be a string.
         */
        local_set: function(name, value) {
            if (typeof(Storage) !== "undefined") {
                localStorage[name] = value;
            }
        },

        /**
         * Deletes a value from HTML5 local storage if it exists
         */
        local_delete: function(name) {
            if (typeof(Storage) !== "undefined") {
                try {
                    localStorage.removeItem(name); 
                }
                catch (ex) {}
            }
        },

        /**
         * Returns true if v is an array
         */
        is_array: function(v) {
            return v instanceof Array || Object.prototype.toString.call(v) === '[object Array]';
        },

        /**
         * Returns true if v is a date or a string containing an ISO date
         */
        is_date: function(v) {
            if (!v) { return false; }
            if (v instanceof Date) { return true; }
            if (common.is_string(v) && v.length == 19 && v.indexOf("T") == 10) { return true; }
            return false;
        },

        /** 
         * Returns true if v is a string
         */
        is_string: function(v) {
            return v instanceof String || typeof(v) == "string";
        },

        /**
         * Returns true if the useragent is for an apple idevice
         */
        is_idevice: function() {
            return navigator.userAgent.toLowerCase().indexOf("ipod") != -1 || 
                navigator.userAgent.toLowerCase().indexOf("ipad") != -1 ||
                navigator.userAgent.toLowerCase().indexOf("iphone") != -1;
        },

        is_safari: function() {
            return navigator.userAgent.toLowerCase().indexOf("safari") != -1;
        },
        
        is_opera: function() {
            return navigator.userAgent.toLowerCase().indexOf("opera") != -1;
        },

        is_msie: function() {
            return navigator.userAgent.toLowerCase().indexOf("msie") != -1 ||
                navigator.userAgent.toLowerCase().indexOf("trident") != -1;
        },

        msie_version: function() {
            var v = 999;
            if (navigator.appVersion.indexOf("MSIE") != -1) {
                v = parseFloat(navigator.appVersion.split("MSIE")[1]);
            }
            return v;
        },

        has_permission: function(flag) {
            if (asm.superuser) { return true; }
            if (asm.securitymap.indexOf(flag + " ") != -1) { return true; }
            return false;
        },

        nulltostr: function(s) {
            if (s === undefined) { return ""; }
            if (s == null) { return ""; }
            return s;
        },

            // Safari doesn't parse the response text correctly, so
            // it ends up as "Internal Server Error" instead of the message.
            // parse the responseText instead to work in all browsers.

        /** 
         * Used for reading the error message from an AJAX response. 
         * We have this because Safari seems to end up with "Internal Server Error"
         * as the response variable instead of the real error message.
         */
        get_error_response: function(jqxhr, response) {
            var errmessage = String(response);
            if (response.indexOf("Internal Server") != -1) {
                errmessage = jqxhr.responseText;
                if (errmessage.indexOf("<p>") != -1) {
                    errmessage = errmessage.substring(errmessage.indexOf("<p>")+3, errmessage.indexOf("</p>")+4);
                }
            }
            return errmessage;
        },

        /** Returns a javascript date object representing today without time info */
        today_no_time: function() {
            var d = new Date();
            return new Date(d.getFullYear(), d.getMonth(), d.getDate(), 0, 0, 0);
        },

        /** Adds days to date */
        add_days: function(date, days) {
            var d = new Date();
            d.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
            return d;
        },

        /** Subtracts days from date */
        subtract_days: function(date, days) {
            var d = new Date();
            d.setTime(date.getTime() + 60 - (days * 24 * 60 * 60 * 1000));
            return d;
        },

        /** URL routing mode - client or server */
        route_mode: "client",

        /** Go to a URL */
        route: function(path) {
            if (common.route_mode == "server") { window.location = path; return; }
            Path.history.pushState({}, "", path);
        },

        /** Given a url encoded string a, returns a dictionary of the elements */
        route_criteria: function(a) {
            var i = 0, b = {};
            if (!a) { return {}; }
            $.each(a.split("&"), function(i, v) {
                var x = v.split("=");
                b[x[0]] = decodeURIComponent(x[1].replace(/\+/g, " "));
            });
            return b;
        },

        /** Starts client side routing listening */
        route_listen: function() {
            // Don't do anything if we're in server mode, we'll just visit
            // each URL on the server instead of trying to match routes on the
            // client and deal with them here.
            if (common.route_mode == "server") { return; }
            // Add a rescue route - if we can't find matching client route,
            // we fall back to going to the server for it
            Path.rescue(function(path) {
                window.location = path;
            });
            // Listen for history state changes
            Path.history.listen(true);
            // Catch all clicks for "real" URLs (ones without hashes) 
            // and use client side routing to handle them.
            $(document).on("click", "a", function(event) {
                // If dirty validation is active, check if we're
                // ok to leave.
                if (validate.active) {
                    if (!validate.a_click_handler(event, $(this).attr("href"))) {
                        return false;
                    }
                }
                var href = $(this).attr("href");
                if (href && href.indexOf("#") == -1) {
                    event.preventDefault();
                    Path.history.pushState({}, "", href);
                }
            });
        },

        /** Reload the current route */
        route_reload: function() {
            if (common.route_mode == "server") { window.location.reload(); return; }
            Path.reload();
        },

        /** Loaded modules */
        modules: {},

        /** Currently running module */
        module_running: null,
 
        /**
         * Registers a module.
         * o: The module object, implementing render, bind and sync
         */
        module_register: function(o) {
            common.modules[o.name] = o;
            if (o.routes) { 
                $.each(o.routes, function(k, v) {
                    Path.map(k).to(v);
                });
            }
        },

        /**
         * Loads the data for a module into the global controller
         * object (from uri) and then starts it.
         */
        module_loadandstart: function(modulename, uri) {
            // do we already have one running? If so, try to unload it first
            if (common.module_running) {
                if (common.module_running.destroy) {
                    if (common.module_running.destroy()) {
                        return;
                    }
                }
            }
            // add a json parameter to only retrieve the controller json document
            if (uri.indexOf("?") == -1) { uri += "?json=true"; }
            else { uri += "&json=true"; }
            header.show_loading(_("Loading..."));
            $.ajax({
                type: "GET",
                url: uri,
                dataType: "text",
                mimeType: "textPlain",
                success: function(result) {
                    controller = jQuery.parseJSON(result);
                    try {
                        // This can cause an error if the dialog wasn't open
                        header.hide_loading();
                    }
                    catch (ex) {}
                    // Start the module
                    common.module_start(modulename);
                },
                error: function(jqxhr, textstatus, response) {
                    try {
                        // This can cause an error if the dialog wasn't open
                        header.hide_loading();
                    }
                    catch (ex) {}
                    var errmessage = common.get_error_response(jqxhr, response);
                    header.show_error(errmessage);
                }
            });
        },

        /**
         * Starts a module, unloading any active module first.
         */
        module_start: function(modulename) {
            // do we already have one running? If so, try to unload it first
            if (common.module_running) {
                if (common.module_running.destroy) {
                    if (common.module_running.destroy()) {
                        return;
                    }
                }
            }
            var o = common.modules[modulename];
            if (o.render) { $("#asm-body-container").empty(); $("#asm-body-container").html(o.render()); }
            common.bind_widgets();
            if (o.bind) { o.bind(); }
            if (o.sync) { o.sync(); }
            if (o.title) { $(document).attr("title", o.title()); }
            common.apply_label_overrides(modulename); 
            $("#asm-content").asmcontent(o.animation);
            common.module_running = o;
        },

        /**
         * Performs an AJAX POST for text response, handling errors
         * action: The url to post to
         * formdata: The formdata as a string
         * successfunc: The callback function (will pass response)
         * errorfunc: The callback function on error (will include response)
         */
        ajax_post: function(action, formdata, successfunc, errorfunc) {
            var st = new Date().getTime();
            $.ajax({
                type: "POST",
                url: action,
                data: formdata,
                dataType: "text",
                mimeType: "textPlain",
                success: function(result) {
                    try {
                        // This can cause an error if the dialog wasn't open
                        header.hide_loading();
                    }
                    catch (ex) {}
                    if (successfunc) {
                        successfunc(result, new Date().getTime() - st);
                    }
                },
                error: function(jqxhr, textstatus, response) {
                    try {
                        // This can cause an error if the dialog wasn't open
                        header.hide_loading();
                    }
                    catch (ex) {}
                    var errmessage = common.get_error_response(jqxhr, response);
                    header.show_error(errmessage);
                    if (errorfunc) {
                        errorfunc(errmessage);
                    }
                }
            });
        },

        /**
         * Returns the field value in rows for id given. 
         * rows: The object to search in
         * id: The ID field value to find
         * field: The field value to return
         */
        get_field: function(rows, id, field) {
            var rv = "";
            $.each(rows, function(i, v) {
                if (v.ID == id) {
                    rv = v[field];
                    return false;
                }
            });
            return rv;
        },

        /**
         * Returns the row in rows for id given. 
         * rows: The object to search in
         * id: The ID field value to find
         */
        get_row: function(rows, id, idcolumn) {
            var rv = null, idv = parseInt(id, 10);
            if (!idcolumn) { idcolumn = "ID"; }
            $.each(rows, function(i, v) {
                if (v[idcolumn] == idv) {
                    rv = v;
                    return false;
                }
            });
            return rv;
        },

        /**
         * Deletes the row with the id given
         * rows: The object to search in
         * id: The ID field value to find
         */
        delete_row: function(rows, id, idcolumn) {
            $.each(rows, function(i, row) {
                if (row && row[idcolumn] == id) {
                    rows.splice(i, 1); 
                }
            });
        },

        /** 
         *  An array sorting function for a single field within a list of objects.
         *  Use a - prefix to sort descending.
         *  eg: controller.rows.sort(common.sort_single("ANIMALNAME"));
         **/
        sort_single: function(fieldname) {
            var sortOrder = 1;
            if (fieldname[0] === "-") {
                sortOrder = -1;
                fieldname = fieldname.substr(1);
            }
            return function (a,b) {
                var ca = String(a[fieldname]).toUpperCase();
                var cb = String(b[fieldname]).toUpperCase();
                var result = (ca < cb) ? -1 : (ca > cb) ? 1 : 0;
                return result * sortOrder;
            };
        },

        /** 
         *  An array sorting function for multiple fields within a list of objects
         *  eg: controller.rows.sort(common.sort_multi("SPECIESID,-ANIMALNAME"));
         */
        sort_multi: function(fields) {
            fields = fields.split(",");
            return function (obj1, obj2) {
                var i = 0, result = 0, numberOfProperties = fields.length;
                /* try getting a different result from 0 (equal)
                 * as long as we have extra properties to compare
                 */
                while(result === 0 && i < numberOfProperties) {
                    result = common.sort_single(fields[i])(obj1, obj2);
                    i++;
                }
                return result;
            };
        },

        /** 
         * Splits s to an array based on spliton
         * after splitting, each element is stripped
         * of whitespace.
         */
        split_strip: function(s, spliton) {
            var x = s.split(spliton);
            var o = [];
            $.each(x, function(i, v) {
                o.push($.trim(v));
            });
            return o;
        },

        /**
         * Allows a config option LabelOverride_module to be set that
         * contains a list of triplets containing selector, item to 
         * change and new value. A hat ^ is used instead of string delimiters Eg:
         * label[for=^sheltercode^]|text|New Code
         */
        apply_label_overrides: function(modulename) {
            if (!config.has()) { return; } 
            var overrides = config.str("LabelOverrides_" + modulename);
            if (overrides == "") { return; }
            var oro = overrides.split(",");
            $.each(oro, function(i, v) {
                var ors = v.split("|");
                var selector = ors[0], changeitem = ors[1], newval = ors[2];
                selector = selector.split("^").join("'");
                if (changeitem == "text") {
                    $(selector).text(newval);
                }
                else if (changeitem == "title") {
                    $(selector).attr("title", newval);
                }
                else if (changeitem == "data") {
                    $(selector).attr("data", newval);
                }
                else if (changeitem == "alt") {
                    $(selector).attr("alt", newval);
                }
                else if (changeitem == "value") {
                    $(selector).attr("value", newval);
                }
                else if (changeitem =="display" && newval == "hide") {
                    $(selector).hide();
                }
            });
        },

        /**
         * Inspects the items in the dom for classes used and automatically
         * creates widgets based on them
         */
        bind_widgets: function() {
            // Disable effects if the option is set
            if (config.has() && config.bool("DisableEffects")) {
                jQuery.fx.off = true;
            }
            // textarea zoom dialog
            try {
                var tzb = {};
                tzb[_("Change")] = function() {
                    // Copy edited value back to the field
                    var fid = $("#textarea-zoom-id").val();
                    $("#" + fid).val($("#textarea-zoom-area").val());
                    $("#dialog-textarea-zoom").dialog("close");
                    try { validate.dirty(true); } catch(err) {}
                    $("#" + fid).focus();
                };
                tzb[_("Cancel")] = function() {
                    $("#dialog-textarea-zoom").dialog("close");
                };
                $("#dialog-textarea-zoom").dialog({
                    autoOpen: false,
                    height: 640,
                    width: 800,
                    modal: true,
                    show: dlgfx.zoom_show,
                    hide: dlgfx.zoom_hide,
                    buttons: tzb
                });
            }
            catch(err) {}
            // Get the date format specified by the backend for use by datepicker
            var df = "dd/mm/yy";
            if (asm.dateformat) {
                df = asm.dateformat.replace("%Y", "yy");
                df = df.replace("%m", "mm");
                df = df.replace("%d", "dd");
            }
            // Set the datepicker to use ASM's translations and localisation settings
            var asmregion = {
                renderer: $.ui.datepicker.defaultRenderer,
                monthNames: [ _("January"), _("February"),_("March"),_("April"),_("May"),_("June"),
                _("July"),_("August"),_("September"),_("October"),_("November"),_("December")],
                monthNamesShort: [_("Jan"), _("Feb"), _("Mar"), _("Apr"), _("May"), _("Jun"),
                _("Jul"), _("Aug"), _("Sep"), _("Oct"), _("Nov"), _("Dec")],
                dayNames: [_("Sunday"), _("Monday"), _("Tuesday"), _("Wednesday"), _("Thursday"), _("Friday"), _("Saturday")],
                dayNamesShort: [_("Sun"), _("Mon"), _("Tue"), _("Wed"), _("Thu"), _("Fri"), _("Sat")],
                dayNamesMin: [_("Su"),_("Mo"),_("Tu"),_("We"),_("Th"),_("Fr"),_("Sa")],
                firstDay: 1,
                dateFormat: df,
                prevText: _("Previous"), prevStatus: "",
                prevJumpText: "&#x3c;&#x3c;", prevJumpStatus: "",
                nextText: _("Next"), nextStatus: "",
                nextJumpText: "&#x3e;&#x3e;", nextJumpStatus: "",
                currentText: _("Current"), currentStatus: "",
                todayText: _("Today"), todayStatus: "",
                clearText: _("Clear"), clearStatus: "",
                closeText: _("Done"), closeStatus: "",
                yearStatus: "", monthStatus: "",
                weekText: _("Wk"), weekStatus: "",
                dayStatus: "DD d MM",
                defaultStatus: "",
                isRTL: (asm.locale == "ar" || asm.locale == "he")
            };
            $.datepicker.setDefaults(asmregion);
            // If we're using an RTL language, switch to RTL layout
            if (asm.locale == "ar" || asm.locale == "he") {
                $("html").css("direction", "rtl");
                // Menu text in dropdowns
                $(".asm-menu-body").css("text-align", "right");
                // Screens that show tables of data
                $(".asm-table td").css("text-align", "right");
                // Hotkeys in menus
                $(".asm-hotkey").css("float", "left");
                // JQuery UI tabs
                $(".asm-tabbar").css("direction", "rtl");
                $(".ui-tabs-nav li.ui-state-default").css("float", "right");
                $(".ui-tabs-nav li a").css("float", "right");
            }
            // Create any form controls based on classes used
            $(".asm-datebox").date();
            $(".asm-alphanumberbox").alphanumber();
            $(".asm-numberbox").number();
            $(".asm-intbox").intnumber();
            $(".asm-ipbox").ipnumber();
            $(".asm-timebox").time();
            $(".asm-currencybox").currency();
            $(".asm-selectbox, .asm-doubleselectbox, .asm-halfselectbox, .selectbox").select();
            $(".asm-animalchooser").animalchooser();
            $(".asm-animalchoosermulti").animalchoosermulti();
            $(".asm-personchooser").personchooser();
            $(".asm-textbox, .asm-halftextbox, .asm-doubletextbox").textbox();
            $(".asm-textarea, .asm-textareafixed, .asm-textareafixeddouble").textarea();
            if (_) {
                $(".asm-bsmselect").attr("title", _("Select"));
            }
            $(".asm-bsmselect").asmSelect({
                animate: true,
                sortable: true,
                removeLabel: '<strong>&times;</strong>',
                listClass: 'bsmList-custom',  
                listItemClass: 'bsmListItem-custom',
                listItemLabelClass: 'bsmListItemLabel-custom',
                removeClass: 'bsmListItemRemove-custom'
            });
            // Add extra control styles
            $(".asm-textbox, .asm-halftextbox, .asm-doubletextbox .asm-selectbox, .asm-textarea, .asm-textareafixed, .asm-textareafixeddouble").each(function() {
                $(this).addClass("controlshadow").addClass("controlborder");
            });
            // Inject new target attributes for anchors if option is on
            if (this.current_url().indexOf("/login") == -1) {
                this.inject_target();
            }
            // Bind tooltips
            common.bind_tooltips();

        },

        /**
         * Override browser tooltips to use fancy jQuery ones with
         * a triangle hooking them to the element.
         * If the option is disabled, or the browser is ie8 or ie9, this
         * function does nothing.
         * This function is currently disabled due to reported problems
         * in newer versions of chrome.
         */
        bind_tooltips: function() {
            /*
             positions for tooltips:
             top: my 'center bottom', at 'center top-10'
             bottom: my 'center top', at 'center bottom+10'
             left: my 'right center', at 'left-10 center'
             right: my 'left center', at 'right+10 center'
             */

            // Disabled.
            var disabled = true;
            if (disabled) { return; }

            // It's IE, don't use tooltips as tooltips can prevent
            // select boxes opening on IE9/10 and they don't work
            // at all on IE8
            if (common.is_msie()) { return; }

            // The option is off
            if (!config.bool("FancyTooltips")) { return; }

            // Put all tooltips on the right by default
            $(document).tooltip({
                position: {
                    my: 'left center',
                    at: 'right+10 center',
                    collision: 'fit'
                },
                tooltipClass: 'right',
                show: {
                    delay: 500
                }
            });

            // Move textarea, thumbnail and toolbar tooltips to below the element
            $("textarea, .asm-thumbnail, .asm-toolbar button").tooltip({
                position: {
                    my: 'left top',
                    at: 'left-10 bottom+10',
                    collision: 'none'
                },
                tooltipClass: 'bottom',
                show: {
                    delay: 500
                }
            });

            // Set locale/timezone tooltip on flag on left side, along
            // with the onshelter checkboxes on the animal screen
            $("#asm-topline-flag, #onshelterflags input").tooltip({
                position: {
                    my: 'right center',
                    at: 'left-10 center',
                    collision: 'fit'
                },
                tooltipClass: 'left',
                show: {
                    delay: 500
                }
            });

            // JQuery UI seems to have a random bug that causes tooltips
            // to stick around once a button is pressed. Add an extra
            // handler to every button to hide any associated tooltip.
            $("button").click(function() { 
                $(".ui-tooltip").hide();
            });
        },

        /**
         * Goes through all anchor tags in the page. If the system option for
         * opening records in a new tab is set and it's one of our group of
         * new record pages, creates a named target from the url so that the
         * record gets its own browser tab, but links within it still work.
         */
        inject_target: function() {
            var recpages = [ "animal", "person", "waitinglist", "lostanimal", "foundanimal" ];
            var href, anchor, targetname, r;
            if (config.bool("RecordNewBrowserTab")) {
                $("a").each(function() {
                    if ($(this).attr("href")) {
                        href = String($(this).attr("href"));
                        anchor = $(this);
                        $.each(recpages, function(i, v) {
                            if (href.indexOf(v) == 0 && href.indexOf("?") != -1) {
                                // Create targetname from URL, throwing away any
                                // portion after an underscore to get animal52, etc.
                                targetname = href.substring(href.lastIndexOf("/")+1);
                                if (targetname.indexOf("_") != -1) {
                                    targetname = targetname.substring(0, targetname.indexOf("_"));
                                }
                                else {
                                    targetname = targetname.substring(0, targetname.indexOf("?"));
                                }
                                targetname += href.substring(href.lastIndexOf("?")+1);
                                anchor.attr("target", targetname);
                            }
                        });
                    }
                });
            }
        },

        /** Number of minutes of inactivity */
        inactive_time: 0,

        /** Called every time a minute has elapsed. If we go over our 
         *  timeout value, we logout */
        inactive_time_increment: function() {
            common.inactive_time += 1;
            if (common.inactive_time > config.integer("InactivityTimeout")) {
                common.inactivity_logout();
            }
        },

        /** Called when keyboard/mouse activity happens to reset the inactive time */
        inactivity_reset: function() {
            common.inactive_time = 0;
        },

        /** Called when the inactivity time is up */
        inactivity_logout: function() {
            var a = "";
            if (asm.useraccount) { a = "?smaccount=" + asm.useraccount; }
            window.location = "logout" + a;
        },

        /** Starts the inactivity timer and binds to key/mouse events. If no timeout
         *  value has been configured, does nothing. */
        start_inactivity_timer: function() {
            if (!config.bool("InactivityTimer") || config.integer("InactivityTimeout") == 0) { return; }
            setInterval(common.inactive_time_increment, 60000);
            $(document).keypress(common.inactivity_reset);
            $(document).mousemove(common.inactivity_reset);
        }

    };

    config = {
        has: function() {
            try {
                return asm.config !== undefined;
            }
            catch (err){
                return false;
            }
        },

        str: function(key) {
            try {
                var s = asm.config[0][key];
                if (s) { return s; }
            }
            catch(err) {
            }
            return "";
        },

        bool: function(key) {
            var s = this.str(key);
            return s == "Yes" || s == "True";
        },

        integer: function(key) {
            var s = this.str(key);
            return parseInt(s, 10);
        },

        number: function(key) {
            var s = this.str(key);
            return parseFloat(s);
        },

        currency: function(key) {
            return format.currency(this.integer(key));
        }

    };

    dlgfx = {
            delete_show: "explode",
            delete_hide: "explode",
            add_show:    "fade",
            add_hide:    "drop",
            edit_show:   "fade",
            edit_hide:   "drop",
            zoom_show:   "slide",
            zoom_hide:   "slide"
    };

    format = {
        float_to_dp: function(f, dp) {
            return Math.round(f * Math.pow(10, dp)) / Math.pow(10, dp);
        },

        float_to_str: function(f, dp) {
            var zeroes = "000000000";
            var s = String(f);
            var idp = parseInt(dp, 10);
            var dot = s.indexOf(".");
            if (dot == -1) {
                return s + "." + zeroes.substring(0, idp);
            }
            var dchunk = s.substring(dot + 1);
            if (dchunk.length < idp) {
                return s + zeroes.substring(0, idp - dchunk.length);
            }
            if (dchunk.length > idp) {
                return s.substring(0, dot + idp + 1);
            }
            return s;
        },

        to_float: function(s) {
            try {
                var p = parseFloat(s);
                if (isNaN(p)) {
                    return 0.0;
                }
                return p;
            }
            catch(ex) {}
            return 0.0;
        },


        to_int: function(s) {
            try {
                var i = parseInt(s, 10);
                if (isNaN(i)) {
                    return 0;
                }
                return i;
            }
            catch(ex) {}
            return 0;
        },


        /**
         * Formats a currency integer as money with the
         * correct currency symbol and decimal places.
         */
        currency: function(v) {
            var nv = parseInt(v, 10) / 100,
                cs = html.decode(asm.currencysymbol);
            if (isNaN(nv)) { nv = 0; }
            if (asm.currencyprefix && asm.currencyprefix == "s") {
                return nv.toFixed(asm.currencydp) + cs;
            }
            return cs + nv.toFixed(asm.currencydp);
        },

        currency_to_float: function(c) {
            /*jslint regexp: true */
            c = c.replace(/[^0-9\.\-]/g, '');
            // Some currency formats (eg: Russian py6. and Indian Rs. have a 
            // dot to finish. If we have a leading dot, it must be one of
            // those formats so remove it.
            if (c.substring(0, 1) == ".") {
                c = c.substring(1);
            }
            return parseFloat(c);
        },

        currency_to_int: function(c) {
            var i = format.currency_to_float(c);
            return Math.floor(i * 100);
        },

        /**
         * Turns an iso or js date into a display date
         * empty string is returned if iso is undefined/null
         */
        date: function(iso) {
            if (!iso) { return ""; }
            if (iso instanceof Date) { iso = format.date_iso(iso); }
            var d = format.date_js(iso);
            var f = asm.dateformat.replace("%Y", d.getFullYear());
            f = f.replace("%m", this.padleft(d.getMonth() + 1, 2));
            f = f.replace("%d", this.padleft(d.getDate(), 2));
            f = f.replace("%H", this.padleft(d.getHours(), 2));
            f = f.replace("%M", this.padleft(d.getMinutes(), 2));
            f = f.replace("%S", this.padleft(d.getSeconds(), 2));
            return f;
        },

        /**
         * Checks if d is in between start and end
         * d: js or iso date 
         * start: js or iso date
         * end: js or iso date 
         * ignoretime: if true, removes time component before comparison
         */
        date_in_range: function(d, start, end, ignoretime) {
            d = format.date_js(d); 
            start = format.date_js(start); 
            end = format.date_js(end); 
            if (ignoretime) {
                d.setHours(0,0,0,0);
                start.setHours(0,0,0,0);
                end.setHours(0,0,0,0);
            }
            return start.getTime() <= d.getTime() && d.getTime() <= end.getTime();
        },

        /**
         * Turns a display date or js date into iso format.
         * null is returned if d is undefined/null
         */
        date_iso: function(d) {
            if (!d) { return null; }
            if (d instanceof Date) {
                return format.padleft(d.getFullYear(), 4) + "-" + 
                    format.padleft((d.getMonth() + 1), 2) + "-" + 
                    format.padleft(d.getDate(), 2) + "T00:00:00";
            }
            var fbits = asm.dateformat.split("/"), dbits = d.split("/");
            if (fbits.length < 3 || dbits.length < 3) { return null; }
            var year, month, day, i;
            for (i = 0; i < 3; i++) {
                if (fbits[i] == "%Y") {
                    year = dbits[i];
                    if (year.length == 2) {
                        year = "20" + year;
                    }
                    year = format.padleft(year, 4);
                }
                else if (fbits[i] == "%m") {
                    month = format.padleft(dbits[i], 2);
                }
                else if (fbits[i] == "%d") {
                    day = format.padleft(dbits[i], 2);
                }
            }
            return year + "-" + month + "-" + day + "T00:00:00";
        },

        /**
         * Sets the time component t on iso date d
         * and returns a new iso date.
         */
        date_iso_settime: function(d, t) {
            if (!d) { return null; }
            if (d instanceof Date) {
                d = format.date_iso(d);
            }
            if (t.length <= 8) {
                t += ":00";
            }
            if (t.length <= 5) {
                t += ":00:00";
            }
            return d.replace("00:00:00", t);
        },

        /**
         * Turns an iso date into a js date. null is returned if iso is undefined/null
         */
        date_js: function(iso) {
            if (!iso) { return null; }
            if (iso instanceof Date) { return iso; } // it's already a js date
            // IE8 and below doesn't support ISO date strings so we have to slice it up ourself
            var year = parseInt(iso.substring(0, 4), 10),
                month = parseInt(iso.substring(5, 7), 10) - 1,
                day = parseInt(iso.substring(8, 10), 10),
                hour = parseInt(iso.substring(11, 13), 10),
                minute = parseInt(iso.substring(14, 16), 10),
                second = parseInt(iso.substring(17, 19), 10);
            var d = new Date(year, month, day, hour, minute, second);
            return d;
        },

        /**
         * Returns the ISO 8601 week number for a date
         * d: js or iso date
         */
        date_weeknumber: function(d) {
            d = format.date_js(d);
            d = new Date(+d);
            d.setHours(0,0,0,0);
            // Set to nearest Thursday: current date + 4 - current day number
            // Make Sunday's day number 7
            d.setDate(d.getDate() + 4 - (d.getDay() || 7));
            // Get first day of year
            var yearStart = new Date(d.getFullYear(), 0, 1);
            // Calculate full weeks to nearest Thursday
            var weekNo = Math.ceil( ( ( (d - yearStart) / 86400000) + 1) / 7);
            return weekNo;
        },

        /**
         * Turns an iso or js date into a display time
         * empty string is returned if iso is undefined/null
         * f: the format to use, %H, %h, %M, %S are supported
         */
        time: function(iso, f) {
            var d; 
            if (!f) { f = "%H:%M:%S"; }
            if (!iso) { return ""; }
            if (iso instanceof Date) { 
                d = iso; 
            }
            else {
                d = format.date_js(iso);
            }
            f = f.replace("%H", this.padleft(d.getHours(), 2));
            f = f.replace("%M", this.padleft(d.getMinutes(), 2));
            f = f.replace("%S", this.padleft(d.getSeconds(), 2));
            return f;
        },

        padleft: function(s, d) {
            var zeroes = "000000000000000";
            s = String(s);
            if (s.length > d) { return s; }
            var nr = d - s.length;
            return zeroes.substring(0, nr) + s;
        },

        padright: function(s, d) {
            var zeroes = "000000000000000";
            s = String(s);
            if (s.length > d) { return s; }
            var nr = d - s.length;
            return s + zeroes.substring(0, nr);
        },

        postcode_prefix: function(s) {
            var p = String(s);
            if (p.indexOf(" ") == -1) { return p; }
            p = p.substring(0, p.indexOf(" "));
            return p;
        },

        /**
         * Returns a readable day of the month from a number
         * 0 = Jan, 1 = Feb, etc.
         */
        monthname: function(i) {
            var months = [ _("Jan"), _("Feb"), _("Mar"), _("Apr"), 
                _("May"), _("Jun"), _("Jul"), _("Aug"), _("Sep"), 
                _("Oct"), _("Nov"), _("Dec") ];
            if (i && (i < 0 || i > 11)) { return ""; }
            return months[i];
        },

        /** Returns a readable day of the week from a number
         *  0 = Mon, 1 = Tue, etc.
         */
        weekdayname: function(i) {
            var days = [ _("Mon"), _("Tue"), _("Wed"), _("Thu"), _("Fri"), _("Sat"), _("Sun") ];
            if (i && (i < 0 || i > 6)) { return ""; }
            return days[i];
        }

    };

    html = {

        /**
         * Returns true if animal a is adoptable. Looks at current publishing options
         * and uses the same logic as the backend publisher
         */
        is_animal_adoptable: function(a) {
            var p = config.str("PublisherPresets"),
                exwks = format.to_int(common.url_param(p.replace(/ /g, "&"), "excludeunder")),
                locs = common.url_param(p.replace(/ /g, "&"), "includelocations");
            if (a.ISNOTAVAILABLEFORADOPTION == 1) { return [ false, _("Not for adoption flag set") ]; }
            if (a.NONSHELTERANIMAL == 1) { return [ false, _("Non-Shelter") ]; }
            if (a.DECEASEDDATE) { return [ false, _("Deceased") ]; }
            if (a.CRUELTYCASE == 1 && p.indexOf("includecase") == -1) { return [ false, _("Cruelty Case") ]; }
            if (a.HASACTIVERESERVE == 1 && a.RESERVEDOWNERID && p.indexOf("includereserved") == -1) {
                return [ false, _("Reserved") + " " + html.icon("right") + " " + 
                        "<a href=\"person?id=" + a.RESERVEDOWNERID + "\">" + a.RESERVEDOWNERNAME ];
            }
            if (a.HASACTIVERESERVE == 1 && p.indexOf("includereserved") == -1) { return [ false, _("Reserved") ]; }
            if (a.ISHOLD == 1 && a.HOLDUNTILDATE && p.indexOf("includehold") == -1) { 
                return [ false, _("Hold until {0}").replace("{0}", format.date(a.HOLDUNTILDATE)) ]; 
            }
            if (a.ISHOLD == 1 && p.indexOf("includehold") == -1) { return [ false, _("Hold") ]; }
            if (a.ISQUARANTINE == 1 && p.indexOf("includequarantine") == -1) { return [ false, _("Quarantine") ]; }
            if (a.DECEASEDDATE) { return [ false, _("Deceased") ]; }
            if (a.HASPERMANENTFOSTER == 1) { return [ false, _("Permanent Foster") ]; }
            if (a.ACTIVEMOVEMENTTYPE == 2 && p.indexOf("includefosters") == -1) { return [ false, _("Foster") ]; }
            if (a.ACTIVEMOVEMENTTYPE == 8 && p.indexOf("includeretailer") == -1) { return [ false, _("Retailer") ]; }
            if (a.ACTIVEMOVEMENTTYPE == 1 && a.HASTRIALADOPTION == 1 && p.indexOf("includetrial") == -1) { return [ false, _("Trial Adoption") ]; }
            if (a.ACTIVEMOVEMENTTYPE == 1 && a.HASTRIALADOPTION == 0) { return [ false, _("Adopted") ]; }
            if (a.ACTIVEMOVEMENTTYPE >= 3 && a.ACTIVEMOVEMENTTYPE <= 7) { return [ false, a.DISPLAYLOCATION ]; }
            if (!a.WEBSITEMEDIANAME && p.indexOf("includewithoutimage") == -1) { return [ false, _("No picture") ]; }
            if (exwks) { 
                if (common.add_days(format.date_js(a.DATEOFBIRTH), (exwks * 7)) > new Date()) { 
                    return [ false, _("Under {0} weeks old").replace("{0}", exwks) ]; 
                } 
            }
            if (locs && locs != "null" && !a.ACTIVEMOVEMENTTYPE) {
                var inloc = false;
                $.each(locs.split(","), function(i,v) {
                    if (format.to_int(v) == a.SHELTERLOCATION) { inloc = true; }
                });
                if (!inloc) { return [ false, _("Not in chosen publisher location") ]; }
            }
            return [ true, _("Available for adoption") ];
        },

        /**
         * Renders an animal link thumbnail from the record given
         * a: An animal or brief animal record
         * o: Options to pass on to animal_emblems
         * o.showselector: if true outputs a checkbox to select the animal link
         */
        animal_link: function(a, o) {
            var s = [];
            var title = common.substitute(_("{0}: Entered shelter {1}, Last changed on {2} by {3}. {4} {5} {6} aged {7}"), { 
                "0": a.CODE,
                "1": format.date(a.MOSTRECENTENTRYDATE),
                "2": format.date(a.LASTCHANGEDDATE),
                "3": a.LASTCHANGEDBY,
                "4": a.SEXNAME,
                "5": a.BREEDNAME,
                "6": a.SPECIESNAME,
                "7": a.ANIMALAGE});
            s.push(common.substitute('<a href="animal?id={id}"><img title="{title}" src="{imgsrc}" class="asm-thumbnail thumbnailshadow" /></a><br />', {
                "id" : a.ID,
                "title" : html.title(title),
                "imgsrc" : html.thumbnail_src(a, "animalthumb") }));
            s.push(html.animal_emblems(a, o));
            if (config.bool("ShelterViewShowCodes")) {
                s.push('<a href="animal?id=' + a.ID + '">' + a.CODE + '</a><br />');
            }
            s.push('<a href="animal?id=' + a.ID + '">' + a.ANIMALNAME + '</a>');
            if (o.showselector) {
                s.push('<br /><input type="checkbox" class="animalselect" data="{id}" title="{title}" />'.replace("{id}", a.ID).replace("{title}", _("Select")));
            }
            return s.join("\n");
        },

        /**
         * Renders a series of animal emblems for the animal record given
         * (animal record can be a brief)
         * a: The animal record to show an emblem for
         * o.showlocation: if true, outputs a single emblem icon to represent the
         *                 animal's current location with a tooltip.
         * o.showunit: if true, will include the location unit number as an emblem
         */
        animal_emblems: function(a, o) {
            var s = [];
            if (!o) { o = {}; }
            if (config.bool("EmblemAlwaysLocation")) { o.showlocation = true; }
            s.push("<span class=\"asm-animal-emblems\">");
            if (o && o.showlocation && !a.DECEASEDDATE) {
                if (a.ARCHIVED == 0 && !a.ACTIVEMOVEMENTTYPE) {
                    s.push(html.icon("location", _("On Shelter") + " / " + a.SHELTERLOCATIONNAME + " " + common.nulltostr(a.SHELTERLOCATIONUNIT)));
                }
                else if (a.ACTIVEMOVEMENTTYPE == 2) {
                    s.push(html.icon("person", a.DISPLAYLOCATIONNAME + " / " + a.CURRENTOWNERNAME));
                }
                else if (a.NONSHELTERANIMAL == 0) {
                    s.push(html.icon("movement", a.DISPLAYLOCATIONNAME + " / " + a.CURRENTOWNERNAME));
                }
            }
            if (config.bool("EmblemLongTerm") && a.ARCHIVED == 0 && (a.DAYSONSHELTER > config.integer("LongTermMonths") * 30))  {
                s.push(html.icon("calendar", _("Long term")));
            }
            if (config.bool("EmblemDeceased") && a.DECEASEDDATE != null) {
                s.push(html.icon("death", _("Deceased")));
            }
            if (config.bool("EmblemReserved") && a.HASACTIVERESERVE == 1) {
                s.push(html.icon("reservation", _("Reserved")));
            }
            if (config.bool("EmblemTrialAdoption") && a.HASTRIALADOPTION == 1) {
                s.push(html.icon("trial", _("Trial Adoption")));
            }
            if (config.bool("EmblemCrueltyCase") && a.CRUELTYCASE == 1) {
                s.push(html.icon("case", _("Cruelty Case")));
            }
            if (config.bool("EmblemNonShelter") && a.NONSHELTERANIMAL == 1) {
                s.push(html.icon("nonshelter", _("Non-Shelter")));
            }
            if (config.bool("EmblemPositiveTest") && (
                (a.HEARTWORMTESTED == 1 && a.HEARTWORMTESTRESULT == 2) || 
                (a.COMBITESTED == 1 && a.COMBITESTRESULT == 2) || 
                (a.COMBITESTED == 1 && a.FLVRESULT == 2))) {
                var p = [];
                if (a.HEARTWORMTESTRESULT == 2) { p.push(_("Heartworm+")); }
                if (a.COMBITESTRESULT == 2) { p.push(_("FIV+")); }
                if (a.FLVRESULT == 2) { p.push(_("FLV+")); }
                s.push(html.icon("positivetest", p.join(" ")));
            }
            if (config.bool("EmblemUnneutered") && a.NEUTERED == 0 && a.NONSHELTERANIMAL == 0) {
                s.push(html.icon("health", _("Unaltered")));
            }
            if (config.bool("EmblemNotMicrochipped") && a.IDENTICHIPPED == 0 && a.NONSHELTERANIMAL == 0) {
                s.push(html.icon("microchip", _("Not Microchipped")));
            }
            if (config.bool("EmblemNotForAdoption") && a.ISNOTAVAILABLEFORADOPTION == 1 && (a.ARCHIVED == 0 || a.ACTIVEMOVEMENTTYPE == 2) ) {
                s.push(html.icon("notforadoption", _("Not For Adoption")));
            }
            if (config.bool("EmblemHold") && a.ISHOLD == 1 && (a.ARCHIVED == 0 || a.ACTIVEMOVEMENTTYPE == 2) ) {
                if (a.HOLDUNTILDATE) {
                    s.push(html.icon("hold", _("Hold until {0}").replace("{0}", format.date(a.HOLDUNTILDATE))));
                }
                else {
                    s.push(html.icon("hold", _("Hold")));
                }
            }
            if (config.bool("EmblemQuarantine") && a.ISQUARANTINE == 1 && (a.ARCHIVED == 0 || a.ACTIVEMOVEMENTTYPE == 2) ) {
                s.push(html.icon("quarantine", _("Quarantine")));
            }
            s.push("</span>");
            if (o && o.showunit && a.SHELTERLOCATIONUNIT) {
                s.push(' <span class="asm-search-locationunit" title="' + html.title(_("Unit")) + '">' + a.SHELTERLOCATIONUNIT + '</span>');
            }
            return s.join("");
        },

        /** 
         * Renders a shelter event described in e. Events should have
         * the following attributes:
         * LINKTARGET, CATEGORY, EVENTDATE, ID, TEXT1, TEXT2, TEXT3, LASTCHANGEDBY,
         * ICON, DESCRIPTION
         */
        event_text: function(e, o) {
            var h = "";
            if (o && o.includedate) {
                h += '<span class="asm-timeline-small-date">' + format.date(e.EVENTDATE) + '</span> ';
            }
            if (o && o.includetime) {
                h += '<span class="asm-timeline-time">' + format.time(e.EVENTDATE) + '</span>' ;
            }
            h += ' <a href="' + e.LINKTARGET + '?id=' + e.ID + '">';
            h += html.icon(e.ICON) + ' ' + e.DESCRIPTION;
            h += '</a> <span class="asm-timeline-by">(' + e.LASTCHANGEDBY + ')</span>';
            return h;
        },

        /**
         * Renders a list of <option> tags for person flags.
         * It mixes in any additional person flags to the regular
         * set, sorts them all alphabetically and applies them
         * to the select specified by selector. If a person record
         * is passed, then it will be checked and selected items
         * will be selected.
         * p: A person record (or null if not available)
         * flags: A list of extra person flags from the lookup call
         * node: A jquery dom node of the select box to populate
         * includeall: Have an all/(all) option at the top of the list
         */
        person_flag_options: function(p, flags, node, includeall) {

            var opt = [];
            var field_option = function(fieldname, post, label) {
                var sel = p && p[fieldname] == 1 ? 'selected="selected"' : "";
                return '<option value="' + post + '" ' + sel + '>' + label + '</option>\n';
            };

            var flag_option = function(flag) {
                var sel = "";
                if (!p || !p.ADDITIONALFLAGS) { sel = ""; }
                else {
                    $.each(p.ADDITIONALFLAGS.split("|"), function(i, v) {
                        if (v == flag) {
                            sel = 'selected="selected"';
                        }
                    });
                }
                return '<option ' + sel + '>' + flag + '</option>';
            };

            var h = [
                { label: _("ACO"), html: field_option("ISACO", "aco", _("ACO")) },
                { label: _("Banned"), html: field_option("ISBANNED", "banned", _("Banned")) },
                { label: _("Deceased"), html: field_option("ISDECEASED", "deceased", _("Deceased")) },
                { label: _("Donor"), html: field_option("ISDONOR", "donor", _("Donor")) },
                { label: _("Driver"), html: field_option("ISDRIVER", "driver", _("Driver")) },
                { label: _("Fosterer"), html: field_option("ISFOSTERER", "fosterer", _("Fosterer")) },
                { label: _("Homechecked"), html: field_option("IDCHECK", "homechecked", _("Homechecked")) },
                { label: _("Homechecker"), html: field_option("ISHOMECHECKER", "homechecker", _("Homechecker")) },
                { label: _("Member"), html: field_option("ISMEMBER", "member", _("Member")) },
                { label: _("Other Shelter"), html: field_option("ISSHELTER", "shelter", _("Other Shelter")) },
                { label: _("Staff"), html: field_option("ISSTAFF", "staff", _("Staff")) },
                { label: _("Vet"), html: field_option("ISVET", "vet", _("Vet")) },
                { label: _("Volunteer"), html: field_option("ISVOLUNTEER", "volunteer", _("Volunteer")) }
            ];

            if (!config.bool("DisableRetailer")) {
                h.push({ label: _("Retailer"), html: field_option("ISRETAILER", "retailer", _("Retailer")) });
            }
            if (asm.locale == "en_GB") {
                h.push({ label: _("UK Giftaid"), html: field_option("ISGIFTAID", "giftaid", _("UK Giftaid"))});
            }

            $.each(flags, function(i, v) {
                h.push({ label: v.FLAG, html: flag_option(v.FLAG) });
            });

            h.sort(common.sort_single("label"));

            if (includeall) {
                opt.push('<option value="all">' + _("(all)") + '</option>');
            }

            $.each(h, function(i, v) {
                opt.push(v.html);    
            });

            node.html(opt.join("\n"));
            node.change();

        },

        /**
         * Outputs a div box container with jquery ui style
         */
        box: function(margintop, padding) {
            if (!margintop) { 
                margintop = 0;
            }
            if (!padding) {
                padding = 5;
            }
            return '<div class="ui-helper-reset centered ui-widget-content ui-corner-all" style="margin-top: ' + margintop + 'px; padding: ' + padding + 'px;">';
        },

        /**
         * Returns a hidden field that you can use to prevent
         * JQuery UI dialogs auto focusing
         */
        capture_autofocus: function() {
            return '<span class="ui-helper-hidden-accessible"><input type="text"/></span>';
        },

        /**
         * The header that should wrap all content on screens
         * title: The title to show in the box heading
         * notcontent: If undefined, an id of asm-content is set
         */
        content_header: function(title, notcontent) {
            var ids = "";
            if (!notcontent) {
                ids = "id=\"asm-content\" ";
            }
            if (title) {
                return "<div " + ids + " class=\"ui-accordion ui-widget ui-helper-reset ui-accordion-icons\">" +
                    "<h3 class=\"ui-accordion-header ui-helper-reset ui-corner-top ui-state-active centered\">" +
                    "<a href=\"#\">" + title + "</a></h3>" +
                    "<div class=\"ui-helper-reset ui-widget-content ui-corner-bottom\" style=\"padding: 5px;\">";
            }
            return "<div " + ids + " class=\"ui-accordion ui-widget ui-helper-reset ui-accordion-icons\">";
        },

        /**
         * The footer that closes our content header
         */
        content_footer: function() {
            return "</div></div>";
        },

        /** 
         * Decodes any unicode html entities from the following types of objects:
         *      o can be a string
         *      o can be a list of strings
         *      o can be a list of objects with label properties
         */
        decode: function(o) {
            var decode_str = function(s) {
                try {
                    return $("<div></div>").html(s).text();
                }
                catch(err) {
                    return "";
                }
            };
            if (common.is_array(o)) {
                var oa = [];
                $.each(o, function(i, v) {
                    if (v.label) {
                        // It's an object with a label property
                        v.label = decode_str(v.label);
                        oa.push(v);
                    }
                    else {
                        // It's just a string, decode it
                        oa.push(decode_str(v));
                    }
                });
                return oa;
            }
            return decode_str(o);
        },

        /**
         * Returns the html for an icon by its name, including a
         * title attribute.
         */
        icon: function(name, title, style) {
            var extra = "";
            if (title) {
                extra = " title=\"" + this.title(title) + "\"";
            }
            if (style) {
                extra += " style=\"" + style + "\"";
            }
            return "<span class=\"asm-icon asm-icon-" + name + "\"" + extra + "></span>";
        },

        /**
         * Returns an error bar, with error icon and the text supplied
         */
        error: function(s, containerid) {
            return [
                "<div class=\"ui-widget\" ",
                containerid ? "id=\"" + containerid + "\" " : "",
                ">",
                "<div class=\"ui-state-error ui-corner-all\"><p>",
                "<span class=\"ui-icon ui-icon-alert\" style=\"float: left; margin-right: .3em;\"></span>",
                s,
                "</p></div></div>"
            ].join("\n");
        },

        /**
         * Returns an info bar, with info icon and the text supplied
         */
        info: function(s, containerid) {
            return [
                "<div class=\"ui-widget\" ",
                containerid ? "id=\"" + containerid + "\" " : "",
                ">",
                "<div class=\"ui-state-highlight ui-corner-all\"><p>",
                "<span class=\"ui-icon ui-icon-info\" style=\"float: left; margin-right: .3em;\"></span>",
                s,
                "</p></div></div>"
            ].join("\n");
        },

        /**
         * Returns an warning bar, with warning icon and the text supplied
         */
        warn: function(s, containerid) {
            return [
                "<div class=\"ui-widget\" ",
                containerid ? "id=\"" + containerid + "\" " : "",
                ">",
                "<div class=\"ui-state-highlight ui-corner-all\"><p>",
                "<span class=\"ui-icon ui-icon-alert\" style=\"float: left; margin-right: .3em;\"></span>",
                s,
                "</p></div></div>"
            ].join("\n");
        },

        /**
         * Reads a list of objects and produces HTML options from it.
         * If valueprop is undefined, we assume a single list of elements.
         * l: The list object
         * valueprop: The name of the value property
         * displayprop: The name of the display property
         */
        list_to_options: function(l, valueprop, displayprop) {
            var h = "";
            $.each(l, function(i, v) {
                if (!valueprop) {
                    h += "<option>" + v + "</option>";
                }
                else {
                    h += "<option value=\"" + v[valueprop] + "\">" + v[displayprop] + "</option>\n";
                }
            });
            return h;
        },

        /**
         * Special list to options for breeds, outputs an 
         * option group for each species
         */
        list_to_options_breeds: function(l) {
            var h = [], spid = 0;
            $.each(l, function(i, v) {
                if (v.SPECIESID != spid) {
                    if (spid != 0) {
                        h.push("</optgroup>");
                    }
                    spid = v.SPECIESID;
                    h.push("<optgroup id='ngp-" + v.SPECIESID + "' label='" + v.SPECIESNAME + "'>");
                }
                h.push("<option value=\"" + v.ID + "\">" + v.BREEDNAME + "</option>\n");
            });
            return h.join("\n");
        },

        /** 
         * Removes HTML tags from a string
         */
        strip_tags: function(s) {
            return $("<p>" + s + "</p>").text();
        },

        /**
         * Santises a string to go in an HTML title
         */
        title: function(s) {
            if (s == null || s === undefined) { return ""; }
            return String(s).replace("\"", "&quot;").replace("'", "&pos;"); 
        },

        /**
         * Truncates a string to length. If the string is longer
         * than length, appends ...
         * Throws away html tags too.
         */
        truncate: function(s, length) {
            if (length === undefined) {
                length = 100;
            }
            if (s == null) {
                return "";
            }
            s = this.strip_tags(s);
            if (s.length > length) {
                return s.substring(0, length) + "...";
            }
            return s;
        },

        /**
         * Gets the img src attribute/URI to a picture. If the
         * row doesn't have preferred media, the nopic src is returned instead.
         * Makes life easier for the browser caching things and we can stick
         * a max-age on items being served.
         * row: An animal or person json row containing ID, ANIMALID or PERSONID
         *      and WEBSITEMEDIANAME
         * mode: The mode - animal or person
         */
        img_src: function(row, mode) {
            if (!row.WEBSITEMEDIANAME) {
                return "image?db=" + asm.useraccount + "&mode=dbfs&id=/reports/nopic.jpg";
            }
            var idval = 0, uri = "";
            if (mode == "animal") {
                if (row.hasOwnProperty("ANIMALID")) {
                    idval = row.ANIMALID;
                }
                else if (row.hasOwnProperty("ID")) {
                    idval = row.ID;
                }
            }
            else if (mode == "person") {
                if (row.hasOwnProperty("PERSONID")) {
                    idval = row.PERSONID;
                }
                else if (row.hasOwnProperty("ID")) {
                    idval = row.ID;
                }
            }
            else {
                idval = row.ID;
            }
            uri = "image?db=" + asm.useraccount + "&mode=" + mode + "&id=" + idval;
            if (row.WEBSITEMEDIADATE) {
                uri += "&date=" + encodeURIComponent(row.WEBSITEMEDIADATE);
            }
            return uri;
        },

        /**
         * Gets the img src attribute for a thumbnail picture. If the
         * row doesn't have preferred media, the nopic src is returned instead.
         * Makes life easier for the browser caching things and we can stick
         * a max-age on items being served.
         * row: An animal or person json row containing ID, ANIMALID or PERSONID
         *      and WEBSITEMEDIANAME
         * mode: The mode - aanimalthumb or personthumb
         */
        thumbnail_src: function(row, mode) {
            if (!row.WEBSITEMEDIANAME) {
                return "image?db=" + asm.useraccount + "&mode=dbfs&id=/reports/nopic.jpg";
            }
            var idval = 0, uri = "";
            if (mode == "animalthumb") {
                if (row.hasOwnProperty("ANIMALID")) {
                    idval = row.ANIMALID;
                }
                else if (row.hasOwnProperty("ID")) {
                    idval = row.ID;
                }
            }
            else if (mode == "personthumb") {
                if (row.hasOwnProperty("PERSONID")) {
                    idval = row.PERSONID;
                }
                else if (row.hasOwnProperty("ID")) {
                    idval = row.ID;
                }
            }
            else {
                idval = row.ID;
            }
            uri = "image?db=" + asm.useraccount + "&mode=" + mode + "&id=" + idval;
            if (row.WEBSITEMEDIADATE) {
                uri += "&date=" + encodeURIComponent(row.WEBSITEMEDIADATE);
            }
            return uri;
        }
    };

    validate = {

        /* Whether or not validation is currently active */
        active: false,

        /* Global for whether or not there are unsaved changes */
        unsaved: false,

        /**
         * Does all binding for dirtiable forms.
         * 1. Watches for controls changing and marks the form dirty.
         * 2. If we are in server routing mode, adds a delegate listener 
         *    to links and fires the unsaved dialog if necessary.
         * 3. Catches beforeunload to prevent navigation away if dirty
         */
        bind_dirty: function() {
            // Watch for control changes and call dirty()
            var dirtykey = function(event) { if (event.keyCode != 9) { validate.dirty(true); } };
            var dirtychange = function(event) { validate.dirty(true); };
            validate.active = true;
            $("#asm-content .asm-checkbox").change(dirtychange);
            $("#asm-content .asm-datebox").change(dirtychange);
            $("#asm-content .asm-textbox, #asm-content .asm-doubletextbox, #asm-content .asm-halftextbox, #asm-content .asm-textarea, #asm-content .asm-textareafixed, #asm-content .asm-textareafixeddouble").keyup(dirtykey).bind("paste", dirtychange);
            $("#asm-content .asm-selectbox, #asm-content .asm-doubleselectbox, #asm-content .asm-halfselectbox, #asm-content .selectbox, #asm-content .asm-bsmselect").change(dirtychange);
            // Bind CTRL+S/META+S on Mac to clicking the save button
            Mousetrap.bind(["ctrl+s", "meta+s"], function(e) { $("#button-save").click(); return false; });
            // Watch for links being clicked and the page being navigated away from
            if (common.route_mode == "server") {
                $(document).on("a", "click", validate.a_click_handler);
            }
            window.onbeforeunload = function() {
                if (validate.unsaved) {
                    return _("You have unsaved changes, are you sure you want to leave this page?");
                }
            };
        },

        unbind_dirty: function() {
            validate.active = false;
            window.onbeforeunload = undefined;
        },

        a_click_handler: function(event, href) {
            if ($(this).prop("href") != "#") {
                if (validate.unsaved) {
                    event.preventDefault();
                    if (!href) { href = $(this).attr("href"); }
                    validate.unsaved_dialog(href);
                    return false;
                }
            }
            return true;
        },

        /** Displays the unsaved changes dialog and switches to the
          * target URL if the user says to leave */
        unsaved_dialog: function(target) {
            var b = {}, self = this;
            b[_("Save and leave")] = function() {
                self.save(function() {
                    common.route(target);
                });
            };
            b[_("Leave")] = function() {
                self.active = false;
                self.unsaved = false; // prevent onunload firing
                $("#dialog-unsaved").dialog("close");
                common.route(target);
            };
            b[_("Stay")] = function() { 
                $(this).dialog("close"); 
            };
            $("#dialog-unsaved").dialog({
                 resizable: false,
                 modal: true,
                 width: 500,
                 dialogClass: "dialogshadow",
                 show: dlgfx.delete_show,
                 hide: dlgfx.delete_hide,
                 buttons: b,
                 close: function() {
                     $("#dialog-unsaved").dialog("destroy");
                 }
            });
        },

        /* Accepts an array of ids to test whether they're blank or not
           if they are, their label is highlighted and false is returned */
        notblank: function(fields) {
            var rv = true;
            $.each(fields, function(i, f) {
                var v = $("#" + f).val();
                v = $.trim(v);
                if (v == "") {
                    $("label[for='" + f + "']").addClass("ui-state-error-text");
                    $("#" + f).focus();
                    rv = false;
                    return false;
                }
            });
            return rv;
        },

        /* Accepts an array of ids to test whether they're zero or not
           if they are, their label is highlighted and false is returned */
        notzero: function(fields) {
            var rv = true;
            $.each(fields, function(i, f) {
                var v = $("#" + f).val();
                v = $.trim(v);
                if (v == "0") {
                    $("label[for='" + f + "']").addClass("ui-state-error-text");
                    $("#" + f).focus();
                    rv = false;
                    return false;
                }
            });
            return rv;
        },

        /* Accepts an array of ids to time fields test whether they're valid
           times. Valid values are a blank or 00:00 or 00:00:00
           if they are invalid, their label is highlighted and false is returned */
        validtime: function(fields) {
            var rv = true, valid1 = /^\d\d\:\d\d\:\d\d$/, valid2 = /^\d\d\:\d\d$/;
            $.each(fields, function(i, f) {
                var v = $("#" + f).val();
                v = $.trim(v);
                if (v != "" && !valid1.test(v) && !valid2.test(v)) {
                    // Times rarely have their own label, instead look for the label
                    // in the same table row as our widget
                    $("#" + f).closest("tr").find("label").addClass("ui-state-error-text");
                    $("#" + f).focus();
                    header.show_error(_("Invalid time '{0}', times should be in 00:00 format").replace("{0}", v));
                    rv = false;
                    return false;
                }
            });
            return rv;
        },

        /* Set whether we have dirty form data and enable/disable 
           any on screen save button */
        dirty: function(isdirty) { 
            if (isdirty) { 
                this.unsaved = true; 
                $("#button-save").button("enable"); 
            } 
            else { 
                this.unsaved = false; 
                $("#button-save").button("disable");
            } 
        },

    };

} (jQuery));

$(function() {

    // Execute every time this script is loaded.
    // Check for adequate browser support - no AJAX is a showstopper
    // as is IE below 8 because it doesn't have inline-block support.
    if (!jQuery.support.ajax || common.msie_version() < 8) {
        window.location = "static/pages/unsupported.html";
    }

    // If this is IE8 or IE9, add a special class to the html element so
    // we can apply any CSS hacks via the stylesheet
    if (common.msie_version() == 8) { $("html").addClass("ie8"); }
    if (common.msie_version() == 9) { $("html").addClass("ie9"); }

    // Prevent annoying Firefox errors where it tries to parse all
    // ajax responses that don't have a mimetype as XML - override
    // it to assume plain text
    $.ajaxSetup({ mimeType: "text/plain" });

    // We use mousetrap for hotkey sequences and by default, it will
    // not respond to keyevents when a textarea or input field has
    // the focus, rendering it useless for a data driven app like ASM. 
    // Override its stopCallback behaviour to always respond to events.
    Mousetrap.stopCallback = function(e, element, combo) {
        return false;
    };

    // Make CTRL+H return to the homescreen
    Mousetrap.bind([ "ctrl+h", "meta+h" ], function() {
        common.route("main");
        return false;
    });

    // If an inactivity timeout is configured, starts the timer
    common.start_inactivity_timer();

});
