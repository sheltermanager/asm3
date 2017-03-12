/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global alert, asm3_adoptable_translations */

(function() {

    var adoptables = "{TOKEN_ADOPTABLES}";
    var account = "{TOKEN_ACCOUNT}";
    var baseurl = "{TOKEN_BASE_URL}";

    var filter_template = [
        '<div class="asm3-filters" style="display: block; text-align: center; padding: 5px">',
            '<select id="asm3-select-species">{speciesoptions}</select> ',
            '<select id="asm3-select-agegroup">{ageoptions}</select> ',
            '<select id="asm3-select-gender">{genderoptions}</select>',
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
            '<span class="asm3-adoptable-tagline">{sex} {species}</span><br/>',
            '<span class="asm3-adoptable-age">{agegroup}</span>',
        '</div>'
    ].join("");

    var decode_div = document.createElement('div');
    var decode = function(s) {
        decode_div.innerHTML = s;
        s = decode_div.textContent;
        decode_div.textContent = '';
        return s;
    };

    var translate = function(s) {
        if (typeof asm3_adoptable_translations !== 'undefined') {
            if (asm3_adoptable_translations.hasOwnProperty(s)) {
                return asm3_adoptable_translations[s];
            }
        }
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

    var render_adoptables = function() {

        var hostdiv = document.getElementById("asm3-adoptable-list"), 
            h = [],
            selspecies = document.getElementById("asm3-select-species").value,
            selagegroup = document.getElementById("asm3-select-agegroup").value,
            selgender = document.getElementById("asm3-select-gender").value;

        adoptables.forEach(function(item, index, arr) {

            if (selspecies && item.SPECIESID != selspecies) { return; }
            if (selagegroup && decode(item.AGEGROUP) != decode(selagegroup)) { return; }
            if (selgender && item.SEX != selgender) {return; }
            
            h.push(substitute(thumbnail_template, {
                account: account,
                baseurl: baseurl,
                age: item.ANIMALAGE,
                agegroup: translate(item.AGEGROUP),
                animalid: item.ID,
                animalname: translate(item.ANIMALNAME),
                breed: translate(item.BREEDNAME),
                sex: translate(item.SEXNAME),
                species: translate(item.SPECIESNAME)
            }));

        });

        hostdiv.innerHTML = h.join("\n");
    };

    var render = function() {

        var hostdiv = document.getElementById("asm3-adoptables");
        if (!hostdiv) { alert("#asm3-adoptables not present"); return; }

        hostdiv.innerHTML = substitute(filter_template, {
            speciesoptions: construct_options("(any species)", "SPECIESID", "SPECIESNAME"),
            ageoptions: construct_options("(any age)", "AGEGROUP", "AGEGROUP"),
            genderoptions: construct_options("(any gender)", "SEX", "SEXNAME")
        });

        adoptables.sort(sort_single("ANIMALNAME"));
        render_adoptables();

        document.getElementById("asm3-select-species").addEventListener("change", render_adoptables);
        document.getElementById("asm3-select-agegroup").addEventListener("change", render_adoptables);
        document.getElementById("asm3-select-gender").addEventListener("change", render_adoptables);

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
