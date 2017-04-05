/*jslint browser: true, forin: true, eqeq: true, white: true, plusplus: true, sloppy: true, vars: true, nomen: true */
/*global alert, asm3_adoptable_filters: true, asm3_adoptable_iframe, asm3_adoptable_translations, asm3_adoptable_filter */

(function() {

    var adoptables = "{TOKEN_ADOPTABLES}";
    var account = "{TOKEN_ACCOUNT}";
    var baseurl = "{TOKEN_BASE_URL}";
    var all_filters = "agegroup sex breed size species";

    if (typeof asm3_adoptable_filters === 'undefined') {
        asm3_adoptable_filters = "agegroup sex species";
    }
    var filters_tokens = [];
    asm3_adoptable_filters.split(" ").forEach(function(item, index, arr) {
        filters_tokens.push("{" + item + "}");
    });
    var use_iframe = false;
    if (typeof asm3_adoptable_iframe !== 'undefined') {
        use_iframe = asm3_adoptable_iframe;
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
        var sortOrder = 1;
        if (fieldname[0] === "-") {
            sortOrder = -1;
            fieldname = fieldname.substr(1);
        }
        return function (a,b) {
            var ca = String(a[fieldname]).toUpperCase();
            var cb = String(b[fieldname]).toUpperCase();
            var result = (ca < cb) ? -1 : (ca > cb) ? 1 : 0;
            return result * sortOrder;
        };
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

    var filter_template = [
        '<div id="asm3-adoptable-iframe-overlay" style="z-index: 9999; display: none; position: fixed; left: 0; top: 0; width: 100%; height: 100%; background-color: #fff">',
        '<p style="text-align: right"><a id="asm3-adoptable-iframe-close" style="font-size: 200%;" href="#">&times; ' + translate("CLOSE") + '</a>&nbsp;&nbsp;</p>',
        '<iframe id="asm3-adoptable-iframe" style="position: fixed; left: 5%; top: 5%; width: 90%; height: 90%; box-shadow: 3px 3px 5px #888;"></iframe>',
        '</div>',
        '<div id="asm3-adoptable-filters" class="asm3-filters" style="display: block; text-align: center; padding: 5px">',
            '<select id="asm3-select-species">{speciesoptions}</select> ',
            '<select id="asm3-select-breed">{breedoptions}</select> ',
            '<select id="asm3-select-agegroup">{ageoptions}</select> ',
            '<select id="asm3-select-size">{sizeoptions}</select> ',
            '<select id="asm3-select-sex">{sexoptions}</select>',
        '</div>',
        '<div id="asm3-adoptable-list" class="asm3-adoptable-list" />'
    ].join("");

    var thumbnail_template = [
        '<div class="asm3-adoptable-item" style="display: inline-block; text-align: center; padding: 5px">',
            '<a target="_blank" ',
                'class="asm3-adoptable-link" ',
                'href="{baseurl}/service?account={account}&method=animal_view&animalid={animalid}">',
            '<img class="asm3-adoptable-thumbnail" ',
                'src="{baseurl}/service?account={account}&method=animal_thumbnail&animalid={animalid}" />',
            '<br />',
            '<span class="asm3-adoptable-name">{animalname}</span>',
            '</a>',
            '<br/>',
            '<span class="asm3-adoptable-tagline">' + filters_tokens.join(" ") + '</span><br/>',
        '</div>'
    ].join("");

    var render_adoptables = function() {

        var hostdiv = document.getElementById("asm3-adoptable-list"), 
            h = [],
            selspecies = document.getElementById("asm3-select-species").value,
            selbreed = document.getElementById("asm3-select-breed").value,
            selagegroup = document.getElementById("asm3-select-agegroup").value,
            selsize = document.getElementById("asm3-select-size").value,
            selsex = document.getElementById("asm3-select-sex").value;

        adoptables.forEach(function(item, index, arr) {

            if (selspecies && item.SPECIESID != selspecies) { return; }
            if (selbreed && item.BREEDNAME != decode(selbreed)) { return; }
            if (selagegroup && decode(item.AGEGROUP) != decode(selagegroup)) { return; }
            if (selsize && item.SIZE != selsize) { return; }
            if (selsex && item.SEX != selsex) {return; }

            if (typeof asm3_adoptable_filter !== 'undefined') {
                if (!asm3_adoptable_filter(item)) { return; }
            }
            
            h.push(substitute(thumbnail_template, {
                account: account,
                baseurl: baseurl,
                age: item.ANIMALAGE,
                agegroup: translate(item.AGEGROUP),
                animalid: item.ID,
                animalname: translate(item.ANIMALNAME),
                breed: translate(item.BREEDNAME),
                sex: translate(item.SEXNAME),
                size: translate(item.SIZENAME),
                species: translate(item.SPECIESNAME)
            }));

        });

        hostdiv.innerHTML = h.join("\n");

        if (use_iframe) {
            var i, 
                links = document.getElementsByClassName("asm3-adoptable-link"),
                handler = function(e) {
                    document.getElementById("asm3-adoptable-iframe").src = this.href;
                    document.getElementById("asm3-adoptable-iframe-overlay").style.display = "block";
                    e.preventDefault();
                };
            for (i = 0; i < links.length; i++) {
                links[i].addEventListener("click", handler);
            }
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
            sexoptions: construct_options("(any gender)", "SEX", "SEXNAME")
        });

        adoptables.sort(sort_single("ANIMALNAME"));
        render_adoptables();

        document.getElementById("asm3-select-species").addEventListener("change", render_adoptables);
        document.getElementById("asm3-select-breed").addEventListener("change", render_adoptables);
        document.getElementById("asm3-select-agegroup").addEventListener("change", render_adoptables);
        document.getElementById("asm3-select-size").addEventListener("change", render_adoptables);
        document.getElementById("asm3-select-sex").addEventListener("change", render_adoptables);

        all_filters.split(" ").forEach(function(item, index, arr) {
            if (asm3_adoptable_filters.indexOf(item) == -1) {
                document.getElementById("asm3-select-" + item).style.display = "none";
            }
        });

        if (use_iframe) {
            document.getElementById("asm3-adoptable-iframe-close").addEventListener("click", function(e) {
                document.getElementById("asm3-adoptable-iframe").src = "about:blank";
                document.getElementById("asm3-adoptable-iframe-overlay").style.display = "none";
                e.preventDefault();
            });
        }
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
