/*global $, _, common, asm, config, header */
/*global microchip: true */

"use strict";

/**
 * Module to provide microchip related services.
 */
const microchip = {

    /**
     * Looks up the manufacturer for a given microchip number.
     * The manufacturer list is passed as part of config.js in the asm global (from lookup.py)
     * selnumber: DOM selector for the input containing the number
     * selbrand:  DOM selector for the label showing the manufacturer
     */
    manufacturer: function(selnumber, selbrand) {
        var m, n = $(selnumber).val();
        if (!n) { $(selbrand).fadeOut(); return; }
        if (config.bool("DontShowMicrochipSupplier")) { $(selbrand).fadeOut(); return; }
        $.each(asm.microchipmanufacturers, function(i, v) {
            if (n.length == v.length && new RegExp(v.regex).test(n)) {
                if (v.locales == "" || common.array_in(asm.locale, v.locales.split(" "))) {
                    m = "<span style='font-weight: bold'>" + v.name + "</span>";
                    return false;
                }
            }
        });
        if (!m && (n.length != 9 && n.length != 10 && n.length != 15)) {
            m = "<span style='font-weight: bold; color: red'>" + _("Invalid microchip number length") + "</span>";
        }
        if (!m) {
            m = "<span style='font-weight: bold; color: red'>" + _("Unknown microchip brand") + "</span>";
        }
        $(selbrand).html(m);
        $(selbrand).fadeIn();
    },

    is_check_available: function(chipnumber) {
        if (chipnumber.length != 15 && chipnumber.length != 10 && chipnumber.length != 9) { return false; }
        return asm.locale == "en" || asm.locale == "en_GB";
    },

    check_site_name: function() {
        if (asm.locale == "en") { return _("Check {0}").replace("{0}", "www.aaha.org"); }
        else if (asm.locale == "en_GB") { return _("Check {0}").replace("{0}", "www.checkachip.com"); }
        return "";
    },

    /* Calls out to chip checking services for the user's locale so they can find out where a chip
     * is registered.
     */
    check: function(chipnumber) {
        // USA - use AAHA
        if (asm.locale == "en") {
            header.show_loading(_("Loading..."));
            window.location = "https://www.aaha.org/your-pet/pet-microchip-lookup/microchip-search/?microchip_id=" + chipnumber + "&AllowNonAlphaNumberic=0";
        }
        // UK - use checkachip.com
        else if (asm.locale == "en_GB") {
            header.show_loading(_("Loading..."));
            $("body").append(
                '<form id="cac" method="post" action="https://www.checkachip.com/microchipsearch/">' +
                '<input type="hidden" name="microchip_number" value="' + chipnumber + '">' +
                '<input type="hidden" name="are_you" value="no">' + 
                '<input type="hidden" name="phone_number" value="">' + 
                '</form>');
            $("#cac").submit();
        }
    }

};
