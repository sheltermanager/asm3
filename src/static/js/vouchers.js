/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const vouchers = {

        model: function() {
            const dialog = {
                add_title: _("Add voucher"),
                edit_title: _("Edit voucher"),
                edit_perm: 'vcov',
                helper_text: _("Vouchers need an issue and expiry date."),
                close_on_ok: false,
                columns: 1,
                width: 550,
                fields: [
                    { json_field: "OWNERID", post_field: "person", label: _("Person"), type: "person", validation: "notzero" },
                    { json_field: "ANIMALID", post_field: "animal", label: _("Animal (optional)"), type: "animal" },
                    { json_field: "VOUCHERID", post_field: "type", label: _("Type"), type: "select", options: { displayfield: "VOUCHERNAME", valuefield: "ID", rows: controller.vouchertypes }},
                    { json_field: "VOUCHERCODE", post_field: "vouchercode", label: _("Code"), type: "text", validation: "notblank",
                        callout: _("Specify a unique code to identify this voucher") },
                    { json_field: "DATEISSUED", post_field: "issued", label: _("Issued"), type: "date", validation: "notblank", defaultval: new Date() },
                    { json_field: "DATEEXPIRED", post_field: "expires", label: _("Expires"), type: "date", validation: "notblank", defaultval: new Date() },
                    { json_field: "DATEPRESENTED", post_field: "presented", label: _("Redeemed"), type: "date", callout: _("The date this voucher was used") },
                    { json_field: "VALUE", post_field: "amount", label: _("Amount"), type: "currency" },
                    { json_field: "COMMENTS", post_field: "comments", label: _("Comments"), type: "textarea" }
                ]
            };

            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: async function(row) {
                    await tableform.dialog_show_edit(dialog, row);
                    tableform.fields_update_row(dialog.fields, row);
                    vouchers.set_extra_fields(row);
                    try {
                        await tableform.fields_post(dialog.fields, "mode=update&voucherid=" + row.ID, "voucher");
                        tableform.table_update(table);
                        tableform.dialog_close();
                    }
                    catch(err) {
                        log.error(err, err); 
                        tableform.dialog_enable_buttons();
                    }
                },
                complete: function(row) {
                    if (row.DATEEXPIRED != null && format.date_js(row.DATEEXPIRED) <= new Date()) { return true; }
                    if (row.DATEPRESENTED != null && format.date_js(row.DATEPRESENTED) <= new Date()) { return true; }
                },
                columns: [
                    { field: "VOUCHERNAME", display: _("Type") },
                    { field: "VOUCHERCODE", display: _("Code") },
                    { field: "DATEISSUED", display: _("Issued"), initialsort: true, initialsortdirection: "desc", formatter: tableform.format_date },
                    { field: "DATEEXPIRED", display: _("Expires"), formatter: tableform.format_date },
                    { field: "DATEPRESENTED", display: _("Redeemed"), formatter: tableform.format_date },
                    { field: "VALUE", display: _("Amount"), formatter: tableform.format_currency },
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
                    { field: "ANIMAL", display: _("Animal"), 
                        formatter: function(row) {
                            if (!row.ANIMALID || row.ANIMALID == 0) { return ""; }
                            let s = "";
                            if (controller.name.indexOf("animal_") == -1) { s = html.animal_emblems(row) + " "; }
                            return s + '<a href="animal?id=' + row.ANIMALID + '">' + row.ANIMALNAME + ' - ' + row.SHELTERCODE + '</a>';
                        },
                        hideif: function(row) {
                            return controller.name.indexOf("animal_") != -1;
                        }
                    },
                    { field: "COMMENTS", display: _("Comments"), formatter: tableform.format_comments }
                ]
            };

            const buttons = [
                { id: "new", text: _("New Voucher"), icon: "new", enabled: "always", perm: "vaov", 
                    click: function() { 
                        tableform.dialog_show_add(dialog, { 
                            onadd: async function() {
                                try {
                                    let response = await tableform.fields_post(dialog.fields, "mode=create", "voucher");
                                    let row = {};
                                    row.ID = response;
                                    tableform.fields_update_row(dialog.fields, row);
                                    vouchers.set_extra_fields(row);
                                    controller.rows.push(row);
                                    tableform.table_update(table);
                                    tableform.dialog_close();
                                }
                                catch(err) {
                                    log.error(err, err);
                                    tableform.dialog_enable_buttons();   
                                }
                            },
                            onload: function() {
                                $("#animal").animalchooser("clear");
                                $("#person").personchooser("clear");
                                if (controller.animal) {
                                    $("#animal").animalchooser("loadbyid", controller.animal.ID);
                                }
                                if (controller.person) {
                                    $("#person").personchooser("loadbyid", controller.person.ID);
                                }
                                vouchers.vouchertype_change();
                            }
                        }); 
                    }
                },
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "vdov", 
                    click: async function() { 
                        await tableform.delete_dialog();
                        tableform.buttons_default_state(buttons);
                        let ids = tableform.table_ids(table);
                        await common.ajax_post("voucher", "mode=delete&ids=" + ids);
                        tableform.table_remove_selected_from_json(table, controller.rows);
                        tableform.table_update(table);
                    } 
                },
                { id: "document", text: _("Document"), icon: "document", enabled: "one", perm: "gaf", 
                    tooltip: _("Generate document from this voucher"), type: "buttonmenu" },
                { id: "offset", type: "dropdownfilter", 
                    options: [
                        "i31|" + _("Issued in last month"),
                        "e31|" + _("Expiring in next month"),
                        "p31|" + _("Redeemed in last month"),
                        "a0|" + _("Unredeemed")
                    ],
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

        set_extra_fields: function(row) {
            if (controller.animal) {
                row.ANIMALNAME = controller.animal.ANIMALNAME;
                row.SHELTERCODE = controller.animal.SHELTERCODE;
            }
            else if (vouchers.lastanimal) {
                row.ANIMALNAME = vouchers.lastanimal.ANIMALNAME;
                row.SHELTERCODE = vouchers.lastanimal.SHELTERCODE;
            }
            else {
                row.ANIMALNAME = "";
                row.SHELTERCODE = "";
            }
            if (controller.person) {
                row.OWNERNAME = controller.person.OWNERNAME;
                row.OWNERADDRESS = controller.person.OWNERADDRESS;
                row.HOMETELEPHONE = controller.person.HOMETELEPHONE;
                row.WORKTELEPHONE = controller.person.WORKTELEPHONE;
                row.MOBILETELEPHONE = controller.person.MOBILETELEPHONE;
            }
            else if (vouchers.lastperson) {
                row.OWNERNAME = vouchers.lastperson.OWNERNAME;
                row.OWNERADDRESS = vouchers.lastperson.OWNERADDRESS;
                row.HOMETELEPHONE = vouchers.lastperson.HOMETELEPHONE;
                row.WORKTELEPHONE = vouchers.lastperson.WORKTELEPHONE;
                row.MOBILETELEPHONE = vouchers.lastperson.MOBILETELEPHONE;
            }
            row.VOUCHERNAME = common.get_field(controller.vouchertypes, row.VOUCHERID, "VOUCHERNAME");
        },

        render: function() {
            let s = "";
            this.model();
            s += tableform.dialog_render(this.dialog);
            s += '<div id="button-document-body" class="asm-menu-body">' +
                '<ul class="asm-menu-list">' +
                edit_header.template_list(controller.templates, "VOUCHER", 0) +
                '</ul></div>';
            if (controller.name == "animal_vouchers") {
                s += edit_header.animal_edit_header(controller.animal, "vouchers", controller.tabcounts);
            }
            else if (controller.name == "person_vouchers") {
                s += edit_header.person_edit_header(controller.person, "vouchers", controller.tabcounts);
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
            tableform.dialog_bind(this.dialog);
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);

            if (controller.name.indexOf("animal_") != -1) {
                $("#animal").closest("tr").hide();
                $(".asm-tabbar").asmtabs();
            }
            if (controller.name.indexOf("person_") != -1) {
                $("#person").closest("tr").hide();
                $(".asm-tabbar").asmtabs();
            }

            $("#animal").animalchooser().bind("animalchooserchange", function(event, rec) {
                vouchers.lastanimal = rec;
            });

            $("#animal").animalchooser().bind("animalchooserloaded", function(event, rec) {
                vouchers.lastanimal = rec;
            });

            $("#person").personchooser().bind("personchooserchange", function(event, rec) {
                vouchers.lastperson = rec;
            });

            $("#person").personchooser().bind("personchooserloaded", function(event, rec) {
                vouchers.lastperson = rec;
            });

            $("#type").change(vouchers.vouchertype_change);

            // Generate code button
            $("#vouchercode").after('<button id="button-code">' + _("Generate a unique voucher code") + '</button>');
            $("#button-code")
                .button({ icons: { primary: "ui-icon-refresh" }, text: false })
                .click(function() {
                    $("#vouchercode").val(common.generate_random_code(8));
                });

            // Add click handlers to templates
            $(".templatelink").click(function() {
                // Update the href as it is clicked so default browser behaviour
                // continues on to open the link in a new window
                let template_name = $(this).attr("data");
                $(this).prop("href", "document_gen?linktype=VOUCHER&id=" + tableform.table_selected_row(vouchers.table).ID + "&dtid=" + template_name);
            });

        },

        sync: function() {
            // If an offset is given in the querystring, update the select
            if (common.querystring_param("offset")) {
                $("#offset").select("value", common.querystring_param("offset"));
            }
        },

        destroy: function() {
            common.widget_destroy("#animal");
            common.widget_destroy("#person");
            tableform.dialog_destroy();
            this.lastanimal = null;
            this.lastperson = null;
        },

        vouchertype_change: function() {
            let dc = common.get_field(controller.vouchertypes, $("#type").select("value"), "DEFAULTCOST");
            $("#amount").currency("value", dc);
        },

        name: "vouchers",
        animation: function() { return controller.name == "voucher" ? "book" : "formtab"; },
        title:  function() { 
            let t = "";
            if (controller.name == "animal_vouchers") {
                t = common.substitute(_("{0} - {1} ({2} {3} aged {4})"), { 
                    0: controller.animal.ANIMALNAME, 1: controller.animal.CODE, 2: controller.animal.SEXNAME,
                    3: controller.animal.SPECIESNAME, 4: controller.animal.ANIMALAGE }); 
            }
            else if (controller.name == "person_vouchers") { t = controller.person.OWNERNAME; }
            else if (controller.name == "voucher") { t = _("Voucher Book"); }
            return t;
        },

        routes: {
            "person_vouchers": function() { common.module_loadandstart("vouchers", "person_vouchers?id=" + this.qs.id); },
            "voucher": function() { common.module_loadandstart("vouchers", "voucher?" + this.rawqs); }
        }

    };

    common.module_register(vouchers);

});
