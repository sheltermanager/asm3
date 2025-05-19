/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const boarding_availability = {

        model: function() {
            const dialog = {
                add_title: _("Add Boarding"),
                edit_title: _("Edit Boarding"),
                helper_text: "",
                close_on_ok: false,
                delete_button: true,
                delete_perm: 'dbi',
                columns: 1,
                width: 550,
                fields: [
                    { json_field: "ANIMALID", post_field: "animal", label: _("Animal"), type: "animal", validation: "notzero" },
                    { json_field: "OWNERID", post_field: "person", label: _("Person"), type: "person", validation: "notzero" },
                    { json_field: "BOARDINGTYPEID", post_field: "type", label: _("Type"), type: "select", 
                        options: { displayfield: "BOARDINGNAME", valuefield: "ID", rows: controller.boardingtypes }},
                    { json_field: "INDATETIME", post_field: "in", label: _("In Date"), type: "datetime", validation: "notblank", defaultval: new Date() },
                    { json_field: "OUTDATETIME", post_field: "out", label: _("Out Date"), type: "datetime", validation: "notblank", defaultval: new Date() },
                    { json_field: "DAILYFEE", post_field: "dailyfee", label: _("Daily Fee"), type: "currency" },
                    { json_field: "SHELTERLOCATION", post_field: "location", label: _("Location"), type: "select", 
                        options: { displayfield: "LOCATIONNAME", valuefield: "ID", rows: controller.internallocations }},
                    { json_field: "SHELTERLOCATIONUNIT", post_field: "unit", label: _("Unit"), type: "select" },
                    { json_field: "COMMENTS", post_field: "comments", label: _("Comments"), type: "textarea" }
                ]
            };
            this.dialog = dialog;
        },

        insert_booking: function(row) {
            let locationid = row.SHELTERLOCATION;
            let tablerow = $(".asm-boarding-unit-row[data-locationid='" + locationid + "'][data-unit='" + row.SHELTERLOCATIONUNIT + "']").first();
            let tablecells = tablerow.find(".asm-boarding-availability-cell");
            $.each(tablecells, function(i, tablecell) {
                let celldate = $(tablecell).attr("data-date");
                celldate = format.date_iso(celldate);
                if (format.date_in_range(celldate, row.INDATETIME, row.OUTDATETIME, true)) {
                    $(tablecell).html($(tablecell).html() + '<div class="asm-boarding-item"><a href=# data-id="' + row.ID + '">' + row.ANIMALNAME + " " + row.OWNERSURNAME + '</a></div>');
                }
            });
            boarding_availability.refresh_meters();
        },

        remove_booking: function(id) {
            $(".asm-boarding-item a[data-id='" + id + "']").closest(".asm-boarding-item").remove();
            boarding_availability.refresh_meters();
        },

        refresh_meters: function() {
            let meters = $(".asm-boarding-location-row meter");
            $.each(meters, function(i, meter) {
                let date = $(meter).closest(".asm-boarding-availability-cell").attr("data-date");
                let locationid = $(meter).closest(".asm-boarding-location-row").attr("data-locationid");
                let unitcells = $(".asm-boarding-unit-row[data-locationid='" + locationid + "'] .asm-boarding-availability-cell[data-date='" + date + "']");
                let occupiedunits = 0;
                $.each(unitcells, function(i, unitcell) {
                    if ($(unitcell).find(".asm-boarding-item").length > 0) {
                        occupiedunits++;
                    }
                });
                $(meter).val(occupiedunits);
            });
        },

        set_extra_fields: function(row) {
            if (controller.animal) {
                row.ANIMALNAME = controller.animal.ANIMALNAME;
                row.SHELTERCODE = controller.animal.SHELTERCODE;
                row.SHORTCODE = controller.animal.SHORTCODE;
                row.WEBSITEMEDIANAME = controller.animal.WEBSITEMEDIANAME;
            }
            else if (boarding_availability.lastanimal) {
                row.ANIMALNAME = boarding_availability.lastanimal.ANIMALNAME;
                row.SHELTERCODE = boarding_availability.lastanimal.SHELTERCODE;
                row.SHORTCODE = boarding_availability.lastanimal.SHORTCODE;
                row.WEBSITEMEDIANAME = boarding_availability.lastanimal.WEBSITEMEDIANAME;
            }
            if (controller.person) {
                row.OWNERCODE = controller.person.OWNERCODE;
                row.OWNERNAME = controller.person.OWNERNAME;
                row.OWNERSURNAME = controller.person.OWNERSURNAME;
                row.OWNERADDRESS = controller.person.OWNERADDRESS;
                row.EMAILADDRESS = controller.person.EMAILADDRESS;
                row.HOMETELEPHONE = controller.person.HOMETELEPHONE;
                row.WORKTELEPHONE = controller.person.WORKTELEPHONE;
                row.MOBILETELEPHONE = controller.person.MOBILETELEPHONE;
            }
            else if (boarding_availability.lastperson) {
                row.OWNERCODE = boarding_availability.lastperson.OWNERCODE;
                row.OWNERNAME = boarding_availability.lastperson.OWNERNAME;
                row.OWNERSURNAME = boarding_availability.lastperson.OWNERSURNAME;
                row.OWNERADDRESS = boarding_availability.lastperson.OWNERADDRESS;
                row.EMAILADDRESS = boarding_availability.lastperson.EMAILADDRESS;
                row.HOMETELEPHONE = boarding_availability.lastperson.HOMETELEPHONE;
                row.WORKTELEPHONE = boarding_availability.lastperson.WORKTELEPHONE;
                row.MOBILETELEPHONE = boarding_availability.lastperson.MOBILETELEPHONE;
            }
            row.BOARDINGTYPENAME = common.get_field(controller.boardingtypes, row.BOARDINGTYPEID, "BOARDINGNAME");
            row.SHELTERLOCATIONNAME = common.get_field(controller.internallocations, row.SHELTERLOCATION, "LOCATIONNAME");
            row.DAYS = format.date_diff_days( $("#indate").datepicker("getDate"), $("#outdate").datepicker("getDate") );
        },

        render: function() {
            this.model();
            return [
                tableform.dialog_render(this.dialog),
                html.content_header(_("Boarding Availability")),
                tableform.buttons_render([
                    { id: "prev", icon: "rotate-anti", tooltip: _("Week beginning {0}").replace("{0}", format.date(controller.prevdate)) },
                    { id: "today", icon: "diary", tooltip: _("This week") },
                    { id: "next", icon: "rotate-clock", tooltip: _("Week beginning {0}").replace("{0}", format.date(controller.nextdate)) }
                ]),
                '<table class="asm-boarding-availability">',
                '<thead></thead>',
                '<tbody></tbody>',
                '</table>',
                html.content_footer()
            ].join("\n");
        },

        sync: function() {
            boarding_availability.generate_table();

            $.each($(".asm-boarding-location-row"), function(i, location) {
                let locationid = $(location).attr("data-locationid");
                $.each($(location).find(".asm-boarding-availability-cell"), function(i, cell) {
                    let date = $(cell).attr("data-date");
                    let bookingcells = $(".asm-boarding-unit-row[data-locationid='" + locationid + "'] .asm-boarding-availability-cell[data-date='" + date + "']");
                    let bookings = 0;
                    $.each(bookingcells, function(i, bookingcell) {
                        if ($(bookingcell).find(".asm-boarding-item").length > 0) {
                            bookings++;
                        }
                    });
                    $(cell).find('meter').val(bookings);
                });
            });

            $(".asm-boarding-location-row").click(function() {
                let locationid = $(this).attr("data-locationid");
                $(".asm-boarding-unit-row[data-locationid='" + locationid + "']").toggle();
            });

            $(".asm-boarding-unit-row .asm-boarding-availability-cell").click(function() {
                let date = $(this).attr("data-date");
                let locationid = $(this).closest(".asm-boarding-unit-row").attr("data-locationid");
                let unit = $(this).closest(".asm-boarding-unit-row").children().first().html().trim();
                boarding_availability.new_boarding(date, locationid, unit);
            });
        },

        new_boarding: function(date, locationid, unit) {
            tableform.dialog_show_add(boarding_availability.dialog, {
                onadd: async function() {
                    try {
                        let response = await tableform.fields_post(boarding_availability.dialog.fields, "mode=create", "boarding");
                        let row = {};
                        row.ID = response;
                        tableform.fields_update_row(boarding_availability.dialog.fields, row);
                        boarding_availability.set_extra_fields(row);
                        controller.rows.push(row);
                        boarding_availability.insert_booking(row);
                        tableform.dialog_close();
                    }
                    catch(err) {
                        log.error(err, err);
                        tableform.dialog_enable_buttons();
                    }
                },
                onload: function() {
                    tableform.dialog_enable_buttons();
                    $("#animal").animalchooser("clear");
                    $("#person").personchooser("clear");
                    $("#indate").val(date);
                    $("#outdate").val(date);
                    $("#intime").val("00:00");
                    $("#outtime").val("00:00");
                    $("#location").val(locationid);
                    boarding_availability.location_change();
                    $("#unit").val(unit);
                    boarding_availability.type_change();
                }
            });
        },

        type_change: function() {
            let dc = common.get_field(controller.boardingtypes, $("#type").select("value"), "DEFAULTCOST");
            $("#dailyfee").currency("value", dc);
        },

        location_change: function() {
            let units = common.get_field(controller.internallocations, $("#location").val(), "UNITS");
            let unitlist = [];
            $.each(units.split(","), function(i, unit) {
                unitlist.push(unit.trim());
            });
            if (units && units.indexOf(",") != -1) {
                $("#unit").html(html.list_to_options(unitlist));
            }
            else {
                $("#unit").html("");
            }
        },

        days: [],

        generate_table: function() {

            // Render the header - week number, followed by a column
            // for each day of the week.
            let h = [ '<tr>' ],
                css = "",
                title = "",
                i, 
                d = format.date_js(controller.startdate),
                weekno = 1,
                selattr = "",
                weekoptions = [],
                // We add 6 days when calling these two functions so that if
                // d is in the last week of the year, we show the dropdown list
                // for the next year instead of the one we are leaving.
                w = format.first_iso_monday_of_year(common.add_days(d, 6)),
                thisweekno = format.date_weeknumber(common.add_days(d, 6));
            
            // Generate a list of options for every week of the year
            while (weekno <= 52) {
                selattr = "";
                if (weekno == thisweekno) { selattr = 'selected="selected"'; }
                weekoptions.push('<option value="' + format.date(w) + '" ' + selattr + '>' + _("{0}, Week {1}").replace("{0}", format.date(w)).replace("{1}", weekno) + '</option>');
                w.setDate(w.getDate() + 7);
                weekno += 1;
            }

            h.push('<th><select id="weekselector" class="weekselector asm-selectbox">' + weekoptions.join("\n") + '</select></th>');
            boarding_availability.days = [];
            for (i = 0; i < 7; i += 1) {
                css = "";
                if (format.date(d) == format.date(new Date())) { css = 'asm-boarding-availability-today'; } else { css = 'asm-boarding-availability-day'; }
                h.push('<th class="' + css + '" style="width: 13%;">' + format.weekdayname(i) + '. ' + format.monthname(d.getMonth()) + ' ' + d.getDate() + '</th>');
                boarding_availability.days.push(d);
                d = common.add_days(d, 1);
            }
            h.push('</tr>');
            $(".asm-boarding-availability thead").html(h.join("\n"));
            
            h = [];
            $.each(controller.internallocations, function(i, location) {
                css = "asm-boarding-availability-odd";
                if (i % 2 == 0) { css = "asm-boarding-availability-even"; }
                h.push('<tr class="asm-boarding-location-row" data-locationid=' + location.ID + '>');
                h.push('<td title="' + html.title(title) + '" style="cursor: pointer;">');
                h.push(location.LOCATIONNAME);
                h.push("</td>");
                $.each(boarding_availability.days, function(id, d) {
                    h.push('<td data-date="' + format.date(d) + '" class="asm-boarding-availability-cell">');
                    let max = location.UNITS.split(",").length;
                    let low = max;
                    let high = max;
                    let optimum = max - 1;
                    h.push('<meter min="0" max="' + max + '" low="' + low + '" value="0"></meter>');
                    h.push('</td>');
                });
                h.push("</tr>");
                $.each(location.UNITS.split(","), function(i, unit) {
                    h.push('<tr class="asm-boarding-unit-row" data-locationid=' + location.ID + ' data-unit="' + unit.trim() + '" style="display: none;">');
                    h.push('<td title="' + html.title(title) + '">');
                    h.push(unit);
                    h.push("</td>");
                    $.each(boarding_availability.days, function(id, d) {
                        h.push('<td data-date="' + format.date(d) + '" class="asm-boarding-availability-cell">');
                            $.each(controller.rows, function(i, b) {
                                if ( b.SHELTERLOCATION == location.ID && b.SHELTERLOCATIONUNIT.trim() == unit.trim() && format.date_in_range(d, b.INDATETIME, b.OUTDATETIME, true) ) {
                                    h.push('<div class="asm-boarding-item"><a href=# data-id="' + b.ID + '">' + b.ANIMALNAME + ' ' + b.OWNERSURNAME + '</a></div>');
                                }
                            });
                        h.push('</td>');
                    });
                    h.push("</tr>");
                });
            });
            $(".asm-boarding-availability tbody").html(h.join("\n"));
        },

        bind: function() {

            $(".asm-boarding-availability").on("click", "a", function(e) {
                let id = $(this).attr("data-id");
                let row = common.get_row(controller.rows, id, "ID");
                let cell = $(this).closest("td");
                tableform.dialog_show_edit(boarding_availability.dialog, row, {
                    onload: function() {
                       //boarding_availability.type_change();
                    },
                    onchange: async function() {
                        tableform.fields_update_row(boarding_availability.dialog.fields, row);
                        boarding_availability.set_extra_fields(row);
                        await tableform.fields_post(boarding_availability.dialog.fields, "mode=update&boardingid=" + row.ID, controller.name);

                        boarding_availability.remove_booking(row.ID);
                        boarding_availability.insert_booking(row);

                        tableform.dialog_close();
                    },
                    ondelete: function() {
                        tableform.dialog_enable_buttons();
                        tableform.delete_dialog(function() {
                            common.ajax_post(controller.name, "mode=delete&ids=" + id)
                                .then(function() {
                                    common.delete_row(controller.rows, id, "ID");
                                    boarding_availability.remove_booking(id);
                                })
                                .always(function() {
                                    tableform.dialog_close();
                                });
                        });
                        
                    },
                });
                return false;
            });

            $("#location").change(boarding_availability.location_change);
            $("#type").change(boarding_availability.type_change);

            $(".asm-boarding-availability").on("change", "#weekselector", function() {
                common.route(controller.name + "?start=" + $("#weekselector").select("value"));
            });

            $("#button-prev").button().click(function() {
                common.route(controller.name + "?start=" + format.date(controller.prevdate));
            });

            $("#button-today").button().click(function() {
                common.route(controller.name);
            });

            $("#button-next").button().click(function() { 
                common.route(controller.name + "?start=" + format.date(controller.nextdate));
            });

            $("#animal").animalchooser().bind("animalchooserchange", function(event, rec) {
                boarding_availability.lastanimal = rec;
                // if person is not set, load from the current owner if animal has one
                if ($("#person").val() == "0" && rec.OWNERID) {
                    $("#person").val(rec.OWNERID);
                    $("#person").personchooser("loadbyid", rec.OWNERID);
                }
            });

            $("#animal").animalchooser().bind("animalchooserloaded", function(event, rec) {
                boarding_availability.lastanimal = rec;
                // if person is not set, load from the current owner if animal has one
                if ($("#person").val() == "0" && rec.OWNERID) {
                    $("#person").val(rec.OWNERID);
                    $("#person").personchooser("loadbyid", rec.OWNERID);
                }
            });

            $("#person").personchooser().bind("personchooserchange", function(event, rec) {
                boarding_availability.lastperson = rec;
            });

            $("#person").personchooser().bind("personchooserloaded", function(event, rec) {
                boarding_availability.lastperson = rec;
            });
        },

        name: "boarding_availability",
        animation: "book",
        title: function() { return _("Boarding Availability"); },
        routes: {
            "boarding_availability": function() { common.module_loadandstart("boarding_availability", "boarding_availability?" + this.rawqs); }
        }

    };

    common.module_register(boarding_availability);

});
