/*global $, jQuery, controller */
/*global common, config, format, html */
/*global _, mobile, mobile_ui_addanimal, mobile_ui_animal, mobile_ui_addanimal, mobile_ui_person */
/*global mobile_ui_stock: true */

"use strict";

const mobile_ui_stock = {

    bind: () => {

        // Create the stock take screen when a stock location is chosen
        let active_stocklocation = "";
        $("#content-stocklocations").on("click", "a", function() {
            let pid = $(this).attr("data-id");
            active_stocklocation = $(this).find(".stock-locationname").text();
            mobile.ajax_post("mode=getstocklevel&id=" + pid, function(response) {
                let j = jQuery.parseJSON(response);
                let usage = '<div class="mb-3">' +
                    '<label for="usagetype" class="form-label">' + _("Usage Type") + '</label>' +
                    '<select class="form-select" id="usagetype" name="usage">' +
                    html.list_to_options(j.usagetypes, "ID", "USAGETYPENAME") +
                    '</select>' +
                    '</div>';
                $("#content-stocktake .locations").empty();
                $("#content-stocktake .locations").prepend(usage);
                $.each(j.levels, function(i, v) {
                    let h = '<div class="list-group-item list-group-item-action">' +
                        '<div class="mb-3">' +
                        '<label class="form-label">' + v.NAME + ' (' + v.BALANCE + '/' + v.TOTAL + ')</label>' + 
                        '<input type="text" class="form-control stockbalance" data-id="' + v.ID + '" value="' + v.BALANCE + '">' +
                        '</div>' +
                        '</div>';
                    $("#content-stocktake .locations").append(h);
                });
                $("#btn-submit-stocktake").toggle( j.levels.length > 0 );
                $(".container").hide();
                $("#content-stocktake").show();
            });
        });

        // Handle submitting the stock take screen
        $("#btn-submit-stocktake").click(function() {
            let x = [];
            $("#content-stocktake .stockbalance").each(function() {
                x.push("sl" + $(this).attr("data-id") + "=" + $(this).val());
            });
            $("#btn-submit-stocktake .spinner-border").show();
            mobile.ajax_post("mode=stocktake&usagetype=" + $("#usagetype").val() + "&" + x.join("&"), function() {
                $("#btn-submit-stocktake .spinner-border").hide();
                mobile.show_info(_("Stock Take"), _("Stock levels for location '{0}' updated.").replace("{0}", active_stocklocation));
                $(".container").hide();
                $("#content-stocklocations").show();
            });
        });

    },

    sync: () => {
        // Load stock locations list
        $("#content-stocklocations .list-group").empty();
        $.each(controller.stocklocations, function(i, v) {
            let h = '<a href="#" data-id="' + v.ID + '" class="list-group-item list-group-item-action">' +
                '<h5 class="mb-1"><span class="stock-locationname">' + v.LOCATIONNAME + '</span> ' + 
                '<span class="badge bg-primary rounded-pill">' + v.TOTAL + '</span>' + '</h5>' +
                '<small>' + v.LOCATIONDESCRIPTION + '</small>' + 
                '</a>';
            $("#content-stocklocations .list-group").append(h);
        });
    }

};
