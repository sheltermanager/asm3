/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const move_retailer = {

        render: function() {
            return [
                '<div id="asm-content">',
                '<input id="movementid" type="hidden" />',
                html.content_header(_("Move an animal to a retailer"), true),
                html.textbar(_("This animal is not on the shelter."), { id: "notonshelter", state: "error", icon: "alert", maxwidth: "600px" }),
                tableform.fields_render([
                    { post_field: "animal", label: _("Animal"), type: "animal" },
                    { post_field: "person", label: _("Retailer"), type: "person", personfilter: "retailer" },
                    { post_field: "movementnumber", label: _("Movement Number"), type: "text", rowid: "movementnumberrow", 
                        callout: _("A unique number to identify this movement") },
                    { post_field: "retailerdate", label: _("Date"), type: "date", callout: _("The date the retailer movement is effective from") },
                    { post_field: "comments", label: _("Comments"), type: "textarea", rows: 3 },
                    { type: "additional", markup: additional.additional_new_fields(controller.additional) }
                ], { full_width: false }),
                html.content_footer(),
                tableform.buttons_render([
                   { id: "retailer", icon: "movement", text: _("Move") }
                ], { render_box: true }),
                '</div>'
            ].join("\n");
        },

        bind: function() {
            const validation = function() {
                // Remove any previous errors
                header.hide_error();
                validate.reset();
                if (!validate.notzero([ "animal", "person" ])) { return false; }
                if (!validate.notblank([ "retailerdate" ])) { return false; }
                // mandatory additional fields
                if (!additional.validate_mandatory()) { return false; }
                return true;
            };

            validate.indicator([ "animal", "person", "retailerdate" ]);

            // Callback when animal is changed
            $("#animal").animalchooser().bind("animalchooserchange", function(event, rec) {
              
                // Hide things before we start
                $("#notonshelter").hide();
                $("#button-retailer").button("enable");

                // If the animal is not on the shelter, show that warning
                // and stop everything else
                if (rec.ARCHIVED == "1") {
                    $("#notonshelter").show();
                    $("#button-retailer").button("disable");
                    return;
                }

            });


            $("#notonshelter").hide();
 
            $("#movementnumberrow").hide();
            if (config.bool("MovementNumberOverride")) {
                $("#movementnumberrow").show();
            }

            // Set default values
            $("#retailerdate").date("today");

            // Remove any retired lookups from the lists
            $(".asm-selectbox").select("removeRetiredOptions", "all");

            $("#button-retailer").button().click(async function() {
                if (!validation()) { return; }
                $("#button-retailer").button("disable");
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
                    $("#button-retailer").button("enable");
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
