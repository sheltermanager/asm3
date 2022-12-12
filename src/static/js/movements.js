/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, edit_header, header, html, tableform, validate */

$(function() {

    "use strict";

    const movements = {

        lastanimal: null,
        lastperson: null,
        lastretailer: null,

        model: function() {
            // Filter list of chooseable types
            let choosetypes = [];
            $.each(controller.movementtypes, function(i, v) {
                if (v.ID == 0) {
                    v.MOVEMENTTYPE = _("Reservation");
                    choosetypes.push(v);
                }
                else if (v.ID == 8 && !config.bool("DisableRetailer")) {
                    choosetypes.push(v);
                }
                else if (v.ID < 8 || v.ID > 13) {
                    choosetypes.push(v);
                }
            });

            const dialog = {
                add_title: _("Add movement"),
                edit_title: _("Edit movement"),
                edit_perm: 'camv',
                close_on_ok: false,
                autofocus: false,
                columns: 2,
                fields: [
                    { json_field: "ANIMALID", post_field: "animal", label: _("Animal"), type: "animal" },
                    { json_field: "OWNERID", post_field: "person", label: _("Person"), type: "person" },
                    { json_field: "RETAILERID", post_field: "retailer", label: _("Retailer"), type: "person", personfilter: "retailer", hideif: function() { return config.bool("DisableRetailer"); } },
                    { json_field: "ADOPTIONNUMBER", post_field: "adoptionno", label: _("Movement Number"), tooltip: _("A unique number to identify this movement"), type: "text" },
                    { json_field: "INSURANCENUMBER", post_field: "insurance", label: _("Insurance"), tooltip: _("If the shelter provides initial insurance cover to new adopters, the policy number"), type: "text" },
                    { json_field: "RESERVATIONDATE", post_field: "reservation", label: _("Reservation Date"), tooltip: _("The date this animal was reserved"), type: "datetime" },
                    { json_field: "RESERVATIONSTATUSID", post_field: "reservationstatus", label: _("Reservation Status"), type: "select", options: { displayfield: "STATUSNAME", valuefield: "ID", rows: controller.reservationstatuses }},
                    { json_field: "RESERVATIONCANCELLEDDATE", post_field: "reservationcancelled", label: _("Reservation Cancelled"), type: "date" },
                    { type: "nextcol" },
                    { json_field: "MOVEMENTTYPE", post_field: "type", label: _("Movement Type"), type: "select", options: { displayfield: "MOVEMENTTYPE", valuefield: "ID", rows: choosetypes }},
                    { json_field: "MOVEMENTDATE", post_field: "movementdate", label: _("Movement Date"), type: "date" },
                    { json_field: "ISPERMANENTFOSTER", post_field: "permanentfoster", label: _("Permanent Foster"), tooltip: _("Is this a permanent foster?"), type: "check" },
                    { json_field: "ISTRIAL", post_field: "trial", label: _("Trial Adoption"), tooltip: _("Is this a trial adoption?"), type: "check" },
                    { json_field: "TRIALENDDATE", post_field: "trialenddate", label: _("Trial ends on"), tooltip: _("The date the trial adoption is over"), type: "date" },
                    { json_field: "COMMENTS", post_field: "comments", label: _("Comments"), type: "textarea" },
                    { json_field: "EVENTLINK", post_field: "eventlink", label: _("Link to event"), type: "check", hideif: function(){return !common.has_permission("lem");}},
                    { json_field: "EVENTID", post_field: "event", label: _(""), type: "select"},
                    { json_field: "RETURNDATE", post_field: "returndate", label: _("Return Date"), type: "date" },
                    { json_field: "RETURNEDREASONID", post_field: "returncategory", label: _("Return Category"), type: "select", options: { displayfield: "REASONNAME", valuefield: "ID", rows: controller.returncategories}},
                    { json_field: "RETURNEDBYOWNERID", post_field: "returnedby", label: _("Returned By"), type: "person" },
                    { json_field: "REASONFORRETURN", post_field: "reason", label: _("Reason"), type: "textarea" }
                ]
            };

            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: function(row) {
                    tableform.dialog_show_edit(dialog, row, {
                        onvalidate: function() {
                            return movements.validation();
                        },
                        onchange: function() {
                            tableform.fields_update_row(dialog.fields, row);
                            movements.set_extra_fields(row);
                            tableform.fields_post(dialog.fields, "mode=update&movementid=" + row.ID, "movement")
                                .then(function(response) {
                                    tableform.table_update(table);
                                    tableform.dialog_close();
                                })
                                .fail(function() {
                                    tableform.dialog_enable_buttons();
                                });
                        },
                        onload: function() {
                            tableform.fields_populate_from_json(dialog.fields, row);
                            movements.type_change(); 
                            movements.returndate_change();
                        }
                    });
                },
                overdue: function(row) {
                    // If this is the reservation book, overdue is determined by reservation being 
                    // older than a pre-set period (default 1 week)
                    if (controller.name == "move_book_reservation" && row.RESERVATIONDATE) {
                        let od = format.date_js(row.RESERVATIONDATE), odd = config.integer("ReservesOverdueDays");
                        if (!odd) { odd = 7; }
                        od.setDate(od.getDate() + odd);
                        return od < common.today_no_time();
                    }
                    return false;
                },
                complete: function(row) {
                    // If this is the trial book, completion is determined by trial end date passing or the flag being removed
                    if (controller.name == "move_book_trial_adoption"){
                        if (row.ISTRIAL == 1 && row.TRIALENDDATE && format.date_js(row.TRIALENDDATE) <= new Date()) {
                            return true;
                        }
                        if (row.ISTRIAL == 0) {
                            return true;
                        }
                    }
                    // If this is a cancelled reservation
                    if (row.MOVEMENTTYPE == 0 && row.RESERVATIONCANCELLEDDATE && format.date_js(row.RESERVATIONCANCELLEDDATE) <= new Date()) {
                        return true;
                    }
                    // If the movement is returned and not in the future
                    if (row.MOVEMENTTYPE > 0 && row.RETURNDATE && format.date_js(row.RETURNDATE) <= new Date()) {
                        return true;
                    }
                    // If the animal is deceased
                    if (row.DECEASEDDATE) {
                        return true;
                    }
                },
                button_click: function() {
                    if ($(this).attr("data-link")) {
                        window.open($(this).attr("data-link"));
                    }
                    else if ($(this).attr("data-animalid")) {
                        let animalid = $(this).attr("data-animalid");
                        $("[data-animalid='" + animalid + "']").each(function() {
                            if ($(this).is(":visible")) {
                                $(this).closest("tr").find("input[type='checkbox']").prop("checked", true);
                                $(this).closest("tr").addClass("ui-state-highlight");
                            }
                        });
                        tableform.table_update_buttons(table, buttons);
                    }
                },
                columns: [
                    { field: "MOVEMENTNAME", display: _("Type") }, 
                    { field: "MOVEMENTDATE", display: _("Date"), 
                        initialsort: controller.name != "move_book_trial_adoption", 
                        initialsortdirection: "desc", 
                        formatter: function(row, v) { 
                            // If we're only a reservation, use the reserve date instead
                            if (row.MOVEMENTTYPE == 0) {
                                // If the reserve date has its own time, use that
                                if (format.time(row.RESERVATIONDATE) != "") {
                                    return format.date(row.RESERVATIONDATE) + " " + format.time(row.RESERVATIONDATE);
                                }
                                // Otherwise, include no time
                                return format.date(row.RESERVATIONDATE);
                            }
                            return format.date(row.MOVEMENTDATE);
                        }
                    },
                    { field: "RETURNDATE", display: _("Returning"), formatter: tableform.format_date, 
                        hideif: function(row) {
                            // This is for future returns, so only show on retailer/foster book
                            return controller.name != "move_book_foster" && controller.name != "move_book_retailer";
                        }
                    },
                    { field: "RESERVATIONSTATUSNAME", display: _("Status"),
                        hideif: function(row) {
                            // Don't show this column if we aren't in the reservation book or animal/person
                            return controller.name != "move_book_reservation" && !controller.animal && !controller.person;
                        },
                        formatter: function(row, v) {
                            // Only show anything for reservation
                            if (row.MOVEMENTTYPE == 0) { return row.RESERVATIONSTATUSNAME; }
                            return "";
                        }
                    },
                    { field: "ADOPTIONCOORDINATORNAME", display: _("Coordinator"),
                        hideif: function(row) {
                            // Don't show if adoption coordinators aren't on
                            if (config.bool("DontShowAdoptionCoordinator")) { return true; }
                            // Don't show this column if we aren't reservation, foster or trial adoption book
                            return controller.name != "move_book_reservation" && controller.name != "move_book_trial_adoption" && controller.name != "move_book_foster";
                        },
                        formatter: function(row, v) {
                            return html.person_link(row.ADOPTIONCOORDINATORID, row.ADOPTIONCOORDINATORNAME);
                        }
                    },
                    { field: "RETURNDATE", display: _("Returned"), 
                        formatter: function(row) {
                            let rv = format.date(row.RETURNDATE);
                            if (row.RETURNDATE && (row.MOVEMENTTYPE == 1 || row.MOVEMENTTYPE == 5)) {
                                rv += " <br/>" + row.RETURNEDREASONNAME;
                            }
                            return rv;
                        },
                        hideif: function(row) {
                            // Don't show this column if we are the trial adoption, reservation or foster book
                             return controller.name == "move_book_trial_adoption" || 
                                controller.name == "move_book_reservation" || 
                                controller.name == "move_book_foster";
                        }
                    },
                    { field: "TRIALENDDATE", 
                        display: controller.name == "move_book_trial_adoption" ? _("Trial ends on") : _("Soft release ends on"), 
                        formatter: tableform.format_date,
                        initialsort: controller.name == "move_book_trial_adoption" || controller.name == "move_book_soft_release",
                        initialsortdirection: "desc",
                        hideif: function(row) {
                            // Don't show this column if we aren't in the trial adoption book or soft release book
                            return controller.name != "move_book_trial_adoption" && controller.name != "move_book_soft_release";
                        }
                    },
                    { field: "SPECIESNAME", display: _("Species"), 
                        hideif: function(row) {
                            // Don't show this column for animal movements since species is in the banner
                            return controller.name == "animal_movements";
                        }
                    },
                    { field: "BREEDNAME", display: _("Breed"), 
                        hideif: function(row) {
                            // Only show this column for foster and reservation books
                            return controller.name != "move_book_foster" && controller.name != "move_book_reservation";
                        }
                    },
                    { field: "IMAGE", display: "", 
                        formatter: function(row) {
                            if (!row.ANIMALNAME) { return ""; }
                            return html.animal_link_thumb_bare(row);
                        },
                        hideif: function(row) {
                            // Don't show this column if we aren't a book, or the option is turned off
                            if (controller.name.indexOf("book") == -1 || !config.bool("PicturesInBooks")) {
                                return true;
                            }
                        }
                    },
                    { field: "ANIMAL", display: _("Animal"), 
                        formatter: function(row) {
                            if (!row.ANIMALNAME) { return ""; }
                            let s = html.animal_link(row);
                            if (controller.name == "move_book_reservation") {
                                s += '<button data-icon="check" data-text="false" data-animalid="' + row.ANIMALID + '">' +
                                    _("Select all reservations for this animal") + '</button>';
                            }
                            return s;
                        },
                        hideif: function(row) {
                            // Don't show this column for animal_movement
                            return controller.name == "animal_movements";
                        }
                    },
                    { field: "PERSON", display: _("Person"),
                        formatter: function(row) {
                            if (!row.OWNERID) { return ""; }
                            let s = "";
                            if (controller.name == "move_book_reservation") {
                                s += '<button style="float: right" data-asmicon="media" data-text="false" data-link="person_media?id=' + row.OWNERID + '">' +
                                    _("View media for this person") + '</button>';
                            }
                            s += html.person_link_address(row);
                            return s;
                        },
                        hideif: function(row) {
                            return controller.name == "move_book_retailer" || controller.name == "person_movements";
                        }
                    },
                    { field: "RETAILER", display: _("Retailer"),
                        formatter: function(row) {
                            if (controller.name == "move_book_retailer") {
                                return html.person_link(row.OWNERID, row.OWNERNAME);
                            }
                            if (row.RETAILERID) {
                                return html.person_link(row.RETAILERID, row.RETAILERNAME);
                            }
                            return "";
                        },
                        hideif: function(row) {
                            // Hide if retailer stuff is off or we're in a book that shouldn't show it
                            return config.bool("DisableRetailer") || controller.name == "move_book_foster" || controller.name == "move_book_reservation";
                        }
                    },
                    { field: "ANIMALAGE", display: _("Age"),
                        hideif: function(row) { 
                            // Only show age in the adopted/unneutered and foster books
                            return controller.name != "move_book_unneutered" && controller.name != "move_book_foster" ; 
                        },
                        sorttext: function(row) {
                            return row.DATEOFBIRTH;
                        }
                    },
                    { field: "ADOPTIONNUMBER", display: _("Movement Number"),
                        hideif: function(row) {
                            // Don't show movement numbers for foster or reservation book
                            return controller.name == "move_book_foster" || controller.name == "move_book_reservation";
                        }
                    },
                    { field: "COMMENTS", display: _("Comments"), 
                        formatter: function(row, v) { return tableform.format_comments(row, row.COMMENTS + " " + row.REASONFORRETURN); }
                    }
                ]
            };

            const buttons = [
                { id: "new", text: _("New Movement"), icon: "new", enabled: "always", perm: "aamv", 
                     click: function() { 
                        tableform.dialog_show_add(dialog, {
                            onvalidate: function() {
                                return movements.validation();
                            },
                            onadd: function() {
                                tableform.fields_post(dialog.fields, "mode=create", "movement")
                                    .then(function(response) {
                                        let row = {};
                                        row.ID = response;
                                        tableform.fields_update_row(dialog.fields, row);
                                        movements.set_extra_fields(row);
                                        row.ADOPTIONNUMBER = format.padleft(response, 6);
                                        controller.rows.push(row);
                                        tableform.table_update(table);
                                        tableform.dialog_close();
                                    })
                                    .fail(function() {
                                        tableform.dialog_enable_buttons();   
                                    });
                            },
                            onload: function() {
                                // Setup the dialog for a new record
                                $("#animal").animalchooser("clear");
                                $("#person").personchooser("clear");
                                $("#retailer").personchooser("clear");
                                $("#returnedby").personchooser("clear");
                                if (controller.animal) {
                                    $("#animal").animalchooser("loadbyid", controller.animal.ID);
                                }
                                if (controller.person) {
                                    $("#person").personchooser("loadbyid", controller.person.ID);
                                }
                                $("#type").select("value", "0");
                                $("#returncategory").select("value", config.str("AFDefaultReturnReason"));
                                $("#reservationstatus").select("value", config.str("AFDefaultReservationStatus"));
                                $("#reservationtime").val("00:00:00");
                                $("#adoptionno").closest("tr").hide();

                                // Choose an appropriate default type based on our controller
                                if (controller.name == "move_book_foster") { $("#type").select("value", "2"); }
                                if (controller.name == "move_book_recent_adoption") { $("#type").select("value", "1"); }
                                if (controller.name == "move_book_recent_transfer") { $("#type").select("value", "3"); }
                                if (controller.name == "move_book_retailer") { $("#type").select("value", "8"); }
                                if (controller.name == "move_book_soft_release") { 
                                    $("#type").select("value", "7"); 
                                    $("#trial").prop("checked", true);
                                }
                                if (controller.name == "move_book_trial_adoption") { 
                                    $("#type").select("value", "1"); 
                                    $("#trial").prop("checked", true);
                                }
                                // If we're in a book other than the reservation book, set the movement date to today
                                if (controller.name.indexOf("move_book") == 0 && controller.name != "move_book_reservation") {
                                    $("#movementdate").val(format.date(new Date()));
                                }

                                // If we're in the reservation book, create the reserve for today
                                if (controller.name == "move_book_reservation") {
                                    $("#reservationdate").val(format.date(new Date()));
                                }

                                tableform.dialog_error();
                                movements.type_change();
                                $("#returndate").val("");
                                movements.returndate_change();
                            }
                        });
                     } 
                },
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "damv", 
                    click: async function() { 
                        await tableform.delete_dialog();
                        tableform.buttons_default_state(buttons);
                        let ids = tableform.table_ids(table);
                        await common.ajax_post("movement", "mode=delete&ids=" + ids);
                        tableform.table_remove_selected_from_json(table, controller.rows);
                        tableform.table_update(table);
                    } 
                },
                { id: "document", text: _("Document"), icon: "document", enabled: "one", perm: "gaf", 
                    tooltip: _("Generate a document from this movement"), type: "buttonmenu" 
                },
                { id: "toadoption", text: _("To Adoption"), icon: "person", enabled: "one", perm: "camv",
                    tooltip: _("Convert this reservation to an adoption"),
                    hideif: function() {
                        return controller.name.indexOf("reserv") == -1;
                    },
                    click: function() { 
                        let row = tableform.table_selected_row(table);
                        tableform.fields_populate_from_json(dialog.fields, row);
                        movements.type_change(); 
                        movements.returndate_change();
                        tableform.dialog_show_edit(dialog, row, {
                            onvalidate: function() {
                                return movements.validation();
                            },
                            onchange: function() {
                                tableform.fields_update_row(dialog.fields, row);
                                movements.set_extra_fields(row);
                                tableform.fields_post(dialog.fields, "mode=update&movementid=" + row.ID, "movement", function(response) {
                                    tableform.table_update(table);
                                    tableform.dialog_close();
                                },
                                function(response) {
                                    tableform.dialog_error(response);
                                    tableform.dialog_enable_buttons();
                                });
                            },
                            onload: function() {
                                $("#type").select("value", "1");
                                $("#movementdate").val(format.date(new Date()));
                                movements.type_change(); 
                                movements.returndate_change();
                            }
                        });
                    }
                },
                { id: "cancel", text: _("Cancel"), icon: "cross", enabled: "multi", perm: "camv",
                    tooltip: _("Cancel the selected reservations"),
                    hideif: function() { return controller.name != "move_book_reservation"; },
                    click: async function() {
                        await common.ajax_post("movement", "mode=cancelreserve&ids=" + tableform.table_ids(table));
                        $.each(tableform.table_selected_rows(table), function(i, v) {
                            v.RESERVATIONCANCELLEDDATE = format.date_now_iso();
                        });
                        tableform.buttons_default_state(buttons);
                        tableform.table_update(table);
                    }
                },
                { id: "return", text: _("Return"), icon: "complete", enabled: "one", perm: "camv",
                    tooltip: _("Return this movement and bring the animal back to the shelter"),
                    hideif: function() {
                        return controller.name.indexOf("move_book_recent") == -1 && controller.name.indexOf("move_book_foster") == -1;
                    },
                    click: function() {
                        let row = tableform.table_selected_row(table);
                        tableform.fields_populate_from_json(dialog.fields, row);
                        movements.type_change(); 
                        movements.returndate_change();
                        tableform.dialog_show_edit(dialog, row, { 
                            onvalidate: function() {
                                return movements.validation();
                            },
                            onchange: function() {
                                tableform.fields_update_row(dialog.fields, row);
                                movements.set_extra_fields(row);
                                tableform.fields_post(dialog.fields, "mode=update&movementid=" + row.ID, "movement")
                                    .then(function(response) {
                                        tableform.table_update(table);
                                        tableform.dialog_close();
                                    })
                                    .fail(function() {
                                        tableform.dialog_enable_buttons();
                                    });
                            },
                            onload: function() {
                                $("#returndate").val(format.date(new Date()));
                                movements.returndate_change();
                            }
                        });
                    }
                },
                { id: "trialfull", text: _("Full Adoption"), icon: "complete", enabled: "multi", perm: "camv",
                    tooltip: _("Convert this movement from a trial to full adoption"),
                    hideif: function() {
                        return controller.name.indexOf("move_book_trial") == -1;
                    },
                    click: async function() {
                        await common.ajax_post("movement", "mode=trialfull&ids=" + tableform.table_ids(table));
                        $.each(tableform.table_selected_rows(table), function(i, v) {
                            v.ISTRIAL = 0;
                            if (!v.TRIALENDDATE) { v.TRIALENDDATE = format.date_now_iso(); }
                        });
                        tableform.buttons_default_state(buttons);
                        tableform.table_update(table);
                    }
                },
                { id: "email", text: _("Email"), icon: "email", enabled: "multi", perm: "emo",
                    tooltip: _("BCC all the people linked to these movements"),
                    hideif: function() {
                        return controller.name != "move_book_reservation";
                    },
                    click: function() {
                        // Find the first animal id and person id for use with templates,
                        // also build a list of all the personids to send to the back end
                        // so that logging of the email to their record can be done
                        let animalid = 0, personid = 0, personids = [], bccemails = [];
                        $.each(tableform.table_selected_rows(table), function(i, row) {
                            if (!animalid) { animalid = row.ANIMALID; }
                            if (!personid) { personid = row.OWNERID; }
                            personids.push(row.OWNERID);
                            bccemails.push(row.EMAILADDRESS);
                        });
                        $("#emailform").emailform("show", {
                            title: _("Email people linked to selected movements"),
                            post: "movement",
                            formdata: "mode=email&personids=" + personids.join(","),
                            name: "",
                            email: config.str("EmailAddress"),
                            bccemail: bccemails.join(", "),
                            subject: "",
                            animalid: animalid,
                            personid: personid,
                            templates: controller.templates,
                            logtypes: controller.logtypes,
                            message: ""
                        });
                    }
                },
                { id: "checkout", text: _("Adopter Checkout"), icon: "email", enabled: "one", perm: "emo",
                    tooltip: _("Send a checkout email to the adopter"),
                    hideif: function() {
                        return controller.name.indexOf("move_book_foster") != -1 ||
                            controller.name.indexOf("move_book_soft_release") != -1 ||
                            controller.name.indexOf("move_book_recent_other") != -1 ||
                            config.str("AdoptionCheckoutProcessor") == "";
                    },
                    click: function() {
                        let row = tableform.table_selected_row(table);
                        if (row.MOVEMENTTYPE > 1) { 
                            header.show_error(_("Adopter checkout only applies to reservation and adoption movements."));
                            return;
                        }
                        if (!row.FEE) {
                            header.show_error(_("No adoption fee has been set for this animal."));
                            return;
                        }
                        $("#emailform").emailform("show", {
                            title: _("Email link to adopter checkout"),
                            post: "movement",
                            formdata: "mode=checkout&id=" + row.ID + "&animalid=" + row.ANIMALID + "&personid=" + row.OWNERID,
                            name: row.OWNERNAME,
                            email: row.EMAILADDRESS,
                            subject: _("Adoption checkout for {0}").replace("{0}", row.ANIMALNAME),
                            animalid: row.ANIMALID,
                            personid: row.OWNERID,
                            templates: controller.templates,
                            logtypes: controller.logtypes,
                            message: _("Please use the link below to sign adoption paperwork and pay the adoption fee.")
                        });
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
            s += '<div id="button-document-body" class="asm-menu-body">' +
                '<ul class="asm-menu-list">' +
                edit_header.template_list(controller.templates, "MOVEMENT", 0) +
                '</ul></div>' + 
                '<div id="emailform"></div>';
            if (controller.name == "animal_movements") {
                s += edit_header.animal_edit_header(controller.animal, "movements", controller.tabcounts);
            }
            else if (controller.name == "person_movements") {
                s += edit_header.person_edit_header(controller.person, "movements", controller.tabcounts);
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
             //callback when eventlink changed its status
             $("#eventlink").change(function(){
                // event link needs a movement date
                if (this.checked && $("#movementdate").val() == ""){
                    validate.notblank([ "movementdate" ]);
                    tableform.dialog_error(_("Fill out adoption date before linking to event."));
                    this.checked = false;
                }
                $("#event").empty();
                if (this.checked){
                    $("#event").closest("tr").fadeIn();
                    movements.event_dates();
                }
                else
                    $("#event").closest("tr").fadeOut();

            });
            //callback when movementdate is changed
            $("#movementdate").change(function(){
                $("#event").empty();
                // event link needs a movement date
                if ($("#movementdate").val() == ""){
                    validate.notblank([ "movementdate" ]);
                    tableform.dialog_error(_("Fill out adoption date before linking to event."));
                    $("#eventlink")[0].checked = false;
                }
                if($("#eventlink")[0].checked){
                    movements.event_dates();
                }

            });

            if (controller.name == "animal_movements" || controller.name == "person_movements") {
                $(".asm-tabbar").asmtabs();
            }
            
            $("#emailform").emailform();

            tableform.dialog_bind(this.dialog);
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);

            // Watch for movement type changing
            $("#type").change(movements.type_change);

            // Watch for return date changing
            $("#returndate").change(movements.returndate_change);

            // When we choose a person or animal
            $("#person").personchooser().bind("personchooserchange", function(event, rec) { movements.lastperson = rec; movements.warnings(); });
            $("#person").personchooser().bind("personchooserloaded", function(event, rec) { movements.lastperson = rec; movements.warnings(); });
            $("#person").personchooser().bind("personchooserclear", function(event, rec) { movements.warnings(); });
            $("#animal").animalchooser().bind("animalchooserchange", function(event, rec) { 
                movements.lastanimal = rec; movements.warnings(); movements.set_release_name(rec.SPECIESID); 
            });
            $("#animal").animalchooser().bind("animalchooserloaded", function(event, rec) { 
                movements.lastanimal = rec; movements.warnings(); movements.set_release_name(rec.SPECIESID); 
            });
            $("#retailer").personchooser().bind("personchooserchange", function(event, rec) { movements.lastretailer = rec; movements.warnings(); });
            $("#retailer").personchooser().bind("personchooserloaded", function(event, rec) { movements.lastretailer = rec; movements.warnings(); });

            // Insurance button
            $("#insurance").after('<button id="button-insurance">' + _("Issue a new insurance number for this animal/adoption") + '</button>');
            $("#button-insurance")
                .button({ icons: { primary: "ui-icon-cart" }, text: false })
                .click(function() {
                    common.ajax_post("movement", "mode=insurance")
                        .then(function(result) { 
                            $("#insurance").val(result); 
                        })
                        .fail(function(err) {
                            tableform.dialog_error(err); 
                        });
            });
            if (!config.bool("UseAutoInsurance")) { $("#button-insurance").button("disable"); }

            if (config.bool("DontShowInsurance")) {
                $("#insurance").closest("tr").hide();
            }

            // Add click handlers to templates
            $(".templatelink").click(function() {
                // Update the href as it is clicked so default browser behaviour
                // continues on to open the link in a new window
                let template_name = $(this).attr("data");
                $(this).prop("href", "document_gen?linktype=MOVEMENT&id=" + tableform.table_selected_row(movements.table).ID + "&dtid=" + template_name);
            });

        },

        warnings: function() {
            let p = movements.lastperson, a = movements.lastanimal, warn = [];
            tableform.dialog_error("");

            // None of these warnings are valid if this isn't a reservation, adoption or a reclaim
            if ($("#type").val() != 0 && $("#type").val() != 1 && $("#type").val() != 5) { return; }

            // Animal warnings
            if (a) {

                // If the animal is marked not for adoption
                if (a.ISNOTAVAILABLEFORADOPTION == 1) {
                    warn.push(_("This animal is marked not for adoption."));
                }

                // If the animal is held, we shouldn't be allowed to adopt it
                if (a.ISHOLD == 1) {
                    warn.push(_("This animal is currently held and cannot be adopted."));
                }

                // Cruelty case
                if (a.CRUELTYCASE == 1) {
                    warn.push(_("This animal is part of a cruelty case and should not leave the shelter."));
                }

                // Outstanding medical
                if (config.bool("WarnOSMedical") && a.HASOUTSTANDINGMEDICAL == 1) {
                    warn.push(_("This animal has outstanding medical treatments."));
                }

                // Quarantined
                if (a.ISQUARANTINE == 1) {
                    warn.push(_("This animal is currently quarantined and should not leave the shelter."));
                }

                // Unaltered
                if (config.bool("WarnUnaltered") && a.NEUTERED == 0) {
                    warn.push(_("This animal has not been altered."));
                }

                // Not microchipped
                if (config.bool("WarnNoMicrochip") && a.IDENTICHIPPED == 0) {
                    warn.push(_("This animal has not been microchipped."));
                }

                // Check for bonded animals and warn
                if (a.BONDEDANIMALID || a.BONDEDANIMAL2ID) {
                    let bw = "";
                    if (a.BONDEDANIMAL1NAME) {
                        bw += a.BONDEDANIMAL1CODE + " - " + a.BONDEDANIMAL1NAME;
                    }
                    if (a.BONDEDANIMAL2NAME) {
                        if (bw != "") { bw += ", "; }
                        bw += a.BONDEDANIMAL2CODE + " - " + a.BONDEDANIMAL2NAME;
                    }
                    if (bw != "") {
                        warn.push(_("This animal is bonded with {0}").replace("{0}", bw));
                    }
                }

            }

            // If we don't have a person yet, just show any animal warnings and finish
            if (!p) { 
                if (warn.length > 0) { tableform.dialog_error(warn.join("<br/>")); }
                return;
            }

            // To handle person warnings, we need to go back to the server to get
            // extra info on that person (incidents, surrenders, etc)
            edit_header.person_with_adoption_warnings(p.ID).then(function(data) {
                p = jQuery.parseJSON(data)[0];

                // Is this owner banned?
                if (p.ISBANNED == 1 && config.bool("WarnBannedOwner")) {
                    warn.push(_("This person has been banned from adopting animals.")); 
                }

                // Owner previously under investigation
                if (p.INVESTIGATION > 0) {
                    warn.push(_("This person has been under investigation."));
                }

                // Owner part of animal control incident
                if (p.INCIDENT > 0) {
                    warn.push(_("This person has an animal control incident against them."));
                }

                // Owner previously surrendered?
                if (p.SURRENDER > 0 && config.bool("WarnBroughtIn")) {
                    warn.push(_("This person has previously surrendered an animal."));
                }

                // Person at this address previously banned?
                if (p.BANNEDADDRESS > 0 && config.bool("WarnBannedAddress")) {
                    warn.push(_("This person lives at the same address as someone who was previously banned."));
                }

                // Does this owner live in the same postcode area as the animal's
                // original owner?
                if ( format.postcode_prefix($(".animalchooser-oopostcode").val()) == format.postcode_prefix(p.OWNERPOSTCODE) ||
                     format.postcode_prefix($(".animalchooser-bipostcode").val()) == format.postcode_prefix(p.OWNERPOSTCODE) ) {
                    if (config.bool("WarnOOPostcode")) { 
                        warn.push(_("This person lives in the same area as the person who brought the animal to the shelter.")); 
                    }
                }

                // Is this owner not homechecked?
                if (p.IDCHECK == 0) {
                    if (config.bool("WarnNoHomeCheck")) { 
                        warn.push(_("This person has not passed a homecheck."));
                    }
                }

                if (warn.length > 0) {
                    tableform.dialog_error(warn.join("<br/>"));
                }

            });
        },

        validation: function() {

            validate.reset("dialog-tableform");
            let mt = $("#type").val();

            // Movement needs a reservation date or movement type > 0
            if (mt == 0 && $("#reservationdate").val() == "") {
                validate.notblank([ "reservationdate" ]);
                tableform.dialog_error(_("A movement must have a reservation date or type."));
                return false;
            }

            // Movement needs a movement date if movement type != 0
            if ($("#type").val() != 0 && $("#movementdate").val() == "") {
                validate.notblank([ "movementdate" ]);
                tableform.dialog_error(_("This type of movement requires a date."));
                return false;
            }

            // Movement types 4 (escaped), 6 (stolen), 7 (released to wild)
            // don't need a person, but all other movements do
            if ($("#person").val() == "") {
                if (mt != 4 && mt != 6 && mt != 7) {
                    tableform.dialog_error(_("This type of movement requires a person."));
                    validate.highlight("person");
                    return false;
                }
            }

            // All movements require an animal
            if ($("#animal").val() == "0") {
                // Except reservations if the option is on
                if (mt != 0 || !config.bool("MovementPersonOnlyReserves")) {
                    tableform.dialog_error(_("Movements require an animal"));
                    validate.highlight("animal");
                    return false;
                }
            }

            return true;
        },

        /**
         * Sets extra json fields according to what the user has picked. Call
         * this after updating a json row for entered fields to get the
         * extra lookup fields.
         */
        set_extra_fields: function(row) {
            if (movements.lastanimal) {
                row.ANIMALNAME = movements.lastanimal.ANIMALNAME;
                row.SHELTERCODE = movements.lastanimal.SHELTERCODE;
                row.AGEGROUP = movements.lastanimal.AGEGROUP;
                row.SEX = movements.lastanimal.SEXNAME;
                row.SPECIESNAME = movements.lastanimal.SPECIESNAME;
            }
            if (movements.lastperson) {
                row.OWNERNAME = movements.lastperson.OWNERNAME;
                row.OWNERADDRESS = movements.lastperson.OWNERADDRESS;
                row.HOMETELEPHONE = movements.lastperson.HOMETELEPHONE;
                row.WORKTELEPHONE = movements.lastperson.WORKTELEPHONE;
                row.MOBILETELEPHONE = movements.lastperson.MOBILETELEPHONE;
            }
            else {
                row.OWNERNAME = ""; row.OWNERADDRESS = "";
                row.HOMETELEPHONE = ""; row.WORKTELEPHONE = "";
                row.MOBILETELEPHONE = "";
            }
            if (movements.lastretailer) {
                row.RETAILERNAME = movements.lastretailer.OWNERNAME;
            }
            else {
                row.RETAILERNAME = "";
            }
            row.MOVEMENTNAME = common.get_field(controller.movementtypes, row.MOVEMENTTYPE, "MOVEMENTTYPE");
            row.RETURNEDREASONNAME = common.get_field(controller.returncategories, row.RETURNEDREASONID, "REASONNAME");
            row.RESERVATIONSTATUSNAME = common.get_field(controller.reservationstatuses, row.RESERVATIONSTATUSID, "STATUSNAME");
            if (row.RESERVATIONDATE != null && !row.RESERVATIONCANCELLEDDATE && !row.MOVEMENTDATE) { row.MOVEMENTNAME = common.get_field(controller.movementtypes, 9, "MOVEMENTTYPE"); }
            if (row.RESERVATIONDATE != null && row.RESERVATIONCANCELLEDDATE && format.date_js(row.RESERVATIONCANCELLEDDATE) <= new Date() && !row.MOVEMENTDATE) { row.MOVEMENTNAME = common.get_field(controller.movementtypes, 10, "MOVEMENTTYPE"); }
            if (row.MOVEMENTTYPE == 1 && row.ISTRIAL == 1) { row.MOVEMENTNAME = common.get_field(controller.movementtypes, 11, "MOVEMENTTYPE"); }
            if (row.MOVEMENTTYPE == 2 && row.ISPERMANENTFOSTER == 1) { row.MOVEMENTNAME = common.get_field(controller.movementtypes, 12, "MOVEMENTTYPE"); }
            if (row.MOVEMENTTYPE == 7 && movements.lastanimal && movements.lastanimal.SPECIESID == 2) { row.MOVEMENTNAME = common.get_field(controller.movementtypes, 13, "MOVEMENTTYPE"); }
        },

        /** When the animal changes, set the name of the "Release to Wild" movement 
         *  to "TNR" instead if the species we've been given is a cat.
         */
        set_release_name: function(speciesid) {
            if (speciesid == 2) {
                $("#type option[value='7']").html(_("TNR"));
            }
            else {
                $("#type option[value='7']").html(_("Released To Wild"));
            }
        },

        /** Fires whenever the movement type box is changed */
        type_change: function() {
            let mt = $("#type").val();
            // Show trial fields if option is set and the movement is an adoption
            if (config.bool("TrialAdoptions") && mt == 1) {
                $("#trial").closest("tr").find("label").html(_("Trial"));
                $("#trialenddate").closest("tr").find("label").html(_("Trial ends on"));
                $("#trial").closest("tr").fadeIn();
                $("#trialenddate").closest("tr").fadeIn();
            }
            // Show soft release fields if option is set and the movement is a release
            else if (config.bool("SoftReleases") && mt == 7) {
                $("#trial").closest("tr").find("label").html(_("Soft release"));
                $("#trialenddate").closest("tr").find("label").html(_("Soft release ends on"));
                $("#trial").closest("tr").fadeIn();
                $("#trialenddate").closest("tr").fadeIn();
            }
            else {
                $("#trial").closest("tr").hide();
                $("#trialenddate").closest("tr").hide();
            }
            // Show permanent field if the movement is a foster
            if (mt == 2) {
                $("#permanentfoster").closest("tr").fadeIn();
            }
            else {
                $("#permanentfoster").closest("tr").hide();
            }
            // If the movement isn't an adoption, hide the retailer row
            if (mt == 1 && !config.bool("DisableRetailer")) {
                $("#retailer").closest("tr").fadeIn();
            }
            else {
                $("#retailer").closest("tr").hide();
            }
            // Show the insurance row for adoptions
            if (mt == 1 && !config.bool("DontShowInsurance")) {
                $("#insurance").closest("tr").fadeIn();
            }
            else {
                $("#insurance").closest("tr").fadeOut();
            }
            // Show the reservation date field for both reserves and adoptions
            if (mt == 1 || mt == 0) {
                $("#reservationdate").closest("tr").fadeIn();
            }
            else {
                $("#reservationdate").closest("tr").fadeOut();
            }
            // Show the other reservation fields for reserves
            if (mt == 0) {
                $("#reservationstatus").closest("tr").fadeIn();
                $("#reservationcancelled").closest("tr").fadeIn();
                $("#movementdate").closest("tr").fadeOut();
                $("#returndate").closest("tr").fadeOut();
            }
            else {
                $("#reservationstatus").closest("tr").fadeOut();
                $("#reservationcancelled").closest("tr").fadeOut();
                $("#movementdate").closest("tr").fadeIn();
                $("#returndate").closest("tr").fadeIn();
            }
            // If the movement is one that doesn't require a person, hide the person row
            if (mt == 4 || mt == 6) {
                $("#person").closest("tr").fadeOut();
            }
            else {
                $("#person").closest("tr").fadeIn();
            }
            //show event link only when movement type is adoption
            if (mt == 1){
                $("#eventlink").closest("tr").fadeIn();
            }
            else{
                $("#eventlink").closest("tr").fadeOut();
            }
            //show event selection if eventlink is checked
            if (mt == 1 && $("#eventlink").is(":checked")){
                $("#event").closest("tr").fadeIn();
            }
            else{
                $("#event").closest("tr").fadeOut();
            }
            movements.warnings();
        },

        /** Fires when the return date is changed */
        returndate_change: function() {
            // Show return category/reason for movements that need them 
            // (adoptions and reclaims)
            if ($("#returndate").val() && ( $("#type").val() == 1 || $("#type").val() == 5 )) {
                $("#returncategory").closest("tr").fadeIn();
                $("#reason").closest("tr").fadeIn();
                $("#returnedby").closest("tr").fadeIn();
            }
            else {
                $("#returncategory").closest("tr").fadeOut();
                $("#reason").closest("tr").fadeOut();
                $("#returnedby").closest("tr").fadeOut();
            }
        },

        event_dates: async function(){
            let result = await common.ajax_post("movement", "mode=eventlink&movementdate=" + $("#movementdate").val());
            let dates = jQuery.parseJSON(result);
            $.each(dates, function(i, v){
                $("#event").append("<option value='" + v.ID + "'>" + format.date(v.STARTDATETIME) + " - " + format.date(v.ENDDATETIME) +
                " " + v.EVENTNAME + " " + v.EVENTADDRESS + ", " + v.EVENTTOWN + ", " + v.EVENTCOUNTY + ", " + v.EVENTCOUNTRY + "</option>");
            });
        },

        destroy: function() {
            common.widget_destroy("#animal");
            common.widget_destroy("#person");
            common.widget_destroy("#retailer");
            common.widget_destroy("#emailform");
            tableform.dialog_destroy();
            this.lastanimal = null;
            this.lastperson = null;
            this.lastretailer = null;
        },

        name: "movements",
        animation: function() { return controller.name.indexOf("move_book") == 0 ? "book" : "formtab"; },
        title:  function() {
            let t = "";
            if (controller.name == "animal_movements") {
                t = common.substitute(_("{0} - {1} ({2} {3} aged {4})"), { 
                    0: controller.animal.ANIMALNAME, 1: controller.animal.CODE, 2: controller.animal.SEXNAME,
                    3: controller.animal.SPECIESNAME, 4: controller.animal.ANIMALAGE }); 
            }
            else if (controller.name == "person_movements") { t = controller.person.OWNERNAME; }
            else if (controller.name == "move_book_foster") { t = _("Foster Book"); }
            else if (controller.name == "move_book_recent_adoption") { t = _("Return an animal from adoption"); }
            else if (controller.name == "move_book_recent_other") { t = _("Return an animal from another movement"); }
            else if (controller.name == "move_book_recent_transfer") { t = _("Return an animal from transfer"); }
            else if (controller.name == "move_book_reservation") { t = _("Reservation Book"); }
            else if (controller.name == "move_book_retailer") { t = _("Retailer Book"); }
            else if (controller.name == "move_book_soft_release") { t = _("Soft release book"); }
            else if (controller.name == "move_book_trial_adoption") { t = _("Trial adoption book"); }
            else if (controller.name == "move_book_unneutered") { t = _("Unaltered Adopted Animals"); }
            return t;
        },

        routes: {
            "animal_movements": function() { common.module_loadandstart("movements", "animal_movements?id=" + this.qs.id); },
            "person_movements": function() { common.module_loadandstart("movements", "person_movements?id=" + this.qs.id); },
            "move_book_foster": function() { common.module_loadandstart("movements", "move_book_foster"); },
            "move_book_recent_adoption": function() { common.module_loadandstart("movements", "move_book_recent_adoption"); },
            "move_book_recent_other": function() { common.module_loadandstart("movements", "move_book_recent_other"); },
            "move_book_recent_transfer": function() { common.module_loadandstart("movements", "move_book_recent_transfer"); },
            "move_book_reservation": function() { common.module_loadandstart("movements", "move_book_reservation"); },
            "move_book_retailer": function() { common.module_loadandstart("movements", "move_book_retailer"); },
            "move_book_soft_release": function() { common.module_loadandstart("movements", "move_book_soft_release"); },
            "move_book_trial_adoption": function() { common.module_loadandstart("movements", "move_book_trial_adoption"); },
            "move_book_unneutered": function() { common.module_loadandstart("movements", "move_book_unneutered"); }
        }

    };

    common.module_register(movements);

});
