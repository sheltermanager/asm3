/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    var sql = {

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
                        "dumpsqlnomedia|" + _("SQL dump (without media)"),
                        "dumpddlmysql|" + _("DDL dump (MySQL)"),
                        "dumpddlpostgres|" + _("DDL dump (PostgreSQL)"),
                        // ASM2_COMPATIBILITY
                        "dumpsqlasm2|" + _("SQL dump (ASM2 HSQLDB Format)"),
                        "dumpsqlasm2nomedia|" + _("SQL dump (ASM2 HSQLDB Format, without media)"),
                        // ASM2_COMPATIBILITY
                        "animalcsv|" + _("CSV of animal/adopter data"), 
                        "personcsv|" + _("CSV of person data"),
                        "incidentcsv|" + _("CSV of incident data"),
                        "licencecsv|" + _("CSV of license data"),
                        "paymentcsv|" + _("CSV of payment data")
                    ]}
                ], true),
                '</div>',
                '<textarea id="sql" class="asm-sqleditor" data-height="150px" data="sql" rows="10"></textarea>',
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
                '<label for="sqlfile">' + _("Script") + ' <input id="sqlfile" type="file" name="sqlfile" /></label>',
                '</form>',
                '</div>'
            ].join("\n");
        },

        /** One of the three dump button choices so once the confirm dialog has been agreed
         *  to, we know where to redirect to
         */
        dumpchoice: "dumpsql",

        bind_scriptdialog: function() {

            var b = { };
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

            var dbuttons = {};
            dbuttons[_("Yes")] = function() {
                $(this).dialog("close");
                common.route("sql_dump?ajax=false&mode=" + sql.dumpchoice);
            };
            dbuttons[_("No")] = function() {
                $(this).dialog("close");
            };

            var confirm_dump = function(action) {
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

            $("#button-exec").button().click(function() {
                var formdata = "mode=exec&" + $("#sql").toPOST();
                $("#button-exec").button("disable");
                header.show_loading(_("Executing..."));
                common.ajax_post("sql", formdata)
                    .then(function(result) { 
                        if (result.indexOf("<thead") == 0) {
                            $("#sql-results").html(result);
                            $("#sql-results").table();
                            $("#sql-results").fadeIn();
                            var norecs = String($("#sql-results tr").length - 1);
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
                    })
                    .always(function() {
                        $("#button-exec").button("enable");
                    });
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
