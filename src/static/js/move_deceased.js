/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    var move_deceased = {

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
                '<td></td>',
                '<td><input class="asm-checkbox" type="checkbox" id="diedoffshelter" data="diedoffshelter" title="' + html.title(_("This animal died outside the care of the shelter, and the death should be kept out of reports")) + '" />',
                '<label for="diedoffshelter">' + _("Died off shelter") + '</label>',
                '</td></tr>',
                '<tr>',
                '<td><label for="ptsreason">' + _("Notes") + '</label></td>',
                '<td>',
                '<textarea class="asm-textarea" title="' + _("Notes about the death of the animal") + '" id="ptsreason" data="ptsreason" rows="8"></textarea>',
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
            var validation = function() {
                // Remove any previous errors
                header.hide_error();
                $("label").removeClass("ui-state-error-text");
                // animal
                if ($("#animal").val() == "") {
                    $("label[for='animal']").addClass("ui-state-error-text");
                    $("#animal").focus();
                    return false;
                }
                // date
                if ($.trim($("#deceaseddate").val()) == "") {
                    $("label[for='deceaseddate']").addClass("ui-state-error-text");
                    $("#deceaseddate").focus();
                    return false;
                }
                return true;
            };

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

            $("#deceased").button().click(function() {
                if (!validation()) { return; }
                $("#deceased").button("disable");
                header.show_loading(_("Updating..."));

                var formdata = $("input, select, textarea").toPOST();
                common.ajax_post("move_deceased", formdata, function(data) {
                    header.hide_loading();
                    header.show_info(_("Animal '{0}' successfully marked deceased.").replace("{0}", $(".animalchooser-display .asm-embed-name").html()));
                    $("#deceaseddate").datepicker("setDate", new Date());
                    $("#animal").animalchooser("clear");
                    $("#ptsreason").val("");
                    $("#puttosleep").attr("checked", false);
                    $("#deadonarrival").attr("checked", false);
                    $("#diedoffshelter").attr("checked", false);
                    $("#deceased").button("enable");
                }, function() {
                    $("#deceased").button("enable");
                });
            });
        },

        destroy: function() {
            common.widget_destroy("#animal");
        },

        name: "move_deceased",
        animation: "newdata",
        title: function() { return _("Mark an animal deceased"); },
        routes: {
            "move_deceased": function() { common.module_loadandstart("move_deceased", "move_deceased"); }
        }

    };

    common.module_register(move_deceased);

});
