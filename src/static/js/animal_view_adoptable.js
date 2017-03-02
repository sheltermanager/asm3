/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global alert */

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
        h.push('<option value="">' + defaultlabel + '</option>');
        adoptables.sort(sort_single(labelfield));
        adoptables.forEach(function(item, index, arr) {
            if (!seenvalues.hasOwnProperty(item[valuefield])) {
                h.push('<option value="' + item[valuefield] + '">' + item[labelfield] + '</option>');
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
            if (selagegroup && item.AGEGROUP != selagegroup) { return; }
            if (selgender && item.SEX != selgender) {return; }
            
            h.push(substitute(thumbnail_template, {
                account: account,
                baseurl: baseurl,
                age: item.ANIMALAGE,
                agegroup: item.AGEGROUP,
                animalid: item.ID,
                animalname: item.ANIMALNAME,
                breed: item.BREEDNAME,
                sex: item.SEXNAME,
                species: item.SPECIESNAME
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
