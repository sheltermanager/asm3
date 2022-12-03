/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const litters = {

        lastanimal: null,

        model: function() {
            const dialog = {
                add_title: _("Add litter"),
                edit_title: _("Edit litter"),
                edit_perm: 'cll',
                close_on_ok: false,
                hide_read_only: true, 
                columns: 1,
                fields: [
                    { json_field: "ACCEPTANCENUMBER", post_field: "litterref", label: _("Litter Reference"), type: "text",
                        tooltip: _("A unique reference for this litter"), validation: "notblank" },
                    { json_field: "PARENTANIMALID", post_field: "animal", label: _("Mother"), type: "animal", animalfilter: "female" },
                    { json_field: "ANIMALS", post_field: "animals", label: _("Littermates"), type: "animalmulti", readonly: true },
                    { json_field: "SPECIESID", post_field: "species", label: _("Species"), type: "select", 
                        options: { rows: controller.species, valuefield: "ID", displayfield: "SPECIESNAME" }},
                    { json_field: "DATE", post_field: "startdate", label: _("Start date"), 
                        tooltip: _("The date the litter entered the shelter"), type: "date", validation: "notblank" },
                    { json_field: "NUMBERINLITTER", post_field: "numberinlitter", label: _("Number in litter"), type: "number", validation: "notblank" },
                    { json_field: "INVALIDDATE", post_field: "expirydate", label: _("Expiry date"), type: "date" },
                    { json_field: "COMMENTS", post_field: "comments", label: _("Comments"), type: "textarea" }
                ]
            };

            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: async function(row) {
                    $("#animal").animalchooser("clear");
                    tableform.fields_populate_from_json(dialog.fields, row);
                    await tableform.dialog_show_edit(dialog, row);
                    tableform.fields_update_row(dialog.fields, row);
                    litters.set_extra_fields(row);
                    await tableform.fields_post(dialog.fields, "mode=update&litterid=" + row.ID, "litters");
                    tableform.table_update(table);
                    tableform.dialog_close();
                },
                complete: function(row) {
                    return (row.INVALIDDATE && format.date_js(row.INVALIDDATE) <= new Date()) || row.CACHEDANIMALSLEFT == 0;
                },
                columns: [
                    { field: "ACCEPTANCENUMBER", display: _("Litter Ref") },
                    { field: "PARENTANIMALID", display: _("Parent"), formatter: function(row) {
                        if (row.PARENTANIMALID) {
                            return '<a href="animal?id=' + row.PARENTANIMALID + '">' + row.MOTHERNAME + ' - ' + row.MOTHERCODE + '</a>';
                        }
                        return "";
                    }},
                    { field: "SPECIESNAME", display: _("Species") },
                    { field: "DATE", display: _("Starts"), formatter: tableform.format_date, initialsort: true, initialsortdirection: "desc" },
                    { field: "INVALIDDATE", display: _("Expires"), formatter: tableform.format_date },
                    { field: "NUMBERINLITTER", display: _("Number in litter") },
                    { field: "CACHEDANIMALSLEFT", display: _("Remaining") },
                    { field: "LITTERMATES", display: _("Littermates"), formatter: function(row) {
                        let mates = [];
                        $.each(controller.littermates, function(i, v) {
                            if (v.ACCEPTANCENUMBER == row.ACCEPTANCENUMBER) {
                                mates.push( html.animal_link(v) );
                            }
                        });
                        return mates.join("<br/>");
                    }},
                    { field: "COMMENTS", display: _("Comments"), formatter: tableform.format_comments }
                ]
            };

            const buttons = [
                { id: "new", text: _("New Litter"), icon: "new", enabled: "always", perm: "all", 
                    click: async function() { 
                        let formdata = "mode=nextlitterid";
                        let result = await common.ajax_post("litters", formdata);
                        await tableform.dialog_show_add(dialog, { 
                            onload: function() {
                                litters.lastanimal = null;
                                $("#litterref").val(result);
                                $("#animal").animalchooser("clear");
                            },
                            onvalidate: function() {
                                // Don't allow more than 20 animals in a litter (world records are 24 for dogs, 19 for cats)
                                if ($("#animals").val().split(",").length > 20) {
                                    tableform.dialog_error(_("Litter creation is limited to 20 animals"));
                                    return false;
                                }
                                return true;
                            }
                        });
                        let response = await tableform.fields_post(dialog.fields, "mode=create", "litters");
                        common.route_reload(); // Cannot lazy load littermates column so reload screen
                        /*
                        let row = {};
                        row.ID = response;
                        tableform.fields_update_row(dialog.fields, row);
                        litters.set_extra_fields(row);
                        controller.rows.push(row);
                        tableform.table_update(table);
                        tableform.dialog_close();
                        */
                    } 
                },
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "dll", 
                    click: async function() { 
                        await tableform.delete_dialog();
                        tableform.buttons_default_state(buttons);
                        let ids = tableform.table_ids(table);
                        await common.ajax_post("litters", "mode=delete&ids=" + ids);
                        tableform.table_remove_selected_from_json(table, controller.rows);
                        tableform.table_update(table);
                    } 
                },
                { id: "littermates", text: _("Littermates"), icon: "litter", enabled: "one", perm: "va", 
                    click: function() { 
                        let row = tableform.table_selected_row(table);
                        common.route("animal_find_results?mode=ADVANCED&q=&filter=includedeceased&litterid=" + encodeURIComponent(row.ACCEPTANCENUMBER));
                    }
                },
                { id: "offset", type: "dropdownfilter", 
                    options: [ "active|" + _("Active"), "m182|" + _("In the last 6 months"), "m365|" + _("In the last year"), "730|" + _("In the last 2 years"), "1095|" + _("In the last 3 years"), "a|" + _("All time") ],
                    click: function(selval) {
                        common.route("litters?offset=" + selval);
                    },
                    hideif: function(row) {
                        // Don't show for animal records
                        if (controller.animal) {
                            return true;
                        }
                    }
                }
            ];
            this.dialog = dialog;
            this.buttons = buttons;
            this.table = table;
        },

        render: function() {
            let s = "";
            this.model();
            s += tableform.dialog_render(this.dialog);
            s += html.content_header(_("Litters"));
            s += tableform.buttons_render(this.buttons);
            s += tableform.table_render(this.table);
            s += html.content_footer();
            return s;
        },

        bind: function() {
            tableform.dialog_bind(this.dialog);
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);
            $("#animal").animalchooser().bind("animalchooserchange", function(event, rec) { litters.lastanimal = rec; $("#species").select("value", rec.SPECIESID); });
            $("#animal").animalchooser().bind("animalchooserloaded", function(event, rec) { litters.lastanimal = rec; });
        },

        sync: function() {
            // If an offset is given in the querystring, update the select
            if (common.querystring_param("offset")) {
                $("#offset").select("value", common.querystring_param("offset"));
            }
        },

        set_extra_fields: function(row) {
            row.MOTHERNAME = ""; row.MOTHERCODE = "";
            if (litters.lastanimal) {
                row.MOTHERNAME = litters.lastanimal.ANIMALNAME;
                row.MOTHERCODE = litters.lastanimal.SHELTERCODE;
            }
            row.SPECIESNAME = common.get_field(controller.species, row.SPECIESID, "SPECIESNAME");
            if (row.CACHEDANIMALSLEFT === undefined) {
                row.CACHEDANIMALSLEFT = row.NUMBERINLITTER;
            }
        },

        destroy: function() {
            common.widget_destroy("#animal");
            tableform.dialog_destroy();
            this.lastanimal = null;
        },

        name: "litters",
        animation: "book",
        title: function() { return _("Litters"); },
        routes: {
            "litters": function() { common.module_loadandstart("litters", "litters?" + this.rawqs); }
        }

    };

    common.module_register(litters);

});
