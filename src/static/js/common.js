/*global $, console, performance, jQuery, FileReader, Modernizr, Mousetrap, Path */
/*global alert, asm, schema, atob, btoa, header, _, escape, unescape, navigator */
/*global consts: true, common: true, config: true, controller: true, dlgfx: true, format: true, html: true, log: true, validate: true */

"use strict";

const common = {

    /** Speed of all JQuery animations */
    fx_speed: 90, 

    replace_all: function(str, find, replace) {
        if (!str) { return ""; }
        return str.replace(new RegExp(find, 'g'), replace);
    },

    /** Returns the number of times find appears in str */
    count_occurrences: function(str, find) {
        return str.split(find).length - 1;
    },

    substitute: function(str, sub) {
        /*jslint regexp: true */
        return str.replace(/\{(.+?)\}/g, function($0, $1) {
            return sub.hasOwnProperty($1) ? sub[$1] : $0;
        });
    },

    iif: function(cond, yes, no) {
        if (cond) { return yes; } else { return no; }
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
     * Returns true if v is present in array arr.
     * NB: Types must match, int 1 !== str "1"
     */
    array_in: function(v, arr) {
        return $.inArray(v, arr) != -1;
    },

    base64_encode: function(i) {
        return btoa(encodeURIComponent(i));
    },

    base64_decode: function(i) {
        return decodeURIComponent(atob(i));
    },

    /**
     * Generates a type 4 UUID
     */
    generate_uuid: function() {
        // Timestamp
        var d = new Date().getTime(); 
        // Time in microseconds since page-load or 0 if unsupported
        var d2 = (performance && performance.now && (performance.now()*1000)) || 0;
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            var r = Math.random() * 16;//random number between 0 and 16
            if (d > 0){ // Use timestamp until depleted
                r = (d + r) % 16 | 0;
                d = Math.floor(d/16);
            } else { // Use microseconds since page-load if supported
                r = (d2 + r) % 16 | 0;
                d2 = Math.floor(d2/16);
            }
            return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
        });
    },

    /**
     * Generates a random code of length chars 
     */
    generate_random_code: function(length) {
        var result = "";
        var i = 0;
        var c = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
        var cl = c.length;
        for ( i = 0; i < length; i++ ) {
            result += c.charAt(Math.floor(Math.random() * cl));
        }
        return result;
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
     * Copies 'text' to the clipboard.
     * Uses a temporarily created textarea. Note that this has
     * to be called by code spawned from a click event so that
     * a user interaction started it.
     */
    copy_to_clipboard: function(text) {
        var input = document.createElement('textarea');
        input.innerHTML = text;
        document.body.appendChild(input);
        input.select();
        var result = document.execCommand('copy');
        document.body.removeChild(input);
        return result;
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

    browser_is: {
        android: navigator.userAgent.match(/Android/i) != null,
        ios:     navigator.userAgent.match(/iPod|iPad/i) != null,
        chrome:  navigator.userAgent.match(/Chrome/i) != null,
        safari:  navigator.userAgent.match(/Safari/i) != null,
        opera:   navigator.userAgent.match(/Opera/i) != null,
        ie610:   navigator.userAgent.match(/MSIE/i) != null,
        ie11:    navigator.userAgent.match(/rv:11.0/) != null,
        mobile:  navigator.userAgent.match(/Android|iPhone|iPod|BlackBerry|Windows Phone|webOS/i) != null
    },

    /**
     * Returns an object containing name and version parameters
     * for the browser. Uses some funky regex to parse the UA since
     * navigator.appName and navigator.version are completely useless.
     */
    browser_info: function() {
        let ua=navigator.userAgent,
            tem,
            M=ua.match(/(opera|chrome|safari|firefox|msie|trident(?=\/))\/?\s*(\d+)/i) || [];
        if (/trident/i.test(M[1])) {
            tem = /\brv[ :]+(\d+)/g.exec(ua) || []; 
            return { name:'Internet Explorer',version:(tem[1]||'') };
        }   
        if (M[1] === 'Chrome') {
            tem = ua.match(/\bOPR\/(\d+)/);
            if (tem) { return { name: 'Opera', version:tem[1] }; }
            tem = ua.match(/\bEdg\/(\d+)/);
            if (tem) { return { name: 'Edge', version:tem[1] }; }
        }   
        M = M[2]? [M[1], M[2]]: [navigator.appName, navigator.appVersion, '-?'];
        tem = ua.match(/version\/(\d+)/i);
        if (tem) { M.splice(1,1,tem[1]); }
        return { name: M[0], version: M[1] };
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

    trim: function(s) {
        return String(s).trim();
    },

    /** 
     * Used for reading the error message from an AJAX response. 
     * We have this because Safari seems to end up with "Internal Server Error"
     * as the response variable instead of the real error message and 
     * Chrome has just "error".
     */
    get_error_response: function(jqxhr, textstatus, response) {
        var errmessage = String(response);
        if (jqxhr && jqxhr.responseText && jqxhr.responseText.indexOf("Error</h1>") != -1) {
            errmessage = jqxhr.responseText;
            if (errmessage.indexOf("<p>") != -1) {
                errmessage = errmessage.substring(errmessage.indexOf("<p>")+3, errmessage.indexOf("</p>")+4);
            }
        }
        if (!errmessage && textstatus) {
            errmessage = textstatus;
        }
        return errmessage;
    },

    /** Returns a javascript date object representing today without time info */
    today_no_time: function() {
        var d = new Date();
        return new Date(d.getFullYear(), d.getMonth(), d.getDate(), 0, 0, 0);
    },

    /** Adds days to js date */
    add_days: function(date, days) {
        var d = new Date();
        d.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        return d;
    },

    /** Subtracts days from js date */
    subtract_days: function(date, days) {
        var d = new Date();
        d.setTime(date.getTime() + 60 - (days * 24 * 60 * 60 * 1000));
        return d;
    },

    /** Calculates the amount of tax/VAT from amount (an integer currency value)
     *  at rate (integer percentage).
     *  assumes that amount is already inclusive of tax.
     *  Return value is integer currency.
     */
    tax_from_inclusive: function(amount, rate) {
        var realrate = 1 + (rate / 100),
            decamt = amount / 100.0,
            netamt = (decamt / realrate) * 100;
        return amount - netamt;
    },

    /** Calculates the amount of tax/VAT from an amount (an integer currency value)
     * at rate (integer percentage).
     *  assumes that amount is exclusive of tax.
     *  Return value is integer currency.
     */
    tax_from_exclusive: function(amount, rate) {
        return (amount / 100.0) * rate;
    },

    /** URL routing mode - client or server */
    route_mode: "client",

    /** Go to a URL
     * path: The path to go to - eg: animal?id=52
     * forceserver: If set to true, does not use ajax and client routing 
     */
    route: function(path, forceserver) {
        if (!common.route_is_client(path)) { forceserver = true; }
        if (common.route_mode == "server" || forceserver) { window.location = path; return; }
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

        // Listen for history state changes.
        Path.history.listen();

        // Catch all URL clicks to see if we can use client side routing to handle them.
        $(document).on("click", "a", function(e) {
            
            // If dirty validation is active, check if we're
            // ok to leave.
            if (validate.active) {
                if (!validate.a_click_handler(e, $(this).attr("href"))) {
                    return false;
                }
            }
            
            // If CTRL is held down, do what the browser would normally do
            // (open a new window) and allow the navigation
            if (e.ctrlKey) {
                return true;
            }

            // If the URL has a target attribute, allow the browser to
            // use its normal behaviour to open in a new window
            if ($(this).attr("target")) {
                return true;
            }

            // If the clicked anchor goes to a URL we can handle with the
            // client, do it.
            var href = $(this).attr("href");
            if (common.route_is_client(href)) {
                e.preventDefault();
                common.route(href);
                return false;
            }
        });
    },

    /** Returns true if the path supplied can be handled by client side routing */
    route_is_client: function(path) {
        var NOT_CLIENT_SIDE = [ "#", "/", "http", "image?", "document_edit", "document_gen", "document_media_edit", 
            "logout", "lostfound_match", "mailmerge?", "onlineform_incoming_print", "person_lookingfor", 
            "publish_log_view", "report?", "report_export_csv", "sql_dump", "static" ],
            isclient = true;
        if (!path) { return true; }
        if (path.indexOf("ajax=false") != -1) { return false; }
        $.each(NOT_CLIENT_SIDE, function(i, v) {
            if (path.indexOf(v) == 0) { isclient = false; return false; }
        });
        return isclient;
    },

    /** Reload the current route */
    route_reload: function(forceserver) {

        // We're sending everything to server, reload the page
        if (common.route_mode == "server" || forceserver) { window.location.reload(); return; }

        // If the browser doesn't support the history api, reload the page
        // as Path.reload does not work with hash changes.
        if (!Modernizr.history) { window.location.reload(); return; }

        // Reload the current route on the client
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
        if (common.module_unload()) { return; }

        // add a json parameter to only retrieve the controller json document
        uri += (uri.indexOf("?") == -1 ? "?" : "&") + "json=true";
        header.show_loading(_("Loading..."));
        $.ajax({
            type: "GET",
            url: uri,
            cache: false,
            dataType: "text",
            mimeType: "textPlain",
            success: function(result) {
                try {
                    // This can cause an error if the dialog wasn't open
                    header.hide_loading();
                }
                catch (ex) {}

                // If we lost our session at some point, the AJAX request
                // will have been redirected and we'll have the
                // login page. If that's the case, force a reload of
                // the page to get the new version of the application
                // and to follow the redirect back to login
                if (result.indexOf("login.render()") != -1) {
                    common.route_reload(true);
                    return;
                }
                
                // Start the module
                controller = jQuery.parseJSON(result);
                common.module_start(modulename);
            },
            error: function(jqxhr, textstatus, response) {
                try {
                    // This can cause an error if the dialog wasn't open
                    header.hide_loading();
                }
                catch (ex) {}
                var errmessage = common.get_error_response(jqxhr, textstatus, response);
                header.show_error(errmessage);
            }
        });
    },

    /**
     * Starts a module, unloading any active module first.
     * Runs through the lifecycle events of render, bind, sync, title, animation
     * if any throw errors, they're caught and logged at the backend so the 
     * application can recover if necessary.
     */
    module_start: function(modulename) {

        const errhandler = function(name, e) {
            let msg = "accessing " + common.current_url() +
                ", module_start [" + modulename + "]: " + name + ": " + e;
            log.error(msg, e);
            common.ajax_post("jserror", 
                "user=" + encodeURIComponent(asm.user) +
                "&account=" + encodeURIComponent(asm.useraccount) + 
                "&msg=" + encodeURIComponent(msg) + 
                "&stack=" + encodeURIComponent(String(e.stack))
            );
            alert(msg + "\n" + e.stack);
        };

        // do we already have one running? If so, try to unload it first
        if (common.module_unload()) { return; }

        var o = common.modules[modulename];
        $("#asm-body-container").empty(); 
        if (o.render) { 
            try {
                $("#asm-body-container").html(o.render()); 
            }
            catch (exrender) {
                errhandler("render", exrender);
            }
        }
        common.bind_widgets();
        if (o.bind) { 
            try {
                o.bind(); 
            }
            catch (exbind) {
                errhandler("bind", exbind);
            }
        }
        if (o.sync) {
            try {
                o.sync(); 
            }
            catch (exsync) {
                errhandler("sync", exsync);
            }
        }
        if (o.title) { 
            try {
                $(document).attr("title", html.decode(o.title())); 
            }
            catch (extitle) {
                errhandler("title", extitle);
            }
        }
        common.apply_label_overrides(modulename);
        try {
            $("#asm-content").asmcontent(o.animation instanceof Function ? o.animation() : o.animation);
        }
        catch (exanim) {
            errhandler("animation", exanim);
        }
        common.module_running = o;
        if (o.autofocus && !asm.mobileapp) {
            // Datepickers being the target of autofocus inside a containing widget that is
            // not loaded yet (eg: accordion) can cause issues with them trying to render
            // the calendar dropdown too early and in the wrong place. 
            // We leave a 100ms delay before focusing the default widget to make sure
            // other widgets have initialised first.
            setTimeout(function() {
                $(o.autofocus).focus();
            }, 100); 
        }
    },

    /**
     * Unloads the currently loaded module (if one is)
     * returns true if the unload was cancelled.
     */
    module_unload: function() {
        if (common.module_running && common.module_running.destroy) {
            var logprefix = "module_unload [" + common.module_running.name + "]: ";
            try {
                if (common.module_running.destroy()) {
                    return true;
                }
                common.module_running = null;
            }
            catch (exdestroy) {
                log.error(logprefix + "destroy: " + exdestroy);
            }
        }
        return false;
    },

    /**
     * Performs an AJAX POST for text response, handling errors
     * action: The url to post to
     * formdata: The formdata as a string
     * successfunc: The callback function (will pass response)
     * errorfunc: The callback function on error (will include response)
     * returns a promise.
     */
    ajax_post: function(action, formdata, successfunc, errorfunc) {
        var st = new Date().getTime(),
            deferred = $.Deferred();
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

                // If we lost our session at some point, the AJAX request
                // will have been redirected and we'll have been sent the
                // login page. If that's the case, force a reload of
                // the page to get the new version of the application
                // and to follow the redirect back to login
                if (result.indexOf("login.render()") != -1) {
                    common.route_reload(true);
                    deferred.reject("login");
                    return;
                }

                if (successfunc) {
                    successfunc(result, new Date().getTime() - st);
                }
                deferred.resolve(result, new Date().getTime() - st);
            },
            error: function(jqxhr, textstatus, response) {
                try {
                    // This can cause an error if the dialog wasn't open
                    header.hide_loading();
                }
                catch (ex) {}
                var errmessage = common.get_error_response(jqxhr, textstatus, response);
                header.show_error(errmessage);
                if (errorfunc) {
                    errorfunc(errmessage);
                }
                deferred.reject(errmessage);
            }
        });
        return deferred.promise();
    },

    /** 
     * Convenience method for reading a data URL from FileReader.
     * Returns a promise with result.
     */
    read_file_as_data_url: function(file) {
        var reader = new FileReader(),
            deferred = $.Deferred();
        reader.onload = function(e) {
            deferred.resolve(e.target.result);
        };
        reader.onerror = function(e) {
            deferred.reject(reader.error.message);
        };
        reader.readAsDataURL(file);
        return deferred.promise();
    },

    /** 
     * Convenience method for reading an array buffer from FileReader.
     * Returns a promise with result.
     */
    read_file_as_array_buffer: function(fslice) {
        var reader = new FileReader(),
            deferred = $.Deferred();
        reader.onload = function(e) {
            deferred.resolve(e.target.result);
        };
        reader.onerror = function(e) {
            deferred.reject(reader.error.message);
        };
        reader.readAsArrayBuffer(fslice);
        return deferred.promise();
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
        var rv = null;
        if (!idcolumn) { idcolumn = "ID"; }
        $.each(rows, function(i, v) {
            if (v[idcolumn] == id) {
                rv = v;
                return false;
            }
        });
        return rv;
    },

    /*Returns a sorted array of column names that are in tablename
      uses the global schema object. */
    get_table_columns(tablename) {
        let a = [];
        $.each(schema[tablename], function(k, v) {
            a.push(k);
        });
        return a.sort();
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
            o.push(common.trim(v));
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
        // Set the default fx speed for all jQuery transitions
        $.fx.speeds._default = common.fx_speed;
        // Disable effects if the option is set
        if (config.has() && config.bool("DisableEffects")) {
            jQuery.fx.off = true;
        }
        // Disable effects if we're running in the mobile app
        if (asm.mobileapp) {
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
            firstDay: config.integer("FirstDayOfWeek"),
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
        // If we're using an RTL language, load the RTL stylesheet
        if (asm.locale == "ar" || asm.locale == "he") {
            if ($("#rtlcss").length == 0) { // Only add the link if it isn't already there
                $("head").append('<link id="rtlcss" rel="stylesheet" href="static/css/asm-rtl.css?b=' + 
                    asm.build + '" type="text/css">');
            }
        }
        // Create any form controls based on classes used
        $(".asm-callout").callout();
        $(".asm-datebox").date();
        $(".asm-alphanumberbox").alphanumber();
        $(".asm-numberbox").number();
        $(".asm-intbox").intnumber();
        $(".asm-ipbox").ipnumber();
        $(".asm-latlong").latlong();
        $(".asm-timebox").time();
        $(".asm-currencybox").currency();
        $(".asm-phone").phone();
        $(".asm-selectbox, .asm-doubleselectbox, .asm-halfselectbox, .selectbox").select();
        $(".asm-animalchooser").animalchooser();
        $(".asm-animalchoosermulti").animalchoosermulti();
        $(".asm-personchooser").personchooser();
        $(".asm-htmleditor").htmleditor();
        $(".asm-sqleditor").sqleditor();
        $(".asm-textbox, .asm-halftextbox, .asm-doubletextbox").textbox();
        $(".asm-textarea, .asm-textareafixed, .asm-textareafixeddouble").textarea();
        $(".asm-richtextarea").richtextarea();
        $(".asm-table").table();
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
        $(".asm-textbox, .asm-halftextbox, .asm-doubletextbox .asm-selectbox, .asm-richtextarea, .asm-textarea, .asm-textareafixed, .asm-textareafixeddouble").each(function() {
            $(this).addClass("controlshadow").addClass("controlborder");
        });
        // Inject new target attributes for anchors if option is on
        if (this.current_url().indexOf("/login") == -1) {
            this.inject_target();
        }

    },

    /**
     * Goes through all anchor tags in the page. If the system option for
     * opening records in a new tab is set and it's one of our group of
     * new record pages, creates a named target from the url so that the
     * record gets its own browser tab, but links within it still work.
     */
    inject_target: function() {
        var recpages = [ "animal", "incident", "person", "waitinglist", "lostanimal", "foundanimal" ];
        var href, anchor, targetname, r, url = common.current_url();
        if (config.bool("RecordNewBrowserTab")) {
            $("a").each(function() {
                if ($(this).attr("href")) {
                    href = String($(this).attr("href"));
                    anchor = $(this);
                    $.each(recpages, function(i, v) {
                        // If the URL target begins with one of our recpages, it's a candidate
                        // for adding a target attribute for a new tab.
                        if (href.indexOf(v) == 0 && href.indexOf("?") != -1) {
                            // If this is not a find page and the current url we're looking at 
                            // begins with this base page, don't do anything - we don't want 
                            // it to open in a new tab as it's a satellite tab
                            if (url.indexOf("/" + v + "_find") == -1 && url.indexOf("/" + v) != -1) {
                                return;
                            }
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

    /** Called every time a minute has elapsed. If we go over our 
     *  timeout value, we logout. 
     *  Store the inactive time in localStorage so that it is shared
     *  among all open tabs of the application.
     */
    inactive_time_increment: function() {
        var inactive_mins = format.to_int(common.local_get("inactive_mins")) + 1;
        common.local_set("inactive_mins", String(inactive_mins));
        if (inactive_mins > config.integer("InactivityTimeout")) {
            common.inactivity_logout();
        }
    },

    /** Called when keyboard/mouse activity happens to reset the inactive time */
    inactivity_reset: function() {
        common.local_set("inactive_mins", "0");
    },

    /** Called when the inactivity time is up */
    inactivity_logout: function() {
        common.local_delete("inactive_mins");
        var a = "";
        if (asm.useraccount) { a = "?smaccount=" + asm.useraccount; }
        window.location = "logout" + a;
    },

    /** Starts the inactivity timer and binds to key/mouse events. If no timeout
     *  value has been configured, does nothing. */
    start_inactivity_timer: function() {
        common.local_delete("inactive_mins");
        if (!config.bool("InactivityTimer") || config.integer("InactivityTimeout") == 0) { return; }
        setInterval(common.inactive_time_increment, 60000);
        $(document).keypress(common.inactivity_reset);
        $(document).mousemove(common.inactivity_reset);
    },

    /** Destroys a JQuery widget by calling its destroy method.
     * Infers type from selector if it is not supplied:
     *     animal = animalchooser
     *     animals = animalschoosermulti
     *     owner/person = personchooser
     *     dialog- = dialog
     */
    widget_destroy: function(selector, type, noremove) {
        var types = {
            "#animals": "animalchoosermulti",
            "#animal": "animalchooser",
            "#emailbody": "richtextarea",
            "#owner": "personchooser",
            "#person": "personchooser",
            "#retailer": "personchooser",
            "#dialog-": "dialog",
            "#emailform": "emailform",
            "#sql": "sqleditor",
            "#html": "htmleditor"
        };
        if (!type) {
            $.each(types, function(k, v) {
                if (selector.indexOf(k) == 0) { type = v; return false; }
            });
        }
        try {
            if (type == "animalchooser") { 
                $(selector).animalchooser("destroy").remove();
            }
            else if (type == "animalchoosermulti") {
                $(selector).animalchoosermulti("destroy").remove();
            }
            else if (type == "personchooser") {
                $(selector).personchooser("destroy").remove();
            }
            else if (type == "emailform") {
                $(selector).emailform("destroy").remove();
            }
            else if (type == "htmleditor") {
                $(selector).htmleditor("destroy").remove();
            }
            else if (type == "richtextarea") {
                $(selector).richtextarea("destroy").remove();
            }
            else if (type == "sqleditor") {
                $(selector).sqleditor("destroy").remove();
            }
            else if (type == "dialog") {
                if (noremove) {
                    $(selector).dialog("destroy");
                }
                else {
                    $(selector).dialog("destroy").remove();
                }
            }
            else {
                log.error("widget_destroy: invalid type '" + type + "' for selector '" + selector + "'");
            }
        }
        catch (ex) {
            log.trace("widget_destroy: " + selector + " " + type + ",\n" + ex);
        }
    }
};

const config = {
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
            var s = asm.config[key];
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

const dlgfx = {
        delete_show: "explode",
        delete_hide: "explode",
        add_show:    "fade",
        add_hide:    "drop",
        edit_show:   "fade",
        edit_hide:   "drop",
        zoom_show:   "slide",
        zoom_hide:   "slide"
};

const format = {

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
    currency: function(v, commagroups) {
        var nv = parseInt(v, 10) / 100,
            cs = html.decode(asm.currencysymbol),
            rv = "";
        if (isNaN(nv)) { nv = 0; }
        nv = nv.toFixed(asm.currencydp);
        rv = nv.toString();
        // add a group digit separator every 3 digits of the whole numbers
        // (note that radix is swapped below here when fractional portion appended)
        var parts = nv.toString().split(".");
        rv = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, asm.currencydigitgrouping) + (parts[1] ? asm.currencyradix + parts[1] : "");
        // tack the currency symbol onto the beginning or end according to locale
        if (asm.currencyprefix && asm.currencyprefix == "s") {
            rv = rv + cs;
        }
        else {
            rv = cs + rv;
        }
        return rv;
    },

    currency_to_float: function(c) {
        // Remove any HTML entities since the numbers inside will mess us up
        c = c.replace(new RegExp("&[^;]+;", "ig"), '');
        // Remove anything else that isn't a digit, sign or our decimal mark
        c = c.replace(new RegExp("[^0-9\\" + asm.currencyradix + "\\-]", "g"), '');
        c = common.trim(c);
        // Some currency formats (eg: Russian py6. and Indian Rs. have a 
        // dot to finish. If we have a leading dot, it must be one of
        // those formats so remove it.
        if (c.substring(0, 1) == ".") {
            c = c.substring(1);
        }
        // Replace our decimal mark with a ".", as that's all parseFloat understands
        // There should only ever be one of them so standard js replace is ok
        c = c.replace(asm.currencyradix, ".");
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
     * Returns now as an ISO date
     */
    date_now_iso: function() {
        var d = new Date(); 
        return format.padleft(d.getFullYear(), 4) + "-" + 
            format.padleft((d.getMonth() + 1), 2) + "-" + 
            format.padleft(d.getDate(), 2) + "T" +
            format.padleft(d.getHours(), 2) + ":" +
            format.padleft(d.getMinutes(), 2) + ":" +
            format.padleft(d.getSeconds(), 2);
    },

    /**
     * Turns a display date or js date into iso format.
     * null is returned if d is undefined/null
     */
    date_iso: function(d) {
        var time = "00:00:00";
        if (!d) { return null; }
        if (d instanceof Date) {
            return format.padleft(d.getFullYear(), 4) + "-" + 
                format.padleft((d.getMonth() + 1), 2) + "-" + 
                format.padleft(d.getDate(), 2) + "T00:00:00";
        }
        // d is String, Extract time if present
        d = common.trim(d);
        if (d.indexOf(" ") != -1 && d.indexOf(":") != -1) {
            time = d.substring(d.indexOf(" ")+1);
            d = d.substring(0, d.indexOf(" "));
        }
        // Substitute other date separators for / first
        d = d.replace(/[\.\-]/g, "/");
        var dformat = asm.dateformat.replace(/[\.\-]/g, "/");
        // Chop up date and format, then parse
        var fbits = dformat.split("/");
        var dbits = d.split("/");
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
        var rv = year + "-" + month + "-" + day + "T" + time;
        log.trace("format.date_iso: in: '" + d + "', out: '" + rv + "'");
        return rv;
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
        return d.substring(0, d.indexOf("T")+1) + t;
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
     * Given a date, returns a date that corresponds to the first monday of the year
     * according to ISO 8601 rules (the first week of the year has a thursday in it)
     * d: js or iso date
     */
    first_iso_monday_of_year: function(d) {
        var i = 1;
        d = format.date_js(d);
            // Move to the first Thursday of the year
        while (new Date(d.getFullYear(), 0, i).getDay() != 4) { i++; }
        // Move back to the Monday
        return new Date(d.getFullYear(), 0, i - 3 , 0, 0, 0);
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

    numbers_only: function(s) {
        if (!s) { return ""; }
        /*jslint regexp: true */
        return s.replace(/[^\d]/g, "");
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

const html = {

    /**
     * Returns a two-item list containing true if animal a is adoptable and the reason.
     * Looks at current publishing options and uses the same logic as the backend publisher
     */
    is_animal_adoptable: function(a) {
        var p = config.str("PublisherPresets"),
            exwks = format.to_int(common.url_param(p.replace(/ /g, "&"), "excludeunder")),
            locs = common.url_param(p.replace(/ /g, "&"), "includelocations");
        if (a.ISCOURTESY == 1) { return [ true, _("Courtesy Listing") ]; }
        if (a.ISNOTAVAILABLEFORADOPTION == 1) { return [ false, _("Not for adoption flag set") ]; }
        if (a.NONSHELTERANIMAL == 1) { return [ false, _("Non-Shelter") ]; }
        if (a.DECEASEDDATE) { return [ false, _("Deceased") ]; }
        if (a.CRUELTYCASE == 1 && p.indexOf("includecase") == -1) { return [ false, _("Cruelty Case") ]; }
        if (a.NEUTERED == 0 && p.indexOf("includenonneutered") == -1 && 
            common.array_in(String(a.SPECIESID), config.str("AlertSpeciesNeuter").split(","))
            ) { return [ false, _("Unaltered") ]; }
        if (a.HASACTIVERESERVE == 1 && a.RESERVEDOWNERID && p.indexOf("includereserved") == -1) {
            return [ false, _("Reserved") + " " + html.icon("right") + " " + 
                    html.person_link(a.RESERVEDOWNERID, a.RESERVEDOWNERNAME) ];
        }
        if (a.HASACTIVERESERVE == 1 && p.indexOf("includereserved") == -1) { return [ false, _("Reserved") ]; }
        if (a.ISHOLD == 1 && a.HOLDUNTILDATE && p.indexOf("includehold") == -1) { 
            return [ false, _("Hold until {0}").replace("{0}", format.date(a.HOLDUNTILDATE)) ]; 
        }
        if (a.HASFUTUREADOPTION == 1) { return [ false, _("Adopted") ]; }
        if (a.ISHOLD == 1 && p.indexOf("includehold") == -1) { return [ false, _("Hold") ]; }
        if (a.ISQUARANTINE == 1 && p.indexOf("includequarantine") == -1) { return [ false, _("Quarantine") ]; }
        if (a.DECEASEDDATE) { return [ false, _("Deceased") ]; }
        if (a.HASPERMANENTFOSTER == 1) { return [ false, _("Permanent Foster") ]; }
        if (a.ACTIVEMOVEMENTTYPE == 2 && p.indexOf("includefosters") == -1) { return [ false, _("Foster") ]; }
        if (a.ACTIVEMOVEMENTTYPE == 8 && p.indexOf("includeretailer") == -1) { return [ false, _("Retailer") ]; }
        if (a.ACTIVEMOVEMENTTYPE == 1 && a.HASTRIALADOPTION == 1 && p.indexOf("includetrial") == -1) { return [ false, _("Trial Adoption") ]; }
        if (a.ACTIVEMOVEMENTTYPE == 1 && a.HASTRIALADOPTION == 0) { return [ false, _("Adopted") ]; }
        if (a.ACTIVEMOVEMENTTYPE >= 3 && a.ACTIVEMOVEMENTTYPE <= 7) { return [ false, a.DISPLAYLOCATIONNAME ]; }
        if (!a.WEBSITEMEDIANAME && p.indexOf("includewithoutimage") == -1) { return [ false, _("No picture") ]; }
        if (p.indexOf("includewithoutdescription") == -1 && config.bool("PublisherUseComments") && !a.ANIMALCOMMENTS) { return [ false, _("No description") ]; }
        if (p.indexOf("includewithoutdescription") == -1 && !config.bool("PublisherUseComments") && !a.WEBSITEMEDIANOTES) { return [ false, _("No description") ]; }
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
     * Returns true if ADDITIONALFLAGS in s contains flag f
     */
    is_animal_flag: function(s, f) {
        if (!s || !f) { return false; }
        var rv = false;
        $.each(s.split("|"), function(i, v) {
            if (v == f) { rv = true; }
        });
        return rv;
    },

    /**
     * Renders an animal link from the record given.
     * a: An animal or brief animal record
     * o: Options to pass on to animal_emblems
     * o.noemblems: Don't show the emblems
     * o.emblemsright: Show the emblems to the right of the link
     */
    animal_link: function(a, o) {
        var s = "", e = "", animalid = a.ANIMALID || a.ID;
        if (o && o.noemblems) { 
            e = ""; 
        } 
        else { 
            e = html.animal_emblems(a, o) + " "; 
        }
        s = '<a class="asm-embed-name" href="animal?id=' + animalid + '">' + a.ANIMALNAME + ' - ' + 
            (config.bool("UseShortShelterCodes") ? a.SHORTCODE : a.SHELTERCODE) + '</a>';
        if (!o || (o && o.emblemsright)) {
            s += ' ' + e;
        }
        else {
            s = e + ' ' + s;    
        }
        return s;
    },

    /**
     * Renders an animal link thumbnail from the record given
     * a: An animal or brief animal record
     * o: Options to pass on to animal_emblems
     * o.showselector: if true outputs a checkbox to select the animal link
     */
    animal_link_thumb: function(a, o) {
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
        s.push(common.substitute('<a href="animal?id={id}"><img title="{title}" src="{imgsrc}" class="{thumbnailclasses}" /></a><br />', {
            "id" : a.ID,
            "title" : html.title(title),
            "thumbnailclasses": html.animal_link_thumb_classes(a),
            "imgsrc" : html.thumbnail_src(a, "animalthumb") }));
        var emblems = html.animal_emblems(a, o);
        s.push(emblems);
        if (common.count_occurrences(emblems, "title=") >= 3) {
            s.push("<br />");
        }
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
     * Renders a bare animal link thumbnail (just the thumbnail surrounded by a link to the record)
     */
    animal_link_thumb_bare: function(a) {
        var animalid = a.ANIMALID || a.ID,
            classes = html.animal_link_thumb_classes(a); 
        return '<a href="animal?id=' + animalid + '"><img src=' + html.thumbnail_src(a, "animalthumb") + ' class="' + classes + '" /></a>';
    },

    /**
     * Returns the classes for animal thumbnails
     */
    animal_link_thumb_classes: function(a) {
        var sxc = (a.SEX == 0 ? "asm-thumbnail-female" : (a.SEX == 1 ? "asm-thumbnail-male" : ""));
        return "asm-thumbnail thumbnail-shadow " + (config.bool("ShowSexBorder") ? sxc : "");
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
        if (config.bool("EmblemAlwaysLocation")) { 
            o.showlocation = true; 
        }
        s.push("<span class=\"asm-animal-emblems\">");
        if (o && o.showlocation && !a.DECEASEDDATE) {
            if (a.ARCHIVED == 0 && !a.ACTIVEMOVEMENTTYPE && a.SHELTERLOCATIONNAME) {
                s.push(html.icon("location", _("On Shelter") + " / " + a.SHELTERLOCATIONNAME + " " + common.nulltostr(a.SHELTERLOCATIONUNIT)));
            }
            else if (a.ACTIVEMOVEMENTTYPE == 2 && a.DISPLAYLOCATIONNAME && a.CURRENTOWNERNAME && common.has_permission("vo")) {
                s.push(html.icon("person", a.DISPLAYLOCATIONNAME + " / " + a.CURRENTOWNERNAME));
            }
            else if (a.NONSHELTERANIMAL == 0 && a.DISPLAYLOCATIONNAME && a.CURRENTOWNERNAME && common.has_permission("vo")) {
                s.push(html.icon("movement", a.DISPLAYLOCATIONNAME + " / " + a.CURRENTOWNERNAME));
            }
        }
        if (config.bool("EmblemBonded") && (a.BONDEDANIMALID || a.BONDEDANIMAL2ID)) {
            s.push(html.icon("bonded", _("Bonded")));
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
        if (config.bool("EmblemRabies") && !a.RABIESTAG && 
            config.str("AlertSpeciesRabies").split(",").indexOf(String(a.SPECIESID)) != -1) {
            s.push(html.icon("rabies", _("Rabies not given")));
        }
        if (config.bool("EmblemSpecialNeeds") && a.HASSPECIALNEEDS == 1) {
            s.push(html.icon("health", _("Special Needs")));
        }
        if (config.bool("EmblemUnneutered") && a.NEUTERED == 0 && 
            config.str("AlertSpeciesNeuter").split(",").indexOf(String(a.SPECIESID)) != -1) {
            s.push(html.icon("unneutered", _("Unaltered")));
        }
        if (config.bool("EmblemNotMicrochipped") && a.IDENTICHIPPED == 0 && a.NONSHELTERANIMAL == 0 && 
            config.str("AlertSpeciesMicrochip").split(",").indexOf(String(a.SPECIESID)) != -1) {
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
        if (a.POPUPWARNING) {
            s.push(html.icon("warning", String(a.POPUPWARNING)));
        }
        $.each([1,2,3,4,5,6,7,8,9,10], function(i, v) {
            var cflag = config.str("EmblemsCustomFlag" + v), ccond = config.str("EmblemsCustomCond" + v), cemblem = config.str("EmblemsCustomValue" + v);
            if (cflag && cemblem && (ccond == "has" || !ccond) && html.is_animal_flag(a.ADDITIONALFLAGS, cflag)) {
                s.push('<span class="custom" title="' + html.title(cflag) + '">' + cemblem + '</span>');
            }
            if (cflag && cemblem && ccond == "not" && !html.is_animal_flag(a.ADDITIONALFLAGS, cflag)) {
                s.push('<span class="custom" title="' + html.title(_("Not {0}").replace("{0}", cflag)) + '">' + cemblem + '</span>');
            }
        });
        s.push("</span>");
        if (o && o.showunit && a.SHELTERLOCATIONUNIT && a.ARCHIVED == 0 && !a.ACTIVEMOVEMENTTYPE ) {
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
        // If the user does not have permission to see person records, hide events
        // that involve people
        var PEOPLE_EVENTS = { "RESERVED": true, "CANCRESERVE": true, "ADOPTED": true, 
            "FOSTERED": true, "TRANSFER": true, "RECLAIMED": true, "RETAILER": true, 
            "RETURNED": true, "INCIDENTOPEN": true, "INCIDENTCLOSE": true, 
            "LOST": true, "FOUND": true, "WAITINGLIST": true };
        if (PEOPLE_EVENTS[e.CATEGORY] && !common.has_permission("vo")) { return ""; }
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
     * Renders a list of <option> tags for animal flags.
     * It mixes in any additional animal flags to the regular
     * set, sorts them all alphabetically and applies them
     * to the select specified by selector. If an animal record
     * is passed, then it will be checked and selected items
     * will be selected.
     * a: An animal record (or null if not available)
     * flags: A list of extra animal flags from the lookup call
     * node: A jquery dom node of the select box to populate
     * includeall: Have an all/(all) option at the top of the list
     */
    animal_flag_options: function(a, flags, node, includeall) {

        var opt = [];
        var field_option = function(fieldname, post, label) {
            var sel = a && a[fieldname] == 1 ? 'selected="selected"' : "";
            return '<option value="' + post + '" ' + sel + '>' + label + '</option>\n';
        };

        var flag_option = function(flag) {
            var sel = "";
            if (!a || !a.ADDITIONALFLAGS) { sel = ""; }
            else {
                $.each(a.ADDITIONALFLAGS.split("|"), function(i, v) {
                    if (v == flag) {
                        sel = 'selected="selected"';
                    }
                });
            }
            return '<option ' + sel + '>' + flag + '</option>';
        };

        var h = [
            { loc: "any", label: _("Courtesy Listing"), html: field_option("ISCOURTESY", "courtesy", _("Courtesy Listing")) },
            { loc: "on", label: _("Cruelty Case"), html: field_option("CRUELTYCASE", "crueltycase", _("Cruelty Case")) },
            { loc: "any", label: _("Non-Shelter"), html: field_option("NONSHELTERANIMAL", "nonshelter", _("Non-Shelter")) },
            { loc: "on", label: _("Not For Adoption"), html: field_option("ISNOTAVAILABLEFORADOPTION", "notforadoption", _("Not For Adoption")) },
            { loc: "off", label: _("Do Not Publish"), html: field_option("ISNOTAVAILABLEFORADOPTION", "notforadoption", _("Do Not Publish")) },
            { loc: "any", label: _("Do Not Register Microchip"), html: field_option("ISNOTFORREGISTRATION", "notforregistration", _("Do Not Register Microchip")) },
            { loc: "on", label: _("Quarantine"), html: field_option("ISQUARANTINE", "quarantine", _("Quarantine")) }
        ];

        $.each(flags, function(i, v) {
            h.push({ label: v.FLAG, html: flag_option(v.FLAG) });
        });

        h.sort(common.sort_single("label"));

        if (includeall) {
            opt.push('<option value="all">' + _("(all)") + '</option>');
        }

        $.each(h, function(i, v) {
            // Skip if the flag is only for on-shelter and the animal is off-shelter
            if (v.loc == "on" && a && a.ARCHIVED == 1 && a.ACTIVEMOVEMENTTYPE != 2) { return; }
            // Skip if the flag is for off shelter only and the animal is on shelter
            if (v.loc == "off" && a && a.ARCHIVED == 0) { return; }
            opt.push(v.html);    
        });

        node.html(opt.join("\n"));
        node.change();

    },

    /**
     * Renders an accordion panel that contains audit information from
     * the controller
     */
    audit_trail_accordion: function(controller) {
        if (!controller.hasOwnProperty("audit") || !common.has_permission("vatr") || controller.audit.length == 0) {
            return "";
        }
        var h = [
            '<h3><a href="#">' + _("Audit Trail") + '</a></h3>',
            '<div>',
            '<table class="asm-table">',
            '<thead>',
            '<tr>',
            '<th>' + _("Date") + '</th>',
            '<th>' + _("User") + '</th>',
            '<th>' + _("Action") + '</th>',
            '<th>' + _("Table") + '</th>',
            '<th>' + _("Details") + '</th>',
            '</tr>',
            '</thead>',
            '<tbody>'
        ], readableaction = {
            0: _("Add"),
            1: _("Edit"),
            2: _("Delete"),
            3: _("Move"),
            4: _("Login"),
            5: _("Logout"),
            6: _("View"),
            7: _("Report"),
            8: _("Email")
        };
        $.each(controller.audit, function(i, v) {
            if (!config.bool("ShowViewsInAuditTrail") && v.ACTION == 6) { return; }
            h.push('<tr>');
            h.push('<td>' + format.date(v.AUDITDATE) + ' ' + format.time(v.AUDITDATE) + '</td>');
            h.push('<td>' + v.USERNAME + '</td>');
            h.push('<td>' + readableaction[v.ACTION] + '</td>');
            h.push('<td>' + v.TABLENAME + '</td>');
            h.push('<td>' + v.DESCRIPTION + '</td>');
            h.push('</tr>');
        });
        h.push('</tbody>');
        h.push('</table>');
        h.push('</div>');
        return h.join("\n");
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
    person_flag_options: function(p, flags, node, include_all, include_previous_adopter) {

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
            { label: _("Adopter"), html: field_option("ISADOPTER", "adopter", _("Adopter")) },
            { label: _("Adoption Coordinator"), html: field_option("ISADOPTIONCOORDINATOR", "coordinator", _("Adoption Coordinator")) },
            { label: _("Banned"), html: field_option("ISBANNED", "banned", _("Banned")) },
            { label: _("Deceased"), html: field_option("ISDECEASED", "deceased", _("Deceased")) },
            { label: _("Donor"), html: field_option("ISDONOR", "donor", _("Donor")) },
            { label: _("Driver"), html: field_option("ISDRIVER", "driver", _("Driver")) },
            { label: _("Exclude from bulk email"), html: field_option("EXCLUDEFROMBULKEMAIL", "excludefrombulkemail", _("Exclude from bulk email")) },
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

        if (include_previous_adopter) {
            h.push({ label: _("Previous Adopter"), html: field_option("", "padopter", _("Previous Adopter"))});
        }

        $.each(flags, function(i, v) {
            h.push({ label: v.FLAG, html: flag_option(v.FLAG) });
        });

        h.sort(common.sort_single("label"));

        if (include_all) {
            opt.push('<option value="all">' + _("(all)") + '</option>');
        }

        $.each(h, function(i, v) {
            opt.push(v.html);    
        });

        node.html(opt.join("\n"));
        node.change();

    },

    /**
     * Returns a link to a person with the address below - 
     * but only if the view person permission is set
     */
    person_link_address: function(row) {
        if (!common.has_permission("vo")) { return _("Forbidden"); }
        return html.person_link(row.OWNERID, row.OWNERNAME) +
            '<br/>' + common.nulltostr(row.OWNERADDRESS) + 
            '<br/>' + common.nulltostr(row.OWNERTOWN) + 
            '<br/>' + common.nulltostr(row.OWNERCOUNTY) + ' ' + common.nulltostr(row.OWNERPOSTCODE) + 
            '<br/>' + common.nulltostr(row.HOMETELEPHONE) + " " + common.nulltostr(row.WORKTELEPHONE) + " " + common.nulltostr(row.MOBILETELEPHONE);
    },

    /**
     * Returns a link to a person - but only if the view person permission is set
     * to hide their name.
     * personid: The person ID
     * name: The person name
     */
    person_link: function(personid, name) {
        var h = "";
        if (!name) { name = ""; }
        if (common.has_permission("vo")) {
            h = '<a href="person?id=' + personid + '">' + name + '</a>';
        }
        return h;
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
            // Just return the string as is if there are no html entities in there
            // to save unnecessary creating of DOM elements.
            if (String(s).indexOf("&") == -1) { return s; }
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
                if (v.hasOwnProperty("label")) {
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
     * Returns a text bar containing s with options o
     * id: The containing div id
     * display: (no default, css display parameter of container)
     * state: highlight (default) | error 
     * icon: info (default, jquery ui icon)
     * padding: (default 5px)
     * margintop: (default not set)
     */
    textbar: function(s, o) {
        let containerid = "", display = "", state = "highlight", icon = "info", padding = "", margintop = "";
        if (!o) { o = {}; }
        if (!o.padding) { o.padding = "5px"; }
        if (o.id) { containerid = 'id="' + o.id + '"'; }
        if (o.display) { display = "display: " + o.display + ";"; }
        if (o.state) { state = o.state; }
        if (o.icon) { icon = o.icon; }
        if (o.padding) { padding = "padding: " + o.padding + ";"; }
        if (o.margintop) { margintop = "margin-top: " + o.margintop + ";"; }
        return [
            "<div class=\"ui-widget\" " + containerid + " style=\"" + margintop + display + "\">",
            "<div class=\"ui-state-" + state + " ui-corner-all\" style=\"" + padding + "\"><p>",
            "<span class=\"ui-icon ui-icon-" + icon + "\"></span>",
            s,
            "</p></div></div>"
        ].join("\n");
       
    },

    /**
     * Returns an error bar, with error icon and the text supplied
     */
    error: function(s, id) {
        return html.textbar(s, { "id": id, "state": "error", "icon": "alert" });
    },

    /**
     * Returns an info bar, with info icon and the text supplied
     */
    info: function(s, id) {
        return html.textbar(s, { "id": id });
    },

    /**
     * Returns an warning bar, with warning icon and the text supplied
     */
    warn: function(s, id) {
        return html.textbar(s, { "id": id, "icon": "alert" });
    },

    /**
     * Reads a list of objects and produces HTML options from it.
     * If valueprop is undefined, we assume a single list of elements.
     *     if the values have a pipe delimiter, we assume value/label pairs
     * l: The list object
     * valueprop: The name of the value property
     * displayprop: The name of the display property
     */
    list_to_options: function(l, valueprop, displayprop) {
        var h = "", retired = "";
        $.each(l, function(i, v) {
            if (!valueprop) {
                if (v.indexOf("|") == -1) {
                    h += "<option value=\"" + html.title(v) + "\">" + v + "</option>";
                }
                else {
                    h += "<option value=\"" + v.split("|")[0] + "\">" + v.split("|")[1] + "</option>";
                }
            }
            else {
                retired = "";
                if (v.ISRETIRED && v.ISRETIRED == 1) { retired = "data-retired=\"1\""; }
                h += "<option " + retired + " value=\"" + v[valueprop] + "\">" + v[displayprop] + "</option>\n";
            }
        });
        return h;
    },

    /**
     * Special list to options for breeds, outputs an 
     * option group for each species
     */
    list_to_options_breeds: function(l) {
        var h = [], spid = 0, retired = "";
        $.each(l, function(i, v) {
            if (v.SPECIESID != spid) {
                if (spid != 0) {
                    h.push("</optgroup>");
                }
                spid = v.SPECIESID;
                h.push("<optgroup id='ngp-" + v.SPECIESID + "' label='" + v.SPECIESNAME + "'>");
            }
            retired = "";
            if (v.ISRETIRED && v.ISRETIRED == 1) { retired = "data-retired=\"1\""; }
            h.push("<option " + retired + " value=\"" + v.ID + "\">" + v.BREEDNAME + "</option>\n");
        });
        return h.join("\n");
    },

    data_url_to_array_buffer: function(url) {
        var bytestring = window.atob(url.split(",")[1]);
        var bytes = new Uint8Array(bytestring.length);
        for (var i = 0; i < bytestring.length; i++) {
            bytes[i] = bytestring.charCodeAt(i);
        }
        return bytes.buffer;
    },

    /** Get the EXIF orientation for file 1-8. 
     *  Also returns -2 (not jpeg) and -1 (no orientation found).
     *  Asynchronous and returns a promise. */
    get_exif_orientation: function(file) {
        var deferred = $.Deferred();
        common.read_file_as_array_buffer(file.slice(0, 64 * 1024))
        .then(function(result) {
            var view = new DataView(result);
            if (view.getUint16(0, false) != 0xFFD8) {
                deferred.resolve(-2);
                return;
            }
            var length = view.byteLength,
                offset = 2;
            while (offset < length) {
                var marker = view.getUint16(offset, false);
                offset += 2;
                if (marker == 0xFFE1) {
                    if (view.getUint32(offset += 2, false) != 0x45786966) {
                        deferred.resolve(-1);
                        return;
                    }
                    var little = view.getUint16(offset += 6, false) == 0x4949;
                    offset += view.getUint32(offset + 4, little);
                    var tags = view.getUint16(offset, little);
                    offset += 2;
                    for (var i = 0; i < tags; i++)
                        if (view.getUint16(offset + (i * 12), little) == 0x0112) {
                            deferred.resolve(view.getUint16(offset + (i * 12) + 8, little));
                            return;
                        }
                }
                else if ((marker & 0xFF00) != 0xFF00) break;
                else offset += view.getUint16(offset, false);
            }
            deferred.resolve(-1);
            return;
        });
        return deferred.promise();
    },

    /**
     * Loads an img element from a file. 
     * Returns a promise, the result is the loaded img.
     */
    load_img: function(file) {
        var reader = new FileReader(),
            img = document.createElement("img"),
            deferred = $.Deferred();
        reader.onload = function(e) {
            img.src = e.target.result;
        };
        reader.onerror = function(e) {
            deferred.reject(reader.error.message);
        };
        img.onload = function() {
            deferred.resolve(img);
        };
        reader.readAsDataURL(file);
        return deferred.promise();
    },

    /** Applies a canvas transformation based on the EXIF orientation passed.
     *  The next drawImage will be rotated correctly. 
     *  It also resizes the canvas if the orientation changes.
     *  If the web browser oriented the image before rendering to the canvas, does nothing.
     **/
    rotate_canvas_to_exif: function(canvas, ctx, orientation) {
        // This web browser already rotated the image when it was loaded, do nothing
        if (Modernizr.exiforientation) { return; }
        var width = canvas.width,
            height = canvas.height;
        if (4 < orientation && orientation < 9) {
            canvas.width = height;
            canvas.height = width;
        } 
        else {
            canvas.width = width;
            canvas.height = height;
        }
        switch (orientation) {
            case 2: ctx.transform(-1, 0, 0, 1, width, 0); break;
            case 3: ctx.transform(-1, 0, 0, -1, width, height); break;
            case 4: ctx.transform(1, 0, 0, -1, 0, height); break;
            case 5: ctx.transform(0, 1, 1, 0, 0, 0); break;
            case 6: ctx.transform(0, 1, -1, 0, height, 0); break;
            case 7: ctx.transform(0, -1, -1, 0, height, width); break;
            case 8: ctx.transform(0, -1, 1, 0, 0, width); break;
            default: break;
        }
    },

    /**
     * Scales and rotates Image object img to h and w px, returning a data URL.
     * Depending on the size of the image, chooses an appropriate number
     * of steps to avoid aliasing. Handles rotating the image first
     * via its Exif orientation (1-8).
     */
    scale_image: function(img, w, h, orientation) {
        var scaled;
        if (img.height > h * 2 || img.width > w * 2) { 
            scaled = html.scale_image_2_step(img, w, h, orientation); 
        }
        else {
            scaled = html.scale_image_1_step(img, w, h, orientation);
        }
        return scaled;
    },

    /**
     * Scales DOM element img to h and w, returning a data URL.
     */
    scale_image_1_step: function(img, w, h, orientation) {
        var canvas = document.createElement("canvas"),
            ctx = canvas.getContext("2d");
        canvas.height = h;
        canvas.width = w;
        html.rotate_canvas_to_exif(canvas, ctx, orientation);
        ctx.drawImage(img, 0, 0, w, h);
        return canvas.toDataURL("image/jpeg");
    },

    /**
     * Scales DOM element img to h and w, returning a data URL.
     * Uses a two step process to avoid aliasing.
     */
    scale_image_2_step: function(img, w, h, orientation) {
        var canvas = document.createElement("canvas"),
            ctx = canvas.getContext("2d"),
            oc = document.createElement("canvas"),
            octx = oc.getContext("2d");
        canvas.height = h;
        canvas.width = w;
        // step 1 - render the image at 50% of its size to the first canvas
        oc.width = img.width * 0.5;
        oc.height = img.height * 0.5;
        octx.drawImage(img, 0, 0, oc.width, oc.height);
        // step 2 / final - render the 50% sized canvas to the final canvas at the correct size
        html.rotate_canvas_to_exif(canvas, ctx, orientation);
        ctx.drawImage(oc, 0, 0, oc.width, oc.height, 0, 0, w, h);
        return canvas.toDataURL("image/jpeg");
    },

    /**
     * Looks up the manufacturer for a given microchip number.
     * selnumber: DOM selector for the input containing the number
     * selbrand:  DOM selector for the label showing the manufacturer
     */
    microchip_manufacturer: function(selnumber, selbrand) {
        var m, n = $(selnumber).val();
        if (!n) { $(selbrand).fadeOut(); return; }
        $.each(asm.microchipmanufacturers, function(i, v) {
            if (n.length == v.length && new RegExp(v.regex).test(n)) {
                if (v.locales == "" || common.array_in(asm.locale, v.locales.split(" "))) {
                    m = "<span style='font-weight: bold'>" + v.name + "</span>";
                    return false;
                }
            }
        });
        if (!m && (n.length != 9 && n.length != 10 && n.length != 15)) {
            m = "<span style='font-weight: bold; color: red'>" + _("Invalid microchip number length") + "</span>";
        }
        if (!m) {
            m = "<span style='font-weight: bold; color: red'>" + _("Unknown microchip brand") + "</span>";
        }
        $(selbrand).html(m);
        $(selbrand).fadeIn();
    },

    /** Returns a list of all US states as a set of option tags */
    states_us_options: function(selected) {
        let US_STATES = [ ["Alabama","AL"], ["Alaska","AK"], ["Arizona","AZ"], ["Arkansas","AR"], ["American Samoa","AS"], 
            ["California","CA"], ["Colorado","CO"], ["Connecticut","CT"], ["District of Columbia","DC"], ["Delaware","DE"], 
            ["Florida","FL"], ["Federated States of Micronesia","FM"], ["Georgia","GA"], ["Guam","GU"], ["Hawaii","HI"], 
            ["Idaho","ID"], ["Illinois","IL"], ["Indiana","IN"], ["Iowa","IA"], ["Kansas","KS"], ["Kentucky","KY"], 
            ["Louisiana","LA"], ["Maine","ME"], ["Marshall Islands","MH"], ["Maryland","MD"], ["Massachusetts","MA"], 
            ["Michigan","MI"], ["Minnesota","MN"], ["Mississippi","MS"], ["Missouri","MO"], ["Montana","MT"], ["Nebraska","NE"], 
            ["Nevada","NV"], ["New Hampshire","NH"], ["New Jersey","NJ"], ["New Mexico","NM"], ["New York","NY"],
            ["North Carolina","NC"], ["North Dakota","ND"], ["Northern Mariana Islands","MP"], ["Ohio","OH"], ["Oklahoma","OK"], 
            ["Oregon","OR"], ["Palau","PW"], ["Pennsylvania","PA"], ["Puerto Rico","PR"], ["Rhode Island","RI"], 
            ["South Carolina","SC"], ["South Dakota","SD"], ["Tennessee","TN"], ["Texas","TX"], ["Utah","UT"],
            ["Vermont","VT"], ["Virgin Islands","VI"], ["Virginia","VA"], ["Washington","WA"], ["West Virginia","WV"], 
            ["Wisconsin","WI"],["Wyoming","WY"]
        ], opts = [ '<option value=""></option>' ];
        $.each(US_STATES, function(i, v) {
            let sel = common.iif(selected == v[1], 'selected="selected"', '');
            opts.push('<option value="' + v[1] + '" ' + sel + '>' + v[1] + " - " + v[0] + '</option>');
        });
        return opts.join("\n");
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
        s = String(s);
        s = common.replace_all(s, "\"", "&quot;");
        s = common.replace_all(s, "'", "&apos;");
        return s;
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
            return "image?db=" + asm.useraccount + "&mode=nopic";
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
            return "image?db=" + asm.useraccount + "&mode=nopic";
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

const log = {

    level: 1,

    trace: function(s) {
        if (log.level > 0) { return; }
        log.console_log("TRACE: " + s);
    },

    debug: function(s) {
        if (log.level > 1) { return; }
        log.console_log("DEBUG: " + s);
    },

    info: function(s) {
        if (log.level > 2) { return; }
        log.console_log("INFO: " + s);
    },

    warn: function(s) {
        if (log.level > 3) { return; }
        log.console_log("WARN: " + s);
    },

    error: function(s, e) {
        if (log.level > 4) { return; }
        if (!window.console) { return; }
        if (e) {
            console.log("ERROR: " + s, "from", e.stack);
        }
        else {
            console.log("ERROR: " + s);
        }
    },

    console_log: function(str) {
        if (window.console) { console.log(str); }
    }
};

const validate = {

    /* Whether or not validation is currently active */
    active: false,

    /* Global for whether or not there are unsaved changes */
    unsaved: false,

    /* The CSS class to be applied to labels that are in error -
        * used to be ui-state-error-text for JQUI but it quite often
        * produces white text on a white background??? */
    ERROR_LABEL_CLASS: "asm-error-text",

    /**
     * Does all binding for dirtiable forms.
     * 1. Watches for controls changing and marks the form dirty.
     * 2. If we are in server routing mode, adds a delegate listener 
     *    to links and fires the unsaved dialog if necessary.
     * 3. Catches beforeunload to prevent navigation away if dirty
     */
    bind_dirty: function() {
        // Watch for control changes and call dirty()
        // These are control keys that should not trigger form dirtying (tab, cursor keys, ctrl/shift/alt, windows key, scroll up, etc)
        // See http://www.javascriptkeycode.com/
        const ctrl_keys = [ 9, 16, 17, 18, 19, 20, 27, 33, 34, 35, 36, 37, 38, 39, 
            40, 45, 91, 92, 93, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 144, 145 ];
        const dirtykey = function(event) { if (ctrl_keys.indexOf(event.keyCode) == -1) { validate.dirty(true); } };
        const dirtychange = function(event) { validate.dirty(true); };
        validate.active = true;
        $("#asm-content .asm-checkbox").change(dirtychange);
        $("#asm-content .asm-datebox").change(dirtychange);
        $("#asm-content .asm-selectbox, #asm-content .asm-doubleselectbox, #asm-content .asm-halfselectbox, #asm-content .selectbox, #asm-content .asm-bsmselect").change(dirtychange);
        $("#asm-content .asm-textbox, #asm-content .asm-doubletextbox, #asm-content .asm-halftextbox, #asm-content .asm-textarea, #asm-content .asm-richtextarea, #asm-content .asm-textareafixed, #asm-content .asm-textareafixeddouble").change(dirtychange);
        $("#asm-content .asm-textbox, #asm-content .asm-doubletextbox, #asm-content .asm-halftextbox, #asm-content .asm-textarea, #asm-content .asm-richtextarea, #asm-content .asm-textareafixed, #asm-content .asm-textareafixeddouble").bind("paste", dirtychange).bind("cut", dirtychange);
        $("#asm-content .asm-textbox, #asm-content .asm-doubletextbox, #asm-content .asm-halftextbox, #asm-content .asm-textarea, #asm-content .asm-richtextarea, #asm-content .asm-textareafixed, #asm-content .asm-textareafixeddouble").keyup(dirtykey);
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
        // Default state
        validate.dirty(false);
        // Fix for Chrome 79.0.3925+ bug. 
        // https://chromium.googlesource.com/chromium/src/+/8bdd4fc873801be72f20f7cb5746059526098d99
        // A race condition causes Chrome to reload saved control state into the wrong input fields
        // when the user clicks back from a non-client route page (typically preferred pictures or reports).
        // Here, we detect that the page was loaded by the back button and force a full reload to work around it #716
        // We do it here because it only affects bottom level screens with input fields that require the dirty/save functionality.
        if (common.browser_is.chrome && window.performance && window.performance.navigation.type === window.performance.navigation.TYPE_BACK_FORWARD) {
            window.location.reload();
        }

    },

    unbind_dirty: function() {
        validate.active = false;
        window.onbeforeunload = function() {};
    },

    a_click_handler: function(event, href) {
        // If the URL starts with a hash, don't do anything as it wouldn't
        // be navigating away from the page.
        if (!href) { href = $(this).attr("href"); }
        if (href.indexOf("#") != 0) {
            if (validate.unsaved) {
                event.preventDefault();
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
            $(this).dialog("close"); 
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

    /* Given a field ID, highlights the label and focuses the field. */
    highlight: function(fid) {
        $("label[for='" + fid + "']").addClass(validate.ERROR_LABEL_CLASS);
        $("#" + fid).focus();
    },

    /* Accepts an array of IDs and adds a marker to the field label to show
     * that there is validation on those fields */
    indicator: function(fields) {
        $.each(fields, function(i, f) {
            $("label[for='" + f + "']").after('&nbsp;<span class="asm-has-validation">*</span>');
        });
    },

    /* Given a container ID, removes highlighting from all the labels
        * if container is not supplied, #asm-content is assumed
        */
    reset: function(container) {
        if (!container) { container = "asm-content"; }
        $("#" + container + " label").removeClass(validate.ERROR_LABEL_CLASS);
    },

    /* Accepts an array of ids to test whether they're blank or not
        if they are, their label is highlighted and false is returned */
    notblank: function(fields) {
        var rv = true;
        $.each(fields, function(i, f) {
            var v = $("#" + f).val();
            v = common.trim(v);
            if (v == "") {
                validate.highlight(f);
                rv = false;
                return false;
            }
        });
        return rv;
    },

    /**
     * Validates one or more email addresses separated by commas.
     * Shows a global error and returns false if one or more of the addresses is invalid.
     */
    email: function(v) {
        /*jslint regexp: true */
        var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        var rv = true;
        $.each(v.split(","), function(i, e) {
            e = common.trim(e);
            if (e.indexOf("<") != -1 && e.indexOf(">") != -1) { e = e.substring(e.indexOf("<")+1, e.indexOf(">")); }
            if (!re.test(String(e).toLowerCase())) { 
                rv = false; 
                header.show_error(_("Invalid email address '{0}'").replace("{0}", e));
            }
        });
        return rv;
    },

    /** Accepts an array of ids to test whether they're zero or not
     *  if they are, their label is highlighted and false is returned */
    notzero: function(fields) {
        var rv = true;
        $.each(fields, function(i, f) {
            var v = $("#" + f).val();
            v = common.trim(v);
            if (v == "0") {
                validate.highlight(f);
                rv = false;
                return false;
            }
        });
        return rv;
    },

    /**
     * Accepts an array of ids to email fields to test whether they're valid
     * valid values are blank, a single email address or multiple email addresses
     */
    validemail: function(fields) {
        var rv = true;
        $.each(fields, function(i, f) {
            var v = $("#" + f).val();
            v = common.trim(v);
            if (v != "" && !validate.email(v)) {
                validate.highlight(f);
                rv = false;
                return false;
            }
        });
        return rv;
    },

    /**
     * Accepts an array of ids to time fields test whether they're valid
     * times. Valid values are a blank or 00:00 or 00:00:00
     * if they are invalid, their label is highlighted and false is returned */
    validtime: function(fields) {
        var rv = true, valid1 = /^\d\d\:\d\d\:\d\d$/, valid2 = /^\d\d\:\d\d$/;
        $.each(fields, function(i, f) {
            var v = $("#" + f).val();
            v = common.trim(v);
            if (v != "" && !valid1.test(v) && !valid2.test(v)) {
                // Times rarely have their own label, instead look for the label
                // in the same table row as our widget
                $("#" + f).closest("tr").find("label").addClass(validate.ERROR_LABEL_CLASS);
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
    }

};

// add a class to the html element for desktop or mobile
// this allows asm.css to change some elements if it is running
// inside the mobile app context
if (typeof asm !== "undefined" && asm.mobileapp) { 
    $("html").removeClass("desktop").addClass("mobile");
}
else { 
    $("html").removeClass("mobile").addClass("desktop");
}

// Prevent annoying Firefox errors where it tries to parse all
// ajax responses that don't have a mimetype as XML - override
// it to assume plain text
// Also, do not cache any GET requests (adds an extra parameter)
// as there is no scenario where ASM would make an Ajax GET
// for something where a cached copy would do.
$.ajaxSetup({ 
    mimeType: "text/plain",
    cache: false
});

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

// Hide broken thumbnail animal images instead of showing the icon
// On reflection, better to show the broken thumbnail than hide it.
// $(document).on("error", ".asm-thumbnail", function() {
//    $(this).hide();
//});

// If an inactivity timeout is configured, starts the timer
common.start_inactivity_timer();

