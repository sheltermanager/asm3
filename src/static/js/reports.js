/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    var recommended = [
        "Active Donors", "Active Fosters", "Active Members", "Adoptions by Date with Addresses",
        "Animal Entry Reasons", "Animal Return Reasons", "Animals Inducted by Date and Species",
        "Animals Without Photo Media", "Annual Figures (by species)", "Annual Figures (by type)",
        "Asilomar Figures", "Audit Trail: All Changes by Date", "Audit Trail: All Changes by Specific user",
        "Audit Trail: Deletions by Date", "Average Time On Shelter By Species", "Banned Owners",
        "Brought In Figures", "Cage Card", "Deceased Reasons by Species and Date",
        "Detailed Shelter Inventory", "In/Out", "In/Out by Species", "In/Out with Donations",
        "Long Term Animals", "Medical Diary", "Monthly Adoptions By Species", 
        "Monthly Figures (by species)", "Monthly Figures (by type)", "Most Common Name",
        "Non-Microchipped Animals", "Non-Neutered/Spayed Animals Aged Over 6 Months",
        "Print Animal Record", "Reserves without Homechecks", "Returned Animals",
        "Shelter Inventory", "Shelter Inventory with Pictures by Location",
        "Vaccination Diary (Off Shelter)", "Vaccination Diary (On Shelter)"
    ];

    var emailhours = [
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

    var reports = {

        model: function() {
            var dialog = {
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
                        '<option value="MAP">' + _("Map") + '</option>' ].join("\n") },
                    { json_field: "CATEGORY", post_field: "category", classes: "asm-doubletextbox", label: _("Category"), type: "text", validation: "notblank" },
                    { json_field: "TITLE", post_field: "title", classes: "asm-doubletextbox", label: _("Report Title"), type: "text", validation: "notblank" },
                    { json_field: "DESCRIPTION", post_field: "description", classes: "asm-doubletextbox", label: _("Description"), type: "text" },
                    { json_field: "DAILYEMAIL", post_field: "dailyemail", classes: "asm-doubletextbox", label: _("Daily Email To"), type: "text",
                        tooltip: _("An optional comma separated list of email addresses to send the output of this report to each day")},
                    { json_field: "DAILYEMAILHOUR", post_field: "dailyemailhour", label: _("Time"), type: "select",
                        options: { displayfield: "display", valuefield: "value", rows: emailhours }},
                    { json_field: "OMITHEADERFOOTER", post_field: "omitheaderfooter", label: _("Omit header/footer"), type: "check" },
                    { json_field: "OMITCRITERIA", post_field: "omitcriteria", label: _("Omit criteria"), type: "check" },
                    { json_field: "VIEWROLEIDS", post_field: "viewroles", label: _("View Roles"), type: "selectmulti", 
                        options: { rows: controller.roles, valuefield: "ID", displayfield: "ROLENAME" }},
                    { type: "raw", label: "", markup: '<button id="button-checksql">' + _("Syntax check this SQL") + '</button>' +
                        '<button id="button-genhtml">' + _("Generate HTML from this SQL") + '</button>' },
                    { json_field: "SQLCOMMAND", post_field: "sql", label: _("SQL"), rows: 10, type: "textarea", validation: "notblank" },
                    { json_field: "HTMLBODY", post_field: "html", label: _("HTML"), rows: 10, type: "textarea" }
                ]
            };

            var table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: function(row) {
                    tableform.dialog_error("");
                    tableform.dialog_show_edit(dialog, row, function() {
                        if (!reports.validation()) { tableform.dialog_enable_buttons(); return; }
                        tableform.fields_update_row(dialog.fields, row);
                        tableform.fields_post(dialog.fields, "mode=update&reportid=" + row.ID, "reports", function(response) {
                            tableform.table_update(table);
                            tableform.dialog_close();
                        });
                    }, function(row) {
                        var type = "REPORT";
                        if (row.HTMLBODY.indexOf("GRAPH") == 0 || row.HTMLBODY.indexOf("MAIL") == 0 || row.HTMLBODY.indexOf("MAP") == 0) { type = row.HTMLBODY; }
                        $("#type").select("value", type);
                        reports.change_type();
                    });
                },
                columns: [
                    { field: "CATEGORY", display: _("Type"), formatter: function(row) {
                        var t = "<span style=\"white-space: nowrap\">" +
                            "<input type=\"checkbox\" data-id=\"" + row.ID + "\" title=\"" + html.title(_("Select")) + "\" />" +
                            "<a href=\"#\" class=\"link-edit\" data-id=\"" + row.ID + "\">{val}</a></span>";
                        if (row.HTMLBODY.indexOf("GRAPH") == 0) {
                            return t.replace("{val}", _("Chart"));
                        }
                        if (row.HTMLBODY.indexOf("MAIL") == 0) {
                            return t.replace("{val}", _("Mail Merge"));
                        }
                        if (row.HTMLBODY.indexOf("MAP") == 0) {
                            return t.replace("{val}", _("Map"));
                        }
                        return t.replace("{val}", _("Report"));
                    }},
                    { field: "CATEGORY", display: _("Category") },
                    { field: "VIEWROLES", display: _("Roles"), formatter: function(row) {
                        return row.VIEWROLES ? row.VIEWROLES.replace("|", ", ") : "";
                    }},
                    { field: "TITLE", display: _("Report Title"), initialsort: true },
                    { field: "DESCRIPTION", display: _("Description") }
                ]
            };

            var buttons = [
                 { id: "new", text: _("New Report"), icon: "new", enabled: "always", 
                     click: function() { 
                        tableform.dialog_error("");
                         tableform.dialog_show_add(dialog, function() {
                             if (!reports.validation()) { tableform.dialog_enable_buttons(); return; }
                             tableform.fields_post(dialog.fields, "mode=create", "reports", function(response) {
                                 var row = {};
                                 row.ID = response;
                                 row.VIEWROLES = "";
                                 tableform.fields_update_row(dialog.fields, row);
                                 controller.rows.push(row);
                                 tableform.table_update(table);
                                 tableform.dialog_close();
                             });
                         }, function() {
                            $("#type").select("value", "REPORT");
                            reports.change_type();
                         });
                     } 
                 },
                 { id: "clone", text: _("Clone"), icon: "copy", enabled: "one", 
                     click: function() { 
                         tableform.dialog_error("");
                         tableform.dialog_show_add(dialog, function() {
                             if (!reports.validation()) { tableform.dialog_enable_buttons(); return; }
                             tableform.fields_post(dialog.fields, "mode=create", "reports", function(response) {
                                 var row = {};
                                 row.ID = response;
                                 tableform.fields_update_row(dialog.fields, row);
                                 controller.rows.push(row);
                                 tableform.table_update(table);
                                 tableform.dialog_close();
                             });
                         }, function() {
                             var row = tableform.table_selected_row(table);
                             tableform.fields_populate_from_json(dialog.fields, row);
                             $("#title").val(_("Copy of {0}").replace("{0}", $("#title").val()));
                             var type = "REPORT";
                             if (row.HTMLBODY.indexOf("GRAPH") == 0 || row.HTMLBODY.indexOf("MAIL") == 0 || row.HTMLBODY.indexOf("MAP") == 0) { type = row.HTMLBODY; }
                             $("#type").select("value", type);
                         });
                     } 
                 },
                 { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", 
                     click: function() { 
                         tableform.delete_dialog(function() {
                             tableform.buttons_default_state(buttons);
                             var ids = tableform.table_ids(table);
                             common.ajax_post("reports", "mode=delete&ids=" + ids , function() {
                                 tableform.table_remove_selected_from_json(table, controller.rows);
                                 tableform.table_update(table);
                             });
                         });
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
                '<div class="ui-state-highlight ui-corner-all">',
                    '<p>',
                        '<span class="ui-icon ui-icon-info" style="float: left; margin-right: .3em;"></span>',
                        _("These are the HTML headers and footers used when generating reports."),
                    '</p>',
                '</div>',
                '<table width="100%">',
                '<tr>',
                '<td valign="top">',
                '<label for="rhead">' + _("Header") + '</label><br />',
                '<textarea id="rhead" data="header" class="asm-textarea headfoot" style="font-family: monospace" rows="10">',
                controller.header,
                '</textarea>',
                '<label for="rfoot">' + _("Footer") + '</label><br />',
                '<textarea id="rfoot" data="footer" class="asm-textarea headfoot" style="font-family: monospace" rows="10">',
                controller.footer,
                '</textarea>',
                '</td>',
                '</tr>',
                '</table>',
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
                '</table>',
                '</div>'
            ].join("\n");
        },

        render: function() {
            var s = "";
            this.model();
            s += this.render_headfoot();
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

        bind_headfoot: function() {
            var headfootbuttons = {};
            headfootbuttons[_("Save")] = function() {
                var formdata = "mode=headfoot&" + $(".headfoot").toPOST();
                common.ajax_post("reports", formdata, function() { 
                    header.show_info(_("Updated."));
                    $("#dialog-headfoot").dialog("close");
                });
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
                buttons: headfootbuttons
            });
        },

        bind_browse_smcom: function() {
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
            $("#button-checkall")
                .button({ icons: { primary: "ui-icon-check" }})
                .click(function() {
                    $("#table-smcom input").attr("checked", true);
                    $("#table-smcom td").addClass("ui-state-highlight");
                    $("#button-install").button("enable");
                });

            $("#button-checkrecommended")
                .button({ icons: { primary: "ui-icon-check" }})
                .click(function() {
                    $("#table-smcom .smcom-title").each(function() {
                        var td = $(this);
                        $.each(recommended, function(i, v) {
                            if (td.text() == v) {
                                td.parent().find("input").attr("checked", true);
                                td.parent().find("td").addClass("ui-state-highlight");
                                $("#button-install").button("enable");
                            }
                        });
                    });
                });
            $("#button-install")
                .button({ icons: { primary: "ui-icon-disk" }})
                .click(function() {
                header.show_loading();
                var formdata = "mode=smcominstall&ids=";
                $("#table-smcom input").each(function() {
                    if ($(this).attr("type") == "checkbox") {
                        if ($(this).is(":checked")) {
                            formdata += $(this).attr("data") + ",";
                        }
                    }
                });
                common.ajax_post("reports", formdata, function() { 
                    header.hide_loading();
                    common.route_reload(true);
                }, function() { header.hide_loading(); });
            });
        },

        bind_dialogbuttons: function() {
            
            $("#button-checksql")
                .button({ icons: { primary: "ui-icon-check" }, text: false })
                .click(function() {
                var formdata = "mode=sql&sql=" + encodeURIComponent($("#sql").val());
                $("#asm-report-error").fadeOut();
                header.show_loading();
                common.ajax_post("reports", formdata, function() { 
                    tableform.dialog_info(_("SQL is syntactically correct."));
                    header.hide_loading();
                }, function() { header.hide_loading(); });
            });

            $("#button-genhtml")
                .button({ icons: { primary: "ui-icon-wrench" }, text: false })
                .click(function() {
                var formdata = "mode=genhtml&sql=" + encodeURIComponent($("#sql").val());
                $("#asm-report-error").fadeOut();
                header.show_loading();
                common.ajax_post("reports", formdata, function(result) { 
                    $("#html").val(result);
                    header.hide_loading();
                }, function(response) { 
                    header.hide_loading(); 
                    tableform.dialog_error(response);
                });
            });
        },

        change_type: function() {
            var type = $("#type").val();
            if (type != "REPORT") {
                $("#html").closest("tr").hide();
                $("#dailyemail").closest("tr").hide();
                $("#dailyemailhour").closest("tr").hide();
                $("#button-genhtml").hide();
                $("#dialog-add").dialog("option", "height", "auto");
            }
            else {
                $("#html").closest("tr").show();
                $("#dailyemail").closest("tr").show();
                $("#dailyemailhour").closest("tr").show();
                $("#button-genhtml").show();
                $("#dialog-add").dialog("option", "height", "auto");
            }
        },

        browse_smcom: function() {
            header.show_loading();
            var formdata = "mode=smcomlist";
            common.ajax_post("reports", formdata, function(result) { 
                $("#table-smcom").html(result);
                $("#table-smcom").table({ sticky_header: false, filter: true, sortList: [[1, 0]] });
                $("#button-install").button("disable");
                $("#table-smcom input").click(function() {
                    if ($("#table-smcom input:checked").length > 0) {
                        $("#button-install").button("enable");
                    }
                    else {
                        $("#button-install").button("disable");
                    }
                });
                header.hide_loading();
                $("#dialog-browse").dialog("open");
            });
        },

        validation: function() {
            var rv = validate.notblank([ "category", "title", "sql" ]);
            if (!rv) { return false; }
            if ($("#type").val() == "REPORT" && $("#html").val() == "") { 
                validate.notblank([ "html" ]); return false; 
            }
            if ($("#type").val() != "REPORT") { 
                $("#html").val($("#type").val()); 
            }
            return true;
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
