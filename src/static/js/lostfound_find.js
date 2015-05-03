/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    var lostfound_find = {

        render: function() {
            return [
                controller.mode == "lost" ? html.content_header(_("Find Lost Animal")) : "",
                controller.mode == "lost" ? '<form id="lostfoundsearchform" action="lostanimal_find_results" method="GET">' : "",
                controller.mode == "found" ? html.content_header(_("Find Found Animal")) : "",
                controller.mode == "found" ? '<form id="lostfoundsearchform" action="foundanimal_find_results" method="GET">' : "",
                '<table class="asm-table-layout">',
                '<tr>',
                '<td>',
                '<label for="number">' + _("Number") + '</label>',
                '</td>',
                '<td>',
                '<input id="number" name="number" class="asm-textbox asm-numberbox" />',
                '</td>',
                '<td>',
                '<label for="contact">' + _("Contact Contains") + '</label>',
                '</td>',
                '<td>',
                '<input id="contact" name="contact" class="asm-textbox" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="area">' + _("Area") + '</label>',
                '</td>',
                '<td>',
                '<input id="area" name="area" class="asm-textbox" />',
                '</td>',
                '<td>',
                '<label for="postcode">' + _("Zipcode") + '</label>',
                '</td>',
                '<td>',
                '<input id="postcode" name="postcode" class="asm-textbox" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="features">' + _("Features") + '</label>',
                '</td>',
                '<td>',
                '<input id="features" name="features" class="asm-textbox" />',
                '</td>',
                '<td>',
                '<label for="agegroup">' + _("Age Group") + '</label>',
                '</td>',
                '<td>',
                '<select id="agegroup" name="agegroup" class="asm-selectbox">',
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
                '<select id="sex" name="sex" class="asm-selectbox">',
                '<option value="-1">' + _("(all)") + '</option>',
                html.list_to_options(controller.sexes, "ID", "SEX"),
                '</select>',
                '</td>',
                '<td>',
                '<label for="species">' + _("Species") + '</label>',
                '</td>',
                '<td>',
                '<select id="species" name="species" class="asm-selectbox">',
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
                '<select id="breed" name="breed" class="asm-selectbox">',
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
                '<select id="colour" name="colour" class="asm-selectbox">',
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
                '<input id="datefrom" name="datefrom" class="asm-textbox asm-datebox" />',
                '</td>',
                '<td>',
                '<label for="dateto">',
                controller.mode == "lost" ? _("Lost to") : _("Found to"),
                '</label>',
                '</td>',
                '<td>',
                '<input id="dateto" name="dateto" class="asm-textbox asm-datebox" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="completefrom">',
                controller.mode == "lost" ? _("Found from") : _("Returned from"),
                '</label>',
                '</td>',
                '<td>',
                '<input id="completefrom" name="completefrom" class="asm-textbox asm-datebox" />',
                '</td>',
                '<td>',
                '<label for="completeto">',
                controller.mode == "lost" ? _("Found to") : _("Returned to"),
                '</label>',
                '</td>',
                '<td>',
                '<input id="completeto" name="completeto" class="asm-textbox asm-datebox" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="excludecomplete">',
                controller.mode == "lost" ? _("Include found") : _("Include returned"),
                '</label>',
                '</td>',
                '<td>',
                '<select id="excludecomplete" name="excludecomplete" class="asm-selectbox">',
                '<option value="1" selected="selected">' + _("No") + '</option>',
                '<option value="0">' + _("Yes") + '</option>',
                '</select>',
                '</td>',
                '<td>',
                '</td>',
                '</tr>',
                '</table>',
                '<p class="centered">',
                '<button type="submit" id="searchbutton">' + _("Search") + '</button>',
                '</p>',
                '</form>',
                html.content_footer()
            ].join("\n");
        },

        bind: function() {
            $("#searchbutton").button();

            // Only show the breeds for the selected species
            // The (all) option is displayed by default
            var changebreedselect1 = function() {
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

            changebreedselect1();

            $('#species').change(function() {
                changebreedselect1();
            });
        },

        name: "lostfound_find",
        animation: "criteria"

    };

    common.module_register(lostfound_find);

});
