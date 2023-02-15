/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, tableform, validate */

$(function() {

    "use strict";

    const onlineform_incoming = {

        model: function() {
            const table = {
                rows: controller.rows,
                idcolumn: "COLLATIONID",
                edit: async function(row) {
                    if (asm.mobileapp) {
                        // Open in a new page on the mobile app rather than a dialog
                        common.route("onlineform_incoming_print?ids=" + row.COLLATIONID, true);
                        return;
                    }
                    header.show_loading(_("Loading..."));
                    try {
                        let result = await common.ajax_post("onlineform_incoming", "mode=view&collationid=" + row.COLLATIONID);
                        $("#dialog-viewer-content").html(result); 
                        $("#dialog-viewer").dialog("open");
                    }
                    finally {
                        header.hide_loading();
                    }
                },
                complete: function(row) {
                    if (row.LINK) { return true; }
                },
                columns: [
                    { field: "FORMNAME", display: _("Name") },
                    { field: "POSTEDDATE", display: _("Received"), initialsort: true, initialsortdirection: "desc", formatter: tableform.format_datetime },
                    { field: "HOST", display: _("From") },
                    { field: "PREVIEW", display: _("Preview") },
                    { field: "LINK", display: _("Link") }
                ]
            };

            const buttons = [
                { id: "delete", text: _("Delete"), icon: "delete", enabled: "multi", perm: "dif", 
                    click: async function() { 
                        await tableform.delete_dialog();
                        tableform.buttons_default_state(buttons);
                        let ids = tableform.table_ids(table);
                        await common.ajax_post("onlineform_incoming", "mode=delete&ids=" + ids);
                        tableform.table_remove_selected_from_json(table, controller.rows);
                        tableform.table_update(table);
                    } 
                },
                { id: "deleteprocessed", text: _("Delete Processed"), icon: "delete", enabled: "always", perm: "dif", 
                    mouseover: function() {
                       onlineform_incoming.highlight_processed(true);
                    },
                    mouseleave: function() {
                       onlineform_incoming.highlight_processed(false);
                    },
                    click: async function() {
                        await tableform.delete_dialog();
                        let ids=[]; // select the rows so we can use remove_selected to update the table
                        $.each(controller.rows, function(i, v) {
                            if (v.LINK) { 
                                ids.push(v.COLLATIONID); 
                                $("[data-id='" + v.COLLATIONID + "']").prop("checked", true);
                            }
                        });
                        await common.ajax_post("onlineform_incoming", "mode=delete&ids=" + ids.join(","));
                        tableform.buttons_default_state(buttons);
                        tableform.table_remove_selected_from_json(table, controller.rows);
                        tableform.table_update(table);
                    }
                },
                { id: "print", text: _("Print"), icon: "print", enabled: "multi", tooltip: _("Print selected forms"), 
                    click: function() {
                        common.route("onlineform_incoming_print?ajax=false&ids=" + encodeURIComponent(tableform.table_ids(table)));
                    }
                },
                { id: "csv", text: _("CSV"), icon: "save", enabled: "multi", tooltip: _("Export selected forms to a CSV file"),
                    click: function() {
                        common.route("onlineform_incoming_csv?ajax=false&ids=" + encodeURIComponent(tableform.table_ids(table)));
                    }
                },
                { id: "attach", icon: "link", text: _("Attach"), enabled: "one", type: "buttonmenu" },
                { id: "create", icon: "complete", text: _("Create"), enabled: "multi", type: "buttonmenu" }

            ];
            this.table = table;
            this.buttons = buttons;
        },

        render_buttonmenus: function() {
            let h = [
                '<div id="button-attach-body" class="asm-menu-body">',
                '<ul class="asm-menu-list">',
                    '<li id="button-attachperson" class="asm-menu-item"><a '
                        + '" href="#">' + html.icon("person-find") + ' ' + _("Person") + '</a></li>',
                    '<li id="button-attachanimal" class="asm-menu-item"><a '
                        + '" href="#">' + html.icon("animal-find") + ' ' + _("Animal") + '</a></li>',
                    '<li id="button-attachanimalbyname" class="asm-menu-item"><a '
                        + '" href="#">' + html.icon("animal-find") + ' ' + _("Animal (via animalname field)") + '</a></li>',
                '</ul>',
                '</div>',
                '<div id="button-create-body" class="asm-menu-body">',
                '<ul class="asm-menu-list">',
                    '<li id="button-animal" class="asm-menu-item"><a '
                        + '" href="#">' + html.icon("animal-add") + ' ' + _("Animal") + '</a></li>',
                    '<li id="button-person" class="asm-menu-item"><a '
                        + '" href="#">' + html.icon("person-add") + ' ' + _("Person") + '</a></li>',
                    '<li id="button-lostanimal" class="asm-menu-item"><a '
                        + '" href="#">' + html.icon("animal-lost-add") + ' ' + _("Lost Animal") + '</a></li>',
                    '<li id="button-foundanimal" class="asm-menu-item"><a '
                        + '" href="#">' + html.icon("animal-found-add") + ' ' + _("Found Animal") + '</a></li>',
                    '<li id="button-incident" class="asm-menu-item"><a '
                        + '" href="#">' + html.icon("call") + ' ' + _("Incident") + '</a></li>',
                    '<li id="button-transport" class="asm-menu-item"><a '
                        + '" href="#">' + html.icon("transport") + ' ' + _("Transport") + '</a></li>',
                    '<li id="button-waitinglist" class="asm-menu-item"><a '
                        + '" href="#">' + html.icon("waitinglist") + ' ' + _("Waiting List") + '</a></li>',
                '</ul>',
                '</div>'

            ];
            return h.join("\n");
        },

        bind_buttonmenus: function() {
            $("#button-attachperson").click(function() {
                $("#dialog-attach-person").dialog("open");
            });
            $("#button-attachanimal").click(function() {
                $("#dialog-attach-animal").dialog("open");
            });
            $("#button-attachanimalbyname").click(function() {
                onlineform_incoming.create_record("attachanimalbyname", "animal");
            });
            $("#button-animal").click(function() {
                onlineform_incoming.create_record("animal", "animal");
            });
            $("#button-person").click(function() {
                onlineform_incoming.create_record("person", "person");
            });
            $("#button-lostanimal").click(function() {
                onlineform_incoming.create_record("lostanimal", "lostanimal");
            });
            $("#button-foundanimal").click(function() {
                onlineform_incoming.create_record("foundanimal", "foundanimal");
            });
            $("#button-incident").click(function() {
                onlineform_incoming.create_record("incident", "incident");
            });
            $("#button-transport").click(function() {
                onlineform_incoming.create_record("transport", "animal_transport");
            });
            $("#button-waitinglist").click(function() {
                onlineform_incoming.create_record("waitinglist", "waitinglist");
            });
        },

        render_viewer: function() {
            return [
                '<div id="dialog-viewer" style="display: none" title="' + html.title(_("View")) + '">',
                '<div id="dialog-viewer-content">',
                '</div>',
                '</div>'
            ].join("\n");
        },

        bind_viewer: function() {
            let viewbuttons = {};
            viewbuttons[_("Close")] = function() { $(this).dialog("close"); };
            $("#dialog-viewer").dialog({
                autoOpen: false,
                resizable: true,
                height: "auto",
                width: 760,
                modal: true,
                dialogClass: "dialogshadow",
                show: dlgfx.add_show,
                hide: dlgfx.add_hide,
                buttons: viewbuttons
            });

        },


        render_attach_person: function() {
            return [
                '<div id="dialog-attach-person" style="display: none" title="' + html.title(_("Select a person")) + '">',
                '<div class="ui-state-highlight ui-corner-all" style="margin-top: 20px; padding: 0 .7em">',
                '<p><span class="ui-icon ui-icon-info"></span>',
                _("Select a person to attach this form to."),
                '</p>',
                '</div>',
                html.capture_autofocus(),
                '<table width="100%">',
                '<tr>',
                '<td><label for="attachperson">' + _("Person") + '</label></td>',
                '<td>',
                '<input id="attachperson" data="attachperson" type="hidden" class="asm-personchooser" value="" />',
                '</td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_attach_animal: function() {
            return [
                '<div id="dialog-attach-animal" style="display: none" title="' + html.title(_("Select an animal")) + '">',
                '<div class="ui-state-highlight ui-corner-all" style="margin-top: 20px; padding: 0 .7em">',
                '<p><span class="ui-icon ui-icon-info"></span>',
                _("Select an animal to attach this form to."),
                '</p>',
                '</div>',
                html.capture_autofocus(),
                '<table width="100%">',
                '<tr>',
                '<td><label for="attachanimal">' + _("Animal") + '</label></td>',
                '<td>',
                '<input id="attachanimal" data="attachanimal" type="hidden" class="asm-animalchooser" value="" />',
                '</td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        bind_attach_person: function() {
            let ab = {}, table = onlineform_incoming.table; 
            ab[_("Attach")] = async function() { 
                if (!validate.notblank(["attachperson"])) { return; }
                try {
                    let formdata = "mode=attachperson&personid=" + $("#attachperson").val() + "&collationid=" + tableform.table_selected_row(table).COLLATIONID;
                    await common.ajax_post("onlineform_incoming", formdata);
                    let personname = $("#attachperson").closest("td").find(".asm-embed-name").html();
                    header.show_info(_("Successfully attached to {0}").replace("{0}", personname));
                    tableform.table_selected_row(table).LINK = 
                        '<a target="_blank" href="person_media?id=' + $("#attachperson").val() + '">' + personname + '</a>';
                    tableform.table_update(table);
                }
                finally {
                    $("#dialog-attach-person").dialog("close");
                }
            };
            ab[_("Cancel")] = function() { $(this).dialog("close"); };
            $("#dialog-attach-person").dialog({
                 autoOpen: false,
                 width: 600,
                 resizable: false,
                 modal: true,
                 dialogClass: "dialogshadow",
                 show: dlgfx.delete_show,
                 hide: dlgfx.delete_hide,
                 buttons: ab
            });
        },

        bind_attach_animal: function() {
            let ab = {}, table = onlineform_incoming.table; 
            ab[_("Attach")] = async function() { 
                if (!validate.notblank(["attachanimal"])) { return; }
                try {
                    let formdata = "mode=attachanimal&animalid=" + $("#attachanimal").val() + "&collationid=" + tableform.table_selected_row(table).COLLATIONID;
                    await common.ajax_post("onlineform_incoming", formdata);
                    let animalname = $("#attachanimal").closest("td").find(".asm-embed-name").html();
                    header.show_info(_("Successfully attached to {0}").replace("{0}", animalname));
                    tableform.table_selected_row(table).LINK = 
                        '<a target="_blank" href="animal_media?id=' + $("#attachanimal").val() + '">' + animalname + '</a>';
                    tableform.table_update(table);
                }
                finally {
                    $("#dialog-attach-animal").dialog("close");
                }
            };
            ab[_("Cancel")] = function() { $(this).dialog("close"); };
            $("#dialog-attach-animal").dialog({
                 autoOpen: false,
                 width: 600,
                 resizable: false,
                 modal: true,
                 dialogClass: "dialogshadow",
                 show: dlgfx.delete_show,
                 hide: dlgfx.delete_hide,
                 buttons: ab
            });
        },

        /**
         * Make an AJAX post to create a record.
         * mode: The type of record to create - person, lostanimal, foundanimal, waitinglist
         * url:  The url to link to the target created record
         */
        create_record: async function(mode, target) {
            header.hide_error();
            header.show_loading(_("Creating..."));
            let table = onlineform_incoming.table, ids = tableform.table_ids(table);
            try {
                let result = await common.ajax_post("onlineform_incoming", "mode=" + mode + "&ids=" + ids);
                let selrows = tableform.table_selected_rows(table);
                $.each(selrows, function(i, v) {
                    $.each(result.split("^$"), function(ir, vr) {
                        let [collationid, linkid, display, status] = vr.split("|");
                        if (collationid == v.COLLATIONID) {
                            v.LINK = '<a target="_blank" href="' + target + '?id=' + linkid + '">' + display + '</a>';
                            if (status && status == 1) {
                                v.LINK += " " + html.icon("copy", _("Updated existing record"));
                            }
                            if (status && status == 2) {
                                v.LINK += " " + html.icon("warning", _("This person has been banned from adopting animals."));
                            }
                        }
                    });
                });
                tableform.table_update(table);
            }
            finally {
                header.hide_loading();
            }
        },

        /**
         * Puts a red border around all processed forms in the list
         */
        highlight_processed: function(enable) {
            let bval = "1px solid red";
            if (!enable) { bval = ""; }
            $.each(controller.rows, function(i, v) {
                if (v.LINK) {
                    $("[data-id='" + v.COLLATIONID + "']").closest("tr").find("td").css({ border: bval });
                }
            });
        },

        /**
         * Called as the form is destroyed, sends a message to the backend to
         * remove any processed forms.
         */
        remove_processed: function() {
            if (config.bool("DontRemoveProcessedForms")) { return; }
            let ids=[];
            $.each(controller.rows, function(i, v) {
                if (v.LINK) { ids.push(v.COLLATIONID); }
            });
            common.ajax_post("onlineform_incoming", "mode=delete&ids=" + ids.join(","));
        },

        render: function() {
            let s = "";
            this.model();
            s += this.render_viewer();
            s += this.render_attach_person();
            s += this.render_attach_animal();
            s += this.render_buttonmenus();
            s += html.content_header(_("Incoming Forms"));
            s += html.info(_("Incoming forms are online forms that have been completed and submitted by people on the web.") + 
                "<br />" + _("You can use incoming forms to create new records or attach them to existing records.") +
                "<br />" + _("Incoming forms will be automatically removed after {0} days.").replace("{0}", config.str("AutoRemoveIncomingFormsDays")) + 
                "<br />" + (config.bool("DontRemoveProcessedForms") ? "" : _("Incoming forms that have been used to create records will be automatically removed when you leave this screen.")) );
            s += tableform.buttons_render(this.buttons);
            s += tableform.table_render(this.table);
            s += html.content_footer();
            return s;
        },

        bind: function() {
            tableform.buttons_bind(this.buttons);
            tableform.table_bind(this.table, this.buttons);
            this.bind_viewer();
            this.bind_attach_animal();
            this.bind_attach_person();
            this.bind_buttonmenus();
        },

        sync: function() {
        },

        destroy: function() {
            common.widget_destroy("#dialog-viewer");
            common.widget_destroy("#dialog-attach-animal");
            common.widget_destroy("#dialog-attach-person");
            common.widget_destroy("#attachanimal", "animalchooser");
            common.widget_destroy("#attachperson", "personchooser");
            onlineform_incoming.remove_processed(); 
        },

        name: "onlineform_incoming",
        animation: "formtab",
        title: function() { return _("Incoming Forms"); },
        routes: {
            "onlineform_incoming": function() { common.module_loadandstart("onlineform_incoming", "onlineform_incoming"); }
        }

    };

    common.module_register(onlineform_incoming);

});
