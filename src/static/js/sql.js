/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const sql = {

        editor: null, 

        render: function() {
            return [
                this.render_scriptdialog(),
                html.content_header(_("SQL Interface")),
                '<div id="dialog-dump" class="hidden" title="' + html.title(_("Confirm")) + '">',
                _("Exporting the complete database can take some time and generate a very large file, are you sure?") + "<br />" +
                _("The database will be inaccessible to all users while the export is in progress.") + '</div>',
                '<div class="asm-toolbar">',
                tableform.buttons_render([
                    { type: "raw", markup: 
                    '<span id="callout-sql" class="asm-callout">' + 
                        _("SQL editor: Press F11 to go full screen and press CTRL+SPACE to autocomplete table and column names") + 
                    '</span>'},
                    { id: "exec", text: _("Execute"), tooltip: _("Execute the SQL in the box below"), icon: "sql" },
                    { id: "script", text: _("Execute Script"), tooltip: _("Upload an SQL script"), icon: "sql" },
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
                    ]}
                ], true),
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
            $("#button-export").asmmenu();
            $("#button-export-body a").click(function() {
                confirm_dump($(this).attr("data"));
                return false;
            });

            $("#button-exec").button().click(async function() {
                let formdata = "mode=exec&" + $("#sql").toPOST();
                $("#button-exec").button("disable");
                header.hide_error();
                header.show_loading(_("Executing..."));
                try {
                    let result = await common.ajax_post("sql", formdata);
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
                            header.show_info(result);
                        }
                        else {
                            header.show_info(_("No results."));
                        }
                    }
                }
                finally {
                    $("#button-exec").button("enable");
                }
            });

            $("#button-script").button().click(function() {
                $("#dialog-script").dialog("open");
            });
        },

        name: "sql",
        animation: "options",
        autofocus: "#sql",
        title: function() { return _("SQL Interface"); },

        destroy: function() {
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
