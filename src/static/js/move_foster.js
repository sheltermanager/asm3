/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const move_foster = {

        render: function() {
            return [
                '<div id="asm-content">',
                '<input id="movementid" type="hidden" />',
                html.content_header(_("Foster an animal"), true),
                html.textbar(_("This animal is not on the shelter."), { id: "notonshelter", state: "error", icon: "alert", maxwidth: "600px" }),
                tableform.fields_render([
                    { post_field: "animal", label: _("Animal"), type: "animal" },
                    { post_field: "person", label: _("New Fosterer"), type: "person", personfilter: "fosterer" },
                    { post_field: "movementnumber", label: _("Movement Number"), type: "text", rowid: "movementnumberrow", 
                        callout: _("A unique number to identify this movement") },
                    { post_field: "fosterdate", label: _("Date"), type: "date" },
                    { post_field: "permanentfoster", label: _("Permanent Foster"), type: "check" },
                    { post_field: "returndate", label: _("Returning"), type: "date", 
                        callout: _("The date the foster animal will be returned if known") },
                    { post_field: "comments", label: _("Comments"), type: "textarea", rows: 3 }
                ], 1, { full_width: false }),
                '<table class="asm-table-layout">',
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
                if (!validate.notzero([ "animal", "person" ])) { return false; }
                if (!validate.notblank([ "fosterdate" ])) { return false; }
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
