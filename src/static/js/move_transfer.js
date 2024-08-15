/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const move_transfer = {

        render: function() {
            return [
                '<div id="asm-content">',
                '<input id="movementid" type="hidden" />',
                html.content_header(_("Transfer an animal"), true),
                html.textbar('<span id="awarntext"></span>', { id: "animalwarn", state: "error", icon: "alert", maxwidth: "600px" }),
                html.textbar('<span id="warntext"></span>', { id: "ownerwarn", state: "error", icon: "alert", maxwidth: "600px" }),
                tableform.fields_render([
                    { post_field: "animal", label: _("Animal"), type: "animal" },
                    { post_field: "person", label: _("Transfer To"), type: "person", personfilter: "shelter" },
                    { post_field: "movementnumber", label: _("Movement Number"), type: "text", rowid: "movementnumberrow", 
                        callout: _("A unique number to identify this movement") },
                    { post_field: "transferdate", label: _("Date"), type: "date", callout: _("The date the transfer is effective from") },
                    { post_field: "comments", label: _("Comments"), type: "textarea", rows: 3 }
                ], { full_width: false }),
                '<table class="asm-table-layout">',
                additional.additional_new_fields(controller.additional),
                '</table>',
                html.content_footer(),
                html.box(5),
                '<button id="transfer">' + html.icon("movement") + ' ' + _("Transfer") + '</button>',
                '</div>',
                '</div>'
            ].join("\n");
        },

        bind: function() {

            const validation = function() {
                // Remove any previous errors
                header.hide_error();
                validate.reset();
                if (!validate.notzero([ "animal", "person" ])) { return false; }
                if (!validate.notblank([ "transferdate" ])) { return false; }
                // mandatory additional fields
                if (!additional.validate_mandatory()) { return false; }
                return true;
            };

            validate.indicator([ "animal", "person", "transferdate" ]);

            $("#animalwarn").hide();
            $("#ownerwarn").hide();

            // Callback when animal is changed
            $("#animal").animalchooser().bind("animalchooserchange", function(event, a) {
              
                $("#animalwarn").fadeOut();
                $("#transfer").button("enable");

                // Disable the transfer button if the animal is not in care
                if ((a.ARCHIVED == 1 && a.ACTIVEMOVEMENTTYPE != 2 && a.ACTIVEMOVEMENTTYPE != 8)) {
                    $("#transfer").button("disable");
                }

                let warn = html.animal_movement_warnings(a);
                if (warn.length > 0) {
                    $("#awarntext").html(warn.join("<br>"));
                    $("#animalwarn").fadeIn();
                }

            });

            // Callback when person is changed
            $("#person").personchooser().bind("personchooserchange", function(event, p) {

                let warn = html.person_movement_warnings(p);
                if (warn.length > 0) {
                    $("#warntext").html(warn.join("<br>"));
                    $("#ownerwarn").fadeIn();
                }
            });

            $("#movementnumberrow").hide();
            if (config.bool("MovementNumberOverride")) {
                $("#movementnumberrow").show();
            }

            // Set default values
            $("#transferdate").date("today");

            // Remove any retired lookups from the lists
            $(".asm-selectbox").select("removeRetiredOptions", "all");

            $("#transfer").button().click(async function() {
                if (!validation()) { return; }
                $("#transfer").button("disable");
                header.show_loading(_("Creating..."));
                try {
                    let formdata = "mode=create&" + $("input, select, textarea").toPOST();
                    let data = await common.ajax_post("move_transfer", formdata);
                    $("#movementid").val(data);
                    let u = "move_gendoc?" +
                        "linktype=MOVEMENT&id=" + data + 
                        "&message=" + encodeURIComponent(common.base64_encode(_("Transfer successfully created.") + " " + 
                            $(".animalchooser-display").html() + " " + html.icon("right") + " " +
                            $(".personchooser-display .justlink").html() ));
                    common.route(u);
                }
                finally {
                    header.hide_loading();
                    $("#transfer").button("enable");
                }
            });
        },

        destroy: function() {
            common.widget_destroy("#animal");
            common.widget_destroy("#person");
        },

        name: "move_transfer",
        animation: "newdata",
        autofocus: "#asm-content button:first",
        title: function() { return _("Transfer an animal"); },
        routes: {
            "move_transfer": function() { common.module_loadandstart("move_transfer", "move_transfer"); }
        }

    };

    common.module_register(move_transfer);

});
