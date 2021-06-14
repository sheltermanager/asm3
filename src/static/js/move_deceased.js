/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const move_deceased = {

        render: function() {
            return [
                html.content_header(_("Mark an animal deceased")),
                '<table class="asm-table-layout">',
                '<tr>',
                '<td>',
                '<label for="animal">' + _("Animal") + '</label>',
                '</td>',
                '<td>',
                '<input id="animal" data="animal" type="hidden" class="asm-animalchooser" value=\'\' />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="deceaseddate">' + _("Deceased Date") + '</label>',
                '</td>',
                '<td>',
                '<input class="asm-textbox asm-datebox" id="deceaseddate" data="deceaseddate" title=\'' + _("The date the animal died") + '\' />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="deathcategory">' + _("Category") + '</label>',
                '</td>',
                '<td>',
                '<select class="asm-selectbox" id="deathcategory" data="deathcategory">',
                html.list_to_options(controller.deathreasons, "ID", "REASONNAME"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td></td>',
                '<td><input class="asm-checkbox" type="checkbox" id="puttosleep" data="puttosleep" title="' + html.title(_("This animal was euthanized")) + '" />',
                '<label for="puttosleep">' + _("Euthanized") + '</label>',
                '</td></tr>',
                '<tr>',
                '<td></td>',
                '<td><input class="asm-checkbox" type="checkbox" id="deadonarrival" data="deadonarrival" title="' + html.title(_("This animal was dead on arrival to the shelter")) + '" />',
                '<label for="deadonarrival">' + _("Dead on arrival") + '</label>',
                '</td></tr>',
                '<tr>',
                '<td><label for="ptsreason">' + _("Notes") + '</label>',
                '<td>',
                '<textarea class="asm-textarea" id="ptsreason" data="ptsreason" rows="8"></textarea>',
                '</td>',
                '</tr>',
                '</table>',
                '<div class="centered">',
                '<button id="deceased">' + html.icon("death") + ' ' + _("Mark Deceased") + '</button>',
                '</div>',
                html.content_footer()
            ].join("\n");
        },

        bind: function() {
            const validation = function() {
                header.hide_error();
                validate.reset();
                return validate.notblank([ "animal", "deceaseddate" ]);
            };

            validate.indicator([ "animal", "deceaseddate" ]);

            // Callback when animal is changed
            $("#animal").animalchooser().bind("animalchooserchange", function(event, rec) {
              
                // If the animal is not on the shelter, automatically
                // tick the died off shelter box
                if (rec.ARCHIVED == "1") {
                    $("#diedoffshelter").attr("checked", true);
                }
                else {
                    $("#diedoffshelter").attr("checked", false);
                }

            });

            // Set default values
            $("#deceaseddate").datepicker("setDate", new Date());
            $("#deathcategory").select("value", config.str("AFDefaultDeathReason"));

            // Remove any retired lookups from the lists
            $(".asm-selectbox").select("removeRetiredOptions");

            $("#deceased").button().click(async function() {
                if (!validation()) { return; }
                $("#deceased").button("disable");
                header.show_loading(_("Updating..."));
                try {
                    let formdata = "mode=create&" + $("input, select, textarea").toPOST();
                    await common.ajax_post("move_deceased", formdata);
                    header.show_info(_("Animal '{0}' successfully marked deceased.").replace("{0}", $(".animalchooser-display .asm-embed-name").html()));
                    $("#deceaseddate").datepicker("setDate", new Date());
                    $("#animal").animalchooser("clear");
                    $("#ptsreason").val("");
                    $("#puttosleep").attr("checked", false);
                    $("#deadonarrival").attr("checked", false);
                    $("#diedoffshelter").attr("checked", false);
                }
                finally {
                    header.hide_loading();
                    $("#deceased").button("enable");
                }
            });
        },

        destroy: function() {
            common.widget_destroy("#animal");
        },

        name: "move_deceased",
        animation: "newdata",
        autofocus: "#asm-content button:first",
        title: function() { return _("Mark an animal deceased"); },
        routes: {
            "move_deceased": function() { common.module_loadandstart("move_deceased", "move_deceased"); }
        }

    };

    common.module_register(move_deceased);

});
