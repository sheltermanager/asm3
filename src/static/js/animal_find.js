/*global $, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const animal_find = {

        render: function() {
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
                '<table class="asm-table-layout">',
                '<tr>',
                '<td>',
                '<label for="animalname">' + _("Name") + '</label>',
                '</td>',
                '<td>',
                '<input id="animalname" data="animalname" class="asm-textbox" />',
                '</td>',
                '<td>',
                '<label for="sheltercode">' + _("Code") + '</label>',
                '</td>',
                '<td>',
                '<input id="sheltercode" data="sheltercode" class="asm-textbox" />',
                '</td>',
                '<td>',
                '<label for="litterid">' + _("Litter") + '</label>',
                '</td>',
                '<td>',
                '<input id="litterid" data="litterid" class="asm-textbox" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="animaltypeid">' + _("Type") + '</label>',
                '</td>',
                '<td>',
                '<select id="animaltypeid" data="animaltypeid" class="asm-selectbox">',
                '<option value="-1">' + _("(all)") + '</option>',
                html.list_to_options(controller.animaltypes, "ID", "ANIMALTYPE"),
                '</select>',
                '</td>',
                '<td>',
                '<label for="speciesid">' + _("Species") + '</label>',
                '</td>',
                '<td>',
                '<select id="speciesid" data="speciesid" class="asm-selectbox">',
                '<option value="-1">' + _("(all)") + '</option>',
                html.list_to_options(controller.species, "ID", "SPECIESNAME"),
                '</select>',
                '</td>',
                '<td>',
                '<label for="breedid">' + _("Breed") + '</label>',
                '</td>',
                '<td>',
                '<select id="breedid" data="breedid" class="asm-selectbox">',
                '<option value="-1">' + _("(all)") + '</option>',
                html.list_to_options_breeds(controller.breeds),
                '</select>',
                '<select id="breedp" data="breedp" class="asm-selectbox" style="display:none;">',
                '<option value="-1">' + _("(all)") + '</option>',
                html.list_to_options_breeds(controller.breeds),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="sex">' + _("Sex") + '</label>',
                '</td>',
                '<td>',
                '<select id="sex" data="sex" class="asm-selectbox">',
                '<option value="-1">' + _("(all)") + '</option>',
                html.list_to_options(controller.sexes, "ID", "SEX"),
                '</select>',
                '</td>',
                '<td>',
                '<label for="hasactivereserve">' + _("Reserved") + '</label>',
                '</td>',
                '<td>',
                '<select id="hasactivereserve" data="reserved" class="asm-selectbox">',
                '<option value="both">' + _("(both)") + '</option>',
                '<option value="reserved">' + _("Reserved") + '</option>',
                '<option value="unreserved">' + _("Unreserved") + '</option>',
                '</select>',
                '</td>',
                '<td>',
                '<label for="logicallocation">' + _("Location") + '</label>',
                '</td>',
                '<td>',
                '<select id="logicallocation" data="logicallocation" class="asm-selectbox">',
                '<option value="all">' + _("(all)") + '</option>',
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
                '<option value="transferred">' + _("Transferred") + '</option>',
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="shelterlocation">' + _("Internal Location") + '</label>',
                '</td>',
                '<td>',
                '<select id="shelterlocation" data="shelterlocation" class="asm-selectbox">',
                '<option value="-1">' + _("(all)") + '</option>',
                html.list_to_options(controller.internallocations, "ID", "LOCATIONNAME"),
                '</select>',
                '</td>',
                '<td>',
                '<label for="size">' + _("Size") + '</label>',
                '</td>',
                '<td>',
                '<select id="size" data="size" class="asm-selectbox">',
                '<option value="-1">' + _("(all)") + '</option>',
                html.list_to_options(controller.sizes, "ID", "SIZE"),
                '</select>',
                '</td>',
                '<td>',
                '<label for="colour">' + _("Color") + '</label>',
                '</td>',
                '<td>',
                '<select id="colour" data="colour" class="asm-selectbox">',
                '<option value="-1">' + _("(all)") + '</option>',
                html.list_to_options(controller.colours, "ID", "BASECOLOUR"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="agedbetweenfrom">' + _("Aged Between") + '</label>',
                '</td>',
                '<td>',
                '<input id="agedbetweenfrom" data="agedbetweenfrom" class="asm-textbox asm-numberbox" title="',
                _("An age in years, eg: 1, 0.5") + '"/>',
                '</td>',
                '<td>',
                '<label for="agedbetweento">' + _("and") + '</label>',
                '</td>',
                '<td>',
                '<input id="agedbetweento" data="agedbetweento" class="asm-textbox asm-numberbox" title="',
                _("An age in years, eg: 1, 0.5") + '" />',
                '</td>',
                '<td>',
                '<label for="agegroup">' + _("Age Group") + '</label>',
                '</td>',
                '<td>',
                '<select id="agegroup" data="agegroup" class="asm-selectbox">',
                '<option value="-1">' + _("(all)") + '</option>',
                html.list_to_options(controller.agegroups),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="inbetweenfrom">' + _("Entered Between") + '</label>',
                '</td>',
                '<td>',
                '<input id="inbetweenfrom" data="inbetweenfrom" class="asm-textbox asm-datebox" />',
                '</td>',
                '<td>',
                '<label for="inbetweento">' + _("and") + '</label>',
                '</td>',
                '<td>',
                '<input id="inbetweento" data="inbetweento" class="asm-textbox asm-datebox" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="entrytype">' + _("Entry Type") + '</label>',
                '</td>',
                '<td>',
                '<select id="entrytype" data="entrytype" class="asm-selectbox">',
                '<option value="-1">' + _("(all)") + '</option>',
                html.list_to_options(controller.entrytypes, "ID", "ENTRYTYPENAME"),
                '</select>',
                '</td>',
                '<td>',
                '<label for="entryreason">' + _("Entry Category") + '</label>',
                '</td>',
                '<td>',
                '<select id="entryreason" data="entryreason" class="asm-selectbox">',
                '<option value="-1">' + _("(all)") + '</option>',
                html.list_to_options(controller.entryreasons, "ID", "REASONNAME"),
                '</select>',
                '</td>',
                '<td>',
                '<label for="reasonforentry">' + _("Reason For Entry") + '</label>',
                '</td>',
                '<td>',
                '<input id="reasonforentry" data="features" class="asm-textbox" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="pickuplocation">' + _("Pickup Location") + '</label>',
                '</td>',
                '<td>',
                '<select id="pickuplocation" data="pickuplocation" class="asm-selectbox">',
                '<option value="-1">' + _("(all)") + '</option>',
                html.list_to_options(controller.pickuplocations, "ID", "LOCATIONNAME"),
                '</select>',
                '</td>',
                '<td>',
                '<label for="pickupaddress">' + _("Pickup Address") + '</label>',
                '</td>',
                '<td>',
                '<input id="pickupaddress" data="pickupaddress" class="asm-textbox" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="diet">' + _("Diet") + '</label>',
                '</td>',
                '<td>',
                '<select id="diet" data="diet" class="asm-selectbox">',
                '<option value="-1">' + _("(all)") + '</option>',
                html.list_to_options(controller.diettypes, "ID", "DIETNAME"),
                '</select>',
                '</td>',
                '<td>',
                '<label for="jurisdiction">' + _("Jurisdiction") + '</label>',
                '</td>',
                '<td>',
                '<select id="jurisdiction" data="jurisdiction" class="asm-selectbox">',
                '<option value="-1">' + _("(all)") + '</option>',
                html.list_to_options(controller.jurisdictions, "ID", "JURISDICTIONNAME"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="outbetweenfrom">' + _("Out Between") + '</label>',
                '</td>',
                '<td>',
                '<input id="outbetweenfrom" data="outbetweenfrom" class="asm-textbox asm-datebox" />',
                '</td>',
                '<td>',
                '<label for="outbetweento">' + _("and") + '</label>',
                '</td>',
                '<td>',
                '<input id="outbetweento" data="outbetweento" class="asm-textbox asm-datebox" />',
                '</td>',
                '<td>',
                '<label for="adoptionno">' + _("Movement Number") + '</label>',
                '</td>',
                '<td>',
                '<input id="adoptionno" data="adoptionno" class="asm-textbox" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="comments">' + _("Description Contains") + '</label>',
                '</td>',
                '<td>',
                '<input id="comments" data="comments" class="asm-textbox" />',
                '</td>',
                '<td>',
                '<label for="hiddencomments">' + _("Hidden Comments") + '</label>',
                '</td>',
                '<td>',
                '<input id="hiddencomments" data="hiddencomments" class="asm-textbox" />',
                '</td>',
                '<td>',
                '<label for="features">' + _("Markings") + '</label>',
                '</td>',
                '<td>',
                '<input id="features" data="features" class="asm-textbox" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="microchip">' + _("Microchip Number") + '</label>',
                '</td>',
                '<td>',
                '<input id="microchip" data="microchip" class="asm-textbox" />',
                '</td>',
                '<td>',
                '<label for="tattoo">' + _("Tattoo Number") + '</label>',
                '</td>',
                '<td>',
                '<input id="tattoo" data="tattoo" class="asm-textbox" />',
                '</td>',
                '<td>',
                '<label for="createdby">' + _("Created By") + '</label>',
                '</td>',
                '<td>',
                '<select id="createdby" data="createdby" class="asm-selectbox">',
                '<option value="">' + _("(anyone)") + '</option>',
                html.list_to_options(controller.users, "USERNAME", "USERNAME"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="insuranceno">' + _("Insurance No") + '</label>',
                '</td>',
                '<td>',
                '<input id="insuranceno" data="insuranceno" class="asm-textbox" />',
                '</td>',
                '<td>',
                '<label for="rabiestag">' + _("Rabies Tag") + '</label>',
                '</td>',
                '<td>',
                '<input id="rabiestag" data="rabiestag" class="asm-textbox" />',
                '</td>',
                '<td>',
                '<label for="filter">' + _("Filter") + '</label>',
                '</td>',
                '<td>',
                '<select id="filter" data="filter" multiple="multiple" class="asm-bsmselect">',
                '<option value="goodwithchildren">' + _("Good with children") + '</option>',
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
                '<option value="showdeclawedonly">' + _("Only show declawed") + '</option>',
                '</select>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="originalowner">' + _("Original Owner") + '</label>',
                '</td>',
                '<td>',
                '<input id="originalowner" data="originalowner" class="asm-textbox" />',
                '</td>',
                '<td>',
                '<label for="medianotes">' + _("Media Notes") + '</label>',
                '</td>',
                '<td>',
                '<input id="medianotes" data="medianotes" class="asm-textbox" />',
                '</td>',
                '<td>',
                '<label for="flags">' + _("Flags") + '</label>',
                '</td>',
                '<td>',
                '<select id="flags" data="flags" class="asm-bsmselect" multiple="multiple">',
                '</select>',
                '</td>',
                '</tr>',
                '<tr><td colspan="6"><hr></td></tr>',
                additional.additional_search_fields(controller.additionalfields, 3),
                '</table>',
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
                common.route("animal_find_results?" + $("#animalsearchform input, #animalsearchform select").toPOST());
            });

            // We need to re-enable the return key submitting the form
            $("#animalsearchform").keypress(function(e) {
                if (e.keyCode == 13) {
                    common.route("animal_find_results?" + $("#animalsearchform input, #animalsearchform select").toPOST());
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

            // Only show the breeds for the selected species
            // The (all) option is displayed by default
            const changebreedselect1 = function() {
                $('optgroup', $('#breedid')).remove();
                $('#breedp optgroup').clone().appendTo($('#breedid'));

                // Only filter if we have a species selected
                if ($("#speciesid").val() != -1) {
                    $('#breedid').children().each(function(){
                        if($(this).attr('id') != 'ngp-'+$('#speciesid').val()){
                            $(this).remove();
                        }
                    });
                }
                $('#breedid').append("<option value='-1'>" + _("(all)") + "</option>");
                $('#breedid').val(-1);
            };
                
            changebreedselect1();

            $('#speciesid').change(function() {
                changebreedselect1();
            });

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
