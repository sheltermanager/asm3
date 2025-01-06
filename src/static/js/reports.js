/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const emailhours = [
        { display: _("With overnight batch"), value: -1 },
        { display: "00:00", value: 0 },
        { display: "01:00", value: 1 },
        { display: "02:00", value: 2 },
        { display: "03:00", value: 3 },
        { display: "04:00", value: 4 },
        { display: "05:00", value: 5 },
        { display: "06:00", value: 6 },
        { display: "07:00", value: 7 },
        { display: "08:00", value: 8 },
        { display: "09:00", value: 9 },
        { display: "10:00", value: 10 },
        { display: "11:00", value: 11 },
        { display: "12:00", value: 12 },
        { display: "13:00", value: 13 },
        { display: "14:00", value: 14 },
        { display: "15:00", value: 15 },
        { display: "16:00", value: 16 },
        { display: "17:00", value: 17 },
        { display: "18:00", value: 18 },
        { display: "19:00", value: 19 },
        { display: "20:00", value: 20 },
        { display: "21:00", value: 21 },
        { display: "22:00", value: 22 },
        { display: "23:00", value: 23 }
    ];

    const emailfreq = [
        { ID: 0, DISPLAY: _("Every day") },
        { ID: 1, DISPLAY: _("Monday") },
        { ID: 2, DISPLAY: _("Tuesday") },
        { ID: 3, DISPLAY: _("Wednesday") },
        { ID: 4, DISPLAY: _("Thursday") },
        { ID: 5, DISPLAY: _("Friday") },
        { ID: 6, DISPLAY: _("Saturday") },
        { ID: 7, DISPLAY: _("Sunday") },
        { ID: 8, DISPLAY: _("Beginning of month") },
        { ID: 9, DISPLAY: _("End of month") },
        { ID: 10, DISPLAY: _("Start of year") },
        { ID: 11, DISPLAY: _("End of year") }
    ];


    const reports = {

        qb: null, // reference to the querybuilder code

        model: function() {
            const dialog = {
                add_title: _("Add report"),
                edit_title: _("Edit report"),
                edit_perm: 'hcr',
                close_on_ok: false,
                columns: 1,
                width: 800,
                fields: [
                    { json_field: "TYPE", post_field: "type", label: _("Type"), type: "select", options: 
                        [ '<option value="REPORT">' + _("Report") + '</option>',
                        '<option value="GRAPH">' + _("Chart") + '</option>',
                        '<option value="GRAPH BARS">' + _("Chart (Bar)") + '</option>',
                        '<option value="GRAPH LINES">' + _("Chart (Line)") + '</option>',
                        '<option value="GRAPH PIE">' + _("Chart (Pie)") + '</option>',
                        '<option value="GRAPH POINTS">' + _("Chart (Point)") + '</option>',
                        '<option value="GRAPH STEPS">' + _("Chart (Steps)") + '</option>',
                        '<option value="MAIL">' + _("Mail Merge") + '</option>',
                        '<option value="MAP">' + _("Map") + '</option>',
                        '<option value="MAP USER">' + _("Map (Center current loc)") + '</option>',
                        '<option value="MAP FIRST">' + _("Map (Center first valid)") + '</option>' ].join("\n") },

                    { json_field: "CATEGORY", post_field: "category", classes: "asm-doubletextbox", label: _("Category"), type: "text", validation: "notblank" },
                    { json_field: "TITLE", post_field: "title", classes: "asm-doubletextbox", label: _("Report Title"), type: "text", validation: "notblank" },
                    { json_field: "DESCRIPTION", post_field: "description", classes: "asm-doubletextbox", label: _("Description"), type: "text" },
                    { json_field: "DAILYEMAIL", post_field: "dailyemail", classes: "asm-doubletextbox", label: _("Email To"), type: "text", validation: "validemail", 
                        callout: _("An optional comma separated list of email addresses to send the output of this report to")},
                    { json_field: "DAILYEMAILFREQUENCY", post_field: "dailyemailfrequency", label: _("When"), type: "select", options: html.list_to_options(emailfreq, "ID", "DISPLAY") },
                    { json_field: "DAILYEMAILHOUR", post_field: "dailyemailhour", label: _("at"), type: "select",
                        options: { displayfield: "display", valuefield: "value", rows: emailhours }},
                    { json_field: "OMITHEADERFOOTER", post_field: "omitheaderfooter", label: _("Omit header/footer"), type: "check" },
                    { json_field: "OMITCRITERIA", post_field: "omitcriteria", label: _("Omit criteria"), type: "check" },
                    { json_field: "VIEWROLEIDS", post_field: "viewroles", label: _("View Roles"), type: "selectmulti", 
                        options: { rows: controller.roles, valuefield: "ID", displayfield: "ROLENAME" }},
                    { type: "raw", label: "", markup: '<button id="button-checksql">' + _("Syntax check this SQL") + '</button>' +
                        '<button id="button-genhtml">' + _("Generate HTML from this SQL") + '</button>' +
                        '<button id="button-qb">' + _("Use the query builder") + '</button>' },
                    { json_field: "SQLCOMMAND", post_field: "sql", label: _("SQL"), type: "sqleditor", height: "150px", width: "680px",
                        callout: _("SQL editor: Press F11 to go full screen and press CTRL+SPACE to autocomplete table and column names") },
                    { json_field: "HTMLBODY", post_field: "html", label: _("HTML"), type: "htmleditor", height: "150px", width: "680px" }
                ]
            };

            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: function(row) {
                    tableform.dialog_error("");
                    tableform.dialog_show_edit(dialog, row, {
                        onchange: function() {
                            if (!reports.validation()) { tableform.dialog_enable_buttons(); return; }
                            tableform.fields_update_row(dialog.fields, row);
                            reports.set_extra_fields(row);
                            tableform.fields_post(dialog.fields, "mode=update&reportid=" + row.ID, "reports", function(response) {
                                tableform.table_update(table);
                                tableform.dialog_close();
                            });
                        },
                        onload: function(row) {
                            let type = "REPORT";
                            if (row.HTMLBODY.indexOf("GRAPH") == 0 || row.HTMLBODY.indexOf("MAIL") == 0 || row.HTMLBODY.indexOf("MAP") == 0) { type = row.HTMLBODY; }
                            $("#type").select("value", type);
                            reports.change_type();
                            $("#button-qb").toggle( row.SQLCOMMAND.indexOf("-- qbtype") == 0 );
                        }
                    });
                },
                columns: [
                    { field: "CATEGORY", display: _("Type"), formatter: function(row) {
                        let rtype = _("Report");
                        if (row.HTMLBODY.indexOf("GRAPH") == 0) { rtype = _("Chart"); }
                        if (row.HTMLBODY.indexOf("MAIL") == 0) { rtype = _("Mail Merge"); }
                        if (row.HTMLBODY.indexOf("MAP") == 0) { rtype = _("Map"); }
                        return tableform.table_render_edit_link(row.ID, rtype);
                    }},
                    { field: "CATEGORY", display: _("Category") },
                    { field: "VIEWROLES", display: _("Roles"), formatter: function(row) {
                        return common.nulltostr(row.VIEWROLES).replace(/[|]+/g, ", ");
                    }},
                    { field: "DAILYEMAIL", display: _("Email To"), formatter: function(row) {
                        return common.replace_all(row.DAILYEMAIL, ",", "\n");
                    }},
                    { field: "TITLE", display: _("Report Title"), initialsort: true, formatter: function(row) {
                        return row.TITLE + (row.REVISION ? 
                            ' <span class="asm-report-revision" title="' + _("Repository revision") + '">' + 
                            format.padleft(row.REVISION, 2) + '</span>' 
                            : '');
                    }},
                    { field: "DESCRIPTION", display: _("Description") }
                ]
            };

            const buttons = [
                { id: "new", text: _("New Report"), icon: "new", enabled: "always", 
                    click: function() { 
                        tableform.dialog_error("");
                        tableform.dialog_show_add(dialog, {
                            onadd: async function() {
                                if (!reports.validation()) { tableform.dialog_enable_buttons(); return; }
                                let response = await tableform.fields_post(dialog.fields, "mode=create", "reports");
                                let row = {};
                                row.ID = response;
                                tableform.fields_update_row(dialog.fields, row);
                                reports.set_extra_fields(row);
                                controller.rows.push(row);
                                tableform.table_update(table);
                                tableform.dialog_close();
                            },
                            onload: function() {
                                $("#type").select("value", "REPORT");
                                reports.change_type();
                                $("#button-qb").show();
                            }
                        });
                    } 
                },
                { id: "clone", text: _("Clone"), icon: "copy", enabled: "one", 
                    click: function() { 
                        tableform.dialog_error("");
                        tableform.dialog_show_add(dialog, {
                            onadd: async function() {
                                if (!reports.validation()) { tableform.dialog_enable_buttons(); return; }
                                let response = await tableform.fields_post(dialog.fields, "mode=create", "reports");
                                let row = {};
                                row.ID = response;
                                tableform.fields_update_row(dialog.fields, row);
                                controller.rows.push(row);
                                tableform.table_update(table);
                                tableform.dialog_close();
                            },
                            onload: function() {
                                let row = tableform.table_selected_row(table);
                                tableform.fields_populate_from_json(dialog.fields, row);
                                $("#title").val(_("Copy of {0}").replace("{0}", $("#title").val()));
                                let type = "REPORT";
                                if (row.HTMLBODY.indexOf("GRAPH") == 0 || row.HTMLBODY.indexOf("MAIL") == 0 || row.HTMLBODY.indexOf("MAP") == 0) { type = row.HTMLBODY; }
                                $("#type").select("value", type);
                                $("#button-qb").toggle( row.SQLCOMMAND.indexOf("-- qbtype") == 0 );
                            }
                        });
                    } 
                },
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", 
                    click: async function() { 
                        await tableform.delete_dialog();
                        tableform.buttons_default_state(buttons);
                        let ids = tableform.table_ids(table);
                        await common.ajax_post("reports", "mode=delete&ids=" + ids);
                        tableform.table_remove_selected_from_json(table, controller.rows);
                        tableform.table_update(table);
                    } 
                },
                { id: "roles", text: _("Roles"), icon: "auth", enabled: "multi", tooltip: _("Apply roles to reports in bulk"),
                    click: async function() {
                        $("#dialog-bulkroleassign").dialog("open");
                    }
                },
                { id: "browse", text: _("Browse sheltermanager.com"), icon: "logo", enabled: "always", tooltip: _("Get more reports from sheltermanager.com"),
                    click: function() {
                        reports.browse_smcom();
                    }
                },
                { id: "headfoot", text: _("Edit Header/Footer"), icon: "report", enabled: "always", tooltip: _("Edit report template HTML header/footer"),
                    click: function() {
                        $("#dialog-headfoot").dialog("open");
                    }
                },
                { id: "images", text: _("Extra Images"), icon: "image", enabled: "always", tooltip: _("Add extra images for use in reports and documents"),
                    click: function() {
                        common.route("report_images");
                    }
                }
            ];
            this.dialog = dialog;
            this.table = table;
            this.buttons = buttons;
        },

        render_headfoot: function() {
            return [
                '<div id="dialog-headfoot" style="display: none" title="' + html.title(_("Edit Header/Footer")) + '">',
                html.info(_("These are the HTML headers and footers used when generating reports.")),
                '<table width="100%">',
                '<tr>',
                '<td valign="top">',
                '<label for="rhead">' + _("Header") + '</label><br />',
                '<textarea id="rhead" data="header" class="asm-htmleditor headfoot" data-height="250px" data-width="750px">',
                controller.header,
                '</textarea>',
                '<label for="rfoot">' + _("Footer") + '</label><br />',
                '<textarea id="rfoot" data="footer" class="asm-htmleditor headfoot" data-height="250px" data-width="750px">',
                controller.footer,
                '</textarea>',
                '</td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_bulkroleassign: function() {
            return [
                '<div id="dialog-bulkroleassign" style="display: none" title="' + html.title(_("Bulk assign roles")) + '">',
                tableform.fields_render([
                    { post_field: "viewbulkroles", type: "selectmulti", label: _("Roles"), options: { displayfield: "ROLENAME", rows: controller.roles } }
                ]),
                '</div>'
            ].join("\n");
        },

        render_browse_smcom: function() {
            return [
                '<div id="dialog-browse" style="display: none" title="' + html.title(_("Available sheltermanager.com reports")) + '">',
                '<div class="asm-toolbar">',
                '<button id="button-install" title="' + _('Install the selected reports to your database') + '">' + _("Install") + '</button>',
                '<button id="button-checkall">' + _("Select all") + '</button>',
                '<button id="button-checkrecommended">' + _("Select recommended") + '</button>',
                '</div>',
                '<table id="table-smcom">',
                '<thead>',
                '<tr>',
                '<th class="asm-table-sticky-header">' + _("Type") + '</th>',
                '<th class="asm-table-sticky-header">' + _("Title") + '</th>',
                '<th class="asm-table-sticky-header">' + _("Category") + '</th>',
                '<th class="asm-table-sticky-header">' + _("Locale") + '</th>',
                '<th class="asm-table-sticky-header">' + _("Description") + '</th>',
                '</tr>',
                '</thead>',
                '<tbody></tbody>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render: function() {
            let s = "";
            reports.qb = common.modules.reports_querybuilder; // by assigning here, we make sure all the modules are loaded
            this.model();
            s += this.render_headfoot();
            s += this.render_bulkroleassign();
            s += reports.qb.render();
            s += this.render_browse_smcom();
            s += tableform.dialog_render(this.dialog);
            s += html.content_header(_("Reports"));
            s += tableform.buttons_render(this.buttons);
            s += tableform.table_render(this.table);
            s += html.content_footer();
            return s;
        },

        bind: function() {
            tableform.dialog_bind(this.dialog);
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);
            reports.bind_headfoot();
            reports.bind_bulkroleassign();
            reports.qb.bind();
            reports.bind_browse_smcom();
            reports.bind_dialogbuttons();
            $("#category").autocomplete({ source: html.decode(controller.categories).split("|") });
            // Fix for JQuery UI 10.3, autocomplete has to be created after the dialog is
            // shown or the stacking order is wrong. This fixes it now.
            $("#category").autocomplete("widget").css("z-index", 1000);
            $("#type").change(reports.change_type);
        },

        sync: function() {
            if (common.current_url().indexOf("browse=true") != -1) {
                reports.browse_smcom();
            }
        },

        bind_bulkroleassign: function() {
            let bulkroleassignbuttons = {};
            bulkroleassignbuttons[_("Apply")] = {
                text: _("Apply"),
                "class": 'asm-dialog-actionbutton',
                click: async function() {
                    //tableform.buttons_default_state(buttons);
                    let reportids = encodeURIComponent(tableform.table_ids(reports.table));
                    let roleids = $("#viewbulkroles").toPOST();
                    await common.ajax_post("reports", "mode=bulkupdateviewroles&reportids=" + reportids + "&" + roleids);
                    common.route_reload();
                }
            };
            bulkroleassignbuttons[_("Cancel")] = function() { $(this).dialog("close"); };
            $("#dialog-bulkroleassign").dialog({
                autoOpen: false,
                resizable: true,
                height: "auto",
                width: 400,
                modal: true,
                dialogClass: "dialogshadow",
                show: dlgfx.add_show,
                hide: dlgfx.add_hide,
                buttons: bulkroleassignbuttons
            });
        },

        bind_headfoot: function() {
            let headfootbuttons = {};
            headfootbuttons[_("Revert")] = {
                text: _("Revert to default"),
                "class": 'asm-redbutton',
                click: async function() {
                    let formdata = "mode=headfoot&header=&footer=";
                    try {
                        await common.ajax_post("reports", formdata);                    
                        header.show_info(_("Updated."));
                        common.route_reload(); 
                    }
                    finally {
                        $("#dialog-headfoot").dialog("close");
                    }
                }
            };
            headfootbuttons[_("Save")] = {
                text: _("Save"),
                "class": 'asm-dialog-actionbutton',
                click: async function() {
                    let formdata = "mode=headfoot&" + $(".headfoot").toPOST();
                    try {
                        await common.ajax_post("reports", formdata);                    
                        header.show_info(_("Updated."));
                    }
                    finally {
                        $("#dialog-headfoot").dialog("close");
                    }
                }
            };
            headfootbuttons[_("Cancel")] = function() { $(this).dialog("close"); };
            $("#dialog-headfoot").dialog({
                autoOpen: false,
                resizable: true,
                height: "auto",
                width: 800,
                modal: true,
                dialogClass: "dialogshadow",
                show: dlgfx.add_show,
                hide: dlgfx.add_hide,
                buttons: headfootbuttons,
                open: function() {
                    $("#rhead, #rfoot").htmleditor("refresh");
                }
            });
        },

        bind_browse_smcom: function() {
            $("#table-smcom").table({ sticky_header: false, reflow: false, filter: true, sortList: [[1, 0]] });
            $("#dialog-browse").dialog({
                autoOpen: false,
                resizable: true,
                height: 600,
                width: 900,
                modal: true,
                dialogClass: "dialogshadow",
                show: dlgfx.add_show,
                hide: dlgfx.add_hide
            });
            /* Removed as it is not helpful now there are 700+ reports #1332
            $("#button-checkall")
                .button({ icons: { primary: "ui-icon-check" }})
                .click(function() {
                    $("#table-smcom input:visible").prop("checked", true);
                    $("#table-smcom td").addClass("ui-state-highlight");
                    $("#button-install").button("enable");
                });
            */
            $("#button-checkall").hide();

            $("#button-checkrecommended")
                .button({ icons: { primary: "ui-icon-check" }})
                .click(function() {
                    $("#table-smcom .smcom-title").each(function() {
                        let td = $(this);
                        $.each(controller.recommended, function(i, v) {
                            if (td.text() == v && !td.parent().find("input").prop("disabled")) {
                                td.parent().find("input").prop("checked", true);
                                td.parent().find("td").addClass("ui-state-highlight");
                                $("#button-install").button("enable");
                            }
                        });
                    });
                });
            $("#button-install")
                .button({ icons: { primary: "ui-icon-disk" }})
                .click(async function() {
                header.show_loading();
                let formdata = "mode=smcominstall&ids=";
                $("#table-smcom input").each(function() {
                    if ($(this).attr("type") == "checkbox") {
                        if ($(this).is(":checked")) {
                            formdata += $(this).attr("data") + ",";
                        }
                    }
                });
                try {
                    await common.ajax_post("reports", formdata);
                    common.route_reload(true);
                }
                finally {
                    header.hide_loading(); 
                }
            });
        },

        bind_dialogbuttons: function() {
            
            $("#button-checksql")
                .button({ icons: { primary: "ui-icon-check" }, text: false })
                .click(function() {
                let formdata = "mode=sql&sql=" + encodeURIComponent($("#sql").sqleditor("value"));
                $("#asm-report-error").fadeOut();
                header.show_loading();
                common.ajax_post("reports", formdata)
                    .then(function() { 
                        tableform.dialog_info(_("SQL is syntactically correct."));
                    })
                    .fail(function(err) {
                        tableform.dialog_error(err);
                    })
                    .always(function() {
                        header.hide_loading();
                    });
            });

            $("#button-genhtml")
                .button({ icons: { primary: "ui-icon-wrench" }, text: false })
                .click(function() {
                let formdata = "mode=genhtml&sql=" + encodeURIComponent($("#sql").sqleditor("value"));
                $("#asm-report-error").fadeOut();
                header.show_loading();
                common.ajax_post("reports", formdata)
                    .then(function(result) { 
                        $("#html").htmleditor("value", result);
                    })
                    .fail(function(err) {
                        tableform.dialog_error(err);
                    })
                    .always(function() {
                        header.hide_loading(); 
                    });
            });

            $("#button-qb")
                .button({ icons: {primary: "ui-icon-lightbulb" }, text: false })
                .click(reports.qb.qb_click); 
        },

        change_type: function() {
            let type = $("#type").val();
            if (type != "REPORT") {
                $("#htmlrow").hide();
                $("#dailyemailrow").hide();
                $("#dailyemailfrequencyrow").hide();
                $("#dailyemailhourrow").hide();
                $("#omitheaderfooterrow").hide();
                $("#omitcriteriarow").hide();
                $("#button-genhtml").hide();
                $("#dialog-add").dialog("option", "height", "auto");
            }
            else {
                $("#htmlrow").show();
                $("#dailyemailrow").show();
                $("#dailyemailfrequencyrow").show();
                $("#dailyemailhourrow").show();
                $("#omitheaderfooterrow").show();
                $("#omitcriteriarow").show();
                $("#button-genhtml").show();
                $("#dialog-add").dialog("option", "height", "auto");
            }
        },

        browse_smcom: async function() {
            header.show_loading();
            try {
                let formdata = "mode=smcomlist";
                let result = await common.ajax_post("reports", formdata);
                let h = [];
                $.each(jQuery.parseJSON(result), function(i, r) {
                    let extraclasses = "";
                    if (r.INSTALLED) { extraclasses = "asm-completerow"; }
                    h.push('<tr class="' + extraclasses + '"><td>');
                    h.push('<span style="white-space: nowrap">');
                    h.push('<input type="checkbox" class="asm-checkbox" data="' + r.ID + '" id="r' + r.ID + '" title="' + _("Select") + '" '); 
                    if (r.INSTALLED) h.push('disabled="disabled" ');
                    h.push('/> '); 
                    h.push('<label for="r' + r.ID + '">' + r.TYPE + '</label></span>');
                    h.push('<td class="smcom-title">' + r.TITLE + '</td>');
                    h.push('<td class="smcom-category">' + r.CATEGORY + '</td>');
                    h.push('<td class="smcom-locale">' + r.LOCALE + '</td>');
                    h.push('<td class="smcom-description">' + r.DESCRIPTION + '</td>');
                    h.push('</tr>');
                });
                $("#table-smcom > tbody").html(h.join("\n"));
                $("#table-smcom").trigger("update");
                $("#button-install").button("disable");
                $("#table-smcom input").click(function() {
                    if ($("#table-smcom input:checked").length > 0) {
                        $("#button-install").button("enable");
                    }
                    else {
                        $("#button-install").button("disable");
                    }
                });
                $("#dialog-browse").dialog("open");
            }
            finally {
                header.hide_loading();
            }
        },

        set_extra_fields: function(row) {
            // Build list of VIEWROLES from VIEWROLEIDS
            let roles = [];
            let roleids = row.VIEWROLEIDS;
            if ($.isArray(roleids)) { roleids = roleids.join(","); }
            $.each(roleids.split(/[|,]+/), function(i, v) {
                roles.push(common.get_field(controller.roles, v, "ROLENAME"));
            });
            row.VIEWROLES = roles.join("|");
        },

        validation: function() {
            $("#sql").sqleditor("change");
            $("#html").htmleditor("change");
            let rv = validate.notblank([ "category", "title", "sql" ]);
            if (!rv) { return false; }
            if ($("#type").val() == "REPORT" && $("#html").val() == "") { 
                validate.notblank([ "html" ]); return false; 
            }
            if ($("#type").val() != "REPORT") { 
                $("#html").val($("#type").val()); 
            }
            if ($("#dailyemail").val() && ($("#sql").sqleditor("value").indexOf("$VAR") != -1 || $("#sql").sqleditor("value").indexOf("$ASK") != -1)) {
                tableform.dialog_error(_("This report cannot be sent by email as it requires criteria to run."));
                return false;
            }
            return true;
        },

        destroy: function() {
            common.widget_destroy("#dialog-headfoot");
            common.widget_destroy("#dialog-bulkroleassign");
            common.widget_destroy("#dialog-browse");
            common.widget_destroy("#dialog-qb");
            tableform.dialog_destroy();
        },

        name: "reports",
        animation: "options",
        title: function() { return _("Edit Reports"); },
        routes: {
            "reports": function() { common.module_loadandstart("reports", "reports"); }
        }

    };
    
    common.module_register(reports);

});
