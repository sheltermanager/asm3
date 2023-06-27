/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const move_foster = {

        render: function() {
            return [
                '<div id="asm-content">',
                '<input id="movementid" type="hidden" />',
                html.content_header(_("Foster an animal"), true),
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
                '<input id="animal" data="animal" class="asm-animalchooser" type="hidden" value="" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="person">' + _("New Fosterer") + '</label>',
                '</td>',
                '<td>',
                '<input id="person" data="person" data-filter="fosterer" class="asm-personchooser" type="hidden" value="" />',
                '</td>',
                '</tr>',
                '<tr id="movementnumberrow">',
                '<td><label for="movementnumber">' + _("Movement Number") + '</label></td>',
                '<td><input id="movementnumber" data="movementnumber" class="asm-textbox" title=',
                '"' + html.title(_("A unique number to identify this movement")) + '"',
                ' /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="fosterdate">' + _("Date") + '</label></td>',
                '<td>',
                '<input id="fosterdate" data="fosterdate" class="asm-textbox asm-datebox" title="' + html.title(_("The date the foster is effective from")) + '" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td></td>',
                '<td><input type="checkbox" class="asm-checkbox" title="' + html.title(_("Is this a permanent foster?")) + '" data="permanentfoster" /> ',
                '<label for="permanentfoster">' + _("Permanent Foster") + '</label></td>',
                '<td>',
                '</tr>',
                '<tr>',
                '<td><label for="returndate">' + _("Returning") + '</label></td>',
                '<td>',
                '<input id="returndate" data="returndate" class="asm-textbox asm-datebox" title="' + html.title(_("The date the foster animal will be returned if known")) + '" />',
                '</td>',
                '</tr>',
                '<tr id="commentsrow">',
                '<td><label for="comments">' + _("Comments") + '</label></td>',
                '<td>',
                '<textarea class="asm-textarea" id="comments" data="comments" rows="3"></textarea>',
                '</td>',
                '</tr>',
                additional.additional_new_fields(controller.additional),
                '</table>',
                html.content_footer(),
                html.box(5),
                '<button id="foster">' + html.icon("movement") + ' ' + _("Foster") + '</button>',
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
                if (common.trim($("#fosterdate").val()) == "") {
                    header.show_error(_("This type of movement requires a date."));
                    validate.highlight("fosterdate");
                    return false;
                }
                // mandatory additional fields
                if (!additional.validate_mandatory()) { return false; }
                return true;
            };

            validate.indicator([ "animal", "person", "fosterdate" ]);

            // Callback when animal is changed
            $("#animal").animalchooser().bind("animalchooserchange", function(event, rec) {
              
                // Hide things before we start
                $("#notonshelter").fadeOut();
                $("#foster").button("enable");

                // If the animal is not on the shelter and not already fostered, show
                // that warning and stop everything else
                if (rec.ARCHIVED == "1" && rec.ACTIVEMOVEMENTTYPE != "2") {
                    $("#notonshelter").fadeIn();
                    $("#foster").button("disable");
                    return;
                }

            });


            $("#notonshelter").hide();

            $("#movementnumberrow").hide();
            if (config.bool("MovementNumberOverride")) {
                $("#movementnumberrow").show();
            }

            // Set default values
            $("#fosterdate").date("today");

            // Remove any retired lookups from the lists
            $(".asm-selectbox").select("removeRetiredOptions", "all");

            $("#foster").button().click(async function() {
                if (!validation()) { return; }
                $("#foster").button("disable");
                header.show_loading(_("Creating..."));
                try {
                    let formdata = "mode=create&" + $("input, select, textarea").toPOST();
                    let data = await common.ajax_post("move_foster", formdata);
                    $("#movementid").val(data);
                    let u = "move_gendoc?" +
                        "linktype=MOVEMENT&id=" + data + 
                        "&message=" + encodeURIComponent(common.base64_encode(_("Foster successfully created.") + " " + 
                            $(".animalchooser-display").html() + " " + html.icon("right") + " " +
                            $(".personchooser-display .justlink").html() ));
                    common.route(u);
                }
                finally {
                    header.hide_loading();
                    $("#foster").button("enable");
                }
            });
        },

        destroy: function() {
            common.widget_destroy("#animal");
            common.widget_destroy("#person");
        },


        name: "move_foster",
        animation: "newdata",
        autofocus: "#asm-content button:first",
        title: function() { return _("Foster an animal"); },
        routes: {
            "move_foster": function() { common.module_loadandstart("move_foster", "move_foster"); }
        }

    };

    common.module_register(move_foster);

});
