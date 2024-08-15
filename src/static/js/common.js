/*global $, console, performance, jQuery, FileReader, Mousetrap, Path */
/*global alert, atob, btoa, confirm, header, _, escape, unescape, navigator */
/*global asm, schema, validate */
/*global consts: true, common: true, config: true, controller: true, dlgfx: true, format: true, log: true */

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

    /** Substitutes {token} in str for token key in sub dict */
    substitute: function(str, sub) {
        /*jslint regexp: true */
        return str.replace(/\{(.+?)\}/g, function($0, $1) {
            return sub.hasOwnProperty($1) ? sub[$1] : $0;
        });
    },

    /** Looks for {0}, {1}, {2} etc and replaces them with that element of array arr */
    sub_arr: function(str, arr) {
        $.each(arr, function(i, l) {
            str = str.replace("{" + i + "}", l);
        });
        return str;
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
    generate_random_code: function(length, onlynumbers) {
        var result = "";
        var i = 0;
        var c = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
        if (onlynumbers) { c = "0123456789"; }
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
        try {
            if (typeof(Storage) === "undefined") { return ""; }
            if (localStorage[name]) { return localStorage[name]; }
            return "";
        }
        catch (ex) {
            log.warn("local_get: failed accessing localStorage: " + ex);
            return "";
        }
    },

    /**
     * Sets a value in HTML5 local storage. Value must be a string.
     */
    local_set: function(name, value) {
        try {
            if (typeof(Storage) !== "undefined") {
                localStorage[name] = value;
            }
        }
        catch (ex) {
            log.warn("local_set: failed accessing localStorage: " + ex);
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
            catch (ex) {
                log.warn("local_delete: failed accessing localStorage: " + ex);
            }
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
     * Copies all properties from source to target, returning target
     * Basically Object.assign
     */
    copy_object: function(target, source) {
        for (var key in source) {
            if (source.hasOwnProperty(key)) {
                target[key] = source[key];
            }
        }
        return target;
    },

    /**
     * Returns true if v is an array
     */
    is_array: function(v) {
        return v instanceof Array || Object.prototype.toString.call(v) === '[object Array]';
    },

    /**
     * Returns true if the browser is in dark mode
     */
    is_dark_mode: function() {
        return (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
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
        ios:     navigator.userAgent.match(/iPod|iPad|iPhone/i) != null,
        chrome:  navigator.userAgent.match(/Chrome/i) != null,
        edge:    navigator.userAgent.match(/Edge/i) != null,
        safari:  navigator.userAgent.match(/Safari/i) != null,
        opera:   navigator.userAgent.match(/Opera/i) != null,
        ie610:   navigator.userAgent.match(/MSIE/i) != null,
        ie11:    navigator.userAgent.match(/rv:11.0/) != null,
        mobile:  navigator.userAgent.match(/Android|iPhone|iPod|iPad|BlackBerry|Windows Phone|webOS/i) != null
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

    /** Used for containers, returns the min of h and the viewport height */
    vheight: function(h) {
        return Math.min(h, $(window).height());
    },

    /** Used for containers, returns the min of w and the viewport width */
    vwidth: function(w) {
        return Math.min(w, $(window).width());
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
        if (!date) { return date; } // If date is null, return null
        var d = new Date();
        d.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        return d;
    },

    /** Subtracts days from js date */
    subtract_days: function(date, days) {
        if (!date) { return date; } // If date is null, return null
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
        // NO LONGER NEEDED, can't run ASM on anything that doesn't support history api
        // if (!Modernizr.history) { window.location.reload(); return; }

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
            // If user clicks OK, reloads /main to apply any database updates, reload config.js, etc.
            if (confirm(msg + "\n" + e.stack)) { window.location = "main"; }
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
                $(document).attr("title", format.decode_html_str(o.title())); 
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
        if (o.autofocus && !common.browser_is.mobile) {
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
     * Performs an AJAX GET for text response, handling errors
     * action: The url to post to
     * formdata: The formdata as a string
     * successfunc: The callback function (will pass response)
     * errorfunc: The callback function on error (will include response)
     * returns a promise.
     */
    ajax_get: function(action, formdata, successfunc, errorfunc) {
        var st = new Date().getTime(),
            deferred = $.Deferred();
        $.ajax({
            type: "GET",
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
                try {
                    // This can cause an error if header is not loaded
                    header.show_error(errmessage);
                }
                catch (ex) {}
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
        // Updating codemirror from 5.11 to 5.65 changed the columns from a
        // dictionary to a list, so this is no longer needed.
        //$.each(schema[tablename], function(k, v) {
        //    a.push(k);
        //});
        //return a.sort();
        return schema[tablename].sort();
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
     * Allows a config option LabelOverrides_module to be set that
     * contains a list of triplets containing selector, item to 
     * change and new value. A hat ^ is used instead of string delimiters Eg:
     * insert into configuration values ('LabelOverrides_animal', 'label[for=^sheltercode^]|text|New Code')
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
     * Applies the visual theme by loading the correct CSS file 
     */
    apply_theme: function(theme, bg) {
        let href = $("#jqt").attr("href");
        href = href.substring(0, href.indexOf("themes/")) + "themes/" + theme + "/jquery-ui.css";
        $("#jqt").attr("href", href);
        $("body").css("background-color", bg);
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
        // Disable effects if we're running on mobile
        if (common.browser_is.mobile) {
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
        if (_ && !$(".asm-bsmselect").attr("title")) {
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
            "#createpayment": "createpayment",
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
            else if (type == "createpayment") { 
                $(selector).createpayment("destroy").remove();
            }
            else if (type == "emailform") {
                $(selector).emailform("destroy").remove();
            }
            else if (type == "htmleditor") {
                $(selector).htmleditor("destroy").remove();
            }
            else if (type == "personchooser") {
                $(selector).personchooser("destroy").remove();
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
        let s = this.str(key);
        let i = parseInt(s, 10);
        if (isNaN(i)) { return 0; }
        return i;
    },

    number: function(key) {
        let s = this.str(key);
        let f = parseFloat(s);
        if (isNaN(f)) { return 0; }
        return f;
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
            cs = format.decode_html_str(asm.currencysymbol),
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
     * Returns now as a display date
     */
    date_now: function() {
        return format.date(new Date());
    },

    /**
     * Returns now as a display date and time
     */
    datetime_now: function() {
        return format.date_now() + " " + format.time_now();
    },

    /**
     * Returns the difference in days between date1 and date2 (both js Date())
     * Uses abs around the subtraction so it does not matter if date1 > date2
     */
    date_diff_days: function(date1, date2) {
        const dt = Math.abs(date2 - date1);
        const dd = Math.ceil(dt / (1000 * 60 * 60 * 24)); 
        return dd;
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
     * Decodes HTML entities in a string
     */
    decode_html_str: function(s) {
        // Just return the string as is if there are no html entities in there
        // to save unnecessary creating of DOM elements.
        if (String(s).indexOf("&") == -1) { return s; }
        try {
            return $("<div></div>").html(s).text();
        }
        catch(err) {
            return "";
        }
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

    /**
     * Returns the time now for display
     */
    time_now: function() {
        return format.time(new Date());
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

// add a class to the html element for desktop or mobile
// this allows asm.css to change some elements if it is running
// on a mobile device.
if (common.browser_is.mobile) { 
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

