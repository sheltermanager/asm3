/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const sql = {

        history: [ "" ],

        render: function() {
            this.buttons = [
                { type: "raw", markup: 
                '<span id="callout-sql" class="asm-callout">' + 
                    _("SQL editor: Press F11 to go full screen and press CTRL+SPACE to autocomplete table and column names") + 
                '</span>'},
                { id: "exec", text: _("Execute"), tooltip: _("Execute the SQL in the box below"), icon: "sql", hotkey: "ctrl+e",
                    click: function() {
                        // if the editor has the focus when you press CTRL+E, what you see on screen
                        // won't be returned by the value method until it loses the focus
                        $("#button-exec").focus(); 
                        sql.exec();
                    } },
                { id: "script", text: _("Execute Script"), tooltip: _("Upload an SQL script"), icon: "sql", 
                    click: function() {
                        $("#dialog-script").dialog("open");
                    } },
                { id: "export", text: _("Export"), tooltip: _("Export this database in various formats"), icon: "database",
                    type: "buttonmenu", 
                options: [ 
                    "dumpsql|" + _("SQL dump"), 
                    // ASM2_COMPATIBILITY
                    "dumpsqlasm2|" + _("SQL dump (ASM2 HSQLDB Format)"),
                    // ASM2_COMPATIBILITY
                    "animalcsv|" + _("CSV of animal/adopter data"), 
                    "medicalcsv|" + _("CSV of animal/medical data"), 
                    "mediacsv|" + _("CSV of media data"), 
                    "personcsv|" + _("CSV of person data"),
                    "incidentcsv|" + _("CSV of incident data"),
                    "licencecsv|" + _("CSV of license data"),
                    "paymentcsv|" + _("CSV of payment data"),
                    "dumpddlmysql|" + _("DDL dump (MySQL)"),
                    "dumpddlpostgres|" + _("DDL dump (PostgreSQL)"),
                    "dumpddldb2|" + _("DDL dump (DB2)")
                ]},
                { id: "history", type: "dropdownfilter", options: [],
                    click: function(selval) {
                        $("#sql").sqleditor("value", selval);
                    } }
                ];
            return [
                this.render_scriptdialog(),
                html.content_header(_("SQL Interface")),
                '<div id="dialog-dump" class="hidden" title="' + html.title(_("Confirm")) + '">',
                _("Exporting the complete database can take some time and generate a very large file, are you sure?") + "<br />" +
                _("The database will be inaccessible to all users while the export is in progress.") + '</div>',
                '<div class="asm-toolbar">',
                tableform.buttons_render(this.buttons, true),
                '</div>',
                '<textarea id="sql" class="asm-sqleditor" data-width="100%" data-height="150px" data="sql" rows="10"></textarea>',
                '<hr />',
                '<table id="sql-results"></table>',
                html.content_footer()
            ].join("\n");
        },

        render_scriptdialog: function() {
            return [
                '<div id="dialog-script" style="display: none" title="' + html.title(_("Execute Script")) + '">',
                '<form id="sqlfileform" action="sql" method="post" enctype="multipart/form-data">',
                '<input name="mode" value="execfile" type="hidden" />',
                '<label for="sqlfile">' + _("Script") + ' <input id="sqlfile" type="file" name="filechooser" /></label>',
                '</form>',
                '</div>'
            ].join("\n");
        },

        /** One of the three dump button choices so once the confirm dialog has been agreed
         *  to, we know where to redirect to
         */
        dumpchoice: "dumpsql",

        /** 
         * Push a new query into the history
         */
        add_to_history: function(v) {
            // if v is already in the queue, move it to the top
            if (sql.history.includes(v)) {
                sql.history = sql.history.filter(function(item) {
                    return item != v;
                });
            }
            sql.history.push(v);
            common.local_set("sql_history", sql.history.join("||"));
            $("#history").html(html.list_to_options(sql.history.toReversed()));
        },

        /**
         * Read the history from local storage 
         */
        read_history: function() {
            let h = common.local_get("sql_history");
            if (!h) {
                sql.history = [ "" ];
            }
            else {
                sql.history = h.split("||");
                $("#history").html(html.list_to_options(sql.history.toReversed()));
            }
        },

        /**
         * Sends the SQL in the editor to the backend for executing
         */
        exec: async function() {
            let formdata = "mode=exec&" + $("#sql").toPOST();
            $("#button-exec").button("disable");
            header.hide_error();
            header.show_loading(_("Executing..."));
            try {
                let result = await common.ajax_post("sql", formdata);
                // successful query, push to the history queue
                sql.add_to_history($("#sql").sqleditor("value"));
                if (result.indexOf("<thead") == 0) {
                    $("#sql-results").html(result);
                    $("#sql-results").table();
                    $("#sql-results").fadeIn();
                    let norecs = String($("#sql-results tbody tr").length);
                    header.show_info(_("{0} results.").replace("{0}", norecs));
                }
                else {
                    $("#sql-results").fadeOut();
                    if (result != "") {
                        header.show_info(result, 10000);
                    }
                    else {
                        header.show_info(_("No results."), 10000);
                    }
                }
            }
            finally {
                $("#button-exec").button("enable");
            }
        },

        bind_scriptdialog: function() {

            let b = { };
            b[_("Execute Script")] = function() {
                if (!validate.notblank([ "sqlfile" ])) { return; }
                $("#sqlfileform").submit();
            };
            b[_("Cancel")] = function() {
                $("#dialog-script").dialog("close");
            };
            $("#dialog-script").dialog({
                autoOpen: false,
                width: 550,
                modal: true,
                dialogClass: "dialogshadow",
                show: dlgfx.edit_show,
                hide: dlgfx.edit_hide,
                buttons: b
            });

        },

        bind: function() {
            
            tableform.buttons_bind(this.buttons);
            this.bind_scriptdialog();

            let dbuttons = {};
            dbuttons[_("Yes")] = function() {
                $(this).dialog("close");
                common.route("sql_dump?ajax=false&mode=" + sql.dumpchoice);
            };
            dbuttons[_("No")] = function() {
                $(this).dialog("close");
            };

            const confirm_dump = function(action) {
                sql.dumpchoice = action;
                $("#dialog-dump").dialog({ 
                    autoOpen: true,
                    modal: true,
                    dialogClass: "dialogshadow",
                    show: dlgfx.add_show,
                    hide: dlgfx.add_hide,
                    buttons: dbuttons 
                });
            };

            // Handles all export menu clicks by passing the action on to confirm_dump
            $("#button-export-body a").click(function() {
                confirm_dump($(this).attr("data"));
                return false;
            });

        },

        sync: function() {
            this.read_history();
        },

        name: "sql",
        animation: "options",
        autofocus: "#sql",
        title: function() { return _("SQL Interface"); },

        destroy: function() {
            tableform.buttons_destroy(this.buttons);
            common.widget_destroy("#dialog-script");
            common.widget_destroy("#sql");
        },

        routes: {
            "sql": function() {
                common.module_loadandstart("sql", "sql");
            }
        }


    };

    common.module_register(sql);

});
