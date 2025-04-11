/*global $, jQuery, _, additional, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const waitinglist_new = {

        render: function() {
            return [
                html.content_header(_("Add waiting list")),
                tableform.fields_render([
                    { post_field: "dateputon", type: "date", label: _("Date put on") },
                    { post_field: "animalname", type: "text", label: _("Name") },
                    { post_field: "species", type: "select", label: _("Species"), 
                        options: { displayfield: "SPECIESNAME", rows: controller.species }},
                    { post_field: "breed", type: "select", label: _("Breed"), 
                        options: html.list_to_options_breeds(controller.breeds),
                        xmarkup: '<select id="breedp" data="breedp" class="asm-selectbox" style="display:none;">' + 
                            html.list_to_options_breeds(controller.breeds) + '</select>' },
                    { post_field: "sex", type: "select", label: _("Sex"), 
                        options: { displayfield: "SEX", rows: controller.sexes }},
                    { post_field: "neutered", type: "check", label: _("Altered") },
                    { post_field: "size", type: "select", label: _("Size"), 
                        options: { displayfield: "SIZE", rows: controller.sizes }},
                    { post_field: "dateofbirth", type: "date", label: _("Date of Birth") },
                    { post_field: "microchip", type: "text", label: _("Microchip"), maxlength: 15 },
                    { post_field: "description", type: "textarea", label: _("Description"), classes: "asm-textareafixed", rows: 3, 
                        callout: _("A description or other information about the animal") },
                    { post_field: "reasonforwantingtopart", type: "textarea", label: _("Entry reason"), classes: "asm-textareafixed", rows: 3, 
                        callout: _("The reason the owner wants to part with the animal") },
                    { type: "nextcol" },
                    { post_field: "canafforddonation", type: "check", label: _("Can afford donation") },
                    { post_field: "urgency", type: "select", label: _("Urgency"), 
                        options: { displayfield: "URGENCY", rows: controller.urgencies }},
                    { post_field: "comments", type: "textarea", label: _("Comments"), rows: 5, classes: "asm-textareafixed" },
                    { post_field: "owner", type: "person", label: _("Contact") },
                    { type: "additional", markup: additional.additional_new_fields(controller.additional) }
                ], { full_width: false }),
                tableform.buttons_render([
                   { id: "addedit", icon: "animal-add", text: _("Create and edit") },
                   { id: "add", icon: "animal-add", text: _("Create") },
                   { id: "reset", icon: "delete", text: _("Reset") }
                ], { centered: true }),
                html.content_footer()
            ].join("\n");
        },

        update_breed_select: function() {
            // Only show the breeds for the selected species
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
            $("#button-add").button().click(function() {
                add_waiting_list("add");
            });

            $("#button-addedit").button().click(function() {
                add_waiting_list("addedit");
            });

            $("#button-reset").button().click(function() {
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
            $("#breed").val(config.str("AFDefaultBreed"));
            $("#size").val(config.str("AFDefaultSize"));
            $("#sex").val("2");
            $("#urgency").val(config.str("WaitingListDefaultUrgency"));

            // Default dates
            $(".asm-checkbox").prop("checked", false).change();
            $(".asm-personchooser").personchooser("clear");
            $("#dateputon").val(format.date(new Date()));

            // Remove any retired lookups from the lists
            $(".asm-selectbox").select("removeRetiredOptions", "all");

            // Change additional fields to default
            additional.reset_default(controller.additional);

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
