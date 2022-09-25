/*global $, _, asm, common, config, controller, dlgfx, format, edit_header, html, tableform, validate */

$(function() {
    
    "use strict";

    const animal_diet = {

        model: function() {
            const dialog = {
                add_title: _("Add diet"),
                edit_title: _("Edit diet"),
                edit_perm: 'dcad',
                close_on_ok: false,
                columns: 1,
                width: 550,
                fields: [
                    { json_field: "DIETID", post_field: "type", label: _("Type"), type: "select", options: { displayfield: "DIETNAME", valuefield: "ID", rows: controller.diettypes }},
                    { json_field: "DATESTARTED", post_field: "startdate", label: _("Start Date"), type: "date", validation: "notblank", defaultval: new Date() },
                    { json_field: "COMMENTS", post_field: "comments", label: _("Comments"), type: "textarea" }
                ]
            };

            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: async function(row) {
                    await tableform.dialog_show_edit(dialog, row);
                    tableform.fields_update_row(dialog.fields, row);
                    row.DIETNAME = common.get_field(controller.diettypes, row.DIETID, "DIETNAME");
                    row.DIETDESCRIPTION = common.get_field(controller.diettypes, row.DIETID, "DIETDESCRIPTION");
                    await tableform.fields_post(dialog.fields, "mode=update&dietid=" + row.ID, "animal_diet");
                    tableform.table_update(table);
                    tableform.dialog_close();
                },
                complete: function(row) {
                    // Do we have a diet newer than this one? If so, mark it complete
                    let iscomplete = false;
                    $.each(controller.rows, function(i, v) {
                        if (format.date_js(v.DATESTARTED) > format.date_js(row.DATESTARTED)) {
                            iscomplete = true;
                        }
                    });
                    return iscomplete;
                },
                columns: [
                    { field: "DIETNAME", display: _("Type") },
                    { field: "DIETDESCRIPTION", display: _("Description") },
                    { field: "DATESTARTED", display: _("Start Date"), initialsort: true, initialsortdirection: "desc", formatter: tableform.format_date },
                    { field: "COMMENTS", display: _("Comments"), formatter: tableform.format_comments }
                ]
            };

            const buttons = [
                { id: "new", text: _("New Diet"), icon: "new", enabled: "always", perm: "daad",
                    click: async function() { 
                        await tableform.dialog_show_add(dialog);
                        let response = await tableform.fields_post(dialog.fields, "mode=create&animalid="  + controller.animal.ID, "animal_diet");
                        let row = {};
                        row.ID = response;
                        tableform.fields_update_row(dialog.fields, row);
                        row.DIETNAME = common.get_field(controller.diettypes, row.DIETID, "DIETNAME");
                        row.DIETDESCRIPTION = common.get_field(controller.diettypes, row.DIETID, "DIETDESCRIPTION");
                        controller.rows.push(row);
                        tableform.table_update(table);
                        tableform.dialog_close();
                    } 
                },
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "ddad",
                    click: async function() { 
                        await tableform.delete_dialog();
                        tableform.buttons_default_state(buttons);
                        let ids = tableform.table_ids(table);
                        await common.ajax_post("animal_diet", "mode=delete&ids=" + ids);
                        tableform.table_remove_selected_from_json(table, controller.rows);
                        tableform.table_update(table);
                    } 
                }
            ];
            this.dialog = dialog;
            this.buttons = buttons;
            this.table = table;
        },

        render: function() {
            this.model();
            let s = "";
            s += tableform.dialog_render(this.dialog);
            s += edit_header.animal_edit_header(controller.animal, "diet", controller.tabcounts);
            s += tableform.buttons_render(this.buttons);
            s += tableform.table_render(this.table);
            s += html.content_footer();
            return s;
        },

        bind: function() {
            $(".asm-tabbar").asmtabs();
            tableform.dialog_bind(this.dialog);
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);
        },

        destroy: function() {
            tableform.dialog_destroy();
        },

        name: "animal_diet",
        animation: "formtab",

        title:  function() { return common.substitute(_("{0} - {1} ({2} {3} aged {4})"), { 
            0: controller.animal.ANIMALNAME, 1: controller.animal.CODE, 2: controller.animal.SEXNAME,
            3: controller.animal.SPECIESNAME, 4: controller.animal.ANIMALAGE }); },

        routes: {
            "animal_diet": function() {
                common.module_loadandstart("animal_diet", "animal_diet?id=" + this.qs.id);
            }
        }


    };

    common.module_register(animal_diet);

});
