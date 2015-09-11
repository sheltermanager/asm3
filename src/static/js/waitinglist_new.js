/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    var waitinglist_new = {

        render: function() {
            return [
                html.content_header(_("Add waiting list")),
                '<table>',
                '<tr>',
                '<td valign="top">',
                '<table>',
                '<tr>',
                '<td><label for="species">' + _("Species") + '</label></td>',
                '<td nowrap="nowrap">',
                '<select id="species" data="species" class="asm-selectbox">',
                html.list_to_options(controller.species, "ID", "SPECIESNAME"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="size">' + _("Size") + '</label></td>',
                '<td nowrap="nowrap">',
                '<select id="size" data-json="SIZE" data-post="size" class="asm-selectbox">',
                html.list_to_options(controller.sizes, "ID", "SIZE"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="dateputon">' + _("Date put on") + '</label></td>',
                '<td><input type="text" id="dateputon" data="dateputon" class="asm-textbox asm-datebox" title="' + html.title(_("The date this animal was put on the waiting list")) + '" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="description">' + _("Description") + '</label></td>',
                '<td><textarea id="description" data="description" rows="8" class="asm-textareafixed" maxlength="255" title="' + html.title(_("A description or other information about the animal")) + '"></textarea></td>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="reasonforwantingtopart">' + _("Entry reason") + '</label></td>',
                '<td><textarea id="reasonforwaitingtopart" data="reasonforwantingtopart" rows="5" class="asm-textareafixed" title="' + html.title(_("The reason the owner wants to part with the animal")) + '"></textarea></td>',
                '</td>',
                '</tr>',
                '</table>',
                '</td>',
                '<td valign="top">',
                '<table>',
                '<tr>',
                '<td><label for="canafforddonation">' + _("Can afford donation?") + '</label></td>',
                '<td><input type="checkbox" id="canafforddonation" data="canafforddonation" class="asm-checkbox" title="' + html.title(_("Will this owner give a donation?")) + '" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="urgency">' + _("Urgency") + '</label></td>',
                '<td><select id="urgency" data="urgency" class="asm-selectbox" title="' + html.title(_("How urgent is it that we take this animal?")) + '">',
                html.list_to_options(controller.urgencies, "ID", "URGENCY"),
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="comments">' + _("Comments") + '</label></td>',
                '<td><textarea id="comments" data="comments" rows="5" class="asm-textareafixed"></textarea></td>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="owner">' + _("Contact") + '</label></td>',
                '<td>',
                '<input id="owner" data="owner" type="hidden" class="asm-personchooser" value="" />',
                '</td>',
                '</tr>',
                '</table>',
                '</td>',
                '</tr>',
                '</table>',
                '<div class="centered">',
                '<button id="addedit">' + html.icon("animal-add") + ' ' + _("Create and edit") + '</button>',
                '<button id="add">' + html.icon("animal-add") + ' ' + _("Create") + '</button>',
                '<button id="reset">' + html.icon("delete") + ' ' + _("Reset") + '</button>',
                '</div>',
                html.content_footer()
            ].join("\n");
        },

        bind: function() {
            var validation = function() {
                // Remove any previous errors
                header.hide_error();
                validate.reset();

                // owner
                if ($.trim($("#owner").val()) == "") {
                    header.show_error(_("Waiting list entries must have a contact"));
                    validate.highlight("owner");
                    return false;
                }

                // date put on list
                if ($.trim($("#dateputon").val()) == "") {
                    header.show_error(_("Date put on cannot be blank"));
                    validate.highlight("dateputon");
                    return false;
                }

                // description
                if ($.trim($("#description").val()) == "") {
                    header.show_error(_("Description cannot be blank"));
                    validate.highlight("description");
                    return false;
                }

                return true;

            };

            var addWaitingList = function(mode) {
                if (!validation()) { return; }

                $(".asm-content button").button("disable");
                header.show_loading(_("Creating..."));

                var formdata = $("input, select, textarea").toPOST();
                common.ajax_post("waitinglist_new", formdata)
                    .then(function(createdID) {
                        if (mode == "add") {
                            header.show_info(_("Waiting list entry successfully added."));
                        }
                        else {
                            if (createdID != "0") { common.route("waitinglist?id=" + createdID); }
                        }
                    })
                    .always(function() {
                        $(".asm-content button").button("enable");
                    });
            };

            // Buttons
            $("#add").button().click(function() {
                addWaitingList("add");
            });

            $("#addedit").button().click(function() {
                addWaitingList("addedit");
            });

            $("#reset").button().click(function() {
                waitinglist_new.reset();
            });
        },

        sync: function() {
            waitinglist_new.reset();
        },

        reset: function() {
            // Set select box default values
            $("#species").val(config.str("AFDefaultSpecies"));
            $("#size").val(config.str("AFDefaultSize"));
            $("#urgency").val(config.str("WaitingListDefaultUrgency"));

            // Default dates
            $(".asm-textbox, .asm-textarea, .asm-textareafixed").val("").change();
            $(".asm-checkbox").prop("checked", false).change();
            $(".asm-personchooser").personchooser("clear");
            $("#dateputon").val(format.date(new Date()));
        },

        destroy: function() {
            common.widget_destroy("#owner");
        },

        name: "waitinglist_new",
        animation: "newdata",
        autofocus: "#species",
        title: function() { return _("Add waiting list"); },
        routes: {
            "waitinglist_new": function() { common.module_loadandstart("waitinglist_new", "waitinglist_new"); }
        }

    };

    common.module_register(waitinglist_new);

});
