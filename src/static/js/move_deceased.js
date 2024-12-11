/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const move_deceased = {

        render: function() {
            return [
                '<div id="asm-content">',
                html.content_header(_("Mark an animal deceased"), true),
                tableform.fields_render([
                    { post_field: "animal", label: _("Animal"), type: "animal" },
                    { post_field: "deceaseddate", label: _("Deceased Date"), type: "date" },
                    { post_field: "deathcategory", label: _("Category"), type: "select", 
                        options: { displayfield: "REASONNAME", valuefield: "ID", rows: controller.deathreasons }},
                    { post_field: "puttosleep", label: _("Euthanized"), type: "check" },
                    { post_field: "deadonarrival", label: _("Dead on arrival"), type: "check" },
                    { post_field: "ptsreason", label: _("Notes"), type: "textarea", rows: 8 },
                ], { full_width: false }),
                html.content_footer(),
                html.content_header(_("Stock"), true),
                html.textbar(_("These fields allow you to deduct stock for any euthanasia administered."), { maxwidth: "600px" }),
                tableform.fields_render([
                    { post_field: "item", label: _("Item"), type: "select", 
                        options: { displayfield: "ITEMNAME", valuefield: "ID", rows: controller.stockitems }},
                    { post_field: "quantity", label: _("Quantity"), type: "number" },
                    { post_field: "usagetype", label: _("Usage Type"), type: "select",
                        options: { displayfield: "USAGETYPENAME", valuefield: "ID", rows: controller.stockusagetypes }},
                    { post_field: "usagedate", label: _("Usage Date"), type: "date" },
                    { post_field: "usagecomments", label: _("Comments"), type: "textarea" }
                ], { full_width: false, id: "stocktable" }),
                html.content_footer(),
                tableform.buttons_render([
                   { id: "deceased", icon: "death", text: _("Mark Deceased") }
                ], { render_box: true }),
                '</div>'
            ].join("\n");
        },

        bind: function() {
            const validation = function() {
                header.hide_error();
                validate.reset();
                if (!validate.notzero([ "animal" ])) { return false; }
                if (!validate.notblank([ "deceaseddate" ])) { return false; }
                return true;
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
            $("#deceaseddate").date("today");
            $("#deathcategory").select("value", config.str("AFDefaultDeathReason"));
            $("#usagedate").date("today");

            // Add no deduction to list
            $("#item").prepend('<option value="-1">' + _("(no deduction)") + '</option>');
            $("#item").val("-1");

            // Hide stock deductions if stock control is disabled
            if (config.bool("DisableStockControl")) {
                $("#stocktable").parent().parent().hide();
            }

            // Remove any retired lookups from the lists
            $(".asm-selectbox").select("removeRetiredOptions", "all");

            $("#button-deceased").button().click(async function() {
                if (!validation()) { return; }
                $("#button-deceased").button("disable");
                header.show_loading(_("Updating..."));
                try {
                    let formdata = "mode=create&" + $("input, select, textarea").toPOST();
                    await common.ajax_post("move_deceased", formdata);
                    header.show_info(_("Animal '{0}' successfully marked deceased.").replace("{0}", $(".animalchooser-display .asm-embed-name").html()));
                    $("#deceaseddate").date("today");
                    $("#animal").animalchooser("clear");
                    $("#ptsreason").val("");
                    $("#puttosleep").attr("checked", false);
                    $("#deadonarrival").attr("checked", false);
                    $("#diedoffshelter").attr("checked", false);
                }
                finally {
                    header.hide_loading();
                    $("#button-deceased").button("enable");
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
