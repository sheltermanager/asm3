/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const move_retailer = {

        render: function() {
            return [
                '<div id="asm-content">',
                '<input id="movementid" type="hidden" />',
                html.content_header(_("Move an animal to a retailer"), true),
                '<div id="notonshelter" class="ui-state-error ui-corner-all" style="margin-top: 5px; padding: 0 .7em; width: 60%; margin-left: auto; margin-right: auto">',
                '<p class="centered"><span class="ui-icon ui-icon-alert"></span>',
                '<span class="centered">' + _("This animal is not on the shelter.") + '</span>',
                '</p>',
                '</div>',
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
                '<label for="person">' + _("Retailer") + '</label>',
                '</td>',
                '<td>',
                '<input id="person" data="person" data-filter="retailer" type="hidden" class="asm-personchooser" value=\'\' />',
                '</td>',
                '</tr>',
                '<tr id="movementnumberrow">',
                '<td><label for="movementnumber">' + _("Movement Number") + '</label></td>',
                '<td><input id="movementnumber" data="movementnumber" class="asm-textbox" title=',
                '"' + html.title(_("A unique number to identify this movement")) + '"',
                ' /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="retailerdate">' + _("Date") + '</label></td>',
                '<td>',
                '<input id="retailerdate" data="retailerdate" class="asm-textbox asm-datebox" title="' + html.title(_("The date the retailer movement is effective from")) + '" />',
                '</td>',
                '</tr>',
                '<tr id="commentsrow">',
                '<td><label for="comments">' + _("Comments") + '</label></td>',
                '<td>',
                '<textarea class="asm-textarea" id="comments" data="comments" rows="3"></textarea>',
                '</td>',
                '</tr>',
                '</table>',
                html.content_footer(),
                html.box(5),
                '<button id="retailer">' + html.icon("movement") + ' ' + _("Move") + '</button>',
                '</div>',
                '</div>'
            ].join("\n");
        },

        bind: function() {
            const validation = function() {
                // Remove any previous errors
                header.hide_error();
                validate.reset();
                // animal
                if ($("#animal").val() == "") {
                    header.show_error(_("Movements require an animal"));
                    validate.highlight("animal");
                    return false;
                }
                // person
                if ($("#person").val() == "") {
                    header.show_error(_("This type of movement requires a person."));
                    validate.highlight("person");
                    return false;
                }
                // date
                if (common.trim($("#retailerdate").val()) == "") {
                    header.show_error(_("This type of movement requires a date."));
                    validate.highlight("retailerdate");
                    return false;
                }
                return true;
            };

            validate.indicator([ "animal", "person", "retailerdate" ]);

            // Callback when animal is changed
            $("#animal").animalchooser().bind("animalchooserchange", function(event, rec) {
              
                // Hide things before we start
                $("#notonshelter").fadeOut();
                $("#retailer").button("enable");

                // If the animal is not on the shelter, show that warning
                // and stop everything else
                if (rec.ARCHIVED == "1") {
                    $("#notonshelter").fadeIn();
                    $("#retailer").button("disable");
                    return;
                }

            });


            $("#notonshelter").hide();
 
            $("#movementnumberrow").hide();
            if (config.bool("MovementNumberOverride")) {
                $("#movementnumberrow").show();
            }

            // Set default values
            $("#retailerdate").datepicker("setDate", new Date());

            // Remove any retired lookups from the lists
            $(".asm-selectbox").select("removeRetiredOptions", "all");

            $("#retailer").button().click(async function() {
                if (!validation()) { return; }
                $("#retailer").button("disable");
                header.show_loading(_("Creating..."));
                try { 
                    let formdata = "mode=create&" + $("input, select, textarea").toPOST();
                    let data = await common.ajax_post("move_retailer", formdata);
                    $("#movementid").val(data);
                    let u = "move_gendoc?" +
                        "linktype=MOVEMENT&id=" + data +
                        "&message=" + encodeURIComponent(common.base64_encode(_("Retailer movement successfully created.") + " " + 
                            $(".animalchooser-display").html() + " " + html.icon("right") + " " +
                            $(".personchooser-display .justlink").html() ));
                    common.route(u);
                }
                finally {
                    header.hide_loading();
                    $("#retailer").button("enable");
                }
            });

        },

        destroy: function() {
            common.widget_destroy("#animal");
            common.widget_destroy("#person");
        },

        name: "move_retailer",
        animation: "newdata",
        autofocus: "#asm-content button:first",
        title: function() { return _("Move an animal to a retailer"); },
        routes: {
            "move_retailer": function() { common.module_loadandstart("move_retailer", "move_retailer"); }
        }

    };

    common.module_register(move_retailer);

});
