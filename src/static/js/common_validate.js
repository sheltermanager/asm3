/*global $, console, performance, jQuery, FileReader, Modernizr, Mousetrap, Path */
/*global alert, asm, common, dlgfx, schema, atob, btoa, header, _, escape, unescape, navigator */
/*global validate: true */

"use strict";

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
        b[_("Save and leave")] = {
            text: _("Save and leave"),
            "class": 'asm-dialog-actionbutton',
            click: function() {
                $(this).dialog("close"); 
                self.save(function() {
                    common.route(target);
                });
            }
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
     * Returns true if the address is valid.
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


