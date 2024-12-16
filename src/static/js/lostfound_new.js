/*global $, jQuery, _, additional, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const lostfound_new = {

        render: function() {
            this.mode = controller.name.indexOf("lost") != -1 ? "lost" : "found";
            return [
                this.mode == "lost" ? html.content_header(_("Add lost animal")) : html.content_header(_("Add found animal")),
                tableform.fields_render([
                    { post_field: "datelost", type: "date", label: _("Date Lost"), hideif: function() { return lostfound_new.mode != "lost"; }},
                    { post_field: "datefound", type: "date", label: _("Date Found"), hideif: function() { return lostfound_new.mode != "found"; }},
                    { post_field: "datereported", type: "date", label: _("Date Reported") },
                    { post_field: "agegroup", type: "select", label: _("Age Group"), 
                        options: '<option value="Unknown">' + _("(unknown)") + '</option>' +
                            html.list_to_options(controller.agegroups) },
                    { post_field: "sex", type: "select", label: _("Sex"), 
                        options: { displayfield: "SEX", rows: controller.sexes }},
                    { post_field: "species", type: "select", label: _("Species"), 
                        options: { displayfield: "SPECIESNAME", rows: controller.species }},
                    { post_field: "breed", type: "select", label: _("Breed"), 
                        options: html.list_to_options_breeds(controller.breeds),
                        xmarkup: '<select id="breedp" data="breedp" class="asm-selectbox" style="display:none;">' + 
                            html.list_to_options_breeds(controller.breeds) + '</select>' },
                    { post_field: "colour", type: "select", label: _("Color"), 
                        options: { displayfield: "BASECOLOUR", rows: controller.colours }},
                    { post_field: "markings", type: "textarea", label: _("Features"), rows: 4, classes: "asm-textareafixed" },
                    { type: "nextcol" },
                    { post_field: "arealost", type: "textarea", label: _("Area Lost"), rows: 4, classes: "asm-textareafixed", 
                        hideif: function() { return lostfound_new.mode != "lost"; }},
                    { post_field: "areafound", type: "textarea", label: _("Area Found"), rows: 4, classes: "asm-textareafixed",  
                        hideif: function() { return lostfound_new.mode != "found"; }},
                    { post_field: "areapostcode", type: "text", label: _("Zipcode") },
                    { post_field: "microchip", type: "text", label: _("Microchip"), maxlength: 15 },
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
                if ($("#owner").val() == "0") {
                    header.show_error(_("Lost and found entries must have a contact"));
                    validate.highlight("owner");
                    return false;
                }

                // date lost
                if (lostfound_new.mode == "lost" && common.trim($("#datelost").val()) == "") {
                    header.show_error(_("Date lost cannot be blank."));
                    validate.highlight("datelost");
                    return false;
                }

                // date found
                if (lostfound_new.mode == "found" && common.trim($("#datefound").val()) == "") {
                    header.show_error(_("Date found cannot be blank."));
                    validate.highlight("datefound");
                    return false;
                }

                // date reported
                if (common.trim($("#datereported").val()) == "") {
                    header.show_error(_("Date reported cannot be blank."));
                    validate.highlight("datereported");
                    return false;
                }

                // mandatory additional fields
                if (!additional.validate_mandatory()) { return false; }

                return true;

            };

            validate.indicator([ "datelost", "datefound", "datereported", "owner" ]);

            const add_lf_animal = async function(addmode) {
                if (!validation()) { return; }

                $(".asm-content button").button("disable");
                header.show_loading(_("Creating..."));
                try {
                    let formdata = $("input, textarea, select").not(".chooser").toPOST();
                    let createdID = await common.ajax_post(controller.name, formdata);
                    if (addmode == "add") {
                        if (lostfound_new.mode == "lost") {
                            header.show_info(_("Lost animal entry {0} successfully created.").replace("{0}", format.padleft(createdID, 6)));
                        }
                        else {
                            header.show_info(_("FoundLost animal entry {0} successfully created.").replace("{0}", format.padleft(createdID, 6)));
                        }
                    }
                    else {
                        if (lostfound_new.mode == "lost") {
                            if (createdID != "0") { common.route("lostanimal?id=" + createdID); }
                        }
                        else {
                            if (createdID != "0") { common.route("foundanimal?id=" + createdID); }
                        }
                    }
                }
                finally {
                    $(".asm-content button").button("enable");
                    header.hide_loading();
                }
            };

            // Buttons
            $("#button-add").button().click(function() {
                add_lf_animal("add");
            });

            $("#button-addedit").button().click(function() {
                add_lf_animal("addedit");
            });

            $("#button-reset").button().click(function() {
                lostfound_new.reset();
            });

            $('#species').change(function() {
                lostfound_new.update_breed_select();
            });
        },

        sync: function() {
            lostfound_new.reset();
        },  

        reset: function() {
            $("#dispatchaddress, #dispatchtown, #dispatchcounty, #dispatchpostcode").val("").change();
            $(".asm-checkbox").prop("checked", false).change();
            $(".asm-personchooser").personchooser("clear");
            // Set select box default values
            $("#colour").val(config.str("AFDefaultColour"));
            $("#species").val(config.str("AFDefaultSpecies"));
            lostfound_new.update_breed_select();
            $("#breed").val(config.str("AFDefaultBreed"));
            // Default dates
            if (lostfound_new.mode == "lost") {
                $("#datelost").val(format.date(new Date()));
            }
            if (lostfound_new.mode == "found") {
                $("#datefound").val(format.date(new Date()));
            }
            $("#datereported").val(format.date(new Date()));

            // Remove any retired lookups from the lists
            $(".asm-selectbox").select("removeRetiredOptions");

        },

        destroy: function() {
            common.widget_destroy("#owner");
        },

        name: "lostfound_new",
        animation: "newdata",
        autofocus: "#datereported",
        title: function() { 
            if (controller.name.indexOf("lost") != -1) {
                return _("Add lost animal");
            }
            return _("Add found animal");
        },
        routes: {
            "lostanimal_new": function() { common.module_loadandstart("lostfound_new", "lostanimal_new"); },
            "foundanimal_new": function() { common.module_loadandstart("lostfound_new", "foundanimal_new"); }
        }

    };

    common.module_register(lostfound_new);

});
