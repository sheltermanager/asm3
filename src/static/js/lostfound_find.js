/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const lostfound_find = {

        render: function() {
            let col1 = [
                html.search_field_number("number", _("Number")),
                html.search_field_text("contact", _("Contact Contains")),
                html.search_field_text("microchip", _("Microchip")),
                html.search_field_text("area", _("Area")),
                html.search_field_text("postcode", _("Zipcode")),
                html.search_field_text("features", _("Features")),
                html.search_field_select("agegroup", _("Age Group"), html.list_to_options(controller.agegroups))
            ].join("\n");
            let col2 = [
                html.search_field_select("sex", _("Sex"), html.list_to_options(controller.sexes, "ID", "SEX")),
                html.search_field_select("species", _("Species"), html.list_to_options(controller.species, "ID", "SPECIESNAME")),
                html.search_field_select("breed", _("Breed"), html.list_to_options_breeds(controller.breeds)),
                html.search_field_select("colour", _("Color"), html.list_to_options(controller.colours, "ID", "BASECOLOUR")),
                html.search_field_daterange("datefrom", "dateto", controller.mode == "lost" ? _("Lost between") : _("Found between")),
                html.search_field_daterange("completefrom", "completeto", controller.mode == "lost" ? _("Found between") : _("Returned between")),
                html.search_field_select("excludecomplete", controller.mode == "lost" ? _("Include found") : _("Include returned"), 
                    '<option value="1" selected="selected">' + _("No") + '</option><option value="0">' + _("Yes") + '</option>')
            ].join("\n");
            return [
                controller.mode == "lost" ? html.content_header(_("Find Lost Animal")) : "",
                controller.mode == "found" ? html.content_header(_("Find Found Animal")) : "",
                '<div id="lostfoundsearchform">',
                '<div class="asm-search-criteriacolumns">',
                html.search_column(col1),
                html.search_column(col2),
                html.search_column(additional.additional_search_fields(controller.additionalfields, 1)),
                '</div>',
                '</div>',
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
