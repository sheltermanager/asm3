/*global $, _, asm, common, config, controller, dlgfx, format, edit_header, html, tableform, validate */

$(function() {
    
    "use strict";

    const animal_condition = {

        model: function() {
            const dialog = {
                add_title: _("Add condition"),
                edit_title: _("Edit condition"),
                edit_perm: 'caco',
                close_on_ok: false,
                columns: 1,
                width: 550,
                fields: [
                    { json_field: "CONDITIONID", post_field: "conditionid", label: _("Type"), type: "select", options: { displayfield: "CONDITIONNAME", valuefield: "ID", rows: controller.conditions }},
                    { json_field: "STARTDATETIME", post_field: "start", label: _("Start"), type: "datetime", validation: "notblank", defaultval: new Date() },
                    { json_field: "ENDDATETIME", post_field: "end", label: _("End"), type: "datetime" },
                    { json_field: "COMMENTS", post_field: "comments", label: _("Comments"), type: "textarea" }
                ]
            };

            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: async function(row) {
                    await tableform.dialog_show_edit(dialog, row, {
                            onvalidate: function() {
                                if (!$("#starttime").val()) { $("#starttime").val("00:00:00"); }
                                let enddate = $("#enddate").val();
                                let endtime = $("#endtime").val();
                                if (enddate && !endtime) { $("#endtime").val("00:00:00"); }
                                return true;
                            }
                        }
                    );
                    tableform.fields_update_row(dialog.fields, row);
                    row.CONDITIONNAME = common.get_field(controller.conditions, row.CONDITIONID, "CONDITIONNAME");
                    await tableform.fields_post(dialog.fields, "mode=update&animalconditionid=" + row.ID, "animal_condition");
                    tableform.table_update(table);
                    tableform.dialog_close();
                },
                columns: [
                    { field: "CONDITIONNAME", display: _("Condition") },
                    { field: "STARTDATETIME", display: _("Start"), 
                        formatter: function(row, v) {
                            return format.date(v) + " " + format.time(v, "%H:%M:%S", true);
                        }
                    },
                    { field: "ENDDATETIME", display: _("End"), 
                        formatter: function(row, v) {
                            return format.date(v) + " " + format.time(v, "%H:%M:%S", true);
                        }
                    },
                    { field: "COMMENTS", display: _("Comments"), formatter: tableform.format_comments }
                ]
            };

            const buttons = [
                { id: "new", text: _("New Condition"), icon: "new", enabled: "always", perm: "aaco",
                    click: async function() {
                        await tableform.dialog_show_add(dialog, {
                            onvalidate: function() {
                                if (!$("#starttime").val()) { $("#starttime").val("00:00:00"); }
                                let enddate = $("#enddate").val();
                                let endtime = $("#endtime").val();
                                if (enddate && !endtime) { $("#endtime").val("00:00:00"); }
                                return true;
                            },
                            onload: function() {
                                // Reset the date fields
                                $("#startdate").datepicker("setDate", new Date());
                                $("#starttime, #enddate, #endtime").val("");
                            }
                        });
                        let response = await tableform.fields_post(dialog.fields, "mode=create&animalid="  + controller.animal.ID, "animal_condition");
                        let row = {};
                        row.ID = response;
                        tableform.fields_update_row(dialog.fields, row);
                        row.CONDITIONNAME = common.get_field(controller.conditions, row.CONDITIONID, "CONDITIONNAME");
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
                        await common.ajax_post("animal_condition", "mode=delete&ids=" + ids);
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
            s += edit_header.animal_edit_header(controller.animal, "condition", controller.tabcounts);
            s += tableform.buttons_render(this.buttons);
            s += tableform.table_render(this.table);
            s += html.content_footer();
            return s;
        },

        bind: function() {
            tableform.dialog_bind(this.dialog);
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);
        },

        destroy: function() {
            tableform.dialog_destroy();
        },

        name: "animal_condition",
        animation: "formtab",

        title:  function() { return common.substitute(_("{0} - {1} ({2} {3} aged {4})"), { 
            0: controller.animal.ANIMALNAME, 1: controller.animal.CODE, 2: controller.animal.SEXNAME,
            3: controller.animal.SPECIESNAME, 4: controller.animal.ANIMALAGE }); },

        routes: {
            "animal_condition": function() {
                common.module_loadandstart("animal_condition", "animal_condition?id=" + this.qs.id);
            }
        }


    };

    common.module_register(animal_condition);

});
