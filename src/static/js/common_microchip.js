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
        return asm.locale == "en" || asm.locale == "en_AU" || asm.locale == "en_GB";
    },

    check_site_name: function() {
        if (asm.locale == "en") { return _("Check {0}").replace("{0}", "www.aaha.org"); }
        else if (asm.locale == "en_AU") { return _("Check {0}").replace("{0}", "www.petaddress.com.au"); }
        else if (asm.locale == "en_GB") { return _("Check {0}").replace("{0}", "www.checkachip.com"); }
        return "";
    },

    /* Calls out to chip checking services for the user's locale so they can find out where a chip
     * is registered.
     */
    check: async function(chipnumber) {
        header.show_loading(_("Loading..."));
        let data = await common.ajax_post("animal", "mode=checkchip&n=" + chipnumber);
        let results = JSON.parse(data);
        let h = [];
        $.each(results.results, function(i, v) {
            h.push('<a target="_blank" href="' + v[0] + '">' + v[1] + '</a><br>');
        });
        if (results.results.length == 0) {
            h.push('<p>' + _("No results.") + '</p>');
        }
        $("#chipcheck-number").text(chipnumber);
        $("#chipcheck-service").html(results.name);
        $("#chipcheck-results").html(h.join("\n"));
        await tableform.show_okcancel_dialog("#dialog-chipcheck", _("Ok"), { hidecancel: true });
    },

    render_checkresults_dialog: function() {
        return '<div id="dialog-chipcheck" style="display: none" title="' + html.title(_("Check Microchip")) + '">' +
            html.info(_("{0} results for {1}")
                .replace("{0}", '<span id="chipcheck-service"></span>')
                .replace("{1}", '<span id="chipcheck-number"></span>')) +
                '<p id="chipcheck-results"></p></div>';
    }
};
