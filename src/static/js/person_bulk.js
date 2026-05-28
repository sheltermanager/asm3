/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {
    
    "use strict";

    const person_bulk = {
        render_details: function() {
            let flagoptions = html.person_flag_options(null, controller.flags, $("#addflag"));
            return [
                { post_field: "addflag", label: _("Add Flag"), type: "select" },
                { post_field: "removeflag", label: _("Remove Flag"), type: "select" }
                ];
        }, 
        render_diary: function() {
            return [
                { post_field: "diaryfor", label: _("Add Diary"), type: "select", halfsize: true, 
                    options: person_bulk.options(controller.forlist, "USERNAME", "USERNAME", 3),
                    xmarkup: [ " ", _("on"), 
                        tableform.render_date({ post_field: "diarydate", halfsize: true, justwidget: true}),
                        tableform.render_time({ post_field: "diarytime", halfsize: true, justwidget: true }),
                        '<span class="diaryend">' + _(" to "),
                        tableform.render_date({ post_field: "diaryenddate", halfsize: true, justwidget: true}),
                        tableform.render_time({ post_field: "diaryendtime", halfsize: true, justwidget: true }),
                        '</span>'
                        ].join("\n")
                },
               { post_field: "diarycolourscheme", label: _("Color Scheme"), type: "selectcolour", defaultval: 1, 
                    callout: _("The color scheme to be used when displaying this note on the calendar and home screen") },
                { post_field: "diarysubject", label: _("Subject"), type: "text" },
                { post_field: "diarynotes", label: _(""), labelpos: "above", type: "textarea", colclasses: "bottomborder" }
            ];
        }, 
        render_log: function() {
            return [
                { post_field: "logtype", label: _("Add Log"), type: "select", halfsize: true, 
                    options: person_bulk.options(controller.logtypes, "ID", "LOGTYPENAME", 3),
                    xmarkup: [ " ", _("on"), 
                        tableform.render_date({ post_field: "logdate", halfsize: true, justwidget: true}),
                        ].join("\n")
                },
                { post_field: "lognotes", label: _(""), labelpos: "above", type: "textarea", colclasses: "bottomborder" }
            ];
        }, 
        render_additional: function() {
            return [
                { post_field: "updateadditional", type: "check", label: _("Update additional fields") },
                { type: "additional", markup: additional.additional_fields_linktype(controller.additional, 1) },
                { type: "additional", markup: additional.additional_fields_linktype(controller.additional, 7) },
                { type: "additional", markup: additional.additional_fields_linktype(controller.additional, 8) },
                { type: "additional", markup: additional.additional_fields_linktype(controller.additional, 31) }
            ];
        }, 
        render: function() {
            return [
                '<div id="dialog-deletion-breakdown" style="display: none;" title="' + html.title(_("Deletion Breakdown")) + '"></div>',
                html.content_header(_("Bulk change people")),
                tableform.buttons_render([
                    { id: "update", icon: "save", text: _("Update")  }, 
                    { id: "delete", icon: "delete", text: _("Delete") }, 
                    { type: "raw", markup: '<label for="people">' + _("People") + '</label><div style="display: inline-block; vertical-align: middle; width: 400px;"><input type="hidden" class="asm-field asm-personchoosermulti" id="people" data-post="people"></div>' }, 
                 ], { centered: false }),
                tableform.render_accordion({ id: "asm-details-accordion", panes: [
                   { title: _("Details"), fields: person_bulk.render_details(), full_width: false },
                   { title: _("Diary"), fields: person_bulk.render_diary(), full_width: false },
                   { title: _("Log"), fields: person_bulk.render_log(), full_width: false },
                   { title: _("Additional"), fields: person_bulk.render_additional(), full_width: false }
                ]}),
                 html.content_footer()
            ].join("\n");
        }, 

        sync: function() {
            // Load person flags
            html.person_flag_options(null, controller.flags, $("#addflag"));
            html.person_flag_options(null, controller.flags, $("#removeflag"));
            $("#addflag").prepend("<option></option>").val("");
            $("#removeflag").prepend("<option></option>").val("");

            if (config.bool("DisableDiaryEndDatetime")) {
                $(".diaryend").hide();
            }
        },

        bind: function() {

            validate.indicator([ "people" ]);
            
            $("#button-update").button().click(async function() {
                if (!validate.notblank([ "people" ])) { return; }
                $("#button-update").button("disable");
                header.show_loading(_("Updating..."));
                let formdata = "mode=update&" + $("input, select, textarea, .asm-selectcolour").not(".chooser").toPOST();
                try {
                    let response = await common.ajax_post("person_bulk", formdata);
                    header.hide_loading();
                    header.show_info(_("{0} people successfully updated.").replace("{0}", response));
                }
                finally {
                    $("#button-update").button("enable");
                }
            });

            $("#button-delete").button().click(async function() {
                if (!validate.notblank([ "people" ])) { return; }
                try {
                    await tableform.delete_dialog(null, _("This will permanently remove the selected people, are you sure?"));
                    $("#button-delete").button("disable");
                    header.show_loading(_("Deleting..."));
                    let formdata = "mode=delete&" + $("input, select, textarea").toPOST();
                    $.ajax({
                        type: "POST",
                        url:  "person_bulk",
                        data: formdata,
                        dataType: "text",
                        success: async function(data, textStatus, jqXHR) {
                            let people = jQuery.parseJSON(data);
                            let selected = $("#people").val().split(",").length;
                            let successful = selected - people.length;
                            let feedback = '<div>' + _("{0} records successfully deleted.").replace("{0}", successful) + '</div>';
                            if (people.length) {
                                feedback += '<div>' + _("Unable to delete the following {0} records.").replace("{0}", people.length) + '</div>';
                                feedback += '<hr>';
                                $.each(people, function(i, p) {
                                    feedback += '<div style="margin-bottom: 5px;"><b><a href="person?id=' + p.ID + '">' + p.OWNERNAME + '</a></b> ' + p.ERROR + '</div>';
                                });
                            }
                            $("#dialog-deletion-breakdown").html(feedback);
                            header.hide_loading();
                            await tableform.show_okcancel_dialog("#dialog-deletion-breakdown", _("Ok"), { hidecancel: true, width: "calc(100% - 100px)" });
                            $("#people").personchoosermulti("clear");
                        },
                        error: function(jqxhr, textstatus, response) {
                            log.error(response);
                            header.hide_loading();
                        }
                    });
                }
                finally {
                    $("#button-delete").button("enable");
                }
            });

            if (!common.has_permission("ca")) { $("#button-update").hide(); }
            if (!common.has_permission("da")) { $("#button-delete").hide(); }

            // Remove any retired lookups from the lists
            $(".asm-selectbox").select("removeRetiredOptions");

            // Remove sections that add records if the user doesn't have permissions
            if (!common.has_permission("adn")) { $("#diaryforrow, #diarysubjectrow, #diarynotesrow").hide(); }
            if (!common.has_permission("ale")) { $("#logtyperow, #lognotesrow").hide(); }

            $("#updateadditional").change(person_bulk.updateadditional_change);
            person_bulk.updateadditional_change();

        },

        updateadditional_change: function() {
            if ($("#updateadditional").prop("checked")) {
                $(".additional").closest(".asm-formfield").show();
            }
            else {
                $(".additional").closest(".asm-formfield").hide();
            }
        },

        /**
         * Wrapper for html.list_to_options
         * if firstval is undefined or 1, include a "no change" option at the top
         * if firstval == 2, show a blank value at the top
         * if firstval == 3, show a blank but with a value of -1
         */
        options: function(rows, idcol, displaycol, firstval) {
            const nochange = '<option value="-1">' + _("(no change)") + '</option>';
            const blankrow = '<option value=""></option>';
            const mrow = '<option value="-1"></option>';
            let s = "";
            if (firstval === undefined || firstval == 1) { s += nochange; }
            if (firstval == 2) { s += blankrow; }
            if (firstval == 3) { s += mrow; }
            s += html.list_to_options(rows, idcol, displaycol);
            return s;
        },

        destroy: function() {
            common.widget_destroy("#people");
            common.widget_destroy("#dialog-deletion-breakdown");
        },

        name: "person_bulk",
        animation: "newdata",
        title: function() { return _("Bulk change people"); },

        routes: {
            "person_bulk": function() {
                common.module_loadandstart("person_bulk", "person_bulk");
            }
        }


    };

    common.module_register(person_bulk);

});
