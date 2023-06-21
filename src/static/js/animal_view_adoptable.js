/*global alert */
/*global asm3_adoptable_filters, asm3_adoptable_iframe, asm3_adoptable_iframe_height, asm3_adoptable_iframe_bgcolor, asm3_adoptable_iframe_fixed */
/*global asm3_adoptable_translations, asm3_adoptable_extra, asm3_adoptable_filter, asm3_adoptable_limit, asm3_adoptable_sort, asm3_adoptable_style */

// NOTE: This file stands alone and should try for compatibility 
//       with as many browsers as possible. It also does not use jQuery.
//       Avoid use of let/const, async/await, destructuring, etc.

(function() {

    var adoptables = "{TOKEN_ADOPTABLES}";
    var account = "{TOKEN_ACCOUNT}";
    var baseurl = "{TOKEN_BASE_URL}";
    var all_filters = "agegroup sex breed size species goodwith where";

    var active_filters = "agegroup sex species";
    if (typeof asm3_adoptable_filters !== 'undefined') {
        active_filters = asm3_adoptable_filters;
    }
    var filters_tokens = [];
    active_filters.split(" ").forEach(function(item, index, arr) {
        filters_tokens.push("{" + item + "}");
    });

    var fullsize_images = false;
    if (typeof asm3_adoptable_fullsize_images !== 'undefined') {
        fullsize_images = asm3_adoptable_fullsize_images;
    }

    var use_iframe = false;
    if (typeof asm3_adoptable_iframe !== 'undefined') {
        use_iframe = asm3_adoptable_iframe;
    }

    var iframe_back = true;
    if (typeof asm3_adoptable_iframe_closeonback !== 'undefined') {
        iframe_back = asm3_adoptable_iframe_closeonback;
    }

    var iframe_fixed = false;
    if (typeof asm3_adoptable_iframe_fixed !== 'undefined') {
        iframe_fixed = asm3_adoptable_iframe_fixed;
    }
    var iframe_position = iframe_fixed ? "fixed" : "absolute";

    var iframe_height = "6000px";
    if (typeof asm3_adoptable_iframe_height !== 'undefined') {
        iframe_height = asm3_adoptable_iframe_height;
    }

    var iframe_bgcolor = "#fff";
    if (typeof asm3_adoptable_iframe_bgcolor !== 'undefined') {
        iframe_bgcolor = asm3_adoptable_iframe_bgcolor;
    }

    var sort_order = "ANIMALNAME";
    if (typeof asm3_adoptable_sort !== 'undefined') {
        sort_order = asm3_adoptable_sort;
    }

    var limit = 0;
    if (typeof asm3_adoptable_limit !== 'undefined') {
        limit = asm3_adoptable_limit;
    }

    var style = "animalview";
    if (typeof asm3_adoptable_style !== 'undefined') {
        style = asm3_adoptable_style;
    }

    var translate = function(s) {
        if (typeof asm3_adoptable_translations !== 'undefined') {
            if (asm3_adoptable_translations.hasOwnProperty(s)) {
                return asm3_adoptable_translations[s];
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

    var sort_single = function(fieldname) {
        var sortOrder = 1, comp = 0;
        if (fieldname.indexOf("-") != -1) {
            sortOrder = -1;
            fieldname = fieldname.replace("-", "");
        }
        if (fieldname.indexOf("@") != -1) {
            fieldname = fieldname.replace("@", "");
            comp = 1; 
        }
        return function (a,b) {
            var ca, cb;
            if (comp == 0) { ca = String(a[fieldname]).toUpperCase(); cb = String(b[fieldname]).toUpperCase(); }
            if (comp == 1) { ca = a[fieldname]; cb = b[fieldname]; }
            var result = (ca < cb) ? -1 : (ca > cb) ? 1 : 0;
            return result * sortOrder;
        };
    };

    var sort_shuffle = function (a, b) {  
        return 0.5 - Math.random();
    };

    var construct_options = function(defaultlabel, valuefield, labelfield) {
        var h = [], seenvalues = {};
        h.push('<option value="">' + translate(defaultlabel) + '</option>');
        adoptables.sort(sort_single(labelfield));
        adoptables.forEach(function(item, index, arr) {
            if (!seenvalues.hasOwnProperty(item[valuefield])) {
                h.push('<option value="' + item[valuefield] + '">' + translate(item[labelfield]) + '</option>');
                seenvalues[item[valuefield]] = 1;
            }
        });
        return h.join("");
    };

    var list_options = function(l) {
        var h = [];
        l.forEach(function(item, index, arr) {
            h.push('<option value="' + item[0] + '">' + translate(item[1]) + '</option>');
        });
        return h.join("");
    };

    var spanwrap = function(cls, content) {
        return '<span class="asm3-adoptable-tag asm3-adoptable-tag-' + cls + '">' + content + '</span>';
    };

    var filter_template = [
        '<div id="asm3-adoptable-filters" class="asm3-filters" style="display: block; text-align: center; padding: 5px">',
            '<select id="asm3-select-species">{speciesoptions}</select> ',
            '<select id="asm3-select-breed">{breedoptions}</select> ',
            '<select id="asm3-select-agegroup">{ageoptions}</select> ',
            '<select id="asm3-select-size">{sizeoptions}</select> ',
            '<select id="asm3-select-sex">{sexoptions}</select>',
            '<select id="asm3-select-goodwith">{goodwithoptions}</select>',
            '<select id="asm3-select-where">{whereoptions}</select>',
        '</div>',
        '<div id="asm3-adoptable-list" class="asm3-adoptable-list"></div>'
    ].join("");

    var overlay_template = [
        '<div id="asm3-adoptable-iframe-overlay" style="z-index: 9999; display: none; overflow: hidden; position: {iframe_position}; left: 0; top: 0; width: 100%; height: {iframe_height}; background-color: {iframe_bgcolor}">',
            '<p style="text-align: right;">',
                '<a id="asm3-adoptable-iframe-close" href="#">&times; ' + translate("CLOSE") + '</a>&nbsp;&nbsp;',
            '</p>',
            '<iframe id="asm3-adoptable-iframe" scrolling="no" style="width: 100%; height: 100%;"></iframe>',
        '</div>'
    ].join("");

    var thumbnail_template = [
        '<div class="asm3-adoptable-item" style="display: inline-block; text-align: center; padding: 5px">',
            '<a target="_blank" ',
                'class="asm3-adoptable-link" ',
                'href="{baseurl}/service?account={account}&method=animal_view&animalid={animalid}&template={style}">',
                '<div class="{isreservedclass}">',
                    '<img class="asm3-adoptable-thumbnail" ',
                        'alt="{animalname}" ',
                        'src="{baseurl}/service?account={account}&method={thumbnail_method}&animalid={animalid}&d={mediadate}" />',
                    '<span></span>',
                '</div>',
                '<div class="asm3-adoptable-name">{animalname}</div>',
            '</a>',
            '<div class="asm3-adoptable-tagline">' + filters_tokens.join(" ") + '</div>',
            '{extra}',
        '</div>'
    ].join("");

    var render_adoptables = function() {

        var hostdiv = document.getElementById("asm3-adoptable-list"), 
            h = [],
            c = 0,
            selspecies = document.getElementById("asm3-select-species").value,
            selbreed = document.getElementById("asm3-select-breed").value,
            selagegroup = document.getElementById("asm3-select-agegroup").value,
            selsize = document.getElementById("asm3-select-size").value,
            selsex = document.getElementById("asm3-select-sex").value;
            selgoodwith = document.getElementById("asm3-select-goodwith").value;
            selwhere = document.getElementById("asm3-select-where").value;

        adoptables.forEach(function(item, index, arr) {

            if (selspecies && item.SPECIESID != selspecies) { return; }
            if (selbreed && item.BREEDNAME != decode(selbreed)) { return; }
            if (selagegroup && decode(item.AGEGROUP) != decode(selagegroup)) { return; }
            if (selsize && item.SIZE != selsize) { return; }
            if (selsex && item.SEX != selsex) {return; }
            if (selgoodwith && selgoodwith == 1 && item.ISGOODWITHDOGS != 0) { return; }
            if (selgoodwith && selgoodwith == 2 && item.ISGOODWITHCATS != 0) { return; }
            if (selgoodwith && selgoodwith == 3 && item.ISGOODWITHCHILDREN != 0) { return; }
            if (selwhere && selwhere == 1 && item.ARCHIVED != 0) { return; }
            if (selwhere && selwhere == 2 && item.ACTIVEMOVEMENTTYPE != 2) { return; }
            if (selwhere && selwhere == 3 && item.ISCOURTESY != 1) { return; }

            if (typeof asm3_adoptable_filter !== 'undefined') {
                if (!asm3_adoptable_filter(item, index, arr)) { return; }
            }

            var extra = "";
            if (typeof asm3_adoptable_extra !== 'undefined') {
                extra = asm3_adoptable_extra(item);
            }

            c = c + 1;
            if (limit > 0 && c > limit) { return; }
            
            h.push(substitute(thumbnail_template, {
                account: account,
                baseurl: baseurl,
                age: item.ANIMALAGE,
                animalid: item.ID,
                animalname: translate(item.ANIMALNAME),
                agegroup: spanwrap("agegroup", translate(item.AGEGROUP)),
                breed: spanwrap("breed", translate(item.BREEDNAME)),
                extra: extra,
                goodwith: "",
                isreservedclass: (item.HASACTIVERESERVE == 1 ? "asm3-adoptable-reserved" : ""),
                mediadate: item.WEBSITEMEDIADATE,
                sex: spanwrap("sex", translate(item.SEXNAME)),
                size: spanwrap("size", translate(item.SIZENAME)),
                species: spanwrap("species", translate(item.SPECIESNAME)),
                style: style,
                thumbnail_method: (fullsize_images ? "animal_image" : "animal_thumbnail"),
                where: ""
            }));

        });

        if (!h.length) {
            h.push('<p class="asm3-adoptable-no-results">' + translate("No results") + '</p>');
        }

        hostdiv.innerHTML = h.join("\n");
    };

    var render_iframe = function() {
        var overlay = document.createElement('div');
        overlay.innerHTML = substitute(overlay_template, { "iframe_position": iframe_position, "iframe_height": iframe_height, "iframe_bgcolor": iframe_bgcolor });
        document.body.appendChild(overlay);
        document.getElementById("asm3-adoptable-iframe-close").addEventListener("click", function(e) {
            if (iframe_back) { window.history.back(); }
            document.getElementById("asm3-adoptable-iframe").src = "about:blank";
            document.getElementById("asm3-adoptable-iframe-overlay").style.display = "none";
            e.preventDefault();
        });
        var i, 
            links = document.getElementsByClassName("asm3-adoptable-link"),
            link_handler = function(e) {
                document.getElementById("asm3-adoptable-iframe").src = this.href;
                document.getElementById("asm3-adoptable-iframe-overlay").style.display = "block";
                if (!iframe_fixed) { window.scrollTo(0, 0); }
                if (iframe_back) { window.history.pushState("close", "", ""); }
                e.preventDefault();
            },
            popstate_handler = function(e) {
                if (e.state != "close") { return; }
                document.getElementById("asm3-adoptable-iframe").src = "about:blank";
                document.getElementById("asm3-adoptable-iframe-overlay").style.display = "none";
            };
        for (i = 0; i < links.length; i++) {
            links[i].addEventListener("click", link_handler);
        }
        if (iframe_back) { 
            window.addEventListener("popstate", popstate_handler);
        }
    };

    var render = function() {

        var hostdiv = document.getElementById("asm3-adoptables");
        if (!hostdiv) { alert("#asm3-adoptables not present"); return; }

        hostdiv.innerHTML = substitute(filter_template, {
            speciesoptions: construct_options("(any species)", "SPECIESID", "SPECIESNAME"),
            breedoptions: construct_options("(any breed)", "BREEDNAME", "BREEDNAME"),
            ageoptions: construct_options("(any age)", "AGEGROUP", "AGEGROUP"),
            sizeoptions: construct_options("(any size)", "SIZE", "SIZENAME"),
            sexoptions: construct_options("(any sex)", "SEX", "SEXNAME"),
            goodwithoptions: list_options([ ["0", "(good with)"], ["1", "Good with dogs"], ["2", "Good with cats"], ["3", "Good with children"] ]),
            whereoptions: list_options([ ["0", "(anywhere)"], ["1", "On shelter"], ["2", "Fostered"], ["3", "Courtesy listing"] ])
        });

        if (sort_order == "SHUFFLE") {
            adoptables.sort(sort_shuffle);
        }
        else {
            adoptables.sort(sort_single(sort_order));
        }
        render_adoptables();

        document.getElementById("asm3-select-species").addEventListener("change", render_adoptables);
        document.getElementById("asm3-select-breed").addEventListener("change", render_adoptables);
        document.getElementById("asm3-select-agegroup").addEventListener("change", render_adoptables);
        document.getElementById("asm3-select-size").addEventListener("change", render_adoptables);
        document.getElementById("asm3-select-sex").addEventListener("change", render_adoptables);
        document.getElementById("asm3-select-goodwith").addEventListener("change", render_adoptables);
        document.getElementById("asm3-select-where").addEventListener("change", render_adoptables);

        all_filters.split(" ").forEach(function(item, index, arr) {
            if (active_filters.indexOf(item) == -1) {
                document.getElementById("asm3-select-" + item).style.display = "none";
            }
        });

        if (use_iframe) { render_iframe(); }
    };

    var onReady = function(event) {
        document.removeEventListener( "DOMContentLoaded", onReady, false );
        window.removeEventListener( "load", onReady );
        render();
    };

    if (document.addEventListener) {
        document.addEventListener("DOMContentLoaded", onReady, false);
        window.addEventListener("load", onReady);
    }

}());
