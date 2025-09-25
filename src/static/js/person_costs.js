/*global $, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    "use strict";
    const person_costs = {

        lastperson: null,
        lastanimal: null,

        model: function() {
            const dialog = {
                add_title: _("Add cost"),
                edit_title: _("Edit cost"),
                edit_perm: 'ccad',
                close_on_ok: false,
                columns: 1,
                width: 550,
                fields: [
                    { json_field: "ANIMALID", post_field: "animal", label: _("Animal"), type: "animal", validation: "notzero" },
                    { json_field: "COSTTYPEID", post_field: "type", label: _("Type"), type: "select", options: { displayfield: "COSTTYPENAME", valuefield: "ID", rows: controller.costtypes }},
                    { json_field: "COSTDATE", post_field: "costdate", label: _("Date"), type: "date", validation: "notblank", defaultval: new Date() },
                    { json_field: "COSTPAIDDATE", post_field: "costpaid", label: _("Paid"), type: "date", hideif: function() { return !config.bool("ShowCostPaid"); } },
                    { json_field: "INVOICENUMBER", post_field: "invoicenumber", label: _("Invoice Number"), type: "text" },
                    { json_field: "COSTAMOUNT", post_field: "cost", label: _("Cost"), type: "currency", validation: "notblank" },
                    { json_field: "DESCRIPTION", post_field: "description", label: _("Description"), type: "textarea" }
                ]
            };

            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: async function(row) {
                    await tableform.dialog_show_edit(dialog, row, {
                        onload: function() {
                            $("#animalrow").show();
                        },
                        onchange: function() {
                            tableform.fields_update_row(dialog.fields, row);
                            row.COSTTYPENAME = common.get_field(controller.costtypes, row.COSTTYPEID, "COSTTYPENAME");
                            if (person_costs.lastanimal) {
                                row.ANIMALNAME = person_costs.lastanimal.ANIMALNAME;
                                row.SHELTERCODE = person_costs.lastanimal.SHELTERCODE;
                                row.SHORTCODE = person_costs.lastanimal.SHORTCODE;
                            }
                            tableform.fields_post(dialog.fields, "mode=update&costid=" + row.ID + "&person=" + controller.person.ID, "person_costs");
                            tableform.table_update(table);
                            tableform.dialog_close();
                        }
                    });
                    
                },
                columns: [
                    { field: "COSTTYPENAME", display: _("Type") },
                    { field: "COSTDATE", display: _("Date"), initialsort: true, initialsortdirection: "desc", formatter: tableform.format_date },
                    { field: "COSTAMOUNT", display: _("Cost"), formatter: tableform.format_currency },
                    { field: "COSTPAIDDATE", display: _("Paid"), formatter: tableform.format_date,
                        hideif: function() { return !config.bool("ShowCostPaid"); }
                    },
                    { field: "INVOICENUMBER", display: _("Invoice Number") },
                    { field: "ANIMALID", display: _("Animal"), 
                        formatter: function(row) {
                            let h = html.animal_link(row, { noemblems: controller.name == "person_costs", emblemsright: true });
                            return h;
                        }
                    },
                    { field: "DESCRIPTION", display: _("Description"), formatter: tableform.format_comments }
                ]
            };

            const buttons = [
                { id: "new", text: _("New Cost"), icon: "new", enabled: "always", perm: "caad",
                    click: function() { 
                        tableform.dialog_show_add(dialog, {
                            onload: function() {
                                $("#animalrow").show();
                            },
                            onadd: function() {
                                let response;
                                response = tableform.fields_post(dialog.fields, "mode=create&person=" + controller.person.ID, "person_costs");
                                let row = {};
                                row.ID = response;
                                tableform.fields_update_row(dialog.fields, row);
                                row.COSTTYPENAME = common.get_field(controller.costtypes, row.COSTTYPEID, "COSTTYPENAME");
                                if (person_costs.lastanimal) {
                                    row.ANIMALNAME = person_costs.lastanimal.ANIMALNAME;
                                    row.SHELTERCODE = person_costs.lastanimal.SHELTERCODE;
                                    row.SHORTCODE = person_costs.lastanimal.SHORTCODE;
                                }
                                controller.rows.push(row);
                                tableform.table_update(table);
                                tableform.dialog_close();
                            }
                        });
                        
                    } 
                },
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "cdad",
                    click: async function() { 
                        await tableform.delete_dialog();
                        tableform.buttons_default_state(buttons);
                        let ids = tableform.table_ids(table);
                        await common.ajax_post("person_costs", "mode=delete&ids=" + ids);
                        tableform.table_remove_selected_from_json(table, controller.rows);
                        tableform.table_update(table);
                        person_costs.calculate_costtotals();
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
            s += edit_header.person_edit_header(controller.person, "costs", controller.tabcounts);
            s += tableform.buttons_render(this.buttons);
            s += tableform.table_render(this.table);
            return s;
        },

        bind: function() {
            $(".asm-tabbar").asmtabs();
            tableform.dialog_bind(this.dialog);
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);

            $("#animal").animalchooser().bind("animalchooserchange", function(event, rec) {
                person_costs.lastanimal = rec;
            });

            $("#animal").animalchooser().bind("animalchooserloaded", function(event, rec) {
                person_costs.lastanimal = rec;
            });
            
            $("#type").change(person_costs.costtype_change);

            $("#button-savecost")
                .button({ icons: { primary: "ui-icon-disk" }, text: false })
                .click(person_costs.save_boarding_cost);

            $("#button-savecost").button("disable");

        },

        costtype_change: function() {
            let dc = common.get_field(controller.costtypes, $("#type").select("value"), "DEFAULTCOST");
            if (!dc) { dc = 0; }
            $("#cost").currency("value", dc);
        },

        sync: function() {
        },

        save_boarding_cost: function() {
            $("#button-savecost").button("disable");
            let formdata = "mode=dailyboardingcost&animalid=" + $("#animalid").val() + 
                "&dailyboardingcost=" + $("#dailyboardingcost").currency("value");
            header.show_loading(_("Saving..."));
            common.ajax_post("animal_costs", formdata)
                .always(function() { 
                    $("#button-savecost").button("enable");
                });
        },

        destroy: function() {
            common.widget_destroy("#animal");
            animal_costs.lastanimal = null;
            tableform.dialog_destroy();
        },

        name: "person_costs",
        animation: function() { return controller.name == "person_costs" ? "book" : "formtab"; },
        title: function() {
            return controller.person.OWNERNAME;
        },

        routes: {
            "person_costs": function() { common.module_loadandstart("person_costs", "person_costs?id=" + this.qs.id);}
        }

    };

    common.module_register(person_costs);

});
