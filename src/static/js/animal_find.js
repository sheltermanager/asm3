/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    var animal_find = {
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
                '<input id="mode" name="mode" type="hidden" value="SIMPLE" />',
                '<input id="q" name="q" class="asm-textbox" />',
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
                '<input id="animalname" name="animalname" class="asm-textbox" />',
                '</td>',
                '<td>',
                '<label for="sheltercode">' + _("Code") + '</label>',
                '</td>',
                '<td>',
                '<input id="sheltercode" name="sheltercode" class="asm-textbox" />',
                '</td>',
                '<td>',
                '<label for="litterid">' + _("Litter") + '</label>',
                '</td>',
                '<td>',
                '<input id="litterid" name="litterid" class="asm-textbox" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="animaltypeid">' + _("Type") + '</label>',
                '</td>',
                '<td>',
                '<select id="animaltypeid" name="animaltypeid" class="asm-selectbox">',
                '<option value="-1">' + _("(all)") + '</option>',
                html.list_to_options(controller.animaltypes, "ID", "ANIMALTYPE"),
                '</select>',
                '</td>',
                '<td>',
                '<label for="speciesid">' + _("Species") + '</label>',
                '</td>',
                '<td>',
                '<select id="speciesid" name="speciesid" class="asm-selectbox">',
                '<option value="-1">' + _("(all)") + '</option>',
                html.list_to_options(controller.species, "ID", "SPECIESNAME"),
                '</select>',
                '</td>',
                '<td>',
                '<label for="breedid">' + _("Breed") + '</label>',
                '</td>',
                '<td>',
                '<select id="breedid" name="breedid" class="asm-selectbox">',
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
                '<select id="sex" name="sex" class="asm-selectbox">',
                '<option value="-1">' + _("(all)") + '</option>',
                html.list_to_options(controller.sexes, "ID", "SEX"),
                '</select>',
                '</td>',
                '<td>',
                '<label for="hasactivereserve">' + _("Reserved") + '</label>',
                '</td>',
                '<td>',
                '<select id="hasactivereserve" name="reserved" class="asm-selectbox">',
                '<option value="both">' + _("(both)") + '</option>',
                '<option value="reserved">' + _("Reserved") + '</option>',
                '<option value="unreserved">' + _("Unreserved") + '</option>',
                '</select>',
                '</td>',
                '<td>',
                '<label for="logicallocation">' + _("Location") + '</label>',
                '</td>',
                '<td>',
                '<select id="logicallocation" name="logicallocation" class="asm-selectbox">',
                '<option value="all">' + _("(all)") + '</option>',
                '<option value="onshelter">' + _("On Shelter") + '</option>',
                '<option value="adoptable">' + _("Adoptable") + '</option>',
                '<option value="adopted">' + _("Adopted") + '</option>',
                '<option value="deceased">' + _("Deceased") + '</option>',
                '<option value="escaped">' + _("Escaped") + '</option>',
                '<option value="fostered">' + _("Fostered") + '</option>',
                '<option value="hold">' + _("Hold") + '</option>',
                '<option value="nonshelter">' + _("Non-Shelter") + '</option>',
                '<option value="notforadoption">' + _("Not For Adoption") + '</option>',
                '<option value="permanentfoster">' + _("Permanent Foster") + '</option>',
                '<option value="quarantine">' + _("Quarantine") + '</option>',
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
                '<select id="shelterlocation" name="shelterlocation" class="asm-selectbox">',
                '<option value="-1">' + _("(all)") + '</option>',
                html.list_to_options(controller.internallocations, "ID", "LOCATIONNAME"),
                '</select>',
                '</td>',
                '<td>',
                '<label for="size">' + _("Size") + '</label>',
                '</td>',
                '<td>',
                '<select id="size" name="size" class="asm-selectbox">',
                '<option value="-1">' + _("(all)") + '</option>',
                html.list_to_options(controller.sizes, "ID", "SIZE"),
                '</select>',
                '</td>',
                '<td>',
                '<label for="colour">' + _("Color") + '</label>',
                '</td>',
                '<td>',
                '<select id="colour" name="colour" class="asm-selectbox">',
                '<option value="-1">' + _("(all)") + '</option>',
                html.list_to_options(controller.colours, "ID", "BASECOLOUR"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="inbetweenfrom">' + _("Entered From") + '</label>',
                '</td>',
                '<td>',
                '<input id="inbetweenfrom" name="inbetweenfrom" class="asm-textbox asm-datebox" />',
                '</td>',
                '<td>',
                '<label for="inbetweento">' + _("Entered To") + '</label>',
                '</td>',
                '<td>',
                '<input id="inbetweento" name="inbetweento" class="asm-textbox asm-datebox" />',
                '</td>',
                '<td>',
                '<label for="microchip">' + _("Microchip Number") + '</label>',
                '</td>',
                '<td>',
                '<input id="microchip" name="microchip" class="asm-textbox" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="outbetweenfrom">' + _("Out Between") + '</label>',
                '</td>',
                '<td>',
                '<input id="outbetweenfrom" name="outbetweenfrom" class="asm-textbox asm-datebox" />',
                '</td>',
                '<td>',
                '<label for="outbetweento">' + _("and") + '</label>',
                '</td>',
                '<td>',
                '<input id="outbetweento" name="outbetweento" class="asm-textbox asm-datebox" />',
                '</td>',
                '<td>',
                '<label for="adoptionno">' + _("Adoption Number") + '</label>',
                '</td>',
                '<td>',
                '<input id="adoptionno" name="adoptionno" class="asm-textbox" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="agedbetweenfrom">' + _("Aged Between") + '</label>',
                '</td>',
                '<td>',
                '<input id="agedbetweenfrom" name="agedbetweenfrom" class="asm-textbox asm-numberbox" title="',
                _("An age in years, eg: 1, 0.5") + '"/>',
                '</td>',
                '<td>',
                '<label for="agedbetweento">' + _("and") + '</label>',
                '</td>',
                '<td>',
                '<input id="agedbetweento" name="agedbetweento" class="asm-textbox asm-numberbox" title="',
                _("An age in years, eg: 1, 0.5") + '" />',
                '</td>',
                '<td>',
                '<label for="agegroup">' + _("Age Group") + '</label>',
                '</td>',
                '<td>',
                '<select id="agegroup" name="agegroup" class="asm-selectbox">',
                '<option value="-1">' + _("(all)") + '</option>',
                html.list_to_options(controller.agegroups),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="comments">' + _("Comments Contain") + '</label>',
                '</td>',
                '<td>',
                '<input id="comments" name="comments" class="asm-textbox" />',
                '</td>',
                '<td>',
                '<label for="hiddencomments">' + _("Hidden Comments") + '</label>',
                '</td>',
                '<td>',
                '<input id="hiddencomments" name="hiddencomments" class="asm-textbox" />',
                '</td>',
                '<td>',
                '<label for="features">' + _("Markings") + '</label>',
                '</td>',
                '<td>',
                '<input id="features" name="features" class="asm-textbox" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="insuranceno">' + _("Insurance No") + '</label>',
                '</td>',
                '<td>',
                '<input id="insuranceno" name="insuranceno" class="asm-textbox" />',
                '</td>',
                '<td>',
                '<label for="rabiestag">' + _("Rabies Tag") + '</label>',
                '</td>',
                '<td>',
                '<input id="rabiestag" name="rabiestag" class="asm-textbox" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="originalowner">' + _("Original Owner") + '</label>',
                '</td>',
                '<td>',
                '<input id="originalowner" name="originalowner" class="asm-textbox" />',
                '</td>',
                '<td>',
                '<label for="medianotes">' + _("Media Notes") + '</label>',
                '</td>',
                '<td>',
                '<input id="medianotes" name="medianotes" class="asm-textbox" />',
                '</td>',
                '</tr>',
                '</table>',
                '<div class="centered bottomborder">',
                '<label for="includedeceased">' + _("Include deceased") + '</label><input id="includedeceased" name="includedeceased" type="checkbox" />',
                '<label for="includenonshelter">' + _("Include non-shelter") + '</label><input id="includenonshelter" name="includenonshelter" type="checkbox" />',
                '</div>',
                '<div class="centered bottomborder">',
                '<label for="goodwithchildren">' + _("Good with children") + '</label><input id="goodwithchildren" name="goodwithchildren" type="checkbox" />',
                '<label for="goodwithcats">' + _("Good with cats") + '</label><input id="goodwithcats" name="goodwithcats" type="checkbox" />',
                '<label for="goodwithdogs">' + _("Good with dogs") + '</label><input id="goodwithdogs" name="goodwithdogs" type="checkbox" />',
                '<label for="housetrained">' + _("Housetrained") + '</label><input id="housetrained" name="housetrained" type="checkbox" />',
                '</div>',
                '<div class="centered bottomborder">',
                '<label for="showtransfersonly">' + _("Only show transfers") + '</label><input id="showtransfersonly" name="showtransfersonly" type="checkbox" />',
                '<label for="showpickupsonly">' + _("Only show pickups") + '</label><input id="showpickupsonly" name="showpickupsonly" type="checkbox" />',
                '<label for="showcrueltycaseonly">' + _("Only show cruelty cases") + '</label><input id="showcrueltycaseonly" name="showcrueltycaseonly" type="checkbox" />',
                '<label for="showspecialneedsonly">' + _("Only show special needs") + '</label><input id="showspecialneedsonly" name="showspecialneedsonly" type="checkbox" />',
                '</div>',
                '</div>',
                '<p class="centered">',
                '<button type="submit" id="searchbutton">' + _("Search") + '</button>',
                '</p>',
                '</form>',
                html.content_footer()
            ].join("\n");
        },

        bind: function() {
            // Switch to simple search criteria
            var simpleMode = function() {
                $("#mode").val("SIMPLE");
                $("#asm-search-selector-advanced").removeClass("asm-link-disabled");
                $("#asm-search-selector-simple").addClass("asm-link-disabled");
                $("#asm-criteria-advanced").slideUp(function() {
                    $("#asm-criteria-simple").slideDown(function() {
                        $("input[name='q']").focus();
                    });
                });
            };

            // Switch to advanced search criteria
            var advancedMode = function() {
                $("#mode").val("ADVANCED");
                $("input[name='q']").val("");
                $("#asm-search-selector-simple").removeClass("asm-link-disabled");
                $("#asm-search-selector-advanced").addClass("asm-link-disabled");
                $("#asm-criteria-simple").slideUp(function() {
                    $("#asm-criteria-advanced").slideDown(function() {
                        $("input[name='animalname']").focus();
                    });
                });
            };

            // Handle switching between modes via the links
            $("#asm-search-selector-simple").click(function() {
                simpleMode();
            });

            $("#asm-search-selector-advanced").click(function() {
                advancedMode();
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
                $("#includedeceased").prop("checked", true);
                $("#includenonshelter").prop("checked", true);
            }

            // Only show the breeds for the selected species
            // The (all) option is displayed by default
            var changebreedselect1 = function() {
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

            // Search button
            $("#searchbutton").button();

        }
    };

    common.module(animal_find, "animal_find", "criteria");

});
