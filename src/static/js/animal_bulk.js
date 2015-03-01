/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    var animal_bulk = {

        render: function() {
            return [
                html.content_header(_("Bulk change animals")),
                '<table class="asm-table-layout" style="padding-bottom: 5px;">',
                '<tr>',
                '<td>',
                '<label for="animals">' + _("Animals") + '</label>',
                '</td>',
                '<td>',
                '<input id="animals" data="animals" type="hidden" class="asm-animalchoosermulti" value=\'\' />',
                '</td>',
                '</tr>',

                '<tr id="litteridrow">',
                '<td>',
                '<label for="litterid">' + _("Litter") + '</label></td>',
                '<td><input type="text" id="litterid" data-post="litterid" class="asm-textbox" title="' + html.title(_("The litter this animal belongs to")) + '" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="animaltype">' + _("Type") + '</label></td>',
                '<td><select id="animaltype" data-post="animaltype" class="asm-selectbox" title="' + html.title(_("The shelter category for this animal")) + '">',
                '<option value="-1">' + _("(no change)") + '</option>',
                html.list_to_options(controller.animaltypes, "ID", "ANIMALTYPE"),
                '</select></td>',
                '</tr>',
                '<tr id="locationrow">',
                '<td><label for="location">' + _("Location") + '</label></td>',
                '<td>',
                '<select id="location" data-post="location" class="asm-selectbox" title="' + html.title(_("Where this animal is located within the shelter")) + '">',
                '<option value="-1">' + _("(no change)") + '</option>',
                html.list_to_options(controller.internallocations, "ID", "LOCATIONNAME"),
                '</select></td>',
                '</tr>',

                '<tr id="feerow">',
                '<td><label for="fee">' + _("Adoption Fee") + '</label></td>',
                '<td><input id="fee" data-post="fee" class="asm-currencybox asm-textbox" /></td>',
                '</tr>',

                '<tr>',
                '<td><label for="notforadoption">' + _("Not For Adoption") + '</label></td>',
                '<td><select id="notforadoption" data-post="notforadoption" class="asm-selectbox">',
                '<option value="-1">' + _("(no change)") + '</option>',
                '<option value="0">' + _("Adoptable") + '</option>',
                '<option value="1">' + _("Not For Adoption") + '</option>',
                '</select>',
                '</td>',
                '</tr>',

                '<tr>',
                '<td>',
                '<label for="goodwithcats">' + _("Good with cats") + '</label>',
                '</td>',
                '<td>',
                '<select class="asm-selectbox" id="goodwithcats" data-post="goodwithcats">',
                '<option value="-1">' + _("(no change)") + '</option>',
                html.list_to_options(controller.ynun, "ID", "NAME"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="goodwithdogs">' + _("Good with dogs") + '</label>',
                '</td>',
                '<td>',
                '<select class="asm-selectbox" id="goodwithdogs" data-post="goodwithdogs">',
                '<option value="-1">' + _("(no change)") + '</option>',
                html.list_to_options(controller.ynun, "ID", "NAME"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="goodwithkids">' + _("Good with kids") + '</label>',
                '</td>',
                '<td>',
                '<select class="asm-selectbox" id="goodwithkids" data-post="goodwithkids">',
                '<option value="-1">' + _("(no change)") + '</option>',
                html.list_to_options(controller.ynun, "ID", "NAME"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="housetrained">' + _("Housetrained") + '</label>',
                '</td>',
                '<td>',
                '<select class="asm-selectbox" id="housetrained" data-post="housetrained">',
                '<option value="-1">' + _("(no change)") + '</option>',
                html.list_to_options(controller.ynun, "ID", "NAME"),
                '</select>',
                '</td>',
                '</tr>',

                '<tr id="neuteredrow">',
                '<td>',
                '<label for="neutereddate">' + _("Altered") + '</label>',
                '</td>',
                '<td>',
                '<input id="neutereddate" data-post="neutereddate" class="asm-textbox asm-datebox" />',
                '</td>',
                '</tr>',

                '<tr id="holdrow">',
                '<td>',
                '<label for="holduntil">' + _("Hold until") + '</label>',
                '</td>',
                '<td>',
                '<input id="holduntil" data-post="holduntil" class="asm-textbox asm-datebox" />',
                '</td>',
                '</tr>',

                '</table>',
                '<div class="centered">',
                '<button id="bulk">' + html.icon("animal") + ' ' + _("Update") + '</button>',
                '</div>',
                html.content_footer()
            ].join("\n");
        },

        bind: function() {

            // Litter autocomplete
            $("#litterid").autocomplete({source: html.decode(controller.autolitters)});

            $("#bulk").button().click(function() {
                if (!validate.notblank([ "animals" ])) { return; }
                $("#bulk").button("disable");
                header.show_loading(_("Updating..."));
                var formdata = $("input, select, textarea").toPOST();
                common.ajax_post("animal_bulk", formdata, function(data) {
                    header.hide_loading();
                    header.show_info(_("{0} animals successfully updated.").replace("{0}", data));
                    $("#bulk").button("enable");
                }, function() {
                    $("#bulk").button("enable");
                });
            });

        }
    };

    common.module(animal_bulk, "animal_bulk", "newdata");

});
