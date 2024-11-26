/*global $, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const animal_find = {

        options_filter: [ '<option value="goodwithchildren">' + _("Good with children") + '</option>',
                '<option value="goodwithcats">' + _("Good with cats") + '</option>',
                '<option value="goodwithdogs">' + _("Good with dogs") + '</option>',
                '<option value="housetrained">' + _("Housetrained") + '</option>',
                '<option value="fivplus">' + _("FIV+") + '</option>',
                '<option value="flvplus">' + _("FLV+") + '</option>',
                '<option value="heartwormplus">' + _("Heartworm+") + '</option>',
                '<option value="heartwormneg">' + _("Heartworm-") + '</option>',
                '<option value="unaltered">' + _("Unaltered") + '</option>',
                '<option value="includedeceased">' + _("Include deceased animals") + '</option>',
                '<option value="includenonshelter">' + _("Include non-shelter animals") + '</option>',
                '<option value="showtransfersonly">' + _("Only show transfers") + '</option>',
                '<option value="showpickupsonly">' + _("Only show pickups") + '</option>',
                '<option value="showspecialneedsonly">' + _("Only show special needs") + '</option>',
                '<option value="showdeclawedonly">' + _("Only show declawed") + '</option>' ].join("\n"),

        options_reserved: [ '<option value="both">' + _("(both)") + '</option>',
                '<option value="reserved">' + _("Reserved") + '</option>',
                '<option value="unreserved">' + _("Unreserved") + '</option>' ].join("\n"),

        options_locations: [ '<option value="all">' + _("(all)") + '</option>',
                '<option value="onshelter">' + _("On Shelter") + '</option>',
                '<option value="adoptable">' + _("Adoptable") + '</option>',
                '<option value="adopted">' + _("Adopted") + '</option>',
                '<option value="deceased">' + _("Deceased") + '</option>',
                '<option value="escaped">' + _("Escaped") + '</option>',
                '<option value="fostered">' + _("Fostered") + '</option>',
                '<option value="hold">' + _("Hold") + '</option>',
                '<option value="permanentfoster">' + _("Permanent Foster") + '</option>',
                '<option value="reclaimed">' + _("Reclaimed") + '</option>',
                '<option value="releasedtowild">' + _("Released To Wild") + '</option>',
                '<option value="reserved">' + _("Reserved") + '</option>',
                '<option value="retailer">' + _("Retailer") + '</option>',
                '<option value="stolen">' + _("Stolen") + '</option>',
                '<option value="transferred">' + _("Transferred") + '</option>' ].join("\n"),


        render: function() {
            let col1 = [
                html.search_field_text("animalname", _("Name")),
                html.search_field_text("sheltercode", _("Code")),
                html.search_field_text("litterid", _("Litter")),
                html.search_field_select("animaltypeid", _("Type"), html.list_to_options(controller.animaltypes, "ID", "ANIMALTYPE")),
                html.search_field_select("speciesid", _("Species"), html.list_to_options(controller.species, "ID", "SPECIESNAME")),
                html.search_field_select("breedid", _("Breed"), html.list_to_options_breeds(controller.breeds)),
                html.search_field_select("sex", _("Sex"), html.list_to_options(controller.sexes, "ID", "SEX")),
                html.search_field_select("reserved", _("Reserved"), animal_find.options_reserved, false),
                html.search_field_select("logicallocation", _("Location"), animal_find.options_locations),
                html.search_field_select("shelterlocation", _("Internal Location"), html.list_to_options(controller.internallocations, "ID", "LOCATIONNAME")),
                html.search_field_select("size", _("Size"), html.list_to_options(controller.sizes, "ID", "SIZE")),
                html.search_field_select("colour", _("Color"), html.list_to_options(controller.colours, "ID", "BASECOLOUR")),
                html.search_field_numberrange("agedbetweenfrom", "agedbetweento", _("Aged Between")),
                html.search_field_select("agegroup", _("Age Group"), html.list_to_options(controller.agegroups)),
            ].join("\n");
            let col2 = [
                html.search_field_daterange("inbetweenfrom", "inbetweento", _("Entered Between")),
                html.search_field_daterange("outbetweenfrom", "outbetweento", _("Out Between")),
                html.search_field_select("entrytype", _("Entry Type"), html.list_to_options(controller.entrytypes, "ID", "ENTRYTYPENAME")),
                html.search_field_select("entryreason", _("Entry Category"), html.list_to_options(controller.entryreasons, "ID", "REASONNAME")),
                html.search_field_text("reasonforentry", _("Reason For Entry")),
                html.search_field_select("pickuplocation", _("Pickup Location"), html.list_to_options(controller.pickuplocations, "ID", "LOCATIONNAME")),
                html.search_field_text("pickupaddress", _("Pickup Address")),
                html.search_field_select("diet", _("Diet"), html.list_to_options(controller.diettypes, "ID", "DIETNAME")),
                html.search_field_select("jurisdiction", _("Jurisdiction"), html.list_to_options(controller.jurisdiction, "ID", "JURISDICTIONNAME")),
                html.search_field_text("adoptionno", _("Movement Number")),
                html.search_field_text("insuranceno", _("Insurance No")),
                html.search_field_text("rabiestag", _("Rabies Tag")),
                html.search_field_text("comments", _("Description Contains")),
                html.search_field_text("hiddencomments", _("Hidden Comments")),
            ].join("\n");
            let col3 = [ 
                html.search_field_text("features", _("Markings")),
                html.search_field_text("microchip", _("Microchip Number")),
                html.search_field_text("tattoo", _("Tattoo Number")),
                html.search_field_text("originalowner", _("Original Owner")),
                html.search_field_text("medianotes", _("Media Notes")),
                html.search_field_select("createdby", _("Created By"), '<option value="">' + _("(anyone)") + '</option>' + html.list_to_options(controller.users, "USERNAME", "USERNAME"), false),
                html.search_field_mselect("filter", _("Filter"), animal_find.options_filter), 
                html.search_field_mselect("flags", _("Flags"), ""),
            ].join("\n");
            return [
                html.content_header(_("Find Animal")),
                '<form id="animalsearchform" action="animal_find_results" method="GET">',
                '<p class="asm-search-selector">',
                '<a id="asm-search-selector-simple" href="#">' + _("Simple") + '</a> |',
                '<a id="asm-search-selector-advanced" href="#">' + _("Advanced") + '</a>',
                '</p>',
                '<div id="asm-criteria-simple">',
                '<table class="asm-table-layout">',
                '<tr>',
                '<td>',
                '<label for="q">' + _("Search") + '</label>',
                '</td>',
                '<td>',
                '<input id="mode" data="mode" type="hidden" value="SIMPLE" />',
                '<input id="q" data="q" type="search" class="asm-textbox" />',
                '</td>',
                '</tr>',
                '</table>',
                '</div>',
                '<div id="asm-criteria-advanced">',
                html.search_row([
                    html.search_column(col1),
                    html.search_column(col2),
                    html.search_column(col3),
                    html.search_column(additional.additional_search_fields(controller.additionalfields, 1)),
                ]),
                '</div>', 
                '<p class="centered">',
                '<button type="button" id="searchbutton">' + _("Search") + '</button>',
                '</p>',
                '</form>',
                html.content_footer()
            ].join("\n");
        },

        bind: function() {
            // Switch to simple search criteria
            const simpleMode = function() {
                $("#mode").val("SIMPLE");
                $("#asm-search-selector-advanced").removeClass("asm-link-disabled");
                $("#asm-search-selector-simple").addClass("asm-link-disabled");
                $("#asm-criteria-advanced").slideUp(function() {
                    $("#asm-criteria-simple").slideDown(function() {
                        $("input[data='q']").focus();
                    });
                });
            };

            // Switch to advanced search criteria
            const advancedMode = function() {
                $("#mode").val("ADVANCED");
                $("input[data='q']").val("");
                $("#asm-search-selector-simple").removeClass("asm-link-disabled");
                $("#asm-search-selector-advanced").addClass("asm-link-disabled");
                $("#asm-criteria-simple").slideUp(function() {
                    $("#asm-criteria-advanced").slideDown(function() {
                        $("input[data='animalname']").focus();
                    });
                });
            };

            // Handle switching between modes via the links
            $("#asm-search-selector-simple").click(function() {
                simpleMode();
                return false;
            });

            $("#asm-search-selector-advanced").click(function() {
                advancedMode();
                return false;
            });

            // Search button - we don't use the traditional submit because
            // the bsmselect widget craps extra values into the form and 
            // breaks the filter
            $("#searchbutton").button().click(function() {
                if (config.bool("AnimalSearchResultsNewTab")) {
                    window.open("animal_find_results?" + $("#animalsearchform input, #animalsearchform select").toPOST(), "_blank");
                } else {
                    common.route("animal_find_results?" + $("#animalsearchform input, #animalsearchform select").toPOST());
                }
            });

            // We need to re-enable the return key submitting the form
            $("#animalsearchform").keypress(function(e) {
                if (e.keyCode == 13) {
                    if (config.bool("AnimalSearchResultsNewTab")) {
                        window.open("animal_find_results?" + $("#animalsearchform input, #animalsearchform select").toPOST(), "_blank");
                    } else {
                        common.route("animal_find_results?" + $("#animalsearchform input, #animalsearchform select").toPOST());
                    }
                }
            });

            // Get the default mode and set that
            $("#asm-criteria-simple").hide();
            $("#asm-criteria-advanced").hide();
            $("#asm-content").show();
            if (config.bool("AdvancedFindAnimal")) {
                advancedMode();
            }
            else {
                simpleMode();
            }
            if (config.bool("AdvancedFindAnimalOnShelter")) {
                $("#logicallocation").select("value", "onshelter");
            }
            else {
                $("#logicallocation").select("value", "all");
                $("#filter option[value='includedeceased']").prop("selected", true);
                $("#filter option[value='includenonshelter']").prop("selected", true);
                $("#filter").change();
            }

            // Load animal flags
            html.animal_flag_options(controller.animal, controller.flags, $("#flags"));

            // Search button
            $("#searchbutton").button();

        },

        name: "animal_find",
        animation: "criteria",
        title: function() { return _("Find Animal"); },

        routes: {
            "animal_find": function() {
                common.module_loadandstart("animal_find", "animal_find");
            }
        }

    };

    common.module_register(animal_find);

});
