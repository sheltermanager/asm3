/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const licence = {

        model: function() {
            const dialog = {
                add_title: _("Add license"),
                edit_title: _("Edit license"),
                edit_perm: 'capl',
                close_on_ok: false,
                columns: 1,
                width: 550,
                fields: [
                    { json_field: "OWNERID", post_field: "person", label: _("Person"), type: "person", validation: "notzero" },
                    { json_field: "ANIMALID", post_field: "animal", label: _("Animal (optional)"), type: "animal" },
                    { json_field: "LICENCETYPEID", post_field: "type", label: _("Type"), type: "select", options: { displayfield: "LICENCETYPENAME", valuefield: "ID", rows: controller.licencetypes }},
                    { json_field: "LICENCENUMBER", post_field: "number", label: _("License Number"), type: "text", validation: "notblank" },
                    { json_field: "LICENCEFEE", post_field: "fee", label: _("Fee"), type: "currency" },
                    { json_field: "ISSUEDATE", post_field: "issuedate", label: _("Issued"), type: "date", validation: "notblank", defaultval: new Date() },
                    { json_field: "EXPIRYDATE", post_field: "expirydate", label: _("Expires"), type: "date", validation: "notblank" },
                    { json_field: "COMMENTS", post_field: "comments", label: _("Comments"), type: "textarea" }
                ]
            };

            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: async function(row) {
                    await tableform.dialog_show_edit(dialog, row);
                    tableform.fields_update_row(dialog.fields, row);
                    row.LICENCETYPENAME = common.get_field(controller.licencetypes, row.LICENCETYPEID, "LICENCETYPENAME");
                    row.OWNERNAME = $("#person").personchooser("get_selected").OWNERNAME;
                    if (row.ANIMALID && row.ANIMALID != "0") {
                        row.ANIMALNAME = $("#animal").animalchooser("get_selected").ANIMALNAME;
                        row.SHELTERCODE = $("#animal").animalchooser("get_selected").SHELTERCODE;
                    }
                    else {
                        row.ANIMALID = 0;
                        row.ANIMALNAME = "";
                        row.SHELTERCODE = "";
                    }
                    try {
                        await tableform.fields_post(dialog.fields, "mode=update&licenceid=" + row.ID, "licence");
                        tableform.table_update(table);
                        tableform.dialog_close();
                    }
                    finally {
                        tableform.dialog_enable_buttons();
                    }
                },
                complete: function(row) {
                },
                overdue: function(row) {
                    return row.EXPIRYDATE && format.date_js(row.EXPIRYDATE) < common.today_no_time();
                },
                columns: [
                    { field: "LICENCETYPENAME", display: _("Type") },
                    { field: "PERSON", display: _("Person"),
                        formatter: function(row) {
                            if (row.OWNERID) {
                                return html.person_link(row.OWNERID, row.OWNERNAME);
                            }
                            return "";
                        },
                        hideif: function(row) {
                            return controller.name.indexOf("person_") != -1;
                        }
                    },
                    { field: "IMAGE", display: "", 
                        formatter: function(row) {
                            if (!row.ANIMALID) { return ""; }
                            return html.animal_link_thumb_bare(row);
                        },
                        hideif: function(row) {
                            // Don't show this column if we're in the animal's record or the option is turned off
                            if (controller.name == "animal_licence" || !config.bool("PicturesInBooks")) {
                                return true;
                            }
                        }
                    },
                    { field: "ANIMAL", display: _("Animal"), 
                        formatter: function(row) {
                            if (!row.ANIMALNAME) { return ""; }
                            return html.animal_link(row);
                        },
                        hideif: function(row) {
                            return controller.name == "animal_licence";
                        }
                    },
                    { field: "LICENCENUMBER", display: _("License Number") },
                    { field: "LICENCEFEE", display: _("Fee"), formatter: tableform.format_currency },
                    { field: "ISSUEDATE", display: _("Issued"), formatter: tableform.format_date, initialsort: true, intialsortdirection: "desc" },
                    { field: "EXPIRYDATE", display: _("Expires"), formatter: tableform.format_date },
                    { field: "COMMENTS", display: _("Comments"), formatter: tableform.format_comments }
                ]
            };

            const buttons = [
                { id: "new", text: _("New License"), icon: "licence", enabled: "always", perm: "aapl",
                    click: function() { 
                        $("#person").personchooser("clear");
                        $("#animal").animalchooser("clear");
                        if (controller.person) {
                            $("#person").personchooser("loadbyid", controller.person.ID);
                        }
                        if (controller.animal) {
                           $("#animal").animalchooser("loadbyid", controller.animal.ID);
                        }
                        tableform.dialog_show_add(dialog, {
                            onadd: async function() {
                                try {
                                    let response = await tableform.fields_post(dialog.fields, "mode=create", "licence");
                                    let row = {};
                                    row.ID = response;
                                    tableform.fields_update_row(dialog.fields, row);
                                    row.LICENCETYPENAME = common.get_field(controller.licencetypes, row.LICENCETYPEID, "LICENCETYPENAME");
                                    row.OWNERNAME = $("#person").personchooser("get_selected").OWNERNAME;
                                    if (row.ANIMALID && row.ANIMALID != "0") {
                                        row.ANIMALNAME = $("#animal").animalchooser("get_selected").ANIMALNAME;
                                        row.SHELTERCODE = $("#animal").animalchooser("get_selected").SHELTERCODE;
                                    }
                                    else {
                                        row.ANIMALID = 0;
                                        row.ANIMALNAME = "";
                                        row.SHELTERCODE = "";
                                    }
                                    controller.rows.push(row);
                                    tableform.table_update(table);
                                    tableform.dialog_close();
                                }
                                finally {
                                    tableform.dialog_enable_buttons();
                                }
                             },
                             onload: licence.type_change
                         });
                     }
                 },
                 { id: "renew", text: _("Renew License"), icon: "licence", enabled: "one", perm: "aapl",
                    click: function() { 
                        tableform.dialog_show_add(dialog, {
                            onadd: async function() {
                                try {
                                    let response = await tableform.fields_post(dialog.fields, "mode=create", "licence");
                                    let row = {};
                                    row.ID = response;
                                    tableform.fields_update_row(dialog.fields, row);
                                    row.LICENCETYPENAME = common.get_field(controller.licencetypes, row.LICENCETYPEID, "LICENCETYPENAME");
                                    row.OWNERNAME = $("#person").personchooser("get_selected").OWNERNAME;
                                    if (row.ANIMALID && row.ANIMALID != "0") {
                                        row.ANIMALNAME = $("#animal").animalchooser("get_selected").ANIMALNAME;
                                        row.SHELTERCODE = $("#animal").animalchooser("get_selected").SHELTERCODE;
                                    }
                                    else {
                                        row.ANIMALID = 0;
                                        row.ANIMALNAME = "";
                                        row.SHELTERCODE = "";
                                    }
                                    controller.rows.push(row);
                                    tableform.table_update(table);
                                    tableform.dialog_close();
                                }
                                finally {
                                    tableform.dialog_enable_buttons();
                                }
                            },
                            onload: function() {
                                let row = tableform.table_selected_row(table);
                                tableform.fields_populate_from_json(dialog.fields, row);
                                licence.type_change();
                            }
                        });
                    }
                },
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "dapl",
                    click: async function() { 
                        await tableform.delete_dialog();
                        tableform.buttons_default_state(buttons);
                        let ids = tableform.table_ids(table);
                        await common.ajax_post("licence", "mode=delete&ids=" + ids);
                        tableform.table_remove_selected_from_json(table, controller.rows);
                        tableform.table_update(table);
                    }
                },
                { id: "document", text: _("Document"), icon: "document", enabled: "one", perm: "gaf", 
                    tooltip: _("Generate document from this license"), type: "buttonmenu" },
                { id: "offset", type: "dropdownfilter", 
                    options: [ "i7|" + _("Issued in the last week"), 
                        "i31|" + _("Issued in the last month"), 
                        "e7|" + _("Expired in the last week"),
                        "e31|" + _("Expired in the last month") ],
                    click: function(selval) {
                        common.route(controller.name + "?offset=" + selval);
                    },
                    hideif: function(row) {
                         // Don't show for animal or person records
                        if (controller.animal || controller.person) {
                            return true;
                        }
                    }
                }
            ];
            this.dialog = dialog;
            this.table = table;
            this.buttons = buttons;
        },

        render: function() {
            let s = "";
            this.model();
            s += tableform.dialog_render(this.dialog);
            s += '<div id="button-document-body" class="asm-menu-body">' +
                '<ul class="asm-menu-list">' +
                edit_header.template_list(controller.templates, "LICENCE", 0) +
                '</ul></div>';
            if (controller.name.indexOf("person_") == 0) {
                s += edit_header.person_edit_header(controller.person, "licence", controller.tabcounts);
            }
            else if (controller.name.indexOf("animal_") == 0) {
                s += edit_header.animal_edit_header(controller.animal, "licence", controller.tabcounts);
            }
            else {
                s += html.content_header(this.title());
            }
            s += tableform.buttons_render(this.buttons);
            s += tableform.table_render(this.table);
            s += html.content_footer();
            return s;
        },

        bind: function() {
            $(".asm-tabbar").asmtabs();
            $("#type").change(licence.type_change);

            // Add click handlers to templates
            $(".templatelink").click(function() {
                // Update the href as it is clicked so default browser behaviour
                // continues on to open the link in a new window
                let template_name = $(this).attr("data");
                $(this).prop("href", "document_gen?linktype=LICENCE&id=" + tableform.table_selected_row(licence.table).ID + "&dtid=" + template_name);
            });

            tableform.dialog_bind(this.dialog);
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);
        },

        sync: function() {
            // If an offset is given in the querystring, update the select
            if (common.current_url().indexOf("offset=") != -1) {
                let offurl = common.current_url().substring(common.current_url().indexOf("=")+1);
                $("#offset").select("value", offurl);
            }
        },

        type_change: function() {
            let dc = common.get_field(controller.licencetypes, $("#type").select("value"), "DEFAULTCOST");
            $("#fee").currency("value", dc);
        },

        destroy: function() {
            common.widget_destroy("#person");
            common.widget_destroy("#animal");
            tableform.dialog_destroy();
        },

        name: "licence",
        animation: function() { return controller.name == "licence" ? "book" : "formtab"; },
        title:  function() { 
            let t = "";
            if (controller.name == "animal_licence") {
                t = common.substitute(_("{0} - {1} ({2} {3} aged {4})"), { 
                    0: controller.animal.ANIMALNAME, 1: controller.animal.CODE, 2: controller.animal.SEXNAME,
                    3: controller.animal.SPECIESNAME, 4: controller.animal.ANIMALAGE }); 
            }
            else if (controller.name == "person_licence") { t = controller.person.OWNERNAME; }
            else if (controller.name == "licence") { t = _("Licensing"); }
            return t;
        },

        routes: {
            "animal_licence": function() { common.module_loadandstart("licence", "animal_licence?id=" + this.qs.id); },
            "person_licence": function() { common.module_loadandstart("licence", "person_licence?id=" + this.qs.id); },
            "licence": function() { common.module_loadandstart("licence", "licence?offset=" + this.qs.offset); }
        }


    };

    common.module_register(licence);

});
