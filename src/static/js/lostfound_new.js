/*global $, jQuery, _, additional, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const lostfound_new = {

        render: function() {
            this.mode = controller.name.indexOf("lost") != -1 ? "lost" : "found";
            return [
                this.mode == "lost" ? html.content_header(_("Add lost animal")) : html.content_header(_("Add found animal")),
                '<table class="asm-table-layout">',
                '<tr>',
                '<td width="40%">',
                '<table width="100%">',
                '<tr>',
                '<td>',
                this.mode == "lost" ? '<label for="datelost">' + _("Date Lost") + '</label></td>' : "",
                this.mode == "lost" ? '<td><input type="text" id="datelost" data="datelost" class="asm-textbox asm-datebox" title="' + html.title(_("The date this animal was lost")) + '"  />' : "",
                this.mode == "found" ? '<label for="datefound">' + _("Date Found") + '</label></td>' : "",
                this.mode == "found" ? '<td><input type="text" id="datefound" data="datefound" class="asm-textbox asm-datebox" title="' + html.title(_("The date this animal was found")) + '"  />' : "",
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="datereported">' + _("Date Reported") + '</label></td>',
                '<td><input type="text" id="datereported" data="datereported" class="asm-textbox asm-datebox" title="' + html.title(_("The date reported to the shelter")) + '" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="agegroup">' + _("Age Group") + '</label></td>',
                '<td nowrap="nowrap">',
                '<select id="agegroup" data="agegroup" class="asm-selectbox">',
                '<option value="Unknown">' + _("(unknown)") + '</option>',
                html.list_to_options(controller.agegroups),
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
                '<td><label for="colour">' + _("Color") + '</label></td>',
                '<td nowrap="nowrap">',
                '<select id="colour" data="colour" class="asm-selectbox">',
                html.list_to_options(controller.colours, "ID", "BASECOLOUR"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="markings">' + _("Features") + '</label></td>',
                '<td><textarea id="markings" data="markings" rows="4" class="asm-textarea" title="' + html.title(_("Any information about the animal")) + '"></textarea></td>',
                '</td>',
                '</tr>',
                '</table>',
                '</td>',
                '<td width="40%">',
                '<table width="100%">',
                '<tr>',
                '<td>',
                this.mode == "lost" ? '<label for="arealost">' + _("Area Lost") + '</label></td>' : "",
                this.mode == "lost" ? '<td><textarea id="arealost" data="arealost" rows="4" class="asm-textarea" title="' + html.title(_("Area where the animal was lost")) + '"></textarea></td>' : "",
                this.mode == "found" ? '<label for="areafound">' + _("Area Found") + '</label></td>' : "",
                this.mode == "found" ? '<td><textarea id="areafound" data="areafound" rows="4" class="asm-textarea" title="' + html.title(_("Area where the animal was found")) + '"></textarea></td>' : "",
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="areapostcode">' + _("Zipcode") + '</label></td>',
                '<td><input id="areapostcode" data="areapostcode" type="text" class="asm-textbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="microchip">' + _("Microchip") + '</label></td>',
                '<td><input id="microchip" data="microchip" type="text" maxlength="15" class="asm-textbox" /></td>',
                '</tr>',
                '<tr>',
                '<tr>',
                '<td>',
                '<label for="comments">' + _("Comments") + '</label></td>',
                '<td><textarea id="comments" data="comments" rows="5" class="asm-textarea"></textarea></td>',
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
            $("#add").button().click(function() {
                add_lf_animal("add");
            });

            $("#addedit").button().click(function() {
                add_lf_animal("addedit");
            });

            $("#reset").button().click(function() {
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
