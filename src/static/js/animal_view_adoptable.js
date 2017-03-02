/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global alert */

var adoptables = "{TOKEN_ADOPTABLES}";
var account = "{TOKEN_ACCOUNT}";
var baseurl = "{TOKEN_BASE_URL}";

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
        '<span class="asm3-adoptable-tagline">{sex} {breed} {species}</span><br/>',
        '<span class="asm3-adoptable-age">{age}</span>',
    '</div>'
].join("");

function substitute(str, sub) {
    /*jslint regexp: true */
    return str.replace(/\{(.+?)\}/g, function($0, $1) {
        return sub.hasOwnProperty($1) ? sub[$1] : $0;
    });
}

function inject_adoptables() {

    var hostdiv = document.getElementById("asm3-adoptables"), h = [], s = "";
    if (!hostdiv) { alert("#asm3-adoptables not present"); return; }

    adoptables.forEach(function(item, index, arr) {
        h.push(substitute(thumbnail_template, {
            account: account,
            baseurl: baseurl,
            age: item.ANIMALAGE,
            animalid: item.ID,
            animalname: item.ANIMALNAME,
            breed: item.BREEDNAME,
            sex: item.SEXNAME,
            species: item.SPECIESNAME
        }));
    });

    hostdiv.innerHTML = h.join("\n");

}

function onReady( event ) {
    document.removeEventListener( "DOMContentLoaded", onReady, false );
    window.removeEventListener( "load", onReady );
    inject_adoptables();
}

if (document.addEventListener) {
    document.addEventListener("DOMContentLoaded", onReady, false);
    // Use window.onload as fallback
    window.addEventListener("load", onReady);
}

