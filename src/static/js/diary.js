/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const diary = {

        model: function() {
            const dialog = {
                add_title: _("Add diary"),
                edit_title: _("Edit diary"),
                helper_text: _("Diary notes need a date and subject.") + "<br />" + 
                    _("Times should be in HH:MM format, eg: 09:00, 16:30"),
                close_on_ok: false,
                columns: 1,
                width: 500,
                fields: [
                    { json_field: "DIARYFORNAME", post_field: "diaryfor", label: _("For"), type: "select", 
                        options: { rows: controller.forlist, displayfield: "USERNAME", valuefield: "USERNAME" }},
                    { json_field: "DIARYDATETIME", post_field: "diarydate", label: _("Date"), type: "date", validation: "notblank", defaultval: new Date() },
                    { json_field: "DIARYDATETIME", post_field: "diarytime", label: _("Time"), type: "time" },
                    { json_field: "DATECOMPLETED", post_field: "completed", label: _("Completed"), type: "date" },
                    { json_field: "SUBJECT", label: _("Subject"), post_field: "subject", validation: "notblank", type: "text" },
                    { json_field: "NOTE", label: _("Note"), post_field: "note", type: "textarea" },
                    { json_field: "COMMENTS", label: _("Comments"), post_field: "comments", type: "textarea" }
                ]
            };

            const table = {
                rows: controller.rows,
                idcolumn: "ID",
                edit: function(row) {
                    tableform.fields_populate_from_json(dialog.fields, row);
                    tableform.dialog_show_edit(dialog, row, {
                        onchange: async function() {
                            try {
                                tableform.fields_update_row(dialog.fields, row);
                                await tableform.fields_post(dialog.fields, "mode=update&diaryid=" + row.ID, "diary");
                                tableform.table_update(table);
                                tableform.dialog_close();
                            }
                            catch(err) {
                                log.error(err, err);
                                tableform.dialog_error(response);
                                tableform.dialog_enable_buttons();
                            }
                        },
                        onload: function(row) {
                            // If this is my/all diary notes, and the user does not
                            // have the edit all diary notes permission and is not
                            // the person who created the diary note, they should only 
                            // be able to edit the comments.
                            if ((controller.name.indexOf("diary_edit") == 0) && (row.CREATEDBY != asm.user) && (!common.has_permission("eadn"))) {
                                $("#subjecttext").remove();
                                $("#notetext").remove();
                                $("#note").closest("span").hide();
                                $("#subject").hide();
                                $("#note").closest("td").append("<span id='notetext'>" + row.NOTE + "</span>");
                                $("#subject").closest("td").append("<span id='subjecttext'>" + row.SUBJECT + "</span>");
                            }
                            else {
                                $("#subjecttext").remove();
                                $("#notetext").remove();
                                $("#subject").show();
                                $("#note").closest("span").show();
                            }

                            // Allow editing of the comments once the diary is created
                            $("#comments").closest("tr").show();
                        }
                    });
                },
                complete: function(row) {
                    if (row.DATECOMPLETED) { return true; }
                    return false;
                },
                overdue: function(row) {
                    return !row.DATECOMPLETED && format.date_js(row.DIARYDATETIME) < common.today_no_time();
                },
                columns: [
                    { field: "DIARYFORNAME", display: _("For") },
                    { field: "DIARYDATETIME", display: _("Date"), formatter: tableform.format_datetime, initialsort: true, initialsortdirection: "desc" },
                    { field: "DATECOMPLETED", display: _("Completed"), formatter: tableform.format_date },
                    { field: "LINKINFO", display: _("Link"), 
                        formatter: function(row) {
                            let link = "#";
                            if (row.LINKTYPE == 1) { link = "animal?id=" + row.LINKID; }
                            if (row.LINKTYPE == 2) { link = "person?id=" + row.LINKID; }
                            if (row.LINKTYPE == 3) { link = "lostanimal?id=" + row.LINKID; }
                            if (row.LINKTYPE == 4) { link = "foundanimal?id=" + row.LINKID; }
                            if (row.LINKTYPE == 5) { link = "waitinglist?id=" + row.LINKID; }
                            if (row.LINKTYPE == 7) { link = "incident?id=" + row.LINKID; }
                            if (link != "#") { return '<a href="' + link + '">' + row.LINKINFO + '</a>'; }
                            return row.LINKINFO;
                        },
                        hideif: function() {
                            return common.current_url().indexOf("diary_edit") == -1;
                        }
                    },
                    { field: "SUBJECT", display: _("Subject") },
                    { field: "NOTE", display: _("Note") },
                    { field: "CREATEDBY", display: _("By") }
                ]
            };

            const buttons = [
                { id: "new", text: _("New Diary"), icon: "new", enabled: "always", perm: "adn", click: function() { 
                    diary.new_note();
                }},
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "ddn", 
                    click: async function() { 
                        await tableform.delete_dialog();
                        tableform.buttons_default_state(buttons);
                        let ids = tableform.table_ids(table);
                        await common.ajax_post("diary", "mode=delete&ids=" + ids);
                        tableform.table_remove_selected_from_json(table, controller.rows);
                        tableform.table_update(table);
                    } 
                },
                { id: "complete", text: _("Complete"), icon: "complete", enabled: "multi", 
                    click: async function() { 
                        let ids = tableform.table_ids(table);
                        await common.ajax_post("diary", "mode=complete&ids=" + ids);
                        $.each(controller.rows, function(i, v) {
                        if (tableform.table_id_selected(v.ID)) {
                            v.DATECOMPLETED = format.date_iso(new Date());
                        }
                        });
                        tableform.table_update(table);
                    } 
                },
                { id: "filter", type: "dropdownfilter", 
                    options: [ "uncompleted|" + _("Incomplete notes upto today"),
                        "completed|" + _("Completed notes upto today"),
                        "all|" + _("All notes upto today"),
                        "future|" + _("Future notes")
                        ],
                    hideif: function() {
                        return common.current_url().indexOf("diary_edit") == -1;
                    },
                    click: function(selval) {
                        common.route(controller.name + "?filter=" + selval);
                    }
                }
            ];
            this.dialog = dialog;
            this.buttons = buttons;
            this.table = table;
        },

        set_extra_fields: function(row) {
            row.CREATEDBY = asm.user;
        },

        render: function() {
            let h = [];
            this.model();
            h.push(tableform.dialog_render(this.dialog));
            if (controller.name == "animal_diary") {
                h.push(edit_header.animal_edit_header(controller.animal, "diary", controller.tabcounts));
            }
            else if (controller.name == "person_diary") {
                h.push(edit_header.person_edit_header(controller.person, "diary", controller.tabcounts));
            }
            else if (controller.name == "waitinglist_diary") {
                h.push(edit_header.waitinglist_edit_header(controller.animal, "diary", controller.tabcounts));
            }
            else if (controller.name == "lostanimal_diary") {
                h.push(edit_header.lostfound_edit_header("lost", controller.animal, "diary", controller.tabcounts));
            }
            else if (controller.name == "foundanimal_diary") {
                h.push(edit_header.lostfound_edit_header("found", controller.animal, "diary", controller.tabcounts));
            }
            else if (controller.name == "incident_diary") {
                h.push(edit_header.incident_edit_header(controller.incident, "diary", controller.tabcounts));
            }
            else if (controller.name == "diary_edit") {
                h.push(html.content_header(_("Edit diary notes")));
            }
            else if (controller.name == "diary_edit_my") {
                h.push(html.content_header(_("Edit my  diary notes")));
            }
            h.push(tableform.buttons_render(this.buttons));
            h.push(tableform.table_render(this.table));
            h.push(html.content_footer());
            return h.join("\n");
        },

        bind: function() {
            $(".asm-tabbar").asmtabs();
            tableform.dialog_bind(this.dialog);
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);
        },

        sync: function() {
            // If a filter is given in the querystring, update the select
            if (common.current_url().indexOf("filter=") != -1) {
                let filterurl = common.current_url().substring(common.current_url().indexOf("filter=")+7);
                $("#filter").select("value", filterurl);
            }

            if (controller.newnote) {
                diary.new_note();
            }
        },

        new_note: function() {
            tableform.dialog_show_add(diary.dialog, {
                onadd: async function() {
                    let response = await tableform.fields_post(diary.dialog.fields, "mode=create&linktypeid=" + controller.linktypeid + "&linkid=" + controller.linkid, "diary");
                    let row = {};
                    row.ID = response;
                    tableform.fields_update_row(diary.dialog.fields, row);
                    diary.set_extra_fields(row);
                    controller.rows.push(row);
                    tableform.table_update(diary.table);
                    tableform.dialog_close();
                },
                onload: function() {

                    tableform.dialog_enable_buttons(); 

                    // Show the note textarea and subject box and remove any old text display of notes
                    $("#notetext").remove();
                    $("#subjecttext").remove();
                    $("#note").closest("span").show();
                    $("#subject").show();

                    // Hide the comments field for new diary notes
                    $("#comments").closest("tr").hide();

                    // If a default diary person is set, choose them
                    if (config.str("AFDefaultDiaryPerson")) {
                        $("#diaryfor").select("value", config.str("AFDefaultDiaryPerson"));
                    }
                }
            });
        },

        destroy: function() {
            tableform.dialog_destroy();
        },

        name: "diary",
        animation: function() { return controller.name.indexOf("diary_edit") == 0 ? "book" : "formtab"; },
        title:  function() { 
            let t = "";
            if (controller.name == "animal_diary") {
                t = common.substitute(_("{0} - {1} ({2} {3} aged {4})"), { 
                    0: controller.animal.ANIMALNAME, 1: controller.animal.CODE, 2: controller.animal.SEXNAME,
                    3: controller.animal.SPECIESNAME, 4: controller.animal.ANIMALAGE }); 
            }
            else if (controller.name == "diary_edit") { t = _("Edit diary notes"); }
            else if (controller.name == "diary_edit_my") { t = _("Edit my diary notes"); }
            else if (controller.name == "foundanimal_diary") { t = common.substitute(_("Found animal - {0} {1} [{2}]"), {
                0: controller.animal.AGEGROUP, 1: controller.animal.SPECIESNAME, 2: controller.animal.OWNERNAME});
            }
            else if (controller.name == "incident_diary") { t = common.substitute(_("Incident {0}, {1}: {2}"), {
                0: controller.incident.ACID, 1: controller.incident.INCIDENTNAME, 2: format.date(controller.incident.INCIDENTDATETIME)});
            }
            else if (controller.name == "lostanimal_diary") { t = common.substitute(_("Lost animal - {0} {1} [{2}]"), {
                0: controller.animal.AGEGROUP, 1: controller.animal.SPECIESNAME, 2: controller.animal.OWNERNAME});
            }
            else if (controller.name == "person_diary") { t = controller.person.OWNERNAME; }
            else if (controller.name == "waitinglist_diary") { t = common.substitute(_("Waiting list entry for {0} ({1})"), {
                0: controller.animal.OWNERNAME, 1: controller.animal.SPECIESNAME });
            }
            return t;
        },

        routes: {
            "animal_diary": function() { common.module_loadandstart("diary", "animal_diary?id=" + this.qs.id); },
            "diary_edit": function() { common.module_loadandstart("diary", "diary_edit?" + this.rawqs); },
            "diary_edit_my": function() { common.module_loadandstart("diary", "diary_edit_my?" + this.rawqs); },
            "foundanimal_diary": function() { common.module_loadandstart("diary", "foundanimal_diary?id=" + this.qs.id); },
            "incident_diary": function() { common.module_loadandstart("diary", "incident_diary?id=" + this.qs.id); },
            "lostanimal_diary": function() { common.module_loadandstart("diary", "lostanimal_diary?id=" + this.qs.id); },
            "person_diary": function() { common.module_loadandstart("diary", "person_diary?id=" + this.qs.id); },
            "waitinglist_diary": function() { common.module_loadandstart("diary", "waitinglist_diary?id=" + this.qs.id); }
        }

    };

    common.module_register(diary);

});
