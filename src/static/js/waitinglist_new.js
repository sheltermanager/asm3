/*global $, jQuery, _, additional, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const waitinglist_new = {

        render: function() {
            return [
                html.content_header(_("Add waiting list")),
                '<table>',
                '<tr>',
                '<td valign="top">',
                '<table>',
                '<tr>',
                '<td>',
                '<label for="dateputon">' + _("Date put on") + '</label></td>',
                '<td><input type="text" id="dateputon" data="dateputon" class="asm-textbox asm-datebox" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="animalname">' + _("Name") + '</label></td>',
                '<td><input id="animalname" data="animalname" type="text" class="asm-textbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="species">' + _("Species") + '</label></td>',
                '<td nowrap="nowrap">',
                '<select id="species" data="species" class="asm-selectbox">',
                html.list_to_options(controller.species, "ID", "SPECIESNAME"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="breed">' + _("Breed") + '</label></td>',
                '<td nowrap="nowrap">',
                '<select id="breed" data="breed" class="asm-selectbox">',
                html.list_to_options_breeds(controller.breeds),
                '</select>',
                '<select id="breedp" data="breedp" class="asm-selectbox" style="display:none;">',
                html.list_to_options_breeds(controller.breeds),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="sex">' + _("Sex") + '</label></td>',
                '<td nowrap="nowrap">',
                '<select id="sex" data="sex" class="asm-selectbox">',
                html.list_to_options(controller.sexes, "ID", "SEX"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td></td>',
                '<td><input type="checkbox" id="neutered" data="neutered" class="asm-checkbox" />',
                '<label for="neutered">' + _("Altered") + '</label></td>',
                '</tr>',
                '<tr>',
                '<td><label for="size">' + _("Size") + '</label></td>',
                '<td nowrap="nowrap">',
                '<select id="size" data="size" class="asm-selectbox">',
                html.list_to_options(controller.sizes, "ID", "SIZE"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="dateofbirth">' + _("Date of Birth") + '</label></td>',
                '<td><input type="text" id="dateofbirth" data="dateofbirth" class="asm-textbox asm-datebox" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="microchip">' + _("Microchip") + '</label></td>',
                '<td><input id="microchip" data="microchip" type="text" maxlength="15" class="asm-textbox" /></td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="description">' + _("Description") + '</label>',
                '<span id="callout-description" class="asm-callout">' + _("A description or other information about the animal") + '</span>',
                '</td>',
                '<td><textarea id="description" data="description" rows="3" class="asm-textareafixed" maxlength="255"></textarea></td>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="reasonforwantingtopart">' + _("Entry reason") + '</label>',
                '<span id="callout-reasonforwantingtopart" class="asm-callout">' + _("The reason the owner wants to part with the animal") + '</span>',
                '</td>',
                '<td><textarea id="reasonforwantingtopart" data="reasonforwantingtopart" rows="3" class="asm-textareafixed" ></textarea></td>',
                '</td>',
                '</tr>',
                '</table>',
                '</td>',
                '<td valign="top">',
                '<table>',
                '<tr>',
                '<td></td>',
                '<td><input type="checkbox" id="canafforddonation" data="canafforddonation" class="asm-checkbox" />',
                '<label for="canafforddonation">' + _("Can afford donation?") + '</label></td>',
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
                additional.additional_new_fields(controller.additional),
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

        update_breed_select: function() {
            // Only show the breeds for the selected species
            // If the species has no breeds the species is shown
            $('optgroup', $('#breed')).remove();
            $('#breedp optgroup').clone().appendTo($('#breed'));
            $('#breed').children().each(function(){
                if($(this).attr('id') != 'ngp-'+$('#species').val()){
                    $(this).remove();
                }
            });
        },

        bind: function() {
            const validation = function() {
                // Remove any previous errors
                header.hide_error();
                validate.reset();

                // owner
                if (common.trim($("#owner").val()) == "") {
                    header.show_error(_("Waiting list entries must have a contact"));
                    validate.highlight("owner");
                    return false;
                }

                // date put on list
                if (common.trim($("#dateputon").val()) == "") {
                    header.show_error(_("Date put on cannot be blank"));
                    validate.highlight("dateputon");
                    return false;
                }

                // description
                if (common.trim($("#description").val()) == "") {
                    header.show_error(_("Description cannot be blank"));
                    validate.highlight("description");
                    return false;
                }

                // mandatory additional fields
                if (!additional.validate_mandatory()) { return false; }

                return true;

            };

            validate.indicator([ "owner", "dateputon", "description" ]);

            const add_waiting_list = async function(mode) {
                if (!validation()) { return; }

                $(".asm-content button").button("disable");
                header.show_loading(_("Creating..."));

                let formdata = $("input, textarea, select").not(".chooser").toPOST();
                try {
                    let createdID = await common.ajax_post("waitinglist_new", formdata);
                    if (mode == "add") {
                        header.show_info(_("Waiting list entry successfully added."));
                    }
                    else {
                        if (createdID != "0") { common.route("waitinglist?id=" + createdID); }
                    }
                }
                finally {
                    $(".asm-content button").button("enable");
                }
            };

            $('#species').change(function() {
                waitinglist_new.update_breed_select();
            });

            // Buttons
            $("#add").button().click(function() {
                add_waiting_list("add");
            });

            $("#addedit").button().click(function() {
                add_waiting_list("addedit");
            });

            $("#reset").button().click(function() {
                waitinglist_new.reset();
            });
        },

        sync: function() {
            waitinglist_new.reset();
        },

        reset: function() {

            $("#description, #reasonforwantingtopart, #comments").val("").change();

            // Set select box default values
            $("#species").val(config.str("AFDefaultSpecies"));
            waitinglist_new.update_breed_select();
            $("#size").val(config.str("AFDefaultSize"));
            $("#sex").val("2");
            $("#urgency").val(config.str("WaitingListDefaultUrgency"));

            // Default dates
            $(".asm-checkbox").prop("checked", false).change();
            $(".asm-personchooser").personchooser("clear");
            $("#dateputon").val(format.date(new Date()));

            // Remove any retired lookups from the lists
            $(".asm-selectbox").select("removeRetiredOptions");

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
