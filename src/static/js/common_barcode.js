/*global $, console, jQuery, common */
/*global barcode: true */

"use strict";

const barcode = {

    deferred: null,

    /** 
     *  Triggers a barcode scan. Returns a promise that will contain the scan result.
     *  Currently using zxing android/iOS compatible apps with zxing: URL scheme, but should
     *  be able to slot in a pure JS scanner if one comes along that is actually usable.
     *  For now, this works by directing to a zxing URL scheme, which calls back to
     *  a service endpoint with the scanned value. That endpoint puts the result into
     *  localStorage, which we catch with an event here to resolve the promise.
     */
    scan: function() {
        barcode.deferred = $.Deferred();
        common.local_set("zxing_result", "");
        let targeturl = "zxing://scan/?ret=" + asm.serviceurl + "?account=" + asm.useraccount + "&method=barcode_scan_result&barcode={CODE}";
        window.location = targeturl;
        return barcode.deferred;
    },

};

/** We only need one global listener to handle changes to localstorage to look for barcode results from zxing */
window.addEventListener("storage", function() {
    let rv = common.local_get("zxing_result");
    if (rv && rv == "cancel") { barcode.deferred.reject("cancel"); }
    if (rv) { barcode.deferred.resolve(rv); }
});
