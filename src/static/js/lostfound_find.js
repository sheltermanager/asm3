/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const lostfound_find = {

        render: function() {
            return [
                controller.mode == "lost" ? html.content_header(_("Find Lost Animal")) : "",
                controller.mode == "found" ? html.content_header(_("Find Found Animal")) : "",
                '<div id="lostfoundsearchform">',
                '<table class="asm-table-layout">',
                '<tr>',
                '<td>',
                '<label for="number">' + _("Number") + '</label>',
                '</td>',
                '<td>',
                '<input id="number" data="number" class="asm-textbox asm-numberbox" />',
                '</td>',
                '<td>',
                '<label for="contact">' + _("Contact Contains") + '</label>',
                '</td>',
                '<td>',
                '<input id="contact" data="contact" class="asm-textbox" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="microchip">' + _("Microchip") + '</label>',
                '</td>',
                '<td>',
                '<input id="microchip" data="microchip" class="asm-textbox" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="area">' + _("Area") + '</label>',
                '</td>',
                '<td>',
                '<input id="area" data="area" class="asm-textbox" />',
                '</td>',
                '<td>',
                '<label for="postcode">' + _("Zipcode") + '</label>',
                '</td>',
                '<td>',
                '<input id="postcode" data="postcode" class="asm-textbox" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="features">' + _("Features") + '</label>',
                '</td>',
                '<td>',
                '<input id="features" data="features" class="asm-textbox" />',
                '</td>',
                '<td>',
                '<label for="agegroup">' + _("Age Group") + '</label>',
                '</td>',
                '<td>',
                '<select id="agegroup" data="agegroup" class="asm-selectbox">',
                '<option value="-1">' + _("(all)") + '</option>',
                '<option value="Unknown">' + _("(unknown)") + '</option>',
                html.list_to_options(controller.agegroups),
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
                '<label for="species">' + _("Species") + '</label>',
                '</td>',
                '<td>',
                '<select id="species" data="species" class="asm-selectbox">',
                '<option value="-1">' + _("(all)") + '</option>',
                html.list_to_options(controller.species, "ID", "SPECIESNAME"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="breed">' + _("Breed") + '</label>',
                '</td>',
                '<td>',
                '<select id="breed" data="breed" class="asm-selectbox">',
                '<option value="-1">' + _("(all)") + '</option>',
                html.list_to_options_breeds(controller.breeds),
                '</select>',
                '<select id="breedp" data="breedp" class="asm-selectbox" style="display:none;">',
                '<option value="-1">' + _("(all)") + '</option>',
                html.list_to_options_breeds(controller.breeds),
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
                '<label for="datefrom">',
                controller.mode == "lost" ? _("Lost from") : _("Found from"),
                '</label>',
                '</td>',
                '<td>',
                '<input id="datefrom" data="datefrom" class="asm-textbox asm-datebox" />',
                '</td>',
                '<td>',
                '<label for="dateto">',
                controller.mode == "lost" ? _("Lost to") : _("Found to"),
                '</label>',
                '</td>',
                '<td>',
                '<input id="dateto" data="dateto" class="asm-textbox asm-datebox" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="completefrom">',
                controller.mode == "lost" ? _("Found from") : _("Returned from"),
                '</label>',
                '</td>',
                '<td>',
                '<input id="completefrom" data="completefrom" class="asm-textbox asm-datebox" />',
                '</td>',
                '<td>',
                '<label for="completeto">',
                controller.mode == "lost" ? _("Found to") : _("Returned to"),
                '</label>',
                '</td>',
                '<td>',
                '<input id="completeto" data="completeto" class="asm-textbox asm-datebox" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="excludecomplete">',
                controller.mode == "lost" ? _("Include found") : _("Include returned"),
                '</label>',
                '</td>',
                '<td>',
                '<select id="excludecomplete" data="excludecomplete" class="asm-selectbox">',
                '<option value="1" selected="selected">' + _("No") + '</option>',
                '<option value="0">' + _("Yes") + '</option>',
                '</select>',
                '</td>',
                '<td>',
                '</td>',
                '</tr>',
                '<tr><td colspan="4"><hr></td></tr>',
                additional.additional_search_fields(controller.additionalfields, 2),
                '</table>',
                '<p class="centered">',
                '<button type="submit" id="searchbutton">' + _("Search") + '</button>',
                '</p>',
                '</div>',
                html.content_footer()
            ].join("\n");
        },

        bind: function() {

            $("#searchbutton").button().click(function() {
                common.route((controller.mode == "lost" ? "lostanimal_find_results?" : "foundanimal_find_results?") + 
                    $("#lostfoundsearchform input, #lostfoundsearchform select").toPOST());
            });

            // We need to re-enable the return key submitting the form
            $("#lostfoundsearchform").keypress(function(e) {
                if (e.keyCode == 13) {
                    common.route((controller.mode == "lost" ? "lostanimal_find_results?" : "foundanimal_find_results?") + 
                        $("#lostfoundsearchform input, #lostfoundsearchform select").toPOST());
                }
            });

            // Only show the breeds for the selected species
            // The (all) option is displayed by default
            const change_breed_select = function() {
                $('optgroup', $('#breed')).remove();
                $('#breedp optgroup').clone().appendTo($('#breed'));
                $('#breed').append("<option value=''>(all)</option>");

                if($('#species').val() != -1){
                    $('#breed').children().each(function(){
                        if($(this).attr('id') != 'ngp-'+$('#species').val()){
                            $(this).remove();
                        }
                    });
                }

                $('#breed').append("<option value='-1'>" + _("(all)") + "</option>");
                $('#breed').val(-1);
            };
            $('#species').change(change_breed_select);
            change_breed_select();

        },

        name: "lostfound_find",
        animation: "criteria",
        autofocus: "#number",
        title: function() { 
            if (controller.name.indexOf("lost") != -1) {
                return _("Find Lost Animal");
            }
            return _("Find Found Animal");
        },
        routes: {
            "lostanimal_find": function() { common.module_loadandstart("lostfound_find", "lostanimal_find"); },
            "foundanimal_find": function() { common.module_loadandstart("lostfound_find", "foundanimal_find"); }
        }
    };

    common.module_register(lostfound_find);

});
