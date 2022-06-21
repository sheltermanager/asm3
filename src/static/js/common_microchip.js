/*global $, _, common, asm */
/*global microchip: true */

"use strict";

/**
 * Module to provide microchip related services.
 */
const microchip = {

    /**
     * Looks up the manufacturer for a given microchip number.
     * selnumber: DOM selector for the input containing the number
     * selbrand:  DOM selector for the label showing the manufacturer
     */
    manufacturer: function(selnumber, selbrand) {
        var m, n = $(selnumber).val();
        if (!n) { $(selbrand).fadeOut(); return; }
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
    }

};
