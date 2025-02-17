/*global $, jQuery, controller */
/*global common, config, format, html */
/*global _, mobile, mobile_ui_animal, mobile_ui_incident, mobile_ui_person, mobile_ui_stock */
/*global mobile_ui_addanimal: true */

"use strict";

const mobile_ui_addanimal = {

    render: () => {
        return [
            '<h2 class="mt-3">' + _("Add Animal") + '</h2>',
            '<input type="hidden" name="mode" value="addanimal">',
            '<div class="mb-3">',
                '<label for="animalname" class="form-label">' + _("Name") + '</label>',
                '<input type="text" class="form-control" id="animalname" data="animalname">',
            '</div>',
            '<div class="mb-3">',
                '<label for="sheltercode" class="form-label">' + _("Code") + '</label>',
                '<input type="text" class="form-control" id="sheltercode" data="sheltercode">',
            '</div>',
            '<div class="mb-3">',
                '<label for="estimatedage" class="form-label">' + _("Age") + '</label>',
                '<input type="text" class="form-control" id="estimatedage" data="estimatedage" value="1.0">',
            '</div>',
            '<div class="mb-3">',
                '<label for="sex" class="form-label">' + _("Sex") + '</label>',
                '<select class="form-select" name="sex" id="sex">',
                html.list_to_options(controller.sexes, "ID", "SEX"),
                '</select>',
            '</div>',
            '<div class="mb-3">',
                '<label for="animaltype" class="form-label">' + _("Type") + '</label>',
                '<select class="form-select" data="animaltype" id="animaltype">',
                html.list_to_options(controller.animaltypes, "ID", "ANIMALTYPE"),
                '</select>',
            '</div>',
            '<div class="mb-3">',
                '<label for="species" class="form-label">' + _("Species") + '</label>',
                '<select class="form-select" data="species" id="species">',
                html.list_to_options(controller.species, "ID", "SPECIESNAME"),
                '</select>',
            '</div>',
            '<div class="mb-3">',
                '<label for="breed1" class="form-label">' + _("Breed") + '</label>',
                '<select class="form-select" data="breed1" id="breed1">',
                html.list_to_options_breeds(controller.breeds),
                '</select>',
                '<select id="breedp" data="breedp" style="display:none;">',
                html.list_to_options_breeds(controller.breeds),
                '</select>',
            '</div>',
            '<div class="mb-3">',
                '<label for="basecolour" class="form-label">' + _("Color") + '</label>',
                '<select class="form-select" data="basecolour" id="basecolour">',
                html.list_to_options(controller.colours, "ID", "BASECOLOUR"),
                '</select>',
            '</div>',
            '<div class="mb-3">',
                '<label for="size" class="form-label">' + _("Size") + '</label>',
                '<select class="form-select" data="size" id="size">',
                html.list_to_options(controller.sizes, "ID", "SIZE"),
                '</select>',
            '</div>',
            '<div class="mb-3">',
                '<label for="microchipnumber" class="form-label">' + _("Microchip") + '</label>',
                '<input type="text" class="form-control" id="microchipnumber" data="microchipnumber">',
            '</div>',
            '<div class="mb-3">',
                '<label for="internallocation" class="form-label">' + _("Location") + '</label>',
                '<select class="form-select" data="internallocation" id="internallocation">',
                html.list_to_options(controller.internallocations, "ID", "LOCATIONNAME"),
                '</select>',
            '</div>',
            '<div class="mb-3">',
                '<label for="unit" class="form-label">' + _("Unit") + '</label>',
                '<select class="form-select" id="unit" data="unit">',
                '</select>',
            '</div>',
            '<div class="d-flex justify-content-center pb-2">',
            '<button id="addanimal-submit" type="submit" class="btn btn-primary">',
                '<i class="bi bi-plus-square"></i>',
                _("Create"), 
                '<span class="spinner-border spinner-border-sm" style="display: none"></span>',
            '</button>',
            '</div>',
            '</form>'
        ].join("\n");
    },

    update_breed_select: function() {
        // Only show the breeds for the selected species
        $('optgroup', $('#breed1')).remove();
        $('#breedp optgroup').clone().appendTo($('#breed1'));
        $('#breed1').children().each(function(){
            if($(this).attr('id') != 'ngp-'+$('#species').val()){
                $(this).remove();
            }
        });
    },

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

    bind: () => {
        // When the location is changed, update the list of units
        $("#internallocation").change(function() {
            mobile_ui_addanimal.update_units();
        });

        // When species is changed, update the breeds
        $("#species").change(function() {
            mobile_ui_addanimal.update_breed_select();
        });

        // Handle add animal
        $("#addanimal-submit").click(function() {
            $("#addanimal-submit .spinner-border").show();
            let formdata = {
                "mode": "addanimal",
                "animalname": $("#animalname").val(),
                "sheltercode": $("#sheltercode").val(),
                "estimatedage": $("#estimatedage").val(),
                "sex": $("#sex").val(),
                "type": $("#type").val(),
                "species": $("#species").val(),
                "breed1": $("#breed1").val(),
                "basecolour": $("#basecolour").val(),
                "size": $("#size").val(),
                "microchipped": $("#microchipnumber").val() != "" ? "on" : "",
                "microchipnumber": $("#microchipnumber").val(),
                "internallocation": $("#internallocation").val(),
                "unit": $("#unit").val()
            };
            mobile.ajax_post(formdata, function(response) {
                let a = jQuery.parseJSON(response);
                controller.animals.push(a);
                // TODO: This needs to point to mobile_ui_animal instead
                mobile_ui_animal.render(a);
                mobile_ui_animal.render_shelteranimalslist();
                $(".container").hide();
                $("#content-animal").show();
                $("#addanimal-submit .spinner-border").hide();
            });
        });
   
    },

    sync: () => {
        $("#age").val(config.str("DefaultAnimalAge"));
        $("#animaltype").val(config.str("AFDefaultType"));
        $("#basecolour").val(config.str("AFDefaultColour"));
        $("#internallocation").val(config.str("AFDefaultLocation"));
        mobile_ui_addanimal.update_units();
        $("#species").val(config.str("AFDefaultSpecies"));
        mobile_ui_addanimal.update_breed_select();
        $("#breed1").val(config.str("AFDefaultBreed"));
        $("#size").val(config.str("AFDefaultSize"));
        $("#sheltercode").closest("div").toggle(config.bool("ManualCodes"));
    }

};
