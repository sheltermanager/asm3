/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    var donations = {

        // Used to let person_loaded know whether we are creating or not
        create_semaphore: false,

        lastanimal: null,
        lastperson: null,
        dialog_row: null,

        model: function() {

            var dialog = {
                add_title: _("Add payment"),
                edit_title: _("Edit payment"),
                edit_perm: 'ocod',
                close_on_ok: false,
                hide_read_only: true,
                helper_text: _("Payments need at least one date, an amount and a person."),
                columns: 2,
                fields: [
                    { json_field: "DONATIONTYPEID", post_field: "type", label: _("Type"), type: "select", options: { displayfield: "DONATIONNAME", valuefield: "ID", rows: controller.donationtypes }},
                    { json_field: "DONATIONPAYMENTID", post_field: "payment", label: _("Method"), type: "select", options: { displayfield: "PAYMENTNAME", valuefield: "ID", rows: controller.paymenttypes }},
                    { json_field: "FREQUENCY", post_field: "frequency", label: _("Frequency"), type: "select", options: { displayfield: "FREQUENCY", valuefield: "ID", rows: controller.frequencies }},
                    { json_field: "DATEDUE", post_field: "due", label: _("Due"), type: "date" },
                    { json_field: "DATE", post_field: "received", label: _("Received"), type: "date" },
                    { json_field: "QUANTITY", post_field: "quantity", label: _("Quantity"), type: "number", 
                        hideif: function() { return !config.bool("DonationQuantities"); } },
                    { json_field: "UNITPRICE", post_field: "unitprice", label: _("Unit Price"), type: "currency", 
                        hideif: function() { return !config.bool("DonationQuantities"); } },
                    { json_field: "DONATION", post_field: "amount", label: _("Amount"), type: "currency" },
                    { json_field: "", post_field: "destaccount", label: _("Deposit Account"), 
                        hideif: function() { return !config.bool("DonationTrxOverride"); }, 
                        defaultval: config.integer("DonationTargetAccount"),
                        type: "select", options: { displayfield: "CODE", valuefield: "ID", rows: controller.accounts }},
                    { json_field: "CHEQUENUMBER", post_field: "chequenumber", label: _("Check No"), type: "text" },
                    { json_field: "RECEIPTNUMBER", post_field: "receiptnumber", label: _("Receipt No"), type: "text" },
                    { json_field: "ISGIFTAID", post_field: "giftaid", label: _("Gift Aid"), type: "check" },
                    { json_field: "ISVAT", post_field: "vat", label: _("Sales Tax"), type: "check", 
                        hideif: function() { return !config.bool("VATEnabled"); } },
                    { json_field: "VATRATE", post_field: "vatrate", label: _("Tax Rate %"), type: "number", 
                        hideif: function() { return !config.bool("VATEnabled"); } },
                    { json_field: "VATAMOUNT", post_field: "vatamount", label: _("Tax Amount"), type: "currency",
                        hideif: function() { return !config.bool("VATEnabled"); } },
                    { type: "nextcol" },
                    { json_field: "ANIMALID", post_field: "animal", label: _("Animal"), type: "animal" },
                    { json_field: "OWNERID", post_field: "person", label: _("Person"), type: "person" },
                    { json_field: "MOVEMENTID", post_field: "movement", label: _("Movement"), type: "select", options: "" },
                    { json_field: "COMMENTS", post_field: "comments", label: _("Comments"), type: "textarea" }
                ]
            };

            var table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: function(row) {
                    tableform.fields_populate_from_json(dialog.fields, row);
                    donations.dialog_row = row;
                    donations.create_semaphore = false;
                    donations.update_movements(row.OWNERID);
                    // Only allow destination account to be overridden when the received date
                    // hasn't been set yet.
                    $("#destaccount").closest("tr").toggle( config.bool("DonationTrxOverride") && !row.DATE );
                    $("#receiptnumber").closest("tr").show();
                    $("#receiptnumber").prop("disabled", true);
                    if (row.ISVAT == 1) {
                        $("#vatrate").closest("tr").show();
                        $("#vatamount").closest("tr").show();
                    }
                    else {
                        $("#vatrate").closest("tr").hide();
                        $("#vatamount").closest("tr").hide();
                    }
                    tableform.dialog_show_edit(dialog, row)
                        .then(function() {
                            if (!donations.validation()) { tableform.dialog_enable_buttons(); return; }
                            tableform.fields_update_row(dialog.fields, row);
                            donations.set_extra_fields(row);
                            return tableform.fields_post(dialog.fields, "mode=update&donationid=" + row.ID, "donation");
                        })
                        .then(function(response) {
                            donations.calculate_total();
                            tableform.table_update(table);
                            tableform.dialog_close();
                        })
                        .fail(function() {
                            tableform.dialog_enable_buttons();
                        });
                },
                complete: function(row) {
                },
                overdue: function(row) {
                    return !row.DATE && format.date_js(row.DATEDUE) < common.today_no_time();
                },
                columns: [
                    { field: "DONATIONNAME", display: _("Type") },
                    { field: "PAYMENTNAME", display: _("Method") },
                    { field: "FREQUENCYNAME", display: _("Frequency") },
                    { field: "DATEDUE", display: _("Due"), formatter: tableform.format_date },
                    { field: "DATE", display: _("Received"), formatter: tableform.format_date, initialsort: true, initialsortdirection: "desc" },
                    { field: "RECEIPTNUMBER", display: _("Receipt No") },
                    { field: "QUANTITY", display: _("Qty"), hideif: function() { return !config.bool("DonationQuantities"); } },
                    { field: "DONATION", display: _("Amount"), formatter: tableform.format_currency },
                    { field: "VATAMOUNT", display: _("Tax"), formatter: tableform.format_currency, hideif: function() { return !config.bool("VATEnabled"); } },
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
                            var s = "";
                            if (controller.name.indexOf("animal_") == -1) { s = html.animal_emblems(row) + " "; }
                            return s + '<a href="animal?id=' + row.ANIMALID + '">' + row.ANIMALNAME + ' - ' + row.SHELTERCODE + '</a>';
                        },
                        hideif: function(row) {
                            return controller.name.indexOf("animal_") != -1;
                        }
                    },
                    { field: "COMMENTS", display: _("Comments") }
                ]
            };

            var buttons = [
                { id: "new", text: _("New Payment"), icon: "new", enabled: "always", perm: "oaod",
                     click: function() { 
                        tableform.dialog_show_add(dialog, {
                            onvalidate: function() {
                                return donations.validation();
                            },
                            onadd: function() {
                                tableform.fields_post(dialog.fields, "mode=create", "donation")
                                    .then(function(response) {
                                        var row = {};
                                        row.ID = response.split("|")[0];
                                        tableform.fields_update_row(dialog.fields, row);
                                        donations.set_extra_fields(row);
                                        row.RECEIPTNUMBER = response.split("|")[1];
                                        controller.rows.push(row);
                                        tableform.table_update(table);
                                        donations.calculate_total();
                                        tableform.dialog_close();
                                    })
                                    .fail(function() {
                                        tableform.dialog_enable_buttons();   
                                    });
                            },
                            onload: function() {
                                donations.create_semaphore = true;
                                $("#animal").animalchooser("clear");
                                $("#person").personchooser("clear");
                                if (controller.animal) {
                                    $("#animal").animalchooser("loadbyid", controller.animal.ID);
                                }
                                if (controller.person) {
                                    $("#person").personchooser("loadbyid", controller.person.ID);
                                    donations.update_movements(controller.person.ID);
                                }
                                $("#quantity").val("1");
                                $("#type").select("value", config.integer("AFDefaultDonationType"));
                                $("#payment").select("value", config.integer("AFDefaultPaymentMethod"));
                                $("#giftaid").prop("checked", false);
                                $("#receiptnumber").val("");
                                $("#receiptnumber").closest("tr").hide();
                                donations.type_change();
                                $("#vatrate").closest("tr").hide();
                                $("#vatamount").closest("tr").hide();
                            }
                        });
                     } 
                 },
                 { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "odod", 
                     click: function() { 
                         tableform.delete_dialog()
                             .then(function() {
                                 tableform.buttons_default_state(buttons);
                                 var ids = tableform.table_ids(table);
                                 return common.ajax_post("donation", "mode=delete&ids=" + ids);
                             })
                             .then(function() {
                                 tableform.table_remove_selected_from_json(table, controller.rows);
                                 tableform.table_update(table);
                                 donations.calculate_total();
                             });
                     } 
                 },
                 { id: "receive", text: _("Receive"), icon: "complete", enabled: "multi", tooltip: _("Mark selected payments received"), perm: "ocod",
                     click: function() {
                         var ids = tableform.table_ids(table);
                         common.ajax_post("donation", "mode=receive&ids=" + ids)
                             .then(function() {
                                 $.each(controller.rows, function(i, v) {
                                    if (tableform.table_id_selected(v.ID)) {
                                        v.DATE = format.date_iso(new Date());
                                    }
                                 });
                                 tableform.table_update(table);
                                 donations.calculate_total();
                             });
                     }
                 },
                 { id: "document", text: _("Receipt/Invoice"), icon: "document", enabled: "multi", perm: "gaf", 
                     tooltip: _("Generate document from this payment"), type: "buttonmenu" },
                 { id: "offset", type: "dropdownfilter", 
                     options: [ 
                        "m0|" + _("Received today"),
                        "m1|" + _("Received in last day"),
                        "m7|" + _("Received in last week"), 
                        "m31|" + _("Received in last month"),
                        "m365|" + _("Received in last year"),
                        "d0|" + _("Overdue"),
                        "p7|" + _("Due in next week"), 
                        "p31|" + _("Due in next month"), 
                        "p365|" + _("Due in next year") ],
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
            this.buttons = buttons;
            this.dialog = dialog;
            this.table = table;
        },

        validation: function() {
            if (!validate.notzero(["person"])) { return false; }
            if ($("#due").val() == "" && $("#received").val() == "") {
                validate.notblank(["received", "due"]);
                return false;
            }
            return true;
        },

        type_change: function() {
            var dc = common.get_field(controller.donationtypes, $("#type").select("value"), "DEFAULTCOST");
            $("#unitprice, #amount").currency("value", dc);
            if (config.bool("DonationQuantities")) {
                $("#amount").currency("value", format.to_int($("#quantity").val()) * $("#unitprice").currency("value"));
            }
        },

        update_movements: function(personid) {
            common.ajax_post("donation", "mode=personmovements&personid=" + personid)
                .then(function(result) {
                    var h = "<option value=\"0\"></option>";
                    $.each(jQuery.parseJSON(result), function(i,v) {
                        h += "<option value=\"" + v.ID + "\">";
                        h += v.ADOPTIONNUMBER + " - " + v.MOVEMENTNAME + ": " + v.ANIMALNAME;
                        h += "</option>";
                    });
                    $("#movement").html(h);
                    if (donations.dialog_row && donations.dialog_row.MOVEMENTID) {
                        $("#movement").select("value", donations.dialog_row.MOVEMENTID);
                    }
                    $("#movement").closest("tr").fadeIn();
                });
        },

        set_extra_fields: function(row) {
            if (controller.animal) {
                row.ANIMALNAME = controller.animal.ANIMALNAME;
                row.SHELTERCODE = controller.animal.SHELTERCODE;
            }
            else if (donations.lastanimal) {
                row.ANIMALNAME = donations.lastanimal.ANIMALNAME;
                row.SHELTERCODE = donations.lastanimal.SHELTERCODE;
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
            else if (donations.lastperson) {
                row.OWNERNAME = donations.lastperson.OWNERNAME;
                row.OWNERADDRESS = donations.lastperson.OWNERADDRESS;
                row.HOMETELEPHONE = donations.lastperson.HOMETELEPHONE;
                row.WORKTELEPHONE = donations.lastperson.WORKTELEPHONE;
                row.MOBILETELEPHONE = donations.lastperson.MOBILETELEPHONE;
            }
            row.DONATIONNAME = common.get_field(controller.donationtypes, row.DONATIONTYPEID, "DONATIONNAME");
            row.PAYMENTNAME = common.get_field(controller.paymenttypes, row.DONATIONPAYMENTID, "PAYMENTNAME");
            row.FREQUENCYNAME = common.get_field(controller.frequencies, row.FREQUENCY, "FREQUENCY");
        },

        calculate_total: function() {
            var tot = 0, due = 0, vat = 0;
            $.each(controller.rows, function(i, v) {
                if (v.DATE) { tot += v.DONATION; }
                else { due += v.DONATION; }
                if (v.VATAMOUNT) { vat += v.VATAMOUNT; }
            });
            $("#donationtotal").html(format.currency(tot) + " / " + format.currency(due));
            $("#vattotal").html(format.currency(vat));
        },

        render: function() {
            var s = "";
            this.model();
            s += tableform.dialog_render(this.dialog);
            s += '<div id="button-document-body" class="asm-menu-body">' +
                '<ul class="asm-menu-list">' +
                edit_header.template_list(controller.templates, "DONATION", 0) +
                '</ul></div>';
            if (controller.name == "animal_donations") {
                s += edit_header.animal_edit_header(controller.animal, "donations", controller.tabcounts);
            }
            else if (controller.name == "person_donations") {
                s += edit_header.person_edit_header(controller.person, "donations", controller.tabcounts);
            }
            else {
                s += html.content_header(this.title());
            }
            s += tableform.buttons_render(this.buttons);
            s += tableform.table_render(this.table);
            s += '<div class="ui-state-highlight ui-corner-all" style="margin-top: 20px; padding: 0 .7em">';
            s += '<p><span class="ui-icon ui-icon-info" style="float: left; margin-right: .3em;"></span>';
            s += _("Total payments") + ': <span class="strong" id="donationtotal"></span> ';
            if (config.bool("VATEnabled")) {
                s += _("Sales Tax") + ': <span class="strong" id="vattotal"></span> ';
            }
            s += '</p></div>';
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
            if (asm.locale != "en_GB") {
                $("#giftaid").closest("tr").hide();
            }

            $("#movement").closest("tr").hide();

            $("#animal").animalchooser().bind("animalchooserchange", function(event, rec) {
                donations.lastanimal = rec;
            });

            $("#animal").animalchooser().bind("animalchooserloaded", function(event, rec) {
                donations.lastanimal = rec;
            });

            $("#person").personchooser().bind("personchooserchange", function(event, rec) {
                donations.lastperson = rec;
                donations.update_movements(rec.ID);
                $("#giftaid").prop("checked", rec.ISGIFTAID == 1);
            });

            $("#person").personchooser().bind("personchooserloaded", function(event, rec) {
                donations.lastperson = rec;
                if (donations.create_semaphore) {
                    $("#giftaid").prop("checked", rec.ISGIFTAID == 1);
                }
            });

            $("#type").change(function() {
                donations.type_change();
            });

            $("#quantity, #unitprice").blur(function() {
                $("#amount").currency("value", format.to_int($("#quantity").val()) * $("#unitprice").currency("value"));
            });

            $("#vat").change(function() {
                if ($(this).is(":checked")) {
                    $("#vatrate").val(config.number("VATRate"));
                    $("#vatamount").currency("value", ($("#amount").currency("value") / 100) * config.number("VATRate"));
                    $("#vatrate").closest("tr").fadeIn();
                    $("#vatamount").closest("tr").fadeIn();
                }
                else {
                    $("#vatamount").currency("value", "0");
                    $("#vatrate").val("0"); 
                    $("#vatrate").closest("tr").fadeOut();
                    $("#vatamount").closest("tr").fadeOut();
                }
            });

            // Add click handlers to templates
            $(".templatelink").click(function() {
                // Update the href as it is clicked so default browser behaviour
                // continues on to open the link in a new window
                var template_name = $(this).attr("data");
                var ids = tableform.table_ids(donations.table);
                $(this).prop("href", "document_gen?linktype=DONATION&id=" + ids + "&dtid=" + template_name);
            });
        },

        sync: function() {

            this.calculate_total();

            // If an offset is given in the querystring, update the select
            if (common.querystring_param("offset")) {
                $("#offset").select("value", common.querystring_param("offset"));
            }

        },

        destroy: function() {
            common.widget_destroy("#animal");
            common.widget_destroy("#person");
            tableform.dialog_destroy();
            this.create_semaphore = false;
            this.lastanimal = null;
            this.lastperson = null;
            this.dialog_row = null;
        },

        name: "donations",
        animation: function() { return controller.name == "donation" ? "book" : "formtab"; },

        title:  function() { 
            var t = "";
            if (controller.name == "animal_donations") {
                t = common.substitute(_("{0} - {1} ({2} {3} aged {4})"), { 
                    0: controller.animal.ANIMALNAME, 1: controller.animal.CODE, 2: controller.animal.SEXNAME,
                    3: controller.animal.SPECIESNAME, 4: controller.animal.ANIMALAGE }); 
            }
            else if (controller.name == "person_donations") { t = controller.person.OWNERNAME; }
            else if (controller.name == "donation") { t = _("Payment Book"); }
            return t;
        },

        routes: {
            "animal_donations": function() { common.module_loadandstart("donations", "animal_donations?id=" + this.qs.id); },
            "person_donations": function() { common.module_loadandstart("donations", "person_donations?id=" + this.qs.id); },
            "donation": function() { common.module_loadandstart("donations", "donation?" + this.rawqs); }
        }


    };

    common.module_register(donations);

});
