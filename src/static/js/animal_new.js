/*global $, jQuery, _, additional, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const animal_new = {

        /** Only attempt to set the non-shelter animal type once per reset */
        set_nonsheltertype_once: false,

        render: function() {
            return [
                '<div id="dialog-similar" style="display: none" title="' + _("Similar Animal") + '">',
                '<p><span class="ui-icon ui-icon-alert"></span>',
                _("This animal has the same name as another animal recently added to the system.") + '<br /><br />',
                '<span class="similar-animal"></span>',
                '</p>',
                '</div>',
                html.content_header(_("Add a new animal")),
                '<table class="asm-table-layout">',
                '<tr id="nonshelterrow">',
                '<td></td>',
                '<td><input type="checkbox" class="asm-checkbox" data="nonshelter" id="nonshelter" />',
                '<label for="nonshelter">' + _("Non-Shelter") + '</label>',
                '<span id="callout-nonshelter" class="asm-callout">',
                _("This animal should not be shown in figures and is not in the custody of the shelter"),
                '</span>',
                '</td>',
                '</tr>',
                '<tr id="transferinrow">',
                '<td></td>',
                '<td>',
                '<span style="white-space: nowrap">',
                '<input class="asm-checkbox" type="checkbox" id="transferin" />',
                '<label for="transferin">' + _("Transfer In") + '</label>',
                '</span>',
                '</td>',
                '</tr>',
                '<tr id="holdrow">',
                '<td></td>',
                '<td>',
                '<span style="white-space: nowrap">',
                '<input class="asm-checkbox" type="checkbox" id="hold" data-post="hold" />',
                '<label for="hold">' + _("Hold until") + '</label>',
                '<input class="asm-halftextbox asm-datebox" id="holduntil" data-post="holduntil" />',
                '<span id="callout-holduntil" class="asm-callout">',
                _("Hold the animal until this date or blank to hold indefinitely"),
                '</span>',
                '</span>',
                '</td>',
                '</tr>',
                '<tr id="nsownerrow">',
                '<td><label for="nsowner">' + _("Owner") + '</label></td>',
                '<td>',
                '<div style="margin: 0; width: 315px;">',
                '<input id="nsowner" data="nsowner" class="asm-personchooser" type="hidden" value="" />',
                '</div>',
                '</td>',
                '</tr>',
                '<tr id="coderow">',
                '<td><label for="sheltercode">' + _("Code") + '</label></td>',
                '<td nowrap="nowrap">',
                '<input type="text" id="sheltercode" data="sheltercode" class="asm-halftextbox" title="',
                html.title(_("The shelter reference number")) + '" />',
                '<input type="text" id="shortcode" data="shortcode" class="asm-halftextbox" title="',
                html.title(_("A short version of the reference number")) + '" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="animalname">' + _("Name") + '</label>',
                '</td>',
                '<td>',
                '<input id="animalname" data="animalname" class="asm-textbox" />',
                '<button id="button-randomname">' + _("Generate a random name for this animal") + '</button>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="dateofbirth">' + _("Date of Birth") + '</label></td>',
                '<td>',
                '<input id="dateofbirth" data="dateofbirth" class="asm-textbox asm-datebox" title=',
                '"' + html.title(_("The date the animal was born")) + '" />',
                ' <label for="estimatedage">' + _("or estimated age in years") + '</label> ',
                '<input type="text" id="estimatedage" data="estimatedage" class="asm-textbox asm-numberbox" value="" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="sex">' + _("Sex") + '</label>',
                '</td>',
                '<td>',
                '<select id="sex" data="sex" class="asm-selectbox">',
                html.list_to_options(controller.sexes, "ID", "SEX"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="animaltype">' + _("Type") + '</label>',
                '</td>',
                '<td>',
                '<select id="animaltype" data="animaltype" class="asm-selectbox">',
                html.list_to_options(controller.animaltypes, "ID", "ANIMALTYPE"), 
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="species">' + _("Species") + '</label>',
                '</td>',
                '<td>',
                '<select id="species" data="species" class="asm-selectbox">',
                html.list_to_options(controller.species, "ID", "SPECIESNAME"),
                '</select>',
                '</td>',
                '</tr>',
                '',
                '<tr id="breedrow">',
                '<td>',
                '<label for="breed1">' + _("Breed") + '</label>',
                '</td>',
                '<td>',
                '<select id="breed1" data="breed1" class="asm-selectbox">',
                html.list_to_options_breeds(controller.breeds),
                '</select>',
                '<select id="breedp" data="breedp" class="asm-selectbox" style="display:none;">',
                html.list_to_options_breeds(controller.breeds),
                '</select>',
                '<span id="crossbreedcol">',
                '<input id="crossbreed" data="crossbreed" type="checkbox" class="asm-checkbox" />',
                '<label for="crossbreed">' + _("Crossbreed") + '</label>',
                '</span> ',
                '<span id="secondbreedcol">',
                '<select id="breed2" data="breed2" class="asm-selectbox">',
                html.list_to_options_breeds(controller.breeds),
                '</select>',
                '</span>',
                '</td>',
                '</tr>',
                '<tr id="colourrow">',
                '<td>',
                '<label for="basecolour">' + _("Base Color") + '</label>',
                '</td>',
                '<td>',
                '<select id="basecolour" data="basecolour" class="asm-selectbox">',
                html.list_to_options(controller.colours, "ID", "BASECOLOUR"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr id="coattyperow">',
                '<td><label for="coattype">' + _("Coat Type") + '</label></td>',
                '<td><select id="coattype" data="coattype" class="asm-selectbox">',
                html.list_to_options(controller.coattypes, "ID", "COATTYPE"),
                '</select></td>',
                '</tr>',
                '<tr id="locationrow">',
                '<td>',
                '<label for="internallocation">' + _("Internal Location") + '</label>',
                '</td>',
                '<td>',
                '<select id="internallocation" data="internallocation" class="asm-selectbox">',
                html.list_to_options(controller.internallocations, "ID", "LOCATIONNAME"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr id="locationunitrow">',
                '<td><label for="unit">' + _("Unit") + '</label>',
                '<span id="callout-unit" class="asm-callout">',
                _("Unit within the location, eg: pen or cage number"),
                '</span>',
                '</td>',
                '<td>',
                '<select id="unit" data="unit" class="asm-selectbox">',
                '</select>',
                '</td>',
                '</tr>',
                '<tr id="fostererrow">',
                '<td>',
                '<label for="fosterer">' + _("Fosterer") + '</label>',
                '</td>',
                '<td>',
                '<div style="margin: 0; width: 315px;">',
                '<input id="fosterer" data="fosterer" data-filter="fosterer" class="asm-personchooser" type="hidden" value="" />',
                '</div>',
                '</td>',
                '</tr>',
                '<tr id="coordinatorrow">',
                '<td>',
                '<label for="coordinator">' + _("Adoption Coordinator") + '</label>',
                '</td>',
                '<td>',
                '<div style="margin: 0; width: 315px;">',
                '<input id="coordinator" data="adoptioncoordinator" data-filter="coordinator" type="hidden" class="asm-personchooser" />',
                '</div>',
                '</td>',
                '</tr>',
                '<tr id="sizerow">',
                '<td>',
                '<label for="size">' + _("Size") + '</label>',
                '</td>',
                '<td>',
                '<select id="size" data="size" class="asm-selectbox">',
                html.list_to_options(controller.sizes, "ID", "SIZE"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr id="kilosrow">',
                '<td><label for="weight">' + _("Weight") + '</label></td>',
                '<td><span style="white-space: nowrap;">',
                '<input id="weight" data-json="WEIGHT" data-post="weight" class="asm-textbox asm-halftextbox asm-numberbox" />',
                '<label id="kglabel">' + _("kg") + '</label>',
                '</span>',
                '</td>',
                '</tr>',
                '<tr id="poundsrow">',
                '<td><label for="weightlb">' + _("Weight") + '</label></td>',
                '<td><span style="white-space: nowrap;">',
                '<input id="weightlb" class="asm-textbox asm-intbox" style="width: 70px" />',
                '<label id="lblabel">' + _("lb") + '</label>',
                '<input id="weightoz" class="asm-textbox asm-intbox" style="width: 70px" />',
                '<label id="ozlabel">' + _("oz") + '</label>',
                '</span>',
                '</td>',
                '</tr>',
                '<tr id="neuteredrow">',
                '<td>',
                '<label for="neutereddate">' + _("Altered") + '</label>',
                '</td>',
                '<td>',
                '<input id="neutered" data="neutered" type="checkbox" class="asm-checkbox" />',
                '<input id="neutereddate" data="neutereddate" class="asm-textbox asm-datebox" />',
                '</td>',
                '</tr>',
                '<tr id="microchiprow">',
                '<td>',
                '<label for="microchipdate">' + _("Microchipped") + '</label>',
                '</td>',
                '<td>',
                '<input id="microchipped" data="microchipped" type="checkbox" class="asm-checkbox" />',
                '<input id="microchipdate" data="microchipdate" class="asm-textbox asm-datebox" placeholder="',
                html.title(_("Date")) + '" />',
                '<input type="text" id="microchipnumber" data="microchipnumber" maxlength="15" class="asm-textbox" placeholder="', 
                html.title(_("Number")) + '" />',
                '</td>',
                '</tr>',
                '<tr id="tattoorow">',
                '<td>',
                '<label for="tattoodate">' + _("Tattoo") + '</label>',
                '</td>',
                '<td>',
                '<input id="tattoo" data="tattoo" type="checkbox" class="asm-checkbox" />',
                '<input id="tattoodate" data="tattoodate" class="asm-textbox asm-datebox" placeholder="',
                html.title(_("Date")) + '" />',
                '<input type="text" id="tattoonumber" data="tattoonumber" class="asm-textbox" placeholder="',
                html.title(_("Number")) + '" />',
                '</td>',
                '</tr>',
                '<tr id="litterrow">',
                '<td>',
                '<label for="litterid">' + _("Litter") + '</label>',
                '</td>',
                '<td>',
                '<input id="litterid" data="litterid" class="asm-textbox" />',
                '</td>',
                '</tr>',
                '<tr id="entrytyperow">',
                '<td><label for="entrytype">' + _("Entry Type") + '</label></td>',
                '<td>',
                '<select id="entrytype" data="entrytype" class="asm-selectbox">',
                html.list_to_options(controller.entrytypes, "ID", "ENTRYTYPENAME"), 
                '</select>',
                '</td>',
                '</tr>',
                '<tr id="entryreasonrow">',
                '<td><label for="entryreason">' + _("Entry Category") + '</label></td>',
                '<td><select id="entryreason" data="entryreason" class="asm-selectbox">',
                html.list_to_options(controller.entryreasons, "ID", "REASONNAME"),
                '</select></td>',
                '</tr>',
                '<tr id="jurisdictionrow">',
                '<td><label for="jurisdiction">' + _("Jurisdiction") + '</label></td>',
                '<td><select id="jurisdiction" data="jurisdiction" class="asm-selectbox">',
                html.list_to_options(controller.jurisdictions, "ID", "JURISDICTIONNAME"),
                '</select></td>',
                '</tr>',
                '<tr id="feerow">',
                '<td><label for="fee">' + _("Adoption Fee") + '</label></td>',
                '<td><input id="fee" data-post="fee" class="asm-currencybox asm-textbox" value="0" /></td>',
                '</tr>',
                '<tr id="originalownerrow">',
                '<td><label for="originalowner">' + _("Original Owner") + '</label></td>',
                '<td>',
                '<div style="margin: 0; width: 315px;">',
                '<input id="originalowner" data="originalowner" class="asm-personchooser" type="hidden" value="" />',
                '</div>',
                '</td>',
                '<tr id="pickuprow">',
                '<td>',
                '<label for="pickedup">' + _("Picked Up") + '</label>',
                '</td>',
                '<td>',
                '<input id="pickedup" data="pickedup" type="checkbox" class="asm-checkbox" />',
                '<select class="asm-selectbox" id="pickuplocation" data-post="pickuplocation">',
                '<option value="0"></option>',
                html.list_to_options(controller.pickuplocations, "ID", "LOCATIONNAME"),
                '</select>',
                '<input class="asm-textbox" id="pickupaddress" data-post="pickupaddress" placeholder="',
                html.title(_("Pickup Address")) + '" />',
                '</td>',
                '</tr>',
                '<tr id="broughtinbyrow">',
                '<td><label for="broughtinby">' + _("Brought In By") + '</label></td>',
                '<td>',
                '<div style="margin: 0; width: 315px;">',
                '<input id="broughtinby" data="broughtinby" class="asm-personchooser" type="hidden" value="" />',
                '</div>',
                '</td>',
                '</tr>',
                '<tr id="datebroughtinrow">',
                '<td>',
                '<label for="datebroughtin">' + _("Date Brought In") + '</label>',
                '</td>',
                '<td>',
                '<input id="datebroughtin" data="datebroughtin" class="asm-textbox asm-datebox" />',
                '</td>',
                '</tr>',
                '<tr id="timebroughtinrow">',
                '<td>',
                '<label for="timebroughtin">' + _("Time Brought In") + '</label>',
                '</td>',
                '<td>',
                '<input id="timebroughtin" data="timebroughtin" class="asm-textbox asm-timebox" />',
                '</td>',
                '</tr>',
                additional.additional_new_fields(controller.additional),
                '</table>',
                '<p></p>',
                '<div class="centered">',
                '<button id="addedit">' + html.icon("animal-add") + ' ' + _("Create and edit") + '</button>',
                '<button id="add">' + html.icon("animal-add") + ' ' + _("Create") + '</button>',
                '<button id="reset">' + html.icon("delete") + ' ' + _("Reset") + '</button>',
                '</div>',
                html.content_footer()
            ].join("\n");
        },

        /**
         * Posts the animal details to the backend.
         * mode: "add" to stay on this screen after post, anything else to edit the created animal
         */
        add_animal: async function(mode) {

            if (!animal_new.validation()) { return; }

            $(".asm-content button").button("disable");
            header.show_loading(_("Creating..."));
            let formdata = "mode=save&" + $("input, textarea, select").not(".chooser").toPOST();
            try {
                const response = await common.ajax_post("animal_new", formdata);
                const [createdID, newCode] = response.split(" ");
                if (mode == "add") {
                    header.show_info(_("Animal '{0}' created with code {1}").replace("{0}", $("#animalname").val()).replace("{1}", newCode));
                }
                else {
                    if (createdID != "0") { common.route("animal?id=" + createdID); }
                }
            }
            finally {
                $(".asm-content button").button("enable");
                header.hide_loading();
            }
        },

        /**
         * Updates widget enabled/visable after changes
         */
        enable_widgets: function() {

            animal_new.update_units();
                
            // Crossbreed flag being unset disables second breed field
            if ($("#crossbreed").is(":checked")) {
                $("#breed2").fadeIn();
            }
            else {
                $("#breed2").fadeOut();
                $("#breed2").select("value", ($("#breed1").val()));
            }

            // Not having any active litters disables join litter button
            if ($("#sellitter option").length == 0) {
                $("#button-litterjoin").button("disable");
            }

            // If the user ticked hold, there's no hold until date and
            // we have an auto remove days period, default the date
            if ($("#hold").is(":checked") && $("#holduntil").val() == "" && config.integer("AutoRemoveHoldDays") > 0) {
                let holddate = new Date().getTime();
                holddate += config.integer("AutoRemoveHoldDays") * 86400000;
                holddate = format.date( new Date(holddate) );
                $("#holduntil").val(holddate);
            }

            // If the user entered a hold until date and hold is not 
            // ticked, tick it
            if ($("#holduntil").val() != "" && !($("#hold").is(":checked"))) {
                $("#hold").prop("checked", true);
            }

            // Setting non-shelter should assign the non-shelter animal type
            // and show the original owner field as well as getting rid of
            // any fields that aren't relevant to non-shelter animals
            if ($("#nonshelter").is(":checked")) {
                $("#nsownerrow").fadeIn();
                if ($("#animaltype option[value='" + config.integer("AFNonShelterType") + "']").length > 0 && !animal_new.set_nonsheltertype_once) { 
                    animal_new.set_nonsheltertype_once = true;
                    $("#animaltype").select("value", config.integer("AFNonShelterType")); 
                }
                $("#holdrow, #locationrow, #locationunitrow, #fostererrow, #coordinatorrow, #litterrow, #entryreasonrow, #entrytyperow, #transferinrow, #broughtinbyrow, #originalownerrow, #feerow").fadeOut();
            }
            else {
                $("#nsownerrow").fadeOut();
                if (config.bool("AddAnimalsShowAcceptance")) { $("#litterrow").fadeIn(); }
                if (config.bool("AddAnimalsShowBroughtInBy")) { $("#broughtinbyrow").fadeIn(); }
                if (config.bool("AddAnimalsShowOriginalOwner")) { $("#originalownerrow").fadeIn(); }
                if (config.bool("AddAnimalsShowEntryCategory")) { $("#entryreasonrow").fadeIn(); }
                if (config.bool("AddAnimalsShowEntryType")) { 
                    $("#entrytyperow").fadeIn(); $("#transferinrow").fadeOut(); 
                }
                else {
                    $("#entrytyperow").fadeOut(); $("#transferinrow").fadeIn();
                }
                if (config.bool("AddAnimalsShowFee")) { $("#feerow").fadeIn(); }
                if (config.bool("AddAnimalsShowFosterer")) { $("#fostererrow").fadeIn(); }
                if (config.bool("AddAnimalsShowCoordinator")) { $("#coordinatorrow").fadeIn(); }
                if (config.bool("AddAnimalsShowHold")) { $("#holdrow").fadeIn(); }
                if (config.bool("AddAnimalsShowLocation")) { $("#locationrow").fadeIn(); }
                if (config.bool("AddAnimalsShowLocationUnit")) { $("#locationunitrow").fadeIn(); }
            }

            // Fields that apply to both shelter and non-shelter animals based on config
            $("#jurisdictionrow").hide();
            if (config.bool("AddAnimalsShowJurisdiction")) { $("#jurisdictionrow").show(); }

            // If transfer in is available and ticked, change the broughtinby label
            if (!config.bool("AddAnimalsShowEntryType") && $("#transferin").is(":checked")) {
                $("label[for='broughtinby']").html(_("Transferred From")); 
                $("#broughtinby").personchooser("set_filter", "shelter");
            }
            // If entry type is available and set to transfer, change the broughtinby label
            else if (config.bool("AddAnimalsShowEntryType") && $("#entrytype").val() == 3) { 
                $("label[for='broughtinby']").html(_("Transferred From")); 
                $("#broughtinby").personchooser("set_filter", "shelter");
            }
            else { 
                $("label[for='broughtinby']").html(_("Brought In By")); 
                $("#broughtinby").personchooser("set_filter", "all");
            }
    
        },

        /* Update the breed selects to only show the breeds for the selected species.
         * If the species is not in the list of CrossbreedSpecies, hides the crossbreed/second species.
         * If there are no breeds for the species, includes a blank option with ID 0
         * */
        update_breed_select: function() {
            $('optgroup', $('#breed1')).remove();
            $('#breedp optgroup').clone().appendTo($('#breed1'));

            $('#breed1').children().each(function(){
                if($(this).attr('id') != 'ngp-'+$('#species').val()){
                    $(this).remove();
                }
            });

            if ($('#breed1 option').length == 0) {
                $('#breed1').append("<option value='0'></option>");
                //$('#breed1').append("<option value='0'>"+$('#species option:selected').text()+"</option>");
            }

            $('optgroup', $('#breed2')).remove();
            $('#breedp optgroup').clone().appendTo($('#breed2'));

            $('#breed2').children().each(function(){
                if($(this).attr('id') != 'ngp-'+$('#species').val()) {
                    $(this).remove();
                }
            });

            if ($('#breed2 option').length == 0) {
                $('#breed2').append("<option value='0'></option>");
            }

            if (common.array_in($("#species").val(), config.str("CrossbreedSpecies").split(",")) && !config.bool("UseSingleBreedField")) {
                $("#crossbreedcol, #secondbreedcol").show();
            }
            else {
                $("#crossbreedcol, #secondbreedcol").hide();
                $("#crossbreed").prop("checked", false);
            }
        },

        // Set the entry type based on the other field values if it has been disabled
        update_entry_type: function() {
            if (config.bool("AddAnimalsShowEntryType")) { return; }
            let reasonname = common.get_field(controller.entryreasons, $("#entryreason").select("value"), "REASONNAME").toLowerCase();
            let entrytype = 1; //surrender
            if ($("#deadonarrival").is(":checked")) { entrytype = 9; } // dead on arrival
            else if ($("#dateofbirth").val() == $("#datebroughtin").val()) { entrytype = 5; } // born in shelter
            else if ($("#crueltycase").is(":checked")) { entrytype = 7; } // seized
            else if ($("#transferin").is(":checked")) { entrytype = 3; } // transfer in
            else if (reasonname.indexOf("transfer") != -1) { entrytype = 3; } // transfer in
            else if (reasonname.indexOf("born") != -1) { entrytype = 5; } // born in shelter
            else if (reasonname.indexOf("stray") != -1) { entrytype = 2; } // stray
            else if (reasonname.indexOf("tnr") != -1) { entrytype = 4; } // tnr
            else if (reasonname.indexOf("wildlife") != -1) { entrytype = 6; } // wildlife
            else if (reasonname.indexOf("abandoned") != -1) { entrytype = 8; } // abandoned
            $("#entrytype").select("value", entrytype);
        },

        // Update the units available for the selected location
        update_units: async function() {
            let opts = ['<option value=""></option>'];
            $("#unit").empty();
            const response = await common.ajax_post("animal_new", "mode=units&locationid=" + $("#internallocation").val());
            $.each(html.decode(response).split("&&"), function(i, v) {
                let [unit, desc] = v.split("|");
                if (!unit) { return false; }
                if (!desc) { desc = _("(available)"); }
                opts.push('<option value="' + html.title(unit) + '">' + unit +
                    ' : ' + desc + '</option>');
            });
            $("#unit").html(opts.join("\n")).change();
        },

        reset: function() {

            $("#animalname, #dateofbirth, #weight, #weightlb").val("").change();
            $(".asm-checkbox").prop("checked", false).change();
            $(".asm-personchooser").personchooser("clear");

            // Set brought in by label back to non-transfer
            $("label[for='broughtinby']").html(_("Brought In By")); 
            $("#broughtinby").personchooser("set_filter", "all");

            // Set estimated age
            $("#estimatedage").val("");
            if (config.str("DefaultAnimalAge") != "0") {
                $("#estimatedage").val(config.str("DefaultAnimalAge"));
            }

            // Set select box default values
            $("#animaltype").select("value", config.str("AFDefaultType"));
            animal_new.set_nonsheltertype_once = false;
            $("#species").select("value", config.str("AFDefaultSpecies"));
            animal_new.update_breed_select();
            $("#breed1, #breed2").select("value", config.str("AFDefaultBreed"));
            $("#basecolour").select("value", config.str("AFDefaultColour"));
            $("#coattype").select("value", config.str("AFDefaultCoatType"));
            $("#entryreason").select("value", config.str("AFDefaultEntryReason"));
            $("#entrytype").select("value", config.str("AFDefaultEntryType"));
            $("#internallocation").select("value", config.str("AFDefaultLocation"));
            $("#jurisdiction").select("value", config.str("DefaultJurisdiction"));
            $("#size").select("value", config.str("AFDefaultSize"));
            $("#sex").select("value", "2"); // Unknown

            // Remove any retired lookups from the lists
            $(".asm-selectbox").select("removeRetiredOptions");

            // Any lookups that don't have a value after setting the defaults
            // should inherit the first in their list instead.
            $(".asm-selectbox").select("firstIfBlank");

            // Set date/time defaults
            $("#datebroughtin").val(format.date(new Date()));
            if (config.bool("AddAnimalsShowTimeBroughtIn")) {
                $("#timebroughtin").val(format.time(new Date()));
            }

            // Update units according to any location selected
            animal_new.update_units();

            // Currency defaults
            $("#fee").currency("value", 0);
        },

        validation: function() {
            // Remove any previous errors
            header.hide_error();
            validate.reset();

            // code
            if (config.bool("ManualCodes")) {
                if (common.trim($("#sheltercode").val()) == "") {
                    header.show_error(_("Shelter code cannot be blank"));
                    validate.highlight("sheltercode");
                    return false;
                }
            }

            // name
            if (common.trim($("#animalname").val()) == "") {
                header.show_error(_("Name cannot be blank"));
                validate.highlight("animalname");
                return false;
            }

            // date of birth
            if (common.trim($("#dateofbirth").val()) == "" && common.trim($("#estimatedage").val()) == "") {
                header.show_error(_("Date of birth cannot be blank"));
                validate.highlight("dateofbirth");
                return false;
            }

            // mandatory additional fields
            if (!additional.validate_mandatory()) { return false; }

            return true;
        },

        bind: function() {

            validate.indicator(["animalname", "dateofbirth"]);

            let similarbuttons = {};
            similarbuttons[_("Close")] = function() { 
                $(this).dialog("close");
            };
            $("#dialog-similar").dialog({
                 autoOpen: false,
                 resizable: false,
                 modal: true,
                 width: 500,
                 dialogClass: "dialogshadow",
                 show: dlgfx.delete_show,
                 hide: dlgfx.delete_hide,
                 buttons: similarbuttons
            });

            // Check the name has not been used recently once the user leaves
            // the field.
            if (config.bool("WarnSimilarAnimalName")) {
                $("#animalname").blur(async function() {
                    try {
                        let formdata = "mode=recentnamecheck&animalname=" + encodeURIComponent($("#animalname").val());
                        const response = await common.ajax_post("animal_new", formdata);
                        if (response == "None") { return; }
                        const [animalid, sheltercode, animalname] = response.split("|");
                        let h = "<a class='asm-embed-name' href='animal?id=" + animalid + "'>" + sheltercode + " - " + animalname + "</a>";
                        $(".similar-animal").html(h);
                        $("#dialog-similar").dialog("open");
                    }
                    finally {
                        $(".asm-content button").button("enable");
                    }
                });
            }

            // Converting between whole number for weight and pounds and ounces
            const lboz_to_fraction = function() {
                let lb = format.to_int($("#weightlb").val());
                lb += format.to_int($("#weightoz").val()) / 16.0;
                $("#weight").val(String(lb));
            };

            if (config.bool("ShowWeightInLbs")) {
                $("#kilosrow").hide();
                $("#poundsrow").show();
                $("#weightlb, #weightoz").change(lboz_to_fraction);
            }
            else if (config.bool("ShowWeightInLbsFraction")) {
                $("#kglabel").html(_("lb"));
                $("#kilosrow").show();
                $("#poundsrow").hide();
            }
            else {
                $("#kglabel").html(_("kg"));
                $("#kilosrow").show();
                $("#poundsrow").hide();
            }

            // Disable rows based on config options
            if (!config.bool("AddAnimalsShowAcceptance")) { $("#litterrow").hide(); }
            if (!config.bool("AddAnimalsShowBreed")) { $("#breedrow").hide(); }
            if (!config.bool("AddAnimalsShowBroughtInBy")) { $("#broughtinbyrow").hide(); }
            if (!config.bool("AddAnimalsShowCoordinator")) { $("#coordinatorrow").hide(); }
            if (!config.bool("AddAnimalsShowOriginalOwner")) { $("#originalownerrow").hide(); }
            if (!config.bool("AddAnimalsShowCoatType")) { $("#coattyperow").hide(); }
            if (!config.bool("AddAnimalsShowColour")) { $("#colourrow").hide(); }
            if (!config.bool("AddAnimalsShowDateBroughtIn")) { $("#datebroughtinrow").hide(); }
            if (!config.bool("AddAnimalsShowEntryCategory")) { $("#entryreasonrow").hide(); }
            if (!config.bool("AddAnimalsShowFee")) { $("#feerow").hide(); }
            if (!config.bool("AddAnimalsShowFosterer")) { $("#fostererrow").hide(); }
            if (!config.bool("AddAnimalsShowHold")) { $("#holdrow").hide(); }
            if (!config.bool("AddAnimalsShowLocation")) { $("#locationrow").hide(); }
            if (!config.bool("AddAnimalsShowLocationUnit")) { $("#locationunitrow").hide(); }
            if (!config.bool("AddAnimalsShowMicrochip")) { $("#microchiprow").hide(); }
            if (!config.bool("AddAnimalsShowNeutered")) { $("#neuteredrow").hide(); }
            if (!config.bool("AddAnimalsShowPickup")) { $("#pickuprow").hide(); }
            if (!config.bool("AddAnimalsShowSize")) { $("#sizerow").hide(); }
            if (!config.bool("AddAnimalsShowTattoo")) { $("#tattoorow").hide(); }
            if (!config.bool("AddAnimalsShowTimeBroughtIn")) { $("#timebroughtinrow").hide(); }
            if (!config.bool("AddAnimalsShowWeight")) { $("#kilosrow, #poundsrow").hide(); }
            if (config.bool("UseSingleBreedField")) {
                $("#crossbreedcol, #secondbreedcol").hide();
            }
            if (config.bool("DisableShortCodesControl")) {
                $("#shortcode").hide();
                $("#sheltercode").addClass("asm-textbox");
                $("#sheltercode").removeClass("asm-halftextbox");
            }
            if (!config.bool("ManualCodes")) { $("#coderow").hide(); }


            // Keep breed2 in sync with breed1 for non-crossbreeds
            $("#breed1").change(function() {
                if (!$("#crossbreed").is(":checked")) {
                    $("#breed2").select("value", $("#breed1").select("value"));
                }
            });

            // Changing species updates the breed list
            $('#species').change(function() {
                animal_new.update_breed_select();
            });

            // Changing various fields that guess the entry category
            $("#entryreason, #transferin, #datebroughtin, #dateofbirth").change(function() {
                animal_new.update_entry_type();
            });

            // Litter autocomplete
            $("#litterid").autocomplete({source: html.decode(controller.autolitters)});

            // Setting the neutered date sets the checkbox
            $("#neutereddate").change(function() {
                if ($("#neutereddate").val()) {
                    $("#neutered").prop("checked", true);
                }
            });

            // Setting the microchipped date or number sets the checkbox
            $("#microchipdate").change(function() {
                if ($("#microchipdate").val()) {
                    $("#microchipped").prop("checked", true);
                }
            });
            $("#microchipnumber").change(function() {
                if ($("#microchipnumber").val()) {
                    $("#microchipped").prop("checked", true);
                }
            });

            // Setting the tattoo number sets the checkbox
            $("#tattoodate").change(function() {
                if ($("#tattoodate").val()) {
                    $("#tattoo").prop("checked", true);
                }
            });
            $("#tattoonumber").change(function() {
                if ($("#tattoonumber").val()) {
                    $("#tattoo").prop("checked", true);
                }
            });

            // Setting the pickup address or location sets the checkbox
            $("#pickuplocation").change(function() {
                $("#pickedup").prop("checked", true);
            });
            $("#pickupaddress").change(function() {
                if ($("#pickupaddress").val()) {
                    $("#pickedup").prop("checked", true);
                }
            });

            $("#internallocation").change(animal_new.update_units);
            $("#crossbreed").change(animal_new.enable_widgets);
            $("#nonshelter").change(animal_new.enable_widgets);
            $("#transferin").change(animal_new.enable_widgets);
            $("#entrytype").change(animal_new.enable_widgets);
            $("#hold").change(animal_new.enable_widgets);
            $("#holduntil").change(animal_new.enable_widgets);
            animal_new.enable_widgets();

            // Default species has been set, update the available breeds
            // before choosing the default breed
            animal_new.update_breed_select();
            $("#breed1").val(config.str("AFDefaultBreed"));
            $("#breed2").val(config.str("AFDefaultBreed"));

            // Buttons
            $("#add").button().click(function() {
                animal_new.add_animal("add");
            });

            $("#addedit").button().click(function() {
                animal_new.add_animal("addedit");
            });

            $("#reset").button().click(function() {
                animal_new.reset();
            });

            $("#button-randomname")
                .button({ icons: { primary: "ui-icon-tag" }, text: false })
                .click(async function() {
                let formdata = "mode=randomname&sex=" + $("#sex").val();
                const response = await common.ajax_post("animal", formdata);
                $("#animalname").val(response); 
            });

        },

        sync: function() {
            animal_new.reset();
        },

        destroy: function() {
            common.widget_destroy("#dialog-similar");
            common.widget_destroy("#nsowner", "personchooser");
            common.widget_destroy("#coordinator", "personchooser");
            common.widget_destroy("#fosterer", "personchooser");
            common.widget_destroy("#originalowner", "personchooser");
            common.widget_destroy("#broughtinby", "personchooser");
        },

        name: "animal_new",
        animation: "newdata",
        autofocus: "#nonshelter", 
        title: function() { return _("Add a new animal"); },
        
        routes: {
            "animal_new": function() {
                common.module_loadandstart("animal_new", "animal_new");
            }
        }

    };

    common.module_register(animal_new);

});
