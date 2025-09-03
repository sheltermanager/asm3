/*global alert */
/*global asm3_adoptable_filters, asm3_adoptable_iframe, asm3_adoptable_iframe_height, asm3_adoptable_iframe_bgcolor, asm3_adoptable_iframe_fixed */
/*global asm3_adoptable_translations, asm3_adoptable_extra, asm3_adoptable_filter, asm3_adoptable_limit, asm3_adoptable_sort, asm3_adoptable_style */

// NOTE: This file stands alone and should try for compatibility 
//       with as many browsers as possible. It also does not use jQuery.
//       Avoid use of let/const, async/await, destructuring, etc.

(function() {

    var formhtml = `{TOKEN_FORM}`;

    var use_iframe = true;
    if (typeof asm3_form_iframe !== 'undefined') {
        use_iframe = asm3_form_iframe;
    }

    var iframe_back = true;
    if (typeof asm3_adoptable_iframe_closeonback !== 'undefined') {
        iframe_back = asm3_adoptable_iframe_closeonback;
    }

    var iframe_fixed = true;
    if (typeof asm3_form_iframe_fixed !== 'undefined') {
        iframe_fixed = asm3_form_iframe_fixed;
    }
    var iframe_position = iframe_fixed ? "fixed" : "absolute";

    var iframe_height = "6000px";
    if (typeof asm3_form_iframe_height !== 'undefined') {
        iframe_height = asm3_form_iframe_height;
    }

    var iframe_bgcolor = "#fff";
    if (typeof asm3_form_iframe_bgcolor !== 'undefined') {
        iframe_bgcolor = asm3_form_iframe_bgcolor;
    }

    var div_id = "asm3-form";
    if (typeof asm3_form_div_id !== 'undefined') {
        div_id = asm3_form_div_id;
    }

    var delay = 0;
    if (typeof asm3_form_delay !== 'undefined') {
        delay = asm3_form_delay;
    }

    var translate = function(s) {
        if (typeof asm3_form_translations !== 'undefined') {
            if (asm3_form_translations.hasOwnProperty(s)) {
                return asm3_form_translations[s];
            }
        }
        return s;
    };

    var decode_div = document.createElement('div');
    var decode = function(s) {
        decode_div.innerHTML = s;
        s = decode_div.textContent;
        decode_div.textContent = '';
        return s;
    };

    var substitute = function(str, sub) {
        /*jslint regexp: true */
        return str.replace(/\{(.+?)\}/g, function($0, $1) {
            return sub.hasOwnProperty($1) ? sub[$1] : $0;
        });
    };

    var overlay_template = [
        '<div id="asm3-form-iframe-overlay" style="z-index: 9999; display: none; overflow: auto;">',
            // '<p style="text-align: right;">',
            //     '<a id="asm3-form-iframe-close" href="#">&times; ' + translate("CLOSE") + '</a>&nbsp;&nbsp;',
            // '</p>',
            '<iframe id="asm3-form-iframe" scrolling="yes" style="width: 100%;border: 0;"></iframe>',
        '</div>'
    ].join("");

    var render_iframe = function() {
        var hostdiv = document.getElementById(div_id);
        var overlay = hostdiv;
        overlay.innerHTML = overlay_template;
        //document.body.appendChild(overlay);
        // document.getElementById("asm3-form-iframe-close").addEventListener("click", function(e) {
        //     if (iframe_back) { window.history.back(); }
        //     document.getElementById("asm3-form-iframe").src = "about:blank";
        //     document.getElementById("asm3-form-iframe-overlay").style.display = "none";
        //     e.preventDefault();
        // });
        // var i, 
            // link_handler = function(e) {
            //     document.getElementById("asm3-form-iframe").src = this.href;
            //     document.getElementById("asm3-form-iframe-overlay").style.display = "block";
            //     if (!iframe_fixed) { window.scrollTo(0, 0); }
            //     if (iframe_back) { window.history.pushState("close", "", ""); }
            //     e.preventDefault();
            // },
            popstate_handler = function(e) {
                // NOTE: The loading of the form into the iframe causes a new entry in the
                // history stack. There is nothing we can do about this. The first back
                // causes the iframe page to unload back to about:blank, the second then
                // hits our history state here allowing us to close the iframe.
                // if (e.state != "close") { return; }
                document.getElementById("asm3-form-iframe").src = "about:blank";
                // document.getElementById("asm3-form-iframe-overlay").style.display = "none";
            };
        // document.getElementById("asm3-form-iframe").src = this.href;
        // document.getElementById("asm3-form-iframe").innerHTML = formhtml;
        document.getElementById("asm3-form-iframe").src = 'http://localhost:5000/service?method=online_form_html&formid=3';
        document.getElementById("asm3-form-iframe-overlay").style.display = "block";
        if (!iframe_fixed) { window.scrollTo(0, 0); }
        if (iframe_back) { window.history.pushState("close", "", ""); }
        if (iframe_back) { 
            window.addEventListener("popstate", popstate_handler);
        }
    };

    var render = function() {

        // var hostdiv = document.getElementById(div_id);
        var hostdiv = document.getElementById(div_id);

        // if (!hostdiv) { alert("#" + div_id + " not present"); return; }
        if (!hostdiv) { console.log("#" + div_id + " not present"); return; }

        // hostdiv.innerHTML = '<h1>Hello World</h1>';
        // hostdiv.innerHTML = formhtml;

        // console.log(formhtml);

        //render_iframe();
    };

    var onReady = function(event) {
        window.removeEventListener( "load", onReady );
        var hostdiv = document.getElementById(div_id);
        if (!hostdiv) { console.log("#" + div_id + " not present"); return; }
        setTimeout(render_iframe, delay);
    };

    window.addEventListener("load", onReady);

}());
