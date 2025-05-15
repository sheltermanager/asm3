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
                let locationid = location.attributes["data-locationid"].value;
                $.each($(location).find(".asm-boarding-availability-cell"), function(i, cell) {
                    let date = cell.attributes["data-date"].value;
                    let bookings = $(".asm-boarding-unit-row[data-locationid='" + locationid + "'] .asm-boarding-availability-cell[data-date='" + date + "'] .asm-boarding-item");
                    $(cell).find('meter').val(bookings.length);//bookings.length;
                });
            });

            $(".asm-boarding-location-row").click(function() {
                let locationid = $(this).attr("data-locationid");
                $(".asm-boarding-unit-row[data-locationid='" + locationid + "']").toggle();
            });

            $(".asm-boarding-unit-row .asm-boarding-availability-cell").click(function() {
                let date = this.attributes["data-date"].value;
                let locationid = this.parentElement.attributes["data-locationid"].value;
                let unit = this.parentElement.firstElementChild.innerHTML.trim();
                boarding_availability.new_boarding(date, locationid, unit, this);
            });
        },

        new_boarding: function(date, locationid, unit, cell) {
            tableform.dialog_show_add(boarding_availability.dialog, {
                onadd: async function() {
                    try {
                        let response = await tableform.fields_post(boarding_availability.dialog.fields, "mode=create", "boarding");
                        let row = {};
                        row.ID = response;
                        tableform.fields_update_row(boarding_availability.dialog.fields, row);
                        boarding_availability.set_extra_fields(row);
                        controller.rows.push(row);
                        cell.innerHTML = row.ANIMALNAME + " " + row.OWNERSURNAME;
                        let value = parseInt($(".asm-boarding-location-row[data-locationid='" + locationid + "'] td[data-date='" + date + "'] meter")[0].attributes["value"].value);
                        value = value + 1;
                        console.log(value);
                        $(".asm-boarding-location-row[data-locationid='" + locationid + "'] td[data-date='" + date + "'] meter")[0].attributes["value"].value = value;
                        //console.log(meter);
                        //meter.attributes["value"]++;
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
                    if (controller.animal) {
                        $("#animal").animalchooser("loadbyid", controller.animal.ID);
                    }
                    if (controller.person) {
                        $("#person").personchooser("loadbyid", controller.person.ID);
                    }
                    console.log(date);
                    $("#indate").val(date);
                    $("#outdate").val(date);
                    $("#intime").val("00:00");
                    $("#outtime").val("00:00");
                    $("#location").val(locationid);
                    boarding_availability.location_change();
                    console.log("Setting unit to '" + unit + "'");
                    $("#unit").val(unit);
                    //boarding_availability.type_change();
                }
            });
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
                h.push('<th class="' + css + '">' + format.weekdayname(i) + '. ' + format.monthname(d.getMonth()) + ' ' + d.getDate() + '</th>');
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
                h.push('<td class="' + css + '" title="' + html.title(title) + '" style="cursor: pointer;">');
                h.push(location.LOCATIONNAME);
                h.push("</td>");
                $.each(boarding_availability.days, function(id, d) {
                    h.push('<td data-date="' + format.date(d) + '" class="asm-boarding-availability-cell">');
                    h.push('<meter min="0" max="' + location.UNITS.split(",").length + '" value="0" style="width: 100%;"></meter>');
                    h.push('</td>');
                });
                h.push("</tr>");
                $.each(location.UNITS.split(","), function(i, unit) {
                    h.push('<tr class="asm-boarding-unit-row" data-locationid=' + location.ID + ' style="display: none;">');
                    h.push('<td class="' + css + '" title="' + html.title(title) + '">');
                    h.push(unit);
                    h.push("</td>");
                    $.each(boarding_availability.days, function(id, d) {
                        h.push('<td data-date="' + format.date(d) + '" class="asm-boarding-availability-cell">');
                            $.each(controller.rows, function(i, b) {
                                if ( b.SHELTERLOCATION == location.ID && b.SHELTERLOCATIONUNIT.trim() == unit.trim() && format.date_in_range(d, b.INDATETIME, b.OUTDATETIME, true) ) {
                                    h.push('<div class="asm-boarding-item">' + b.ANIMALNAME + ' ' + b.OWNERSURNAME + '</div>');
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

            $("#location").change(boarding_availability.location_change);

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
