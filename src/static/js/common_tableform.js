/*global $, jQuery, Mousetrap */
/*global asm, common, config, dlgfx, format, html, validate, header, _, escape, unescape */
/*global tableform: true */

"use strict";

const tableform = {

    /**
     * Renders a toolbar button set. 
     *
     * buttons: [
     *      { id: "new", text: _("Text"), tooltip: _("Tooltip"), icon: "iconname", enabled: "always|multi|one", perm: "va", hideif: function() {}, click: tableform.click_delete }
     *      { id: "buttonmenu", type: "buttonmenu", text: _("Text"), tooltip: _("Tooltip"), icon: "iconname", enabled: "always|multi|one", 
     *          hideif: function() {}, click: function(selval) {}}
     *      { id: "dropdownfilter", type: "dropdownfilter", options: [ "value1|text1", "value2|text2" ] }
     *      { type: "raw", markup: "<span>" }
     * ]
     * options: 
     *      centered: false, // whether to center buttons within the container
     *      render_container: true, // whether to render the toolbar container
     *      id: "tb", // id attribute of the toolbar container 
     */
    buttons_render: function(buttons, coptions) {
        let b = "", toolbarid = "", centered = "", 
            options = { centered: false, render_container: true, id: "" };
        if (coptions !== undefined) { options = common.copy_object(options, coptions); }
        if (options.render_container) {
            if (options.id) { toolbarid = 'id="' + options.id + '"'; } 
            if (options.centered) { centered = "centered"; }
            b += '<div ' + toolbarid + ' class="asm-toolbar no-print ' + centered + '">';
        }
        $.each(buttons, function(i, v) {
            if (v.hideif && v.hideif()) { return; }
            if (v.perm && !common.has_permission(v.perm)) { return; }
            if (!v.type || v.type == "button") {
                b += "<button id=\"button-" + v.id + "\" title=\"" + html.title(v.tooltip) + "\">" + html.icon(v.icon);
                if (v.text) {
                    b += " " + v.text;
                }
                b += "</button>";
            }
            else if (v.type == "raw") {
                b += v.markup;
            }
            else if (v.type == "dropdownfilter") {
                b += '<span style="float: right"><select id="' + v.id + '" title="' + html.title(v.tooltip) + '" class="asm-selectbox">';
                if (common.is_array(v.options)) {
                    b += html.list_to_options(v.options);
                }
                // Assume v.options is a string 
                else {
                    b += v.options;
                }

                b += '</select></span>';
            }
            else if (v.type == "buttonmenu") {
                b += '<div id="button-' + v.id + '" class="asm-menu-icon" title="' + html.title(v.tooltip) + '">' + html.icon(v.icon);
                if (v.text) {
                    b += " " + v.text;
                }
                b += '</div>';
                // If no options are supplied, don't create the menu body
                if (v.options) {
                    var menu = '<div id="button-' + v.id + '-body" class="asm-menu-body"><ul class="asm-menu-list">';
                    $.each(v.options, function(io, vo) {
                        var opt = vo.split("|");
                        var val, label;
                        val = opt[0];
                        if (opt.length > 1) {
                            label = opt[1];
                        }
                        else {
                            label = opt[0];
                        }
                        menu += '<li class="asm-menu-item"><a href="#" data="' + val + '">' + label + '</a></li>';
                    });
                    menu += '</ul></div>';
                    $("body").prepend(menu);
                }
            }
            b += " ";
        });
        if (options.render_container) {
            b += "</div>";
        }
        return b;
    },

    /**
     * Binds events to a toolbar button set
     *
     * buttons: [
     *      { id: "new", text: _("Text"), tooltip: _("Tooltip"), icon: "iconname", enabled: "always|multi|one", click: tableform.click_delete, mouseover: function(e), mouseleave: function(e) }
     * ]
     */
    buttons_bind: function(buttons) {
        $.each(buttons, function(i, v) {
            if (!v.type || v.type == "button") {
                $("#button-" + v.id).button();
                if (v.click) { $("#button-" + v.id).click(v.click); }
                if (v.mouseover) { $("#button-" + v.id).mouseover(v.mouseover); }
                if (v.mouseleave) { $("#button-" + v.id).mouseleave(v.mouseleave); }
                if (v.enabled != "always") { $("#button-" + v.id).button("disable"); }
            }
            else if (v.type == "buttonmenu") {
                $("#button-" + v.id).asmmenu();
                $("#button-" + v.id + "-body a").each(function() {
                    if (v.click) {
                        var dataval = $(this).attr("data");
                        $(this).click(function() {
                            $("#button-" + v.id).asmmenu("hide_all");
                            v.click(dataval);
                            return false;
                        });
                    }
                });
                if (v.enabled != "always") {
                    $("#button-" + v.id).addClass("ui-state-disabled").addClass("ui-button-disabled");
                }
            }
            else if (v.type == "dropdownfilter") {
                $("#" + v.id).change(function() {
                    if (v.click) {
                        v.click($("#" + v.id).val());
                    }
                });
            }
        });
    },

    /**
     * Resets the default state of any toolbar buttons
     */
    buttons_default_state: function(buttons) {
        $.each(buttons, function(i, v) {
            if (!v.type || v.type == "button") {
                $("#button-" + v.id).button("enable");
                if (v.enabled != "always") { $("#button-" + v.id).button("disable"); }
            }
            else if (v.type == "buttonmenu") {
                if (v.enabled != "always") { 
                    $("#button-" + v.id).addClass("ui-state-disabled").addClass("ui-button-disabled");
                }
            }
        });
    },

    /** Formats a value as comments (truncates to one line or shows full with \n -> <br/> based on config) */
    format_comments: function(row, v) {
        if (config.bool("ShowFullCommentsInTables")) { return common.nulltostr(v).replace(/\n/g, "<br />"); }
        return html.truncate(v, 80);
    },

    /** Formats a value as a currency */
    format_currency: function(row, v) {
        return format.currency(v);
    },

    /** Formats a value as a date */
    format_date: function(row, v) {
        return format.date(v);
    },

    /** Formats a value as a date and time */
    format_datetime: function(row, v) {
        return '<span style="white-space: nowrap;">' + format.date(v) + " " + format.time(v) + '</span>';
    },

    /** Formats a value as a string */
    format_string: function(row, v) {
        if (!v) { return ""; }
        return String(v);
    },

    /** Formats a value as a date time, leaving time blank if not present */
    format_time: function(row, v) {
        return format.time(v);
    },

    /** Formats a value as a time, returning blank for midnight */
    format_time_blank: function(row, v) {
        return (format.time(v) == "00:00:00" ? "" : format.time(v));
    },

    /**
     * Renders a table
     *
     * formatter function is called for every value to display it
     * hideif is called for every column and row. If true is returned, the
     * column is not displayed.
     *
     * table = { rows: {json containing rows}, 
     *   idcolumn: "ID",
     *   truncatelink: 0, // chars to truncate the edit link to in the leftmost column (0 or falsey value to do nothing)
     *   showfilter: false, // whether to allow searching of columns
     *   edit: function(row) { callback for when a row is edited with the row data }
     *   button_click: function() { callback when a button inside the table is clicked, use $(this) }
     *   change: function(rows) { callback when the selected rows changes with the selected rows }
     *   complete: function(row) { return true if the row should be drawn as complete },
     *   overdue: function(row) { return true if the row should be drawn as overdue },
     *   columns:  [
     *      { initialsort: true, 
     *        initialsortdirection: "asc", // or desc
     *        sorttext: function(row) { overrides table.textExtraction and sets sort text }
     *        field: "jsonfield", 
     *        classes: "", // extra classes to add to the td
     *        display: _("Text"),      
     *        formatter: tableform.format_date, 
     *        hideif: function(row) 
     *      } 
     *   ]
     *
     * bodyonly: If you only want the tbody contents, set this to true
     */
    table_render: function(table, bodyonly) {
        var t = [];
        t.push("<table id=\"tableform\" width=\"100%\"><thead><tr>");
        if (!bodyonly) {
            $.each(table.columns, function(i, v) {
                if (v.hideif && v.hideif()) { return; }
                if (i == 0) {
                    // Prepend select/filter buttons to the first column heading
                    t.push('<th>');
                    t.push('<button id="tableform-select-all">' + _("Select all") + '</button>');
                    t.push('<button id="tableform-toggle-filter">' + _("Filter") + '</button>');
                    t.push(' <span>' + v.display + '</span></th>');
                }
                else {
                    t.push("<th>" + v.display + "</th>");
                }
            });
            t.push("</tr></thead><tbody>");
        }
        $.each(table.rows, function(ir, vr) {
            if (table.hideif && table.hideif(vr)) { return; }
            var rowid = vr[table.idcolumn];
            t.push("<tr id=\"row-" + rowid + "\">");
            $.each(table.columns, function(ic, vc) {
                var formatter = vc.formatter;
                if (vc.hideif && vc.hideif(vr)) { return; }
                var extraclasses = "";
                if (table.complete) {
                    if (table.complete(vr)) {
                        extraclasses += " asm-completerow";
                    }
                }
                if (table.overdue) {
                    if (table.overdue(vr)) {
                        extraclasses += " asm-overduerow";
                    }
                }
                if (vc.classes) {
                    extraclasses += " " + vc.classes;
                }
                if (formatter === tableform.format_currency) {
                    extraclasses += " rightalign";
                }
                t.push("<td class=\"" + extraclasses + "\">");
                if (vc.sorttext) {
                    t.push("<span data-sort=\"" + html.title(html.truncate(vc.sorttext(vr))) + "\"></span>");
                }
                if (ic == 0 && formatter === undefined) {
                    var linktext = tableform.format_string(vr, vr[vc.field]);
                    if (table.truncatelink) { linktext = html.truncate(html.decode(linktext), table.truncatelink); }
                    if (linktext == "") { linktext = _("(blank)"); }
                    t.push("<span style=\"white-space: nowrap\">");
                    t.push("<input type=\"checkbox\" data-id=\"" + rowid + "\" title=\"" + html.title(_("Select")) + "\" />");
                    t.push("<a href=\"#\" class=\"link-edit\" data-id=\"" + rowid + "\">" + linktext + "</a>");
                    t.push("</span>");
                }
                else {
                    if (formatter === undefined) { formatter = tableform.format_string; }
                    t.push(formatter(vr, vr[vc.field]));
                }
                t.push("</td>");
            });
            t.push("</tr>");
        });
        if (!bodyonly) {
            t.push("</tbody></table>");
        }
        return t.join("\n");
    },

    /**
     * Updates the contents within the tbody of a table from
     * the table rows.
     *
     * table = ( see render_table )
     */
    table_update: function(table) {
        $("#tableform tbody").empty();
        $("#tableform tbody").html(this.table_render(table, true));
        // If the table had td styling on, re-apply it
        if ($("#tableform").prop("data-style-td")) {
            $("#tableform td").addClass("ui-widget-content");
        }
        this.table_bind_widgets(table);
        $("#tableform").trigger("update");
        this.table_apply_sort(table);
    },

    /**
     * Loads and binds any widgets that are inside the table content
     * (typically buttons).
     */
    table_bind_widgets: function(table) {
        $("#tableform tbody button").each(function() {
            if ($(this).attr("data-asmicon")) {
                let text = $(this).text();
                $(this).prop("title", text);
                $(this).html( html.icon($(this).attr("data-asmicon")) ).button();
            }
            else {
                $(this).button({ 
                    icons: { primary: "ui-icon-" + $(this).attr("data-icon") }, 
                    text: $(this).attr("data-text") == "true" 
                });
            }
        });
    },

    /**
     * Checks the state of the checkboxes in the table and updates
     * the buttons in the toolbar based on how many items are selected.
     */
    table_update_buttons: function(table, buttons) {
        var nosel = $("#tableform input:checked").length;
        $.each(buttons, function(i, b) {
            var bn = $("#button-" + b.id), enabled = false;
            if (b.enabled == "always") {
                enabled = true;
            }
            if (b.enabled == "multi" && nosel > 0) {
                enabled = true;
            }
            if (b.enabled == "one" && nosel == 1) {
                enabled = true;
            }
            if (enabled) {
                if (!b.type || b.type == "button") {
                    bn.button("enable");
                }
                else if (b.type == "buttonmenu") {
                    $("#button-" + b.id).removeClass("ui-state-disabled").removeClass("ui-button-disabled");
                }
            }
            else {
                if (!b.type || b.type == "button") {
                    bn.button("disable");
                }
                else if (b.type == "buttonmenu") {
                    bn.addClass("ui-state-disabled").addClass("ui-button-disabled");
                }
            }
        });
        if (table.change) {
            table.change(tableform.table_selected_rows(table));
        }
    },

    /**
     * Binds table events and widgets. If there's a toolbar button set, can be
     * passed to bind watching for selections to them.
     *
     * table = ( see table_render )
     * buttons = { see buttons_render }
     */
    table_bind: function(table, buttons) {
        if (table.edit) {
            $("#tableform").on("click", ".link-edit", function() {
                let a = $(this);
                $.each(table.rows, function(i, v) {
                    if (v[table.idcolumn] == a.attr("data-id")) {
                        table.edit(v);
                        return false;
                    }
                });
                return false;
            });
        }

        // Watch for buttons inside the table being clicked and send them to
        // the delegate handler.
        if (table.button_click) {
            $("#tableform").on("click", "button", table.button_click);
        }

        // Watch for number of selected checkboxes changing and update 
        // the enable/disabled state of buttons
        if (buttons) {
            $("#tableform").on("click", "input[type='checkbox']", function() {
                tableform.table_update_buttons(table, buttons);
            });
        }

        // selects all the visible rows in the table.
        // does nothing if the dialog is open.
        const select_all = function() {
            if ($("#dialog-tableform").hasClass("ui-dialog-content") && $("#dialog-tableform").dialog("isOpen")) { return false; }
            $("#tableform input[type='checkbox']").each(function() {
                if ($(this).is(":visible")) {
                    $(this).prop("checked", true);
                    $(this).closest("tr").addClass("ui-state-highlight");
                }
            });
            tableform.table_update_buttons(table, buttons);
        };

        // unselects all rows in the table
        const unselect_all = function() {
            $("#tableform input[type='checkbox']").each(function() {
                $(this).prop("checked", false);
                $(this).closest("tr").removeClass("ui-state-highlight");
            });
            tableform.table_update_buttons(table, buttons);
        };

        // Bind the CTRL+A key
        Mousetrap.bind("ctrl+a", function() {
            select_all();
            return false;
        });

        // Bind any widgets inside the table
        this.table_bind_widgets(table);

        // Create the table widget
        $("#tableform").table({ filter: true });

        // old behaviour was to show the filter line if there were 10 or more rows
        // table.filter_toggle = table.rows && table.rows.length >= 10; 
        table.filter_toggle = false;
        $(".tablesorter-filter-row").toggle(table.filter_toggle);
        $(".tablesorter-filter").prop("placeholder", _("Filter"));

        // Bind the select all link in the table header
        // Unlike the CTRL+A sequence, this one will toggle between select/unselect
        $("#tableform-select-all").button({
            icons: { primary: "ui-icon-check" },
            text:  false
        });
        $("#tableform-select-all").click(function(e) {
            e.preventDefault();
            e.stopPropagation();
            if (!table.select_all_toggle) {
                table.select_all_toggle = true;
                select_all();
            }
            else {
                table.select_all_toggle = false;
                unselect_all();
            }
            return false;
        });

        // Bind the toggle search/filter link in the table header
        $("#tableform-toggle-filter").button({
            icons: { primary: "ui-icon-search" },
            text:  false
        });
        $("#tableform-toggle-filter").click(function(e) {
            e.preventDefault();
            e.stopPropagation();
            table.filter_toggle = !table.filter_toggle;
            $(".tablesorter-filter-row").toggle(table.filter_toggle);
            return false;
        });

        // Consume mousedown/mouseup events for both buttons so that tablesorter 
        // doesn't receive them
        $("#tableform-toggle-filter, #tableform-select-all").mouseup(function() {
            return false;
        }).mousedown(function() {
            return false; 
        });

        // And the default sort
        this.table_apply_sort(table);

    },

    /**
     * Applies any sorts necessary to the table
     * table = (see table_render)
     */
    table_apply_sort: function(table) {
        // If we don't have anything in the table, there's no point
        if ($("#tableform tbody tr").length == 0) {
            return;
        }
        var sortList;
        // Since some columns can be hidden, don't count those when figuring
        // out which columns to sort
        var visibleIndex = 0;
        $.each(table.columns, function(i, v) {
            if (sortList) { return; }
            if (v.hideif && v.hideif()) {
                return;
            }
            if (v.initialsort) {
                    var sortdir = 0;
                    if (v.initialsortdirection && v.initialsortdirection == "desc") {
                        sortdir = 1;
                    }
                    sortList = [[visibleIndex, sortdir]];
                    return;
            }
            visibleIndex += 1;
        });
        $("#tableform").trigger("sorton", [sortList]);
    },

    /**
     * Returns a comma separated list of selected ids from
     * the table.
     * table = ( see table_render )
     */
    table_ids: function(table) {
        var s = "";
        $("#tableform input:checked").each(function() {
            s += $(this).attr("data-id") + ",";
        });
        return s;
    },

    /**
     * Returns the selected ID in the table.
     * Returns undefined if nothing is selected.
     */
    table_selected_id: function(table) {
        var selid = $("#tableform input:checked").attr("data-id");
        if (!selid) { return undefined; }
        return selid;
    },

    /**
     * Returns the selected row in the table.
     * Returns undefined if nothing is selected.
     */
    table_selected_row: function(table) {
        var result, selid = $("#tableform input:checked").attr("data-id");
        if (!selid) { return undefined; }
        $.each(table.rows, function(i, v) {
            if (v[table.idcolumn] == selid) {
                result = v;
            }
        });
        return result;
    },

    /**
     * Returns the selected rows in the table.
     * Returns an empty list if nothing is selected.
     */
    table_selected_rows: function(table) {
        var results = [];
        $("#tableform input:checked").each(function() {
            var el = $(this);
            $.each(table.rows, function(i, v) {
                if (v[table.idcolumn] == el.attr("data-id")) {
                    results.push(v);
                }
            });
        });
        return results;
    },

    /**
     * Returns true if the id given is selected in the table currently
     */
    table_id_selected: function(id) {
        var issel = false;
        $("#tableform input:checked").each(function() {
            if ($(this).attr("data-id") == id) {
                issel = true;
            }
        });
        return issel;
    },

    /**
     * Removes selected items in the table from the model
     * table = ( see table_render )
     * rows = the json rows from the controller
     */
    table_remove_selected_from_json: function(table, rows) {
        var ids = this.table_ids(table).split(",");
        $.each(ids, function(ix, id) {
            // Have to use a nest because we can't delete during iteration
            $.each(rows, function(i, row) {
                if (row && row[table.idcolumn] == id) {
                    rows.splice(i, 1); 
                }
            });
        });
    },

    /**
     * Renders dialog
     *
     *   dialog = {
     *      add_title: _("Dialog title"),
     *      edit_title: _("Dialog title"),
     *      helper_text: _("Some info text"),
     *      close_on_ok: false,
     *      hide_read_only: false, // whether or not to hide read only fields in editing
     *      use_default_values: false,
     *      focusfirst: true,
     *      delete_button: false,
     *      delete_perm: 'da',
     *      edit_perm: 'ca',
     *      width: 500,
     *      height: 200, (omit for auto)
     *      resizable: false (omit for false),
     *      html_form_action: target (renders form tag around fields if set)
     *      html_form_enctype: enctype
     *      fields: (see fields_render)
     *  }
     */
    dialog_render: function(dialog) {
        var d =[];
        d.push("<div id=\"dialog-tableform\" style=\"display: none\">");
        if (dialog.helper_text) {
            d.push(html.info('<span id="dialog-tableform-help-text">' + dialog.helper_text + '</span>', "dialog-tableform-help"));
        }
        d.push(html.textbar('<strong><span id="dialog-tableform-error-text"></span></strong>', { "id": "dialog-tableform-error", "display": "none", "state": "error", "icon": "alert" }));
        d.push(html.textbar('<span id="dialog-tableform-info-text"></span></strong>', { "id": "dialog-tableform-info", "display": "none" }));
        d.push("<div id=\"dialog-tableform-fields\" style=\"margin-top: 5px\"></span>");
        if (dialog.html_form_action) {
            d.push("<form id=\"form-tableform\" method=\"post\" action=\"" + dialog.html_form_action + "\"");
            if (dialog.html_form_enctype) { d.push(" enctype=\"" + dialog.html_form_enctype + "\""); }
            d.push(">");
        }
        // If focusfirst is defined and set to false, add a hidden
        // field that prevents JQuery UI autofocusing on any of our
        // fields (good for when choosers are the first field)
        if (dialog.focusfirst === false) {
            d.push(html.capture_autofocus());
        }
        d.push(this.fields_render(dialog.fields));
        if (dialog.html_form_action) {
            d.push("</form>");
        }
        d.push("</div>");
        d.push("</div>");
        return d.join("\n");
    },

    /**
     * Binds dialog field events
     *
     * dialog = (see dialog_render)
     */
    dialog_bind: function(dialog) {
        this.fields_bind(dialog.fields);
    },

    /**
     * Closes the dialog if it's open
     */
    dialog_close: function() {
        $("#dialog-tableform").dialog("close");
    },

    dialog_destroy: function() {
        common.widget_destroy("#dialog-tableform", "dialog", true);
    },

    /**
     * Displays the dialog error text. If no text is supplied, 
     * removes the error.
     */
    dialog_error: function(text) {
        if (!text) {
            $("#dialog-tableform-error").hide();
        }
        else {
            $("#dialog-tableform-error-text").html(text);
            $("#dialog-tableform-error").fadeIn();
        }
    },

    dialog_info: function(text) {
        if (!text) {
            $("#dialog-tableform-info").hide();
        }
        else {
            $("#dialog-tableform-info-text").html(text);
            $("#dialog-tableform-info").fadeIn().delay(5000).fadeOut();
        }
    },

    dialog_disable_buttons: function() {
        $("#dialog-tableform").disable_dialog_buttons();
        $("#dialog-tableform-spinner").fadeIn();
    },

    dialog_enable_buttons: function() {
        $("#dialog-tableform").enable_dialog_buttons();
        $("#dialog-tableform-spinner").fadeOut();
    },

    /**
     * Shows the dialog in add mode 
     * 
     * dialog: (see dialog_render)
     * o: options/events - 
     *  onadd: function to run when the user clicks the add button (after validation)
     *  onload: function to run when the form has loaded and been displayed
     *  onvalidate: function to run to validate the form
     */
    dialog_show_add: function(dialog, o) {

        var deferred = $.Deferred();

        // Make sure any existing dialog is destroyed before starting
        tableform.dialog_destroy();

        var b = {}; 

        // Find any select fields in the dialog and reload their lookups. 
        // This is necessary in case opening a previous record removed a retired lookup element.
        $.each(dialog.fields, function(i, v) {
            if (v.options && v.options.rows) {
                let opts = "";
                if (v.options.prepend) { opts = v.options.prepend; }
                opts += html.list_to_options(v.options.rows, v.options.valuefield, v.options.displayfield);
                $("#" + v.post_field).html(opts);
            }
        });
        
        // Set fields to their default values
        if (dialog.use_default_values === undefined || dialog.use_default_values === true) {
            tableform.fields_default(dialog.fields);
        }

        // Find any fields marked readonly and enable them
        $.each(dialog.fields, function(i, v) {
            if (v.readonly) { 
                $("#" + v.post_field).prop("disabled", false);
                if (dialog.hide_read_only) {
                    $("#" + v.post_field).closest("tr").show(); 
                }
            }
        });

        // Remove any retired lookups
        $.each(dialog.fields, function(i, v) {
            if (v.type == "select") {
                $("#" + v.post_field).select("removeRetiredOptions", "all");
            }
        });

        b[_("Add")] = {
            text: _("Add"),
            "class": 'asm-dialog-actionbutton',
            click: function() {
                if (o && o.onvalidate) { 
                    if (!o.onvalidate()) { 
                        return;
                    }
                }
                if (tableform.fields_validate(dialog.fields)) {
                    if (dialog.close_on_ok) {
                        $(this).dialog("close");
                    }
                    else {
                        tableform.dialog_disable_buttons();
                    }
                    if (o && o.onadd) { o.onadd(); }
                    deferred.resolve();
                }
            }
        };

        b[_("Cancel")] = function() { 
            $(this).dialog("close"); 
            deferred.reject("dialog cancelled");
        };

        $("#dialog-tableform").dialog({
            resizable: (dialog.resizable || false),
            width: common.vwidth(dialog.width || 1024), // use smaller of requested width and viewport width
            height: dialog.height ? common.vheight(dialog.height || 800) : "auto", // use smaller height but only if set
            modal: true,
            dialogClass: "dialogshadow",
            autoOpen: false,
            title: dialog.add_title,
            show: dlgfx.add_show,
            hide: dlgfx.add_hide,
            buttons: b,
            open: function() {
                var bp = $("#dialog-tableform").parent().find(".ui-dialog-buttonpane");
                if (bp.find("#dialog-tableform-spinner").length == 0) {
                    bp.append('<img id="dialog-tableform-spinner" style="display: none; height: 16px" src="static/images/wait/rolling_3a87cd.svg" />');
                }
                // Any code editor widgets need to be refreshed on load
                $.each(dialog.fields, function(i, v) {
                    if (v.type == "htmleditor") {
                        $("#" + v.post_field).htmleditor("refresh");
                    }
                    if (v.type == "sqleditor") {
                        $("#" + v.post_field).sqleditor("refresh");
                    }
                });
                tableform.dialog_enable_buttons();
            },
            close: function() {
                tableform.dialog_enable_buttons();
                tableform.dialog_destroy();
            }
        });
        this.dialog_error("");
        $("#dialog-tableform").dialog("open");
        if (o && o.onload) {
            o.onload();
        }
        return deferred.promise();
    },

    /**
     * Shows the dialog in edit mode 
     * 
     * dialog: (see dialog_render)
     * row: The row to edit
     * o: options/events -
     *  onchange: function to run when the user clicks the change button (after validation)
     *  onload: function to run after the form has been loaded and displayed
     *  ondelete: function to run after the delete button is clicked
     *  onvalidate: function to run to validate the form
     */
    dialog_show_edit: function(dialog, row, o) {

        var deferred = $.Deferred();

        // Make sure any existing dialog is destroyed before starting
        tableform.dialog_destroy();

        // Find any select fields in the dialog and reload their lookups. 
        // This is necessary in case opening a previous record removed a retired lookup element.
        $.each(dialog.fields, function(i, v) {
            if (v.options && v.options.rows) {
                let opts = "";
                if (v.options.prepend) { opts = v.options.prepend; }
                opts += html.list_to_options(v.options.rows, v.options.valuefield, v.options.displayfield);
                $("#" + v.post_field).html(opts);
            }
        });

        // Load the values from storage into the fields
        this.fields_populate_from_json(dialog.fields, row);

        // Remove any retired lookups
        $.each(dialog.fields, function(i, v) {
            if (v.type == "select") {
                $("#" + v.post_field).select("removeRetiredOptions");
            }
        });

        // Find any fields marked readonly and disable/hide them
        $.each(dialog.fields, function(i, v) {
            if (v.readonly) { 
                $("#" + v.post_field).prop("disabled", true);
                if (dialog.hide_read_only) {
                    $("#" + v.post_field).closest("tr").hide(); 
                }
            }
        });

        var b = {}; 
        if (dialog.delete_button && dialog.delete_perm && common.has_permission(dialog.delete_perm)) {
            b[_("Delete")] = {
                text: _("Delete"),
                "class": 'asm-redbutton',
                click: function() {
                    tableform.dialog_disable_buttons();
                    if (o && o.ondelete) {
                        o.ondelete(row);
                    }
                    deferred.reject("delete", row);
                }
            };
        }
        if (!dialog.edit_perm || (dialog.edit_perm && common.has_permission(dialog.edit_perm))) {
            b[_("Change")] = {
                text: _("Change"),
                "class": 'asm-dialog-actionbutton',
                click: function() {
                    if (o && o.onvalidate) { 
                        if (!o.onvalidate()) { 
                            return;
                        }
                    }
                    if (tableform.fields_validate(dialog.fields)) {
                        if (dialog.close_on_ok) {
                            $(this).dialog("close");
                        }
                        else {
                            tableform.dialog_disable_buttons();
                        }
                        if (o && o.onchange) {
                            o.onchange(row);
                        }
                        deferred.resolve(row);
                    }
                }
            };
        }

        b[_("Cancel")] = function() { 
            $(this).dialog("close");
            deferred.reject("dialog cancelled");
        };

        var dw = dialog.width || "auto";
        if (common.browser_is.mobile) {
            dw = dialog.width || 1024;
            dw = Math.min(dw, $(window).width());
        }

        $("#dialog-tableform").dialog({
            resizable: (dialog.resizable || false),
            width: dw,
            height: (dialog.height || "auto"),
            modal: true,
            dialogClass: "dialogshadow",
            autoOpen: false,
            title: dialog.edit_title,
            show: dlgfx.edit_show,
            hide: dlgfx.edit_hide,
            buttons: b,
            open: function() {
                
                var bp = $("#dialog-tableform").parent().find(".ui-dialog-buttonpane");
                
                if (bp.find("#dialog-tableform-activity").length == 0 && row.CREATEDBY && row.CREATEDDATE && row.LASTCHANGEDBY && row.LASTCHANGEDDATE) {
                    var activity = 
                        _("Added by {0} on {1}").replace("{0}", row.CREATEDBY)
                            .replace("{1}", format.date(row.CREATEDDATE) + " " + format.time(row.CREATEDDATE)) + '<br/>' +
                        _("Last changed by {0} on {1}").replace("{0}", row.LASTCHANGEDBY)
                            .replace("{1}", format.date(row.LASTCHANGEDDATE) + " " + format.time(row.LASTCHANGEDDATE));
                    bp.append('<button id="button-dialog-tableform-activity" title="' + 
                        html.title(activity.replace("<br/>", "\n")) +
                        '"><span class="asm-icon asm-icon-users"></span></button>');
                    $("#button-dialog-tableform-activity").button().click(function() {
                        tableform.dialog_info(activity);
                    });
                }
                
                if (bp.find("#dialog-tableform-spinner").length == 0) {
                    bp.append('<img id="dialog-tableform-spinner" style="display: none; height: 16px" src="static/images/wait/rolling_3a87cd.svg" />');
                }

                // Any code editor widgets need to be refreshed on load
                $.each(dialog.fields, function(i, v) {
                    if (v.type == "htmleditor") {
                        $("#" + v.post_field).htmleditor("refresh");
                    }
                    if (v.type == "sqleditor") {
                        $("#" + v.post_field).sqleditor("refresh");
                    }
                });
                
                tableform.dialog_enable_buttons();
            },
            close: function() {
                tableform.dialog_enable_buttons();
                tableform.dialog_destroy();
            }
        });
        this.dialog_error("");
        $("#dialog-tableform").dialog("open");
        if (o && o.onload) {
            o.onload(row);
        }
        return deferred.promise();
    },


    /**
     * Renders fields
     *
     * fields: [
     *      { json_field: "name", 
     *        post_field: "name", 
     *        id: "name", // id attribute for the widget - if not supplied, post_field is used
     *        label: "label", // if label contains <label markup, overrides generation and uses supplied value instead
     *        labelpos: "before|after|above", (only valid for textarea (before|above) and check (before|after))
     *        type: "check|text|textarea|richtextarea|date|time|currency|number|select|animal|person|raw|nextcol", 
     *        rowid: "thisrow", (id for the row containing the label/field)
     *        readonly: false, (shown in dialog_show_add, hidden in dialog_show_edit)
     *        halfsize: false, (use the asm-halftextbox class)
     *        doublesize: false, (use the asm-doubletextbox class)
     *        justwidget: false, (if true only output the widget itself, no label or row container)
     *        hideif: function() { return true; }, if true, omits the widget from the output
     *        defaultval: expression or function to evaluate (note: done in dialog_show_add/edit->fields_default, not here)
     *        value: "123" value to assign to the widget during rendering
     *        validation: "notblank|notzero|validemail" or a function to call (note: done after dialog_show_x/fields_validate, not here)
     *        height/width/margintop: "css expr", (only used by sqleditor/htmleditor)
     *        maxlength: (number of chars limit for text/textarea),
     *        min|max: min/max number for number fields
     *        classes: "extraclass anotherone", extra classes to apply to the widget
     *        rowclasses: "extraclass anotherone", extra classes to apply to the row container
     *        colclasses: "extraclass", extra classes to apply to the column containers within the row
     *        date_onlydays: "0,1,2,3,4,5,6" (for datepicker fields, only allow days to be selected monday-sunday)
     *        date_nofuture: true|false, (for datepicker fields)
     *        date_nopast: true| false, (for datepicker fields)
     *        placeholder: _("Text"), sets the placeholder attribute of the widget
     *        tooltip: _("Text"), sets the title attribute of the widget
     *        callout: _("Text"), mixed markup allowed, shows a callout button next to the widget label
     *        markup: "<input type='text' value='raw' />", // used in conjunction with type raw to supply markup instead
     *        options: [ "Item 1", "Item 2" ] // options for use with type select and selectmulti
     *        options: "<option>test</option>"
     *        options: { displayfield: "DISPLAY", valuefield: "VALUE", rows: [ {rows} ], prepend: "<option>extra</option>" }, 
     *        animalfilter: "all",   (only valid for animal and animalmulti types)
     *        personfilter: "all",   (only valid for person type)
     *        personmode: "full",    (only valid for person type)
     *        change: function(changeevent), (note: done in fields_bind, not here)
     *        blur: function(blurevent), (note: done in fields_bind, not here)
     *        xattr: ' data-linktype="2" ' (add extra attributes to the widget)
     *        xbutton: "text" (render an extra button after the widget with id button-post_field and inner text)
     *        xlabel: "<span>whatever</span>" (render extra markup after the label)
     *        xmarkup: "<span>whatever</span>" (render extra markup after the widget)
     *        coldata: use in conjunction with type "nextcol" to specify the data attribute for the next column
     *      } ]
     * options: modifiers for the container holding the columns of fields. If undefined, defaults are: 
     *      { 
     *          render_container: true; 
     *          full_width: true; 
     *          id: "" 
     *      }
     */
    fields_render: function(fields, coptions) {
        let d = "", startcol = "", endcol = "", colclasses = "",
            options = { render_container: true, full_width: true, id: "" };
        if (coptions !== undefined) { options = common.copy_object(options, coptions); }
        if (options.render_container) {
            d = '<div class="asm-fields-container row" ';
            if (options.id) { d+= 'id="' + options.id + '"'; }
            d += '>';
            colclasses = "asm-table-layout";
            if (options.full_width) { colclasses += " asm-table-fullwidth"; }
            startcol = '<div class="col"><table class="' + colclasses + ' {classes}" data="{data}">';
            endcol = '</table></div>';
            d += startcol.replace("{data}", "").replace("{classes}", ""); 
        }
        $.each(fields, function(i, v) {
            if (v.type == "animal") { d += tableform.render_animal(v); }
            else if (v.type == "animalmulti") { d += tableform.render_animalmulti(v); }
            else if (v.type == "check") { d += tableform.render_check(v); }
            else if (v.type == "currency") { d += tableform.render_currency(v); }
            else if (v.type == "date") { d += tableform.render_date(v); }
            else if (v.type == "datetime") { d += tableform.render_datetime(v); }
            else if (v.type == "file") { d += tableform.render_file(v); }
            else if (v.type == "htmleditor") { d += tableform.render_htmleditor(v); }
            else if (v.type == "intnumber") { d += tableform.render_intnumber(v); }
            else if (v.type == "number") { d += tableform.render_number(v); }
            else if (v.type == "password") { d += tableform.render_text(v); }
            else if (v.type == "person") { d += tableform.render_person(v); }
            else if (v.type == "raw") { d += tableform.render_markup(v); }
            else if (v.type == "richtextarea") { d += tableform.render_richtextarea(v); }
            else if (v.type == "select") { d += tableform.render_select(v); } 
            else if (v.type == "selectmulti") { d += tableform.render_selectmulti(v); }
            else if (v.type == "sqleditor") { d += tableform.render_sqleditor(v); }
            else if (v.type == "text") { d += tableform.render_text(v); }
            else if (v.type == "textarea") { d += tableform.render_textarea(v); }
            else if (v.type == "time") { d += tableform.render_time(v); }
            else if (v.type == "additional") { v.justwidget = true; d += tableform.render_markup(v); }
            else if (v.type == "nextcol") {
                // Special widget that causes rendering to move to a new column
                d += endcol + startcol.replace("{data}", v.coldata).replace("{classes}", v.classes);
            }
        });
        if (options.render_container) {
            d += endcol;
            d += "</div>";
        }
        return d;
    },

    /** Sanitises values being output for HTML attributes */
    _attr_value: function(s) {
        return html.title(s);
    },

    /**
     * Sets the id attribute to post_field if it is undefined
     */
    _check_id: function(v) {
        if (v.id === undefined && v.post_field !== undefined) { v.id = v.post_field; }
        if (v.id === undefined && v.post_field === undefined) { v.id = ""; }
        return v;
    },

    /**
     * Renders the widget class attribute 
     * v: the widget object
     * c: The mandatory classes, eg: asm-textarea asm-textareafixed
     */
    _render_class: function(v, c) {
        if (c === undefined || c === null) { c = ""; }
        if (v.classes) { c += " " + v.classes; }
        if (v.halfsize) { c += " asm-halftextbox"; }
        if (v.doublesize) { c += " asm-doubletextbox"; }
        return ' class="' + c + '" ';
    },

    /**
     * renders the label for a form field, including callout and validation indicator
     * v: field definition
     */
    _render_label: function(v) {
        let label = "", labelx = "", labelfor = "";
        if (v.validation && v.validation instanceof String && v.validation.indexOf("not") == 0) {
            labelx += '&nbsp;<span class="asm-has-validation">*</span>';
        }
        if (v.callout) {
            labelx += '&nbsp;<span id="callout-' + v.id + '" class="asm-callout">' + v.callout + '</span>';
        }
        if (v.xlabel) {
            labelx += v.xlabel;
        }
        if (v.label && v.label.indexOf("<label") != -1) {
            label = v.label; // label already contains markup, let it override our generated label
        }
        else {
            if (v.id) { labelfor = 'for="' + v.id + '"'; }
            label = '<label ' + labelfor + '>' + (v.label || "") + "</label>" + labelx;
        }
        return label;
    },

    /** 
     *  renders the label and surrounding area/row of a form field
     *  v: The field definition object (see fields_render)
     *  h: The generated widget HTML being passed from a render_text/check/etc method.
     */
    _render_formfield: function(v, h) {
        let tr = "<tr>", td = "<td>", rowid = "", rowclasses = "", colclasses = "", label = tableform._render_label(v);
        if (v.hideif && v.hideif()) {
            return "";
        }
        if (v.justwidget) { 
            return h; 
        }
        if (v.rowid) { 
            rowid = ' id="' + v.rowid + '" ';
        }
        else if (v.id) {
            rowid = ' id="' + v.id + "row" + '" ';
        }
        if (v.rowclasses) {
            rowclasses = ' class="' + v.rowclasses + '" ';
        }
        if (v.colclasses) {
            colclasses = ' class="' + v.colclasses + '" ';
        }
        tr = '<tr ' + rowid + rowclasses + '>'; 
        td = '<td ' + colclasses + '>';
        if (v.type == "check") {
            return tr + td + '</td>' + td + h + '</td></tr>';
        }
        else if ((v.type == "textarea" || 
                    v.type == "richtextarea" || 
                    v.type == "htmleditor" || 
                    v.type == "sqleditor") && 
                    v.labelpos && v.labelpos == "above") {
            return tr + '<td colspan="2">' + label + '<br>' + h + '</td></tr>';
        }
        else {
            return tr + td + label + '</td>' + td + h + '</td></tr>';
        }
    },

    render_animal: function(v) {
        let d = "";
        tableform._check_id(v);
        d += "<input type=\"hidden\" ";
        d += tableform._render_class(v, "asm-animalchooser");
        if (v.id) { d += "id=\"" + v.id + "\" "; }
        if (v.json_field) { d += "data-json=\"" + v.json_field + "\" "; }
        if (v.post_field) { d += "data-post=\"" + v.post_field + "\" "; }
        if (v.readonly) { d += "data-noedit=\"true\" "; }
        if (v.animalfilter) { d += "data-filter=\"" + v.animalfilter + "\" "; }
        if (v.validation) { d += "data-validation=\"" + v.validation + "\" "; }
        if (v.value) { d += "value=\"" + tableform._attr_value(v.value) + "\" "; }
        if (v.xattr) { d += v.xattr + " "; }
        d += "/>";
        return tableform._render_formfield(v, d);
    },

    render_animalmulti: function(v) {
        let d = "";
        tableform._check_id(v);
        d += "<input type=\"hidden\" ";
        d += tableform._render_class(v, "asm-animalchoosermulti");
        if (v.id) { d += "id=\"" + v.id + "\" "; }
        if (v.json_field) { d += "data-json=\"" + v.json_field + "\" "; }
        if (v.post_field) { d += "data-post=\"" + v.post_field + "\" "; }
        if (v.extraattributes)
        if (v.readonly) { d += "data-noedit=\"true\" "; }
        if (v.animalfilter) { d += "data-filter=\"" + v.animalfilter + "\" "; }
        if (v.validation) { d += "data-validation=\"" + v.validation + "\" "; }
        if (v.value) { d += "value=\"" + tableform._attr_value(v.value) + "\" "; }
        if (v.xattr) { d += v.xattr + " "; }
        d += "/>";
        return tableform._render_formfield(v, d);
    },

    render_check: function(v) {
        let d = "";
        tableform._check_id(v);
        let label = tableform._render_label(v);
        if (v.labelpos && v.labelpos == "before") { d += label; }
        d += "<input type=\"checkbox\" ";
        d += tableform._render_class(v, "asm-checkbox");
        if (v.id) { d += "id=\"" + v.id + "\" "; }
        if (v.json_field) { d += "data-json=\"" + v.json_field + "\" "; }
        if (v.post_field) { d += "data-post=\"" + v.post_field + "\" "; }
        if (v.readonly) { d += "data-noedit=\"true\" "; }
        if (v.tooltip) { d += "title=\"" + html.title(v.tooltip) + "\""; }
        if (v.value && (v.value !== "0")) { d += "checked=\"checked\" "; }
        if (v.xattr) { d += v.xattr + " "; }
        d += "/>";
        if (!v.labelpos || v.labelpos == "after") { d += label; }
        if (v.xbutton) { d += " <button id=\"button-" + v.id + "\">" + v.xbutton + "</button>"; }
        if (v.xmarkup) { d += v.xmarkup; }
        return tableform._render_formfield(v, d);
    },

    render_currency: function(v) {
        let d = "";
        tableform._check_id(v);
        d += "<input type=\"text\" ";
        d += tableform._render_class(v, "asm-textbox asm-currencybox");
        if (v.id) { d += "id=\"" + v.id + "\" "; }
        if (v.json_field) { d += "data-json=\"" + v.json_field + "\" "; }
        if (v.post_field) { d += "data-post=\"" + v.post_field + "\" "; }
        if (v.readonly) { d += "data-noedit=\"true\" "; }
        if (v.validation) { d += "data-validation=\"" + v.validation + "\" "; }
        if (v.tooltip) { d += "title=\"" + html.title(v.tooltip) + "\""; }
        if (v.placeholder) { d += "placeholder=\"" + v.placeholder + "\" "; }
        if (v.value) { d += "value=\"" + tableform._attr_value(v.value) + "\" "; }
        if (v.xattr) { d += v.xattr + " "; }
        d += "/>";
        if (v.xbutton) { d += " <button id=\"button-" + v.id + "\">" + v.xbutton + "</button>"; }
        if (v.xmarkup) { d += v.xmarkup; }
        return tableform._render_formfield(v, d);
    },

    render_date: function(v) {
        let d = "";
        tableform._check_id(v);
        d += "<input type=\"text\" ";
        d += tableform._render_class(v, "asm-textbox asm-datebox");
        if (v.id) { d += "id=\"" + v.id + "\" "; }
        if (v.date_onlydays) { d += "data-onlydays=\"" + v.onlydays + "\" "; }
        if (v.date_nofuture) { d+= "data-nofuture=\"true\" "; }
        if (v.date_nopast) { d+= "data-nopast=\"true\" "; }
        if (v.json_field) { d += "data-json=\"" + v.json_field + "\" "; }
        if (v.post_field) { d += "data-post=\"" + v.post_field + "\" "; }
        if (v.readonly) { d += "data-noedit=\"true\" "; }
        if (v.validation) { d += "data-validation=\"" + v.validation + "\" "; }
        if (v.tooltip) { d += "title=\"" + html.title(v.tooltip) + "\""; }
        if (v.placeholder) { d += "placeholder=\"" + v.placeholder + "\" "; }
        if (v.value) { d += "value=\"" + tableform._attr_value(v.value) + "\" "; }
        if (v.xattr) { d += v.xattr + " "; }
        d += "/>";
        if (v.xbutton) { d += " <button id=\"button-" + v.id + "\">" + v.xbutton + "</button>"; }
        if (v.xmarkup) { d += v.xmarkup; }
        return tableform._render_formfield(v, d);
    },

    render_datetime: function(v) {
        let d = "";
        tableform._check_id(v);
        d += "<span style=\"white-space: nowrap\">";
        d += "<input type=\"text\" ";
        d += tableform._render_class(v, "asm-textbox asm-datebox asm-halftextbox");
        if (v.id) { d += "id=\"" + v.id + "date\" "; }
        if (v.json_field) { d += "data-json=\"" + v.json_field + "\" "; }
        if (v.post_field) { d += "data-post=\"" + v.post_field + "date\" "; }
        if (v.readonly) { d += "data-noedit=\"true\" "; }
        if (v.validation) { d += "data-validation=\"" + v.validation + "\" "; }
        if (v.tooltip) { d += "title=\"" + html.title(v.tooltip) + "\""; }
        if (v.placeholder) { d += "placeholder=\"" + v.placeholder + "\" "; }
        if (v.value) { d += "value=\"" + tableform._attr_value(v.value) + "\" "; }
        if (v.xattr) { d += v.xattr + " "; }
        d += "/>";
        d += "<input type=\"text\" ";
        d += tableform._render_class(v, "asm-textbox asm-timebox asm-halftextbox");
        if (v.id) { d += "id=\"" + v.id + "time\" "; }
        if (v.json_field) { d += "data-json=\"" + v.json_field + "\" "; }
        if (v.post_field) { d += "data-post=\"" + v.post_field + "time\" "; }
        if (v.readonly) { d += "data-noedit=\"true\" "; }
        if (v.validation) { d += "data-validation=\"" + v.validation + "\" "; }
        if (v.tooltip) { d += "title=\"" + html.title(v.tooltip) + "\""; }
        if (v.xattr) { d += v.xattr + " "; }
        d += "/>";
        if (v.xbutton) { d += " <button id=\"button-" + v.id + "\">" + v.xbutton + "</button>"; }
        if (v.xmarkup) { d += v.xmarkup; }
        d += "</span>";
        return tableform._render_formfield(v, d);
    },

    render_file: function(v) {
        let d = "";
        tableform._check_id(v);
        d += "<input type=\"file\" ";
        d += tableform._render_class(v, "asm-filechooser");
        if (v.id) { d += "id=\"" + v.id + "\" "; }
        if (v.json_field) { d += "data-json=\"" + v.json_field + "\" "; }
        if (v.post_field) { d += "data-post=\"" + v.post_field + "\" name=\"" + v.post_field + "\" "; }
        if (v.readonly) { d += "data-noedit=\"true\" "; }
        if (v.validation) { d += "data-validation=\"" + v.validation + "\" "; }
        if (v.tooltip) { d += "title=\"" + html.title(v.tooltip) + "\""; }
        if (v.xattr) { d += v.xattr + " "; }
        d += "/>";
        return tableform._render_formfield(v, d);
    },

    render_htmleditor: function(v) {
        let d = "";
        tableform._check_id(v);
        if (!v.width) { v.width = "100%"; }
        if (!v.height) { v.height = "150px"; }
        d += "<textarea ";
        d += tableform._render_class(v, "asm-htmleditor");
        if (v.id) { d += "id=\"" + v.id + "\" "; }
        if (v.width && v.height) { d += "data-width=\"" + v.width + "\" data-height=\"" + v.height + "\" "; }
        if (v.json_field) { d += "data-json=\"" + v.json_field + "\" "; }
        if (v.post_field) { d += "data-post=\"" + v.post_field + "\" "; }
        if (v.readonly) { d += "data-noedit=\"true\" "; }
        if (v.validation) { d += "data-validation=\"" + v.validation + "\" "; }
        if (v.tooltip) { d += "title=\"" + html.title(v.tooltip) + "\""; }
        if (v.xattr) { d += v.xattr + " "; }
        d += ">";
        if (v.value) { d += v.value; }
        d += "</textarea>";
        return tableform._render_formfield(v, d);
    },

    render_intnumber: function(v) {
        let d = "";
        tableform._check_id(v);
        d += "<input type=\"text\" ";
        d += tableform._render_class(v, "asm-textbox asm-intbox");
        if (v.id) { d += "id=\"" + v.id + "\" "; }
        if (v.json_field) { d += "data-json=\"" + v.json_field + "\" "; }
        if (v.post_field) { d += "data-post=\"" + v.post_field + "\" "; }
        if (v.min) { d += "data-min=\"" + v.min + "\" " ;}
        if (v.max) { d += "data-max=\"" + v.max + "\" " ;}
        if (v.readonly) { d += "data-noedit=\"true\" "; }
        if (v.validation) { d += "data-validation=\"" + v.validation + "\" "; }
        if (v.tooltip) { d += "title=\"" + html.title(v.tooltip) + "\""; }
        if (v.placeholder) { d += "placeholder=\"" + v.placeholder + "\" "; }
        if (v.value) { d += "value=\"" + tableform._attr_value(v.value) + "\" "; }
        if (v.xattr) { d += v.xattr + " "; }
        d += "/>";
        if (v.xbutton) { d += " <button id=\"button-" + v.id + "\">" + v.xbutton + "</button>"; }
        if (v.xmarkup) { d += v.xmarkup; }
        return tableform._render_formfield(v, d);
    },

    render_markup: function(v) {
        return tableform._render_formfield(v, v.markup);
    },

    render_number: function(v) {
        let d = "";
        tableform._check_id(v);
        d += "<input type=\"text\" ";
        d += tableform._render_class(v, "asm-textbox asm-numberbox");
        if (v.id) { d += "id=\"" + v.id + "\" "; }
        if (v.json_field) { d += "data-json=\"" + v.json_field + "\" "; }
        if (v.post_field) { d += "data-post=\"" + v.post_field + "\" "; }
        if (v.min) { d += "data-min=\"" + v.min + "\" " ;}
        if (v.max) { d += "data-max=\"" + v.max + "\" " ;}
        if (v.readonly) { d += "data-noedit=\"true\" "; }
        if (v.validation) { d += "data-validation=\"" + v.validation + "\" "; }
        if (v.tooltip) { d += "title=\"" + html.title(v.tooltip) + "\""; }
        if (v.placeholder) { d += "placeholder=\"" + v.placeholder + "\" "; }
        if (v.value) { d += "value=\"" + tableform._attr_value(v.value) + "\" "; }
        if (v.xattr) { d += v.xattr + " "; }
        d += "/>";
        if (v.xbutton) { d += " <button id=\"button-" + v.id + "\">" + v.xbutton + "</button>"; }
        if (v.xmarkup) { d += v.xmarkup; }
        return tableform._render_formfield(v, d);
    },

    render_person: function(v) {
        let d = "";
        tableform._check_id(v);
        d += "<input type=\"hidden\" ";
        d += tableform._render_class(v, "asm-personchooser");
        if (v.id) { d += "id=\"" + v.id + "\" "; }
        if (v.json_field) { d += "data-json=\"" + v.json_field + "\" "; }
        if (v.post_field) { d += "data-post=\"" + v.post_field + "\" "; }
        if (v.readonly) { d += "data-noedit=\"true\" "; }
        if (v.personfilter) { d += "data-filter=\"" + v.personfilter + "\" "; }
        if (v.personmode) { d += "data-mode=\"" + v.personmode + "\" "; }
        if (v.validation) { d += "data-validation=\"" + v.validation + "\" "; }
        if (v.value) { d += "value=\"" + tableform._attr_value(v.value) + "\" "; }
        if (v.xattr) { d += v.xattr + " "; }
        d += "/>";
        return tableform._render_formfield(v, d);
    },

    render_richtextarea: function(v) {
        let d = "";
        tableform._check_id(v);
        if (!v.width) { v.width = "100%"; }
        if (!v.height) { v.height = "64px"; }
        if (!v.margintop) { v.margintop = "24px"; }
        d += "<div id=\"" + v.id + "\" ";
        d += tableform._render_class(v, "asm-richtextarea");
        d += "data-width=\"" + v.width + "\" data-height=\"" + v.height + "\" data-margin-top=\"" + v.margintop + "\" " ;
        if (v.json_field) { d += "data-json=\"" + v.json_field + "\" "; }
        if (v.post_field) { d += "data-post=\"" + v.post_field + "\" "; }
        if (v.readonly) { d += "data-noedit=\"true\" "; }
        if (v.validation) { d += "data-validation=\"" + v.validation + "\" "; }
        if (v.tooltip) { d += "title=\"" + html.title(v.tooltip) + "\""; }
        if (v.xattr) { d += v.xattr + " "; }
        d += "></div>";
        return tableform._render_formfield(v, d);
    },

    render_select: function(v) {
        let d = "";
        tableform._check_id(v);
        d += "<select ";
        d += tableform._render_class(v, "asm-selectbox");
        if (v.id) { d += "id=\"" + v.id + "\" "; }
        if (v.json_field) { d += "data-json=\"" + v.json_field + "\" "; }
        if (v.post_field) { d += "data-post=\"" + v.post_field + "\" "; }
        if (v.readonly) { d += "data-noedit=\"true\" "; }
        if (v.validation) { d += "data-validation=\"" + v.validation + "\" "; }
        if (v.tooltip) { d += "title=\"" + html.title(v.tooltip) + "\""; }
        if (v.xattr) { d += v.xattr + " "; }
        d += ">";
        if (common.is_array(v.options)) {
            d += html.list_to_options_array(v.options); 
        }
        else if (common.is_string(v.options)) {
            d += v.options;
        }
        else if (v.options && v.options.rows) {
            if (v.options.prepend) { d += v.options.prepend; }
            if (!v.options.valuefield) { v.options.valuefield = "ID"; } // assume ID if not given - is for most things
            d += html.list_to_options(v.options.rows, v.options.valuefield, v.options.displayfield);
        }
        d += "</select>";
        if (v.xbutton) { d += " <button id=\"button-" + v.id + "\">" + v.xbutton + "</button>"; }
        if (v.xmarkup) { d += v.xmarkup; }
        return tableform._render_formfield(v, d);
    },

    render_selectmulti: function(v) {
        let d = "";
        tableform._check_id(v);
        d += "<select multiple=\"multiple\" ";
        d += tableform._render_class(v, "asm-bsmselect");
        if (v.id) { d += "id=\"" + v.id + "\" "; }
        if (v.json_field) { d += "data-json=\"" + v.json_field + "\" "; }
        if (v.post_field) { d += "data-post=\"" + v.post_field + "\" "; }
        if (v.readonly) { d += "data-noedit=\"true\" "; }
        if (v.validation) { d += "data-validation=\"" + v.validation + "\" "; }
        if (v.tooltip) { d += "title=\"" + html.title(v.tooltip) + "\""; }
        if (v.xattr) { d += v.xattr + " "; }
        d += ">";
        if (v.options && v.options.rows) {
            if (v.options.prepend) { d += v.options.prepend; }
            d += html.list_to_options(v.options.rows, v.options.valuefield, v.options.displayfield);
        }
        else if (v.options) {
            d += v.options;
        }
        d += "</select>";
        return tableform._render_formfield(v, d);
    },

    render_sqleditor: function(v) {
        let d = "";
        tableform._check_id(v);
        if (!v.width) { v.width = "100%"; }
        if (!v.height) { v.height = "150px"; }
        d += "<textarea ";
        d += tableform._render_class(v, "asm-sqleditor");
        if (v.id) { d += "id=\"" + v.id + "\" "; }
        if (v.width && v.height) { d += "data-width=\"" + v.width + "\" data-height=\"" + v.height + "\" "; }
        if (v.json_field) { d += "data-json=\"" + v.json_field + "\" "; }
        if (v.post_field) { d += "data-post=\"" + v.post_field + "\" "; }
        if (v.readonly) { d += "data-noedit=\"true\" "; }
        if (v.validation) { d += "data-validation=\"" + v.validation + "\" "; }
        if (v.tooltip) { d += "title=\"" + html.title(v.tooltip) + "\""; }
        if (v.xattr) { d += v.xattr + " "; }
        d += ">";
        if (v.value) { d += v.value; }
        d += "</textarea>";
        return tableform._render_formfield(v, d);
    },

    render_text: function(v) {
        let d = "";
        tableform._check_id(v);
        d += "<input type=\"" + (v.type || "text") + "\" ";
        d += tableform._render_class(v, "asm-textbox");
        if (v.id) { d += "id=\"" + v.id + "\" "; }
        if (v.json_field) { d += "data-json=\"" + v.json_field + "\" "; }
        if (v.post_field) { d += "data-post=\"" + v.post_field + "\" "; }
        if (v.readonly) { d += "data-noedit=\"true\" "; }
        if (v.validation) { d += "data-validation=\"" + v.validation + "\" "; }
        if (v.tooltip) { d += "title=\"" + html.title(v.tooltip) + "\" "; }
        if (v.placeholder) { d += "placeholder=\"" + v.placeholder + "\" "; }
        if (v.maxlength) { d += "maxlength=" + v.maxlength; }
        if (v.value) { d += "value=\"" + tableform._attr_value(v.value) + "\" "; }
        if (v.xattr) { d += v.xattr + " "; }
        d += "/>";
        if (v.xbutton) { d += " <button id=\"button-" + v.id + "\">" + v.xbutton + "</button>"; }
        if (v.xmarkup) { d += v.xmarkup; }
        return tableform._render_formfield(v, d);
    },

    render_time: function(v) {
        let d = "";
        tableform._check_id(v);
        d += "<input type=\"text\" ";
        d += tableform._render_class(v, "asm-textbox asm-timebox");
        if (v.id) { d += "id=\"" + v.id + "\" "; }
        if (v.json_field) { d += "data-json=\"" + v.json_field + "\" "; }
        if (v.post_field) { d += "data-post=\"" + v.post_field + "\" "; }
        if (v.readonly) { d += "data-noedit=\"true\" "; }
        if (v.validation) { d += "data-validation=\"" + v.validation + "\" "; }
        if (v.tooltip) { d += "title=\"" + html.title(v.tooltip) + "\""; }
        if (v.placeholder) { d += "placeholder=\"" + v.placeholder + "\" "; }
        if (v.value) { d += "value=\"" + tableform._attr_value(v.value) + "\" "; }
        if (v.xattr) { d += v.xattr + " "; }
        d += "/>";
        if (v.xbutton) { d += " <button id=\"button-" + v.id + "\">" + v.xbutton + "</button>"; }
        if (v.xmarkup) { d += v.xmarkup; }
        return tableform._render_formfield(v, d);
    },

    render_textarea: function(v) {
        let d = "";
        tableform._check_id(v);
        if (!v.rows) { v.rows = 5; }
        d += "<textarea "; 
        d += tableform._render_class(v, "asm-textarea");
        if (v.id) { d += "id=\"" + v.id + "\" "; }
        if (v.rows) { d += "rows=\"" + v.rows + "\" "; }
        if (v.json_field) { d += "data-json=\"" + v.json_field + "\" "; }
        if (v.post_field) { d += "data-post=\"" + v.post_field + "\" "; }
        if (v.readonly) { d += "data-noedit=\"true\" "; }
        if (v.validation) { d += "data-validation=\"" + v.validation + "\" "; }
        if (v.tooltip) { d += "title=\"" + html.title(v.tooltip) + "\" "; }
        if (!v.tooltip) { d += "title=\"" + html.title(v.label) + "\" "; } // use the label if a title wasn't given
        if (v.maxlength) { d += "maxlength=" + v.maxlength; }
        if (v.placeholder) { d += "placeholder=\"" + v.placeholder + "\" "; }
        if (v.xattr) { d += v.xattr + " "; }
        d += ">";
        if (v.value) { d += v.value; }
        d += "</textarea>";
        if (v.xbutton) { d += " <button id=\"button-" + v.id + "\">" + v.xbutton + "</button>"; }
        if (v.xmarkup) { d += v.xmarkup; }
        return tableform._render_formfield(v, d);
    },

    /**
     * Binds fields
     *
     * fields: (see fields_render) 
     */
    fields_bind: function(fields) {
        $.each(fields, function(i, v) {
            if (v.change) {
                $("#" + v.post_field).change(v.change);
            }
            if (v.blur) {
                $("#" + v.post_field).blur(v.blur);
            }
        });
    },

    /**
     * Sets on screen fields to their default values
     */
    fields_default: function(fields) {
        $.each(fields, function(i, v) {
            // No default value given, use a blank
            if (!v.defaultval) {
                if (v.type == "check") { $("#" + v.post_field).prop("checked", false); return; }
                if (v.type == "currency") { $("#" + v.post_field).currency("value", 0); return; }
                if (v.type == "animal") { $("#" + v.post_field).animalchooser("clear"); return; }
                if (v.type == "animalmulti") { $("#" + v.post_field).animalchoosermulti("clear"); return; }
                if (v.type == "person") { $("#" + v.post_field).personchooser("clear"); return; }
                if (v.type == "selectmulti") { 
                    $("#" + v.post_field).children().prop("selected", false); 
                    $("#" + v.post_field).change(); 
                    return;
                }
                if (v.type == "textarea") { $("#" + v.post_field).val("");  return; }
                if (v.type == "richtextarea") { $("#" + v.post_field).richtextarea("value", ""); return; }
                if (v.type == "htmleditor") { $("#" + v.post_field).htmleditor("value", ""); return; }
                if (v.type == "sqleditor") { $("#" + v.post_field).sqleditor("value", ""); return; }
                if (v.type != "select" && v.type != "nextcol") { $("#" + v.post_field).val(""); }
            }
            else {
                // Is the default value a function? If so, run it 
                // to get the real value to assign
                var dval = v.defaultval;
                if (v.defaultval instanceof Function) {
                    dval = v.defaultval();
                }
                if (v.defaultval instanceof Date) {
                    dval = format.date(v.defaultval);
                }
                if (v.type == "check") { $("#" + v.post_field).prop("checked", dval); return; }
                if (v.type == "currency") { $("#" + v.post_field).currency("value", dval); return; }
                if (v.type == "animal") { $("#" + v.post_field).animalchooser("loadbyid", dval); return; }
                if (v.type == "person") { $("#" + v.post_field).personchooser("loadbyid", dval); return; }
                if (v.type == "select") { $("#" + v.post_field).select("value", dval); return; }
                if (v.type == "textarea") { $("#" + v.post_field).val(dval); return; }
                if (v.type == "richtextarea") { $("#" + v.post_field).richtextarea("value", dval); return; }
                if (v.type == "htmleditor") { $("#" + v.post_field).htmleditor("value", dval); return; }
                if (v.type == "sqleditor") { $("#" + v.post_field).sqleditor("value", dval); return; }
                if (v.type != "nextcol") { $("#" + v.post_field).val(dval); }
            }
        });
    },

    /**
     * Populates fields
     *
     * fields: ( see fields_render) 
     * row: The json row to use
     */
    fields_populate_from_json: function(fields, row) {
        $.each(fields, function(i, v) {
            var n = $("#" + v.post_field);
            if (v.type == "animal") {
                n.animalchooser("clear", false);
                n.animalchooser("loadbyid", row[v.json_field]);
            }
            else if (v.type == "animalmulti") {
                n.animalchoosermulti("clear");
                n.animalchoosermulti("selectbyids", row[v.json_field]);
            }
            else if (v.type == "person") {
                n.personchooser("clear", false);
                n.personchooser("loadbyid", row[v.json_field]);
            }
            else if (v.type == "currency") {
                n.currency("value", row[v.json_field]);
            }
            else if (v.type == "date") {
                n.val(format.date(row[v.json_field]));
            }
            else if (v.type == "time") {
                n.val(format.time(row[v.json_field]));
            }
            else if (v.type == "datetime") {
                $("#" + v.post_field + "date").val(format.date(row[v.json_field]));
                $("#" + v.post_field + "time").val(format.time(row[v.json_field]));
            }
            else if (v.type == "check") {
                n.prop("checked", row[v.json_field] == 1);
            }
            else if (v.type =="select") {
                n.select("value", html.decode(row[v.json_field])); 
            }
            else if (v.type == "selectmulti") {
                n.children().prop("selected", false);
                $.each(String(row[v.json_field]).split(/[|,]+/), function(mi, mv) {
                    n.find("option").each(function() {
                        var ot = $(this), ov = $(this).prop("value");
                        if (html.decode(mv) == html.decode(ov)) {
                            ot.prop("selected", true);
                        }
                    });
                });
                n.change();
            }
            else if (v.type == "textarea") {
                // Unescaped tags in textareas behave unpredictably
                var s = row[v.json_field];
                if (!s) { s = ""; }
                s = s.replace(/</g, "&lt;").replace(/>/g, "&gt;");
                n.val(html.decode(s));
            }
            else if (v.type == "richtextarea") {
                n.richtextarea("value", row[v.json_field]);
            }
            else if (v.type == "htmleditor") {
                n.htmleditor("value", row[v.json_field]);
            }
            else if (v.type == "sqleditor") {
                n.sqleditor("value", row[v.json_field]);
            }
            else {
                if (n.length == 0) { return; }
                n.val(html.decode(row[v.json_field]));
            }
        });
    },

    /**
     * Updates a row with the field contents
     * fields: (see fields_render)
     * row: The row to update
     */
    fields_update_row: function(fields, row) {
        $.each(fields, function(i, v) {
            var n = $("#" + v.post_field);
            if (v.type == "currency") {
                row[v.json_field] = n.currency("value");
            }
            else if (v.type == "date") {
                row[v.json_field] = format.date_iso(n.val());
            }
            else if (v.type == "time") {
                // always declare time fields after dates so we can
                // modify the time on the timestamp
                var ts = n.val();
                if (!ts) { ts = "00:00:00"; }
                row[v.json_field] = format.date_iso_settime(row[v.json_field], ts);
            }
            else if (v.type == "datetime") {
                var dv = $("#" + v.post_field + "date").val();
                var tv = $("#" + v.post_field + "time").val();
                row[v.json_field] = format.date_iso(dv);
                row[v.json_field] = format.date_iso_settime(row[v.json_field], tv);
            }
            else if (v.type == "check") {
                row[v.json_field] = n.is(":checked") ? 1 : 0;
            }
            else if (v.type == "htmleditor") {
                row[v.json_field] = n.htmleditor("value");
            }
            else if (v.type == "richtextarea") {
                row[v.json_field] = n.richtextarea("value");
            }
            else if (v.type == "sqleditor") {
                row[v.json_field] = n.sqleditor("value");
            }
            else if (v.type == "selectmulti") {
                if (!n.val()) { 
                    row[v.json_field] = ""; 
                }
                else if ($.isArray(n.val())) {
                    row[v.json_field] = n.val().join("|");
                }
                else {
                    row[v.json_field] = n.val();
                }
            }
            else {
                row[v.json_field] = n.val();
            }
        });
    },

    /**
     * Validates the fields against their rules. Returns false if there
     * was a problem or true for ok.
     * Also does the job of highlighting the failed field.
     *
     * fields: (see fields_render) 
     * row: The json row to use
     */
    fields_validate: function(fields) {
        let nbids = [], nzids = [], veids = [], vtids = [];
        let rv = true;
        $.each(fields, function(i, v) {
            $("label[for='" + v.post_field + "']").removeClass(validate.ERROR_LABEL_CLASS);
            if (v.validation == "notblank") {
                nbids.push(v.post_field);
                if (v.type == "datetime") { 
                    nbids.push(v.post_field + "date"); nbids.push(v.post_field + "time"); 
                }
            }
            if (v.validation == "notzero") {
                nzids.push(v.post_field);
            }
            if (v.validation == "validemail") {
                veids.push(v.post_field);
            }
            if (v.validation instanceof Function) {
                rv = v.validation($("#" + v.post_field).val());
                validate.highlight(v.post_field);
                if (!rv) { return false; }// stop iterating
            }
            if (v.type == "time") {
                vtids.push(v.post_field);
            }
        });
        if (!rv) { return rv; } // If one of the fields failed, stop now
        if (nbids.length > 0) {
            rv = validate.notblank(nbids);
            if (!rv) { return rv; }
        }
        if (nzids.length > 0) {
            rv = validate.notzero(nzids);
            if (!rv) { return rv; }
        }
        if (vtids.length > 0) {
            rv = validate.validtime(vtids);
            if (!rv) { return rv; }
        }
        if (veids.length > 0) {
            rv = validate.validemail(veids);
            if (!rv) { return rv; }
        }
        return true;
    },

    /**
     * Posts the fields back to the controller. If an error occurred,
     * the message is output to the header. On success, the callback
     * method is called.
     * fields: (see fields_render) 
     * postvar: any extra post variables to send, eg: mode=amazing - don't leave trailing &
     * postto: The URL to post to
     * callback: function to call on success of the post, the ajax response is passed
     * errorcallback: function to call on error, the response is passed
     * return value is a promise.
     */
    fields_post: function(fields, postvar, postto, callback, errorcallback) {
        var post = "", deferred = $.Deferred();
        if (postvar) { post = postvar; }
        $.each(fields, function(i, v) {
            var n = $("#" + v.post_field);
            if (v.type == "check") {
                if (post != "") { post += "&"; }
                if (n.is(":checked")) {
                    post += v.post_field + "=checked";
                }
                else {
                    post += v.post_field + "=off";
                }
            }
            else if (v.type == "datetime") {
                if (post != "") { post += "&"; }
                post += v.post_field + "date=" + encodeURIComponent($("#" + v.post_field + "date").val());
                post += "&" + v.post_field + "time=" + encodeURIComponent($("#" + v.post_field + "time").val());
            }
            else if (v.type == "richtextarea") {
                if (post != "") { post += "&"; }
                post += v.post_field + "=" + encodeURIComponent(n.richtextarea("value"));
            }
            else if (v.type == "currency") {
                if (post != "") { post += "&"; }
                post += v.post_field + "=" + encodeURIComponent(n.currency("value"));
            }
            else if (v.type != "raw") {
                if (post != "") { post += "&"; }
                var pv = "";
                if (n.val()) { pv = n.val(); }
                post += v.post_field + "=" + encodeURIComponent(pv);
            }
        });
        $.ajax({
            type: "POST",
            url:  postto,
            data: post,
            dataType: "text",
            success: function(result) {
                if (callback) { callback(result); }
                deferred.resolve(result);
            },
            error: function(jqxhr, textstatus, response) {
                var errmessage = common.get_error_response(jqxhr, textstatus, response);
                tableform.dialog_error(errmessage);
                if (errorcallback) { errorcallback(errmessage); }
                deferred.reject(response);
            }
        });
        return deferred.promise();
    },

    /**
     * Prompts the user to delete with a dialog.
     * callback: Function to be run if the user clicks delete
     * text: The delete dialog text (don't pass for the default)
     * returns a promise.
     */
    delete_dialog: function(callback, text) {
        var b = {}, deferred = $.Deferred(); 
        b[_("Delete")] = {
            text: _("Delete"),
            "class": 'asm-redbutton',
            click: function() {
                $("#dialog-delete").dialog("close");
                if (callback) { callback(); }
                deferred.resolve();
            }
        };
        b[_("Cancel")] = function() { 
            $(this).dialog("close"); 
            deferred.reject("dialog cancelled");
        };
        var mess = _("This will permanently remove the selected records, are you sure?"); 
        if (text && text != "") {
            mess = text;
        }
        if ($("#dialog-delete").length == 0) {
            $("body").append('<div id="dialog-delete" style="display: none" title="' +
                _("Delete") + '"><p><span class="ui-icon ui-icon-alert"></span>' +
                '<span id="dialog-delete-text"></span></p></div>');
        }
        $("#dialog-delete-text").html(mess);
        $("#dialog-delete").dialog({
            resizable: false,
            height: "auto",
            width: 400,
            modal: true,
            dialogClass: "dialogshadow",
            show: dlgfx.delete_show,
            hide: dlgfx.delete_hide,
            buttons: b
        });
        return deferred.promise();
    },

    /**
     * Shows an Ok/Cancel dialog.
     * selector: The dialog div
     * oktext: The text to show on the ok button
     * o: Additional options to pass the dialog
     * callback: A function to call when ok is clicked.
     * returns a promise that resolves when ok is clicked.
     */
    show_okcancel_dialog: function(selector, oktext, o) {
        
        var b = {}, deferred = $.Deferred();

        // If this dialog has already been created, destroy it first
        common.widget_destroy(selector, "dialog", true);

        b[oktext] = function() {
            // We've been given a list of fields that should not be blank or zero,
            // validate them before doing anything
            if (o && o.notblank) {
                if (!validate.notblank(o.notblank)) { return; }
            }
            if (o && o.notzero) {
                if (!validate.notzero(o.notzero)) { return; }
            }
            $(selector).dialog("close");
            if (o && o.callback) { o.callback(); }
            deferred.resolve();
        };

        if (o && !o.hidecancel) {
            b[_("Cancel")] = function() { 
                $(this).dialog("close"); 
                deferred.reject("dialog cancelled");
            };
        }

        if (!o) { o = {}; }
        $.extend(o, {
            autoOpen: false,
            modal: true,
            dialogClass: "dialogshadow",
            show: dlgfx.delete_show,
            hide: dlgfx.delete_hide,
            buttons: b
        });
        $(selector).dialog(o).dialog("open");

        return deferred.promise();
    }

};
