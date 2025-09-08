/*global alert */
/*global asm3_adoptable_filters, asm3_adoptable_iframe, asm3_adoptable_iframe_height, asm3_adoptable_iframe_bgcolor, asm3_adoptable_iframe_fixed */
/*global asm3_adoptable_translations, asm3_adoptable_extra, asm3_adoptable_filter, asm3_adoptable_limit, asm3_adoptable_sort, asm3_adoptable_style */

// NOTE: This file stands alone and should try for compatibility 
//       with as many browsers as possible. It also does not use jQuery.
//       Avoid use of let/const, async/await, destructuring, etc.

(function() {
    var div_id = "asm3-onlineform";

    var render_iframe = function() {
        var hostdiv = document.getElementById(div_id);
        hostdiv.innerHTML = '<iframe id="asm3-form-iframe" scrolling="no" style="width: 100%;border: 0;height: auto;"></iframe>';
        document.getElementById("asm3-form-iframe").src = '{SERVICE_URL}?method=online_form_html&formid={TOKEN_FORMID}';
    };

    var onReady = function(event) {
        window.removeEventListener( "load", onReady );
        var hostdiv = document.getElementById(div_id);
        if (!hostdiv) { alert("#" + div_id + " not present"); return; }
        render_iframe();
    };

    window.addEventListener("load", onReady);

    window.addEventListener('message', function(ev) {
		document.getElementById('asm3-form-iframe').style.height = String(ev.data) + 'px';
	});
}());
