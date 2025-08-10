/*global $, jQuery, FileReader, Modernizr, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const maint_undelete = {

        model: function() {
            const table = {
                rows: controller.rows,
                idcolumn: "KEY",
                edit: async function(row) {
                    header.show_loading(_("Loading..."));
                    try {
                        let result = await common.ajax_post("maint_undelete", "mode=view&key=" + row.KEY);
                        $("#dialog-viewer-content").text(result); 
                        $("#dialog-viewer").dialog("open");
                    }
                    finally {
                        header.hide_loading();
                    }
                },

                columns: [
                    { field: "KEY", display: _("ID") },
                    { field: "DATE", display: _("Date"), initialsort: true, initialsortdirection: "desc", formatter: tableform.format_datetime },
                    { field: "DELETEDBY", display: _("By") }
                ]
            };

            const buttons = [
                { id: "restore", text: _("Restore"), icon: "new", enabled: "multi", perm: "", 
                    click: async function() { 
                        let response = await common.ajax_post("maint_undelete", "mode=undelete&ids=" + tableform.table_ids(table));
                        let [success,errors] = response.split(",");
                        header.show_info(success + " sucessfully restored, " + errors + " errors.");
                     } 
                },
                { id: "offset", type: "dropdownfilter",
                     options: [ "9999|(all time)", "7|Last week", "14|Last fortnight", "21|Last 3 weeks", "31|Last month",
                        "62|Last 2 months", "93|Last 3 months" ],
                     click: function(selval) {
                        common.route("maint_undelete?offset=" + selval);
                     }
                },
                { id: "bulk", type: "dropdownfilter", 
                    options: [ "(select)", "animal", "animalcontrol", "animallost", "animalfound", "customreport", 
                        "dbfs", "onlineformincoming", "owner", "templatedocument", "templatehtml", "waitinglist" ],
                    click: function(selval) {
                        $("#tableform input[type='checkbox']").each(function() {
                            if (String($(this).attr("data-id")).indexOf(selval) == 0) { 
                                $(this).prop("checked", true); 
                                $(this).closest("tr").find("td").addClass("ui-state-highlight");
                            }
                        });
                        tableform.table_update_buttons(table, buttons);
                    }
                }
            ];

            this.buttons = buttons;
            this.table = table;
        },

        render_viewer: function() {
            return [
                '<div id="dialog-viewer" style="display: none" title="' + html.title(_("View")) + '">',
                '<div id="dialog-viewer-content">',
                '</div>',
                '</div>'
            ].join("\n");
        },

        bind_viewer: function() {
            let viewbuttons = {};
            viewbuttons[_("Close")] = function() { $(this).dialog("close"); };
            $("#dialog-viewer").dialog({
                autoOpen: false,
                resizable: true,
                height: "auto",
                width: 1024,
                modal: true,
                dialogClass: "dialogshadow",
                show: dlgfx.add_show,
                hide: dlgfx.add_hide,
                buttons: viewbuttons
            });
        },

        render: function() {
            let s = "";
            this.model();
            s += html.content_header(_("Undelete"));
            s += this.render_viewer();
            s += tableform.buttons_render(this.buttons);
            s += tableform.table_render(this.table);
            s += html.content_footer();
            return s;
        },

        bind: function() {
            this.bind_viewer();
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);
        },

        sync: function() {
            // If an offset is given in the querystring, update the select
            if (common.querystring_param("offset")) {
                $("#offset").select("value", common.querystring_param("offset"));
            }
        },

        destroy: function() {
        },

        name: "maint_undelete",
        animation: "options",
        title: function() { return _("Undelete"); },
        routes: {
            "maint_undelete": function() { common.module_loadandstart("maint_undelete", "maint_undelete?" + this.rawqs); }
        }

    };

    common.module_register(maint_undelete);

});
