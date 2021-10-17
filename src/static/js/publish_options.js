/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const publish_options = {

        render_tabs: function() {
            return [
                '<ul>',
                '<li><a href="#tab-animalselection">' + _("Animal Selection") + '</a></li>',
                '<li><a href="#tab-allpublishers">' + _("All Publishers") + '</a></li>',
                '<li class="hashtmlftp"><a href="#tab-htmlftp">' + _("HTML/FTP Publisher") + '</a></li>',
                '<li class="localeus localeca localemx"><a href="#tab-adoptapet">AdoptAPet</a></li>',
                '<li><a href="#tab-helpinglostpets">HelpingLostPets</a></li>',
                '<li class="english hasmaddiesfund"><a href="#tab-maddiesfund">Maddie\'s Fund</a></li>',
                '<li class="english haspetcademy"><a href="#tab-petcademy">Petcademy</a></li>',
                '<li class="localeus localeca localemx"><a href="#tab-petfinder">PetFinder</a></li>',
                '<li class="localegb haspetslocated"><a href="#tab-petslocated">PetsLocated</a></li>',
                '<li class="localeau haspetrescue"><a href="#tab-petrescue">PetRescue</a></li>', 
                '<li class="localeau hassavourlife"><a href="#tab-savourlife">SavourLife</a></li>', 
                '<li class="localeus"><a href="#tab-rescuegroups">RescueGroups</a></li>',
                '<li class="localegb"><a href="#tab-pettrac">AVID UK Microchips</a></li>',
                '<li class="localegb"><a href="#tab-anibase">Identibase UK Microchips</a></li>',
                '<li class="localeus hasakcreunite"><a href="#tab-akcreunite">AKC Reunite Microchips</a></li>',
                '<li class="localeus hasfoundanimals"><a href="#tab-foundanimals">FoundAnimals Microchips</a></li>',
                '<li class="localeus hashomeagain"><a href="#tab-homeagain">HomeAgain Microchips</a></li>',
                '<li class="localeus localeca localemx haspetlink"><a href="#tab-petlink">PetLink Microchips</a></li>',
                '<li class="localeus hassmarttag"><a href="#tab-smarttag">SmartTag Tags/Microchips</a></li>',
                '<li class="localeus hasvetenvoy"><a href="#tab-vetenvoy">VetEnvoy Microchips</a></li>',
                '</ul>'
            ].join("\n");
        },

        render_animalselection: function() {
            return [
                '<div id="tab-animalselection">',
                '<table>',
                '<tr>',
                '<td><label for="caseanimals">' + _("Include cruelty case animals") + '</label></td>',
                '<td><select id="caseanimals" class="asm-selectbox pbool preset" data="includecase">',
                '<option value="0">' + _("No") + '</option>',
                '<option value="1">' + _("Yes") + '</option>',
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="nonneutered">' + _("Include unaltered animals") + '</label></td>',
                '<td><select id="nonneutered" class="asm-selectbox pbool preset" data="includenonneutered">',
                '<option value="0">' + _("No") + '</option>',
                '<option value="1">' + _("Yes") + '</option>',
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="reservedanimals">' + _("Include reserved animals") + '</label></td>',
                '<td><select id="reservedanimals" class="asm-selectbox pbool preset" data="includereserved">',
                '<option value="0">' + _("No") + '</option>',
                '<option value="1">' + _("Yes") + '</option>',
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="retaileranimals">' + _("Include retailer animals") + '</label></td>',
                '<td><select id="retaileranimals" class="asm-selectbox pbool preset" data="includeretailer">',
                '<option value="0">' + _("No") + '</option>',
                '<option value="1">' + _("Yes") + '</option>',
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="fosteredanimals">' + _("Include fostered animals") + '</label></td>',
                '<td><select id="fosteredanimals" class="asm-selectbox pbool preset" data="includefosters">',
                '<option value="0">' + _("No") + '</option>',
                '<option value="1">' + _("Yes") + '</option>',
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="heldanimals">' + _("Include held animals") + '</label></td>',
                '<td><select id="heldanimals" class="asm-selectbox pbool preset" data="includehold">',
                '<option value="0">' + _("No") + '</option>',
                '<option value="1">' + _("Yes") + '</option>',
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="quarantinedanimals">' + _("Include quarantined animals") + '</label></td>',
                '<td><select id="quarantinedanimals" class="asm-selectbox pbool preset" data="includequarantine">',
                '<option value="0">' + _("No") + '</option>',
                '<option value="1">' + _("Yes") + '</option>',
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="trialanimals">' + _("Include animals on trial adoption") + '</label></td>',
                '<td><select id="trialanimals" class="asm-selectbox pbool preset" data="includetrial">',
                '<option value="0">' + _("No") + '</option>',
                '<option value="1">' + _("Yes") + '</option>',
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="nodescription">' + _("Include animals who don't have a description") + '</label></td>',
                '<td><select id="nodescription" class="asm-selectbox pbool preset" data="includewithoutdescription">',
                '<option value="0">' + _("No") + '</option>',
                '<option value="1">' + _("Yes") + '</option>',
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="noimage">' + _("Include animals who don't have a picture") + '</label></td>',
                '<td><select id="noimage" class="asm-selectbox pbool preset" data="includewithoutimage">',
                '<option value="0">' + _("No") + '</option>',
                '<option value="1">' + _("Yes") + '</option>',
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="bonded">' + _("Merge bonded animals into a single record") + '</label></td>',
                '<td><select id="bonded" class="asm-selectbox pbool preset" data="bondedassingle">',
                '<option value="0">' + _("No") + '</option>',
                '<option value="1">' + _("Yes") + '</option>',
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="excludeunder">' + _("Exclude animals who are aged under") + '</label></td>',
                '<td><input id="excludeunder" class="asm-numberbox asm-textbox asm-halftextbox preset" data="excludeunder" data-max="52" data-min="1" />',
                _("weeks") + '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="locations">' + _("Include animals in the following locations"),
                '<span id="callout-locations" class="asm-callout">',
                _("If you don't select any locations, publishers will include animals in all locations."),
                '</span>',
                '</label></td>',
                '<td><select id="locations" class="asm-bsmselect preset" multiple="multiple" data="includelocations">',
                html.list_to_options(controller.locations, "ID", "LOCATIONNAME"),
                '</select></td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_allpublishers: function() {
            return [
                '<div id="tab-allpublishers">',
                '<table>',
                '<tr>',
                '<td><label for="regmic">' + _("Register microchips after") + '</label></td>',
                '<td><select id="regmic" class="asm-bsmselect cfg" multiple="multiple" data="MicrochipRegisterMovements">',
                '<option value="0">' + _("Intake") + '</option>',
                '<option value="1">' + _("Adoption") + '</option>',
                '<option value="2">' + _("Foster") + '</option>',
                '<option value="3">' + _("Transfer") + '</option>',
                '<option value="5">' + _("Reclaim") + '</option>',
                '<option value="11">' + _("Trial Adoption") + '</option>',
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="regfrom">' + _("Register microchips from") + '</label>',
                '<span id="callout-regfrom" class="asm-callout">' + _("Only register microchips where the animal moved after this date") + '</span>',
                '</td>',
                '<td><input id="regfrom" class="asm-textbox asm-datebox cfg" data="MicrochipRegisterFrom" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="updatefreq">' + _("Update adoption websites every") + '</label></td>',
                '<td><select id="updatefreq" class="asm-selectbox cfg" data="PublisherSub24Frequency">',
                '<option value="2">' + _("{0} hours").replace("{0}", "2") + '</option>',
                '<option value="4">' + _("{0} hours").replace("{0}", "4") + '</option>',
                '<option value="6">' + _("{0} hours").replace("{0}", "6") + '</option>',
                '<option value="8">' + _("{0} hours").replace("{0}", "8") + '</option>',
                '<option value="12">' + _("{0} hours").replace("{0}", "12") + '</option>',
                '<option value="0">' + _("{0} hours").replace("{0}", "24") + '</option>',
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="forcereupload">' + _("Reupload animal images every time") + '</label></td>',
                '<td><select id="forcereupload" class="asm-selectbox pbool preset" data="forcereupload">',
                '<option value="0">' + _("No") + '</option>',
                '<option value="1">' + _("Yes") + '</option>',
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="uploadall">' + _("Upload all available images for animals") + '</label></td>',
                '<td><select id="uploadall" class="asm-selectbox pbool preset" data="uploadall">',
                '<option value="0">' + _("No") + '</option>',
                '<option value="1">' + _("Yes") + '</option>',
                '</select></td>',
                '</tr>',
                '',
                '<tr>',
                '<td><label for="order">' + _("Order published animals by") + '</label></td>',
                '<td><select id="order" class="asm-selectbox preset" data="order">',
                '<option value="0">' + _("Entered (oldest first)") + '</option>',
                '<option value="1">' + _("Entered (newest first)") + '</option>',
                '<option value="2">' + _("Animal Name") + '</option>',
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="thumbnailsize">' + _("Thumbnail size") + '</label></td>',
                '<td><select id="thumbnailsize" class="asm-selectbox cfg" data="ThumbnailSize">',
                '<option value="100x100">100px</option>',
                '<option value="150x150">150px</option>',
                '<option value="200x200">200px</option>',
                '<option value="250x250">250px</option>',
                '<option value="300x300">300px</option>',
                '</select>',
                '<tr>',
                '<td><label for="usecomments">' + _("Animal descriptions") + '</label></td>',
                '<td><select id="usecomments" class="asm-selectbox cfg" data="PublisherUseComments">',
                '<option value="Yes">' + _("Use animal description") + '</option>',
                '<option value="No">' + _("Use notes from preferred photo") + '</option>',
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="tppublishersig">' + _("Add this text to all animal descriptions") + '</label></td>',
                '<td><textarea id="tppublishersig" type="text" rows="5" class="asm-textarea cfg" data="TPPublisherSig"',
                'title="' + html.title(_("When publishing to third party services, add this extra text to the bottom of all animal descriptions")) + '"></textarea></td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_pettrac: function() {
            return [
                '<div id="tab-pettrac">',
                html.info('These settings are for registering microchips with new owner information to the AVID PETtrac UK database. <br/>' + 
                    'Find out more at <a href="http://www.pettrac.co.uk">www.pettrac.co.uk</a>'),
                '<p><input id="enabledptuk" type="checkbox" class="asm-checkbox enablecheck" /><label for="enabledptuk">' + _("Enabled") + '</label></p>',
                '<table>',
                '<tr>',
                '<td><label for="avidorgname">Organisation Name</label></td>',
                '<td><input data="AvidOrgName" id="avidorgname" type="text" class="asm-doubletextbox cfg" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="avidorgserial">Serial Number</label></td>',
                '<td><input data="AvidOrgSerial" id="avidorgserial" type="text" class="asm-doubletextbox cfg" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="avidorgpostcode">Postcode</label></td>',
                '<td><input data="AvidOrgPostcode" id="avidorgpostcode" type="text" class="asm-doubletextbox cfg" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="avidorgpassword">Password</label></td>',
                '<td><input data="AvidOrgPassword" id="avidorgpassword" type="text" class="asm-doubletextbox cfg" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="avidrereg">Re-register previously registered microchips</label></td>',
                '<td><select id="avidrereg" data="AvidReRegistration" class="asm-selectbox cfg">',
                '<option value="No">' + _("No") + '</option>',
                '<option value="Yes">' + _("Yes") + '</option>',
                '</select></td>',
                '<tr>',
                '<td><label for="avidauthuser">Authorised user for re-registration</label></td>',
                '<td><select data="AvidAuthUser" id="avidauthuser" class="asm-selectbox cfg">',
                html.list_to_options(controller.users, "USERNAME", "USERNAME"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td></td><td>',
                html.info("An authorised user must be chosen and they must have an electronic signature on file.<br/>" + 
                    "Their details will be used on an authorisation document transmitted to AVID when " +
                    "re-registering previously registered microchips.<br/>Please also make sure the authorised " +
                    "user has a real name on file."),
                '</td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_petlink: function() {
            return [
                '<div id="tab-petlink">',
                html.info('These settings are for uploading new owner information to the PetLink/DataMARS microchip database.<br />' +
                    'Find out more at <a href="http://www.petlink.net/us/">www.petlink.net</a>'),
                '<p><input id="enabledpl" type="checkbox" class="asm-checkbox enablecheck" /><label for="enabledpl">' + _("Enabled") + '</label></p>',
                '<table>',
                '<tr>',
                '<td><label for="plemail">Professional/Vet Account Email</label>',
                '<span id="callout-plemail" class="asm-callout">This is the email address you use to log into the PetLink site as a professional/vet</span>',
                '</td>',
                '<td><input id="plemail" type="text" class="asm-textbox cfg" data="PetLinkEmail" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="plpass">Password</label></td>',
                '<td><input id="plpass" type="text" class="asm-textbox cfg" data="PetLinkPassword" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="plowneremail">Owner Account Email (Optional)</label>',
                '<span id="callout-plowneremail" class="asm-callout">If you are registering animals to the shelter on intake, ',
                'this is the email address of the PetLink owner account to register shelter animals to.</span>',
                '</td>',
                '<td><input id="plowneremail" type="text" class="asm-textbox cfg" data="PetLinkOwnerEmail" /></td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_petslocated: function() {
            return [
                '<div id="tab-petslocated">',
                html.info('Signup at <a href="http://www.petslocated.com">www.petslocated.com</a>'),
                '<p><input id="enabledpcuk" type="checkbox" class="asm-checkbox enablecheck" /><label for="enabledpcuk">' + _("Enabled") + '</label></p>',
                '<table>',
                '<tr>',
                '<td><label for="pcukcustid">petslocated.com customer number</label></td>',
                '<td><input id="pcukcustid" type="text" class="asm-textbox cfg" data="PetsLocatedCustomerID" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="pcukincludeshelter">Include shelter animals</label></td>',
                '<td><select id="pcukincludeshelter" class="asm-selectbox cfg" data="PetsLocatedIncludeShelter">',
                '<option value="No">' + _("No") + '</option>',
                '<option value="Yes">' + _("Yes") + '</option>',
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="pcukanimalflag">Only shelter animals with this flag</label></td>',
                '<td><select id="pcukanimalflag" class="asm-selectbox cfg" data="PetsLocatedAnimalFlag">',
                '<option value=""></option>',
                html.list_to_options(controller.flags, "FLAG", "FLAG"),
                '</select>',
                '</td>',

                '</tr>',

                '</table>',
                '</div>'
            ].join("\n");
        },

        render_htmlftp: function() {
            return [
                '<div id="tab-htmlftp">',
                '<p><input id="enabledhtml" type="checkbox" class="asm-checkbox enablecheck" /><label for="enabledhtml">' + _("Enabled") + '</label></p>',
                '<table>',
                '<tr>',
                '<td>',
                '<table>',
                '<tr>',
                '<td><label for="generatejavascript">' + _("Generate a javascript database for the search page") + '</label></td>',
                '<td><select id="generatejavascript" class="asm-selectbox pbool preset" data="generatejavascriptdb">',
                '<option value="0">' + _("No") + '</option>',
                '<option value="1">' + _("Yes") + '</option>',
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="thumbnails">' + _("Generate image thumbnails as tn_$$IMAGE$$") + '</label></td>',
                '<td><select id="thumbnails" class="asm-selectbox pbool preset" data="thumbnails">',
                '<option value="0">' + _("No") + '</option>',
                '<option value="1">' + _("Yes") + '</option>',
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="scalethumb">' + _("Thumbnail size") + '</label></td>',
                '<td><select id="scalethumb" class="asm-selectbox preset" data="thumbnailsize">',
                '<option value="70x70">70 px</option>',
                '<option value="80x80">80 px</option>',
                '<option value="90x90">90 px</option>',
                '<option value="100x100">100 px</option>',
                '<option value="120x120">120 px</option>',
                '<option value="150x150">150 px</option>',
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="typesplit">' + _("Output a separate page for each animal type") + '</label></td>',
                '<td><select id="typesplit" class="asm-selectbox pbool preset" data="htmlbytype">',
                '<option value="0">' + _("No") + '</option>',
                '<option value="1">' + _("Yes") + '</option>',
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="speciessplit">' + _("Output a separate page for each species") + '</label></td>',
                '<td><select id="speciessplit" class="asm-selectbox pbool preset" data="htmlbyspecies">',
                '<option value="0">' + _("No") + '</option>',
                '<option value="1">' + _("Yes") + '</option>',
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="childadult">' + _("Split species pages with a baby/adult prefix") + '</label></td>',
                '<td><select id="childadult" class="asm-selectbox pbool preset" data="htmlbychildadult">',
                '<option value="0">' + _("No") + '</option>',
                '<option value="1">' + _("Yes") + '</option>',
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="childsplit">' + _("Split baby/adult age at") + '</label></td>',
                '<td><select id="childsplit" class="asm-selectbox preset" data="childadultsplit">',
                '<option value="1">' + _("1 week") + '</option>',
                '<option value="2">' + _("2 weeks") + '</option>',
                '<option value="4">' + _("4 weeks") + '</option>',
                '<option value="8">' + _("8 weeks") + '</option>',
                '<option value="12">' + _("3 months") + '</option>',
                '<option value="26">' + _("6 months") + '</option>',
                '<option value="38">' + _("9 months") + '</option>',
                '<option value="52">' + _("1 year") + '</option>',
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="outputadopted">' + _("Output an adopted animals page") + '</label></td>',
                '<td><select id="outputadopted" class="asm-selectbox pbool preset" data="outputadopted">',
                '<option value="0">' + _("No") + '</option>',
                '<option value="1">' + _("Yes") + '</option>',
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="outputadopteddays">' + _("Show animals adopted") + '</label></td>',
                '<td><select id="outputadopteddays" class="asm-selectbox preset" data="outputadopteddays">',
                '<option value="7">' + _("In the last week") + '</option>',
                '<option value="31">' + _("In the last month") + '</option>',
                '<option value="93">' + _("In the last quarter") + '</option>',
                '<option value="365">' + _("In the last year") + '</option>',
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="outputdeceased">' + _("Output a deceased animals page") + '</label></td>',
                '<td><select id="outputdeceased" class="asm-selectbox pbool preset" data="outputdeceased">',
                '<option value="0">' + _("No") + '</option>',
                '<option value="1">' + _("Yes") + '</option>',
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="outputforms">' + _("Output a page with links to available online forms") + '</label></td>',
                '<td><select id="outputforms" class="asm-selectbox pbool preset" data="outputforms">',
                '<option value="0">' + _("No") + '</option>',
                '<option value="1">' + _("Yes") + '</option>',
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="outputrss">' + _("Output an rss.xml page") + '</label></td>',
                '<td><select id="outputrss" class="asm-selectbox pbool preset" data="outputrss">',
                '<option value="0">' + _("No") + '</option>',
                '<option value="1">' + _("Yes") + '</option>',
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="animalsperpage">' + _("Animals per page") + '</label></td>',
                '<td><select id="animalsperpage" class="asm-selectbox preset" data="animalsperpage">',
                '<option value="5">5</option>',
                '<option value="10" selected="selected">10</option>',
                '<option value="15">15</option>',
                '<option value="20">20</option>',
                '<option value="50">50</option>',
                '<option value="100">100</option>',
                '<option value="999999">Unlimited (one page)</option>',
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="extension">' + _("Page extension") + '</label></td>',
                '<td><select id="extension" class="asm-selectbox preset" data="extension">',
                '<option value="html">html</option>',
                '<option value="xml">xml</option>',
                '<option value="cgi">cgi</option>',
                '<option value="php">php</option>',
                '<option value="py">py</option>',
                '<option value="rb">rb</option>',
                '<option value="jsp">jsp</option>',
                '<option value="asp">asp</option>',
                '<option value="aspx">aspx</option>',
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="template">' + _("Publishing template") + '</label></td>',
                '<td><select id="template" class="asm-selectbox preset" data="style">',
                html.list_to_options(controller.styles),
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="scale">' + _("Scale published animal images to") + '</label></td>',
                '<td><select id="scale" class="asm-selectbox preset" data="scaleimages">',
                '<option value="">' + _("Don't scale") + '</option>',
                '<option value="300x300">300 px</option>',
                '<option value="320x320">320 px</option>',
                '<option value="400x400">400 px</option>',
                '<option value="500x500">500 px</option>',
                '<option value="600x600">600 px</option>',
                '<option value="800x800">800 px</option>',
                '<option value="1024x1024">1024 px</option>',
                '</select></td>',
                '</tr>',
                '<tr id="publishdirrow">',
                '<td><label for="publishdir">' + _("Publish to folder") + '</label></td>',
                '<td><input id="publishdir" type="text" class="asm-textbox preset" data="publishdirectory" /></td>',
                '</tr>',
                '</table>',
                '</td>',
                '<td>',
                '<table id="ftpuploadtable">',
                '<tr>',
                '<td><label for="uploaddirectly">' + _("Enable FTP uploading") + '</label></td>',
                '<td><select id="uploaddirectly" class="asm-selectbox pbool preset" data="uploaddirectly">',
                '<option value="0">' + _("No") + '</option>',
                '<option value="1">' + _("Yes") + '</option>',
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="ftphost">' + _("FTP hostname") + '</label></td>',
                '<td><input id="ftphost" type="text" class="asm-textbox cfg" data="FTPURL" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="ftpuser">' + _("FTP username") + '</label></td>',
                '<td><input id="ftpuser" type="text" class="asm-textbox cfg" data="FTPUser" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="ftppass">' + _("FTP password") + '</label></td>',
                '<td><input id="ftppass" type="text" class="asm-textbox cfg" data="FTPPassword" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="ftproot">' + _("after connecting, chdir to") + '</label></td>',
                '<td><input id="ftproot" type="text" class="asm-textbox cfg" data="FTPRootDirectory" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="clearexisting">' + _("Remove previously published files before uploading") + '</label></td>',
                '<td><select id="clearexisting" class="asm-selectbox pbool preset" data="clearexisting">',
                '<option value="0">' + _("No") + '</option>',
                '<option value="1">' + _("Yes") + '</option>',
                '</select></td>',
                '</tr>',
                '</table>',
                '</td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_petfinder: function() {
            return [
                '<div id="tab-petfinder">',
                html.info('Signup at <a href="http://www.petfinder.com/register/">www.petfinder.com/register/</a>'),
                '<p><input id="enabledpf" type="checkbox" class="asm-checkbox enablecheck" /><label for="enabledpf">' + _("Enabled") + '</label></p>',
                '<table>',
                '<tr>',
                '<td><label for="pfftpuser">PetFinder shelter ID</label></td>',
                '<td><input id="pfftpuser" type="text" class="asm-textbox cfg" data="PetFinderFTPUser" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="pfftppass">PetFinder FTP password</label></td>',
                '<td><input id="pfftppass" type="text" class="asm-textbox cfg" data="PetFinderFTPPassword" /></td>',
                '</tr>',
                '</table>',
                html.info('Make sure to notify the PetFinder helpdesk that you are using ASM to upload animals so that they can give you your FTP password.<br/>' +
                    'It is <b>not</b> the same as your password for the members area.'),
                '</div>'
            ].join("\n");
        },

        render_petrescue: function() {
            return [
                '<div id="tab-petrescue">',
                html.info('Signup at <a href="http://petrescue.com.au">petrescue.com.au</a>'),
                '<p><input id="enabledpr" type="checkbox" class="asm-checkbox enablecheck" /><label for="enabledpr">' + _("Enabled") + '</label></p>',
                '<table>',
                '<tr>',
                '<td><label for="prtoken">PetRescue Token</label></td>',
                '<td><input id="prtoken" type="text" class="asm-doubletextbox cfg" data="PetRescueToken" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="prdesex">Send all animals as desexed</label>',
                '<span id="callout-prdesex" class="asm-callout">',
                'PetRescue will not accept listings for non-desexed animals. Setting this to "Yes" will send all animals as if they are desexed.',
                '</span>',
                '</td>',
                '<td><select id="prdesex" class="asm-selectbox cfg" data="PetRescueAllDesexed">',
                '<option>No</option><option>Yes</option></select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="pradoptablein">Adoptable in states</label>',
                '<span id="callout-printerstate" class="asm-callout">',
                'Choose the states your animals will be adoptable in. The state the animal is currently located in ',
                'will be implicitly included.',
                '</span>',
                '</td>',
                '<td><select id="pradoptablein" multiple="multiple" class="asm-bsmselect cfg" data="PetRescueAdoptableIn">',
                '<option value="ACT">Australian Capital Territory</option>',
                '<option value="NSW">New South Wales</option>',
                '<option value="NT">Northern Territory</option>',
                '<option value="QLD">Queensland</option>',
                '<option value="SA">South Australia</option>',
                '<option value="TAS">Tasmania</option>',
                '<option value="VIC">Victoria</option>',
                '<option value="WA">Western Australia</option>',
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="premail">Contact email</label>',
                '<span id="callout-premail" class="asm-callout">',
                'This is the contact email for PetRescue listings. If you do not set it, the option from Settings &#8594; Options &#8594; Email is used.',
                '</span>',
                '</td>',
                '<td><input id="premail" type="text" class="asm-textbox cfg" data="PetRescueEmail" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="prphone">Contact phone</label>',
                '<span id="callout-prphone" class="asm-callout">',
                'This controls the phone number included as a secondary contact with your listings',
                '</span></td>',
                '<td><select id="prphone" class="asm-selectbox cfg" data="PetRescuePhoneType">',
                '<option value="org">Use organisation number</option>',
                '<option value="spec">Specify a number &#8594;</option>',
                '<option value="none">Do not send a number</option>',
                '</select> ',
                '<input type="text" class="asm-textbox cfg" title="The phone number to use" data="PetRescuePhoneNumber" />',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_savourlife: function() {
            return [
                '<div id="tab-savourlife">',
                html.info('Signup at <a href="http://savourlife.com.au">savour-life.com.au</a>'),
                '<p><input id="enabledsl" type="checkbox" class="asm-checkbox enablecheck" /><label for="enabledsl">' + _("Enabled") + '</label></p>',
                '<table>',
                '<tr>',
                '<td><label for="slusername">Username</label></td>',
                '<td><input id="slusername" type="text" class="asm-textbox cfg" data="SavourLifeUsername" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="slpassword">Password</label></td>',
                '<td><input id="slpassword" type="text" class="asm-textbox cfg" data="SavourLifePassword" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="slinterstate">Mark as interstate</label>',
                '<span id="callout-slinterstate" class="asm-callout">',
                'Set to yes if you will fly adoptable animals to other states',
                '</span>',
                '</td>',
                '<td><select id="slinterstate" class="asm-selectbox cfg" data="SavourLifeInterstate">',
                '<option>No</option><option>Yes</option></select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="slradius">Distance restriction</label>',
                '</td>',
                '<td><select id="slradius" class="asm-selectbox cfg" data="SavourLifeRadius">',
                '<option value="0">No restriction</option>',
                '<option value="20">20 km</option>',
                '<option value="40">40 km</option>',
                '<option value="60">60 km</option>',
                '<option value="100">100 km</option>',
                '<option value="200">200 km</option>',
                '<option value="500">500 km</option>',
                '</select></td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_rescuegroups: function() {
            return [
                '<div id="tab-rescuegroups">',
                html.info('RescueGroups offer a service called Pet Adoption Portal that allows you to upload adoptable animals ' +
                    'to them for republishing on to many other sites. Find out more at ' +
                    '<a href="http://www.rescuegroups.org/services/pet-adoption-portal/">www.rescuegroups.org</a>'),
                '<p><input id="enabledrg" type="checkbox" class="asm-checkbox enablecheck" /><label for="enabledrg">' + _("Enabled") + '</label></p>',
                '<table>',
                '<tr>',
                '<td><label for="rgftpuser">RescueGroups FTP username</label></td>',
                '<td><input id="rgftpuser" type="text" class="asm-textbox cfg" data="RescueGroupsFTPUser" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="rgftppass">RescueGroups FTP password</label></td>',
                '<td><input id="rgftppass" type="text" class="asm-textbox cfg" data="RescueGroupsFTPPassword" /></td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_adoptapet: function() {
            return [
                '<div id="tab-adoptapet">',
                html.info('Signup at <a href="http://www.adoptapet.com">www.adoptapet.com</a>.<br />' +
                    'Use the Shelter/Rescue menu after logging in to adoptapet to manage/setup your autoupload account for ASM'),
                '<p><input id="enabledap" type="checkbox" class="asm-checkbox enablecheck" /><label for="enabledap">' + _("Enabled") + '</label></p>',
                '<table>',
                '<tr>',
                '<td><label for="apftpuser">Autoupload FTP username</label></td>',
                '<td><input id="apftpuser" type="text" class="asm-textbox cfg" data="SaveAPetFTPUser" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="apftppass">Autoupload FTP password</label></td>',
                '<td><input id="apftppass" type="text" class="asm-textbox cfg" data="SaveAPetFTPPassword" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="includecolours">Colors</label></td>',
                '<td><select id="includecolours" class="asm-selectbox pbool preset" data="includecolours">',
                '<option value="0">Do not send colors</option>',
                '<option value="1">Send colors (not recommended, requires mapping)</option>',
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="noimportfile">import.cfg</label></td>',
                '<td><select id="noimportfile" class="asm-selectbox pbool preset" data="noimportfile">',
                '<option value="0">Auto-generate and upload</option>',
                '<option value="1">Do not generate and upload (not recommended)</option>',
                '</select></td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_anibase: function() {
            return [
                '<div id="tab-anibase">',
                html.info('These settings are for uploading new owner information to the Identibase/Anibase UK microchip database. <br/>' + 
                    'Find out more at <a href="http://www.animalcare.co.uk">www.animalcare.co.uk</a>'),
                '<p><input id="enabledabuk" type="checkbox" class="asm-checkbox enablecheck" /><label for="enabledabuk">' + _("Enabled") + '</label></p>',
                '<table>',
                '<tr style="display: none">', // We hide this for now as it isn't needed apparently and a blank is fine
                '<td><label for="anibasepracticeid">Practice ID</label></td>',
                '<td><input data="AnibasePracticeID" id="anibasepracticeid" type="text" class="asm-doubletextbox cfg" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="anibasepinno">Vet Code</label></td>',
                '<td><input data="AnibasePinNo" id="anibasepinno" type="text" class="asm-doubletextbox cfg" /></td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_akcreunite: function() {
            return [
                '<div id="tab-akcreunite">',
                html.info('Learn about AKC Reunite microchips and auto-uploading pet enrollment information at ' +
                    '<a target="_blank" href="https://www.akcreunite.org/shelters">https://www.akcreunite.org/shelters</a>.<br/>' +
                    'Request auto-uploads of pet microchip information to AKC Reunite at ' +
                    '<a target="_blank" href="https://www.akcreunite.org/auto-upload/">https://www.akcreunite.org/auto-upload</a>.'),
                '<p><input id="enabledak" type="checkbox" class="asm-checkbox enablecheck" /><label for="enabledak">' + _("Enabled") + '</label></p>',
                '<p><button id="button-akenroll">Generate an Enrollment Source Id for AKC Reunite</button></p>',
                '<table>',
                '<tr>',
                '<td><label for="akenrollmentid">AKC Reunite Enrollment Source ID</label></td>',
                '<td><input id="akenrollmentid" type="text" class="asm-doubletextbox cfg" disabled="disabled" data="AKCEnrollmentSourceID" /></td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_foundanimals: function() {
            return [
                '<div id="tab-foundanimals">',
                html.info('Find out more at <a href="http://www.found.org">www.found.org</a><br/>' +
                    'Contact clientcare@found.org to get a folder for automatic batch registrations of microchips.'),
                '<p><input id="enabledfa" type="checkbox" class="asm-checkbox enablecheck" /><label for="enabledfa">' + _("Enabled") + '</label></p>',
                '<table>',
                '<tr>',
                '<td><label for="fafolder">Folder name</label></td>',
                '<td><input id="fafolder" type="text" class="asm-textbox asm-doubletextbox cfg" data="FoundAnimalsFolder" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="faemail">Rescue group email</label></td>',
                '<td><input id="faemail" type="text" class="asm-textbox asm-doubletextbox cfg" data="FoundAnimalsEmail" />',
                '<span id="callout-faemail" class="asm-callout">',
                'To stay on record for every pet you register as the permanent rescue contact, enter your group\'s Found Animals Registry ',
                'account email in this field. If you do not have that type of account set up, visit ',
                '<a href="http://www.found.org/start">www.found.org/start</a><br/>',
                '</span>',
                '</td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_homeagain: function() {
            return [
                '<div id="tab-homeagain">',
                html.info('Signup at <a href="http://homeagain.4act.com">http://homeagain.4act.com</a> or contact HomeAgain Customer Service on <a href="tel:1-800-341-5785">(800) 341-5785</a> for more information.'),
                '<p><input id="enabledha" type="checkbox" class="asm-checkbox enablecheck" /><label for="enabledha">' + _("Enabled") + '</label></p>',
                '<table>',
                '<tr>',
                '<td><label for="hauserid">HomeAgain User ID</label></td>',
                '<td><input id="hauserid" type="text" class="asm-doubletextbox cfg" disabled="disabled" data="HomeAgainUserId" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="hauserpassword">HomeAgain User Password</label></td>',
                '<td><input id="hauserpassword" type="text" class="asm-doubletextbox cfg" disabled="disabled" data="HomeAgainUserPassword" /></td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_maddiesfund: function() {
            return [
                '<div id="tab-maddiesfund">',
                html.info('Signup at <a href="http://www.maddiesfund.org/mpa.htm">http://www.maddiesfund.org/mpa.htm</a>'),
                '<p><input id="enabledmf" type="checkbox" class="asm-checkbox enablecheck" /><label for="enabledmf">' + _("Enabled") + '</label></p>',
                '<table>',
                '<tr>',
                '<td><label for="mfemail">MPA API Username</label></td>',
                '<td><input id="mfemail" type="text" class="asm-textbox cfg" data="MaddiesFundUsername" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="mfpassword">MPA API Password</label></td>',
                '<td><input id="mfpassword" type="text" class="asm-textbox cfg" data="MaddiesFundPassword" /></td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_petcademy: function() {
            return [
                '<div id="tab-petcademy">',
                html.info('Signup at <a href="https://petcademy.typeform.com/to/PTTM44">https://petcademy.typeform.com/to/PTTM44</a>'),
                '<p><input id="enabledpc" type="checkbox" class="asm-checkbox enablecheck" /><label for="enabledpc">' + _("Enabled") + '</label></p>',
                '<table>',
                '<tr>',
                '<td><label for="pctoken">Petcademy Token</label></td>',
                '<td><input id="pctoken" type="text" class="asm-textbox cfg" data="PetcademyToken" /></td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_helpinglostpets: function() {
            return [
                '<div id="tab-helpinglostpets">',
                html.info('Signup at <a href="http://www.helpinglostpets.com">www.helpinglostpets.com</a>'),
                '<p><input id="enabledhlp" type="checkbox" class="asm-checkbox enablecheck" /><label for="enabledhlp">' + _("Enabled") + '</label></p>',
                '<table>',
                '<tr>',
                '<td><label for="hlpftpuser">HelpingLostPets FTP username</label></td>',
                '<td><input id="hlpftpuser" type="text" class="asm-textbox cfg" data="HelpingLostPetsFTPUser" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="hlpftppass">HelpingLostPets FTP password</label></td>',
                '<td><input id="hlpftppass" type="text" class="asm-textbox cfg" data="HelpingLostPetsFTPPassword" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="hlporgid">HelpingLostPets Organisation ID</label></td>',
                '<td><input id="hlporgid" type="text" class="asm-textbox cfg" data="HelpingLostPetsOrgID" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="hlppostal">Postal/Zip Code of your shelter</label></td>',
                '<td><input id="hlppostal" type="text" class="asm-textbox cfg" data="HelpingLostPetsPostal" /></td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_smarttag: function() {
            return [
                '<div id="tab-smarttag">',
                html.info('Find out more at <a href="http://www.idtag.com">www.idtag.com</a><br/>' +
                    'Contact SmartTag to get your account ID for automatic registration of chips and tags ' +
                    '212-868-2559 x136 (Mike Cotti) or email mikec@idtag.com'),
                '<p><input id="enabledst" type="checkbox" class="asm-checkbox enablecheck" /><label for="enabledst">' + _("Enabled") + '</label></p>',
                '<table>',
                '<tr>',
                '<td><label for="stuser">SmartTag Account ID</label></td>',
                '<td><input id="stuser" type="text" class="asm-textbox cfg" data="SmartTagFTPUser" /></td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_vetenvoy_signup_dialog: function() {
            return [
                '<div id="dialog-vetenvoy" style="display: none" title="' + html.title("Signup for VetEnvoy") + '">',
                '<table width="100%">',
                '<tr>',
                '<td><label for="vetitle">Title</label></td>',
                '<td><select id="vetitle" data="title" class="asm-selectbox">',
                '<option>Mr</option>',
                '<option>Mrs</option>',
                '<option>Miss</option>',
                '<option>Ms</option>',
                '<option>Dr</option>',
                '<option>Fr</option>',
                '<option>Prof</option>',
                '<option>Ofc</option>',
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="vefirstname">First Name</label></td>',
                '<td><input id="vefirstname" data="firstname" type="textbox" class="asm-textbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="velastname">Last Name</label></td>',
                '<td><input id="velastname" data="lastname" type="textbox" class="asm-textbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="vephone">Phone</label></td>',
                '<td><input id="vephone" data="phone" type="textbox" class="asm-textbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="veemail">Email</label></td>',
                '<td><input id="veemail" data="email" type="textbox" class="asm-textbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="veposition">Position</label></td>',
                '<td><input id="veposition" data="position" type="textbox" class="asm-textbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="vepracticename">Shelter Name</label></td>',
                '<td><input id="vepracticename" data="practicename" type="textbox" class="asm-textbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="veaddress">Address</label></td>',
                '<td><input id="veaddress" data="address" type="textbox" class="asm-textbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="vezipcode">Zipcode</label></td>',
                '<td><input id="vezipcode" data="zipcode" type="textbox" class="asm-textbox" /></td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");

        },

        render_vetenvoy: function() {
            return [
                '<div id="tab-vetenvoy">',
                html.info('VetEnvoy allow ASM to automatically register microchips provided by HomeAgain and AKC Reunite<br />' +
                    'Find out more at <a href="http://www.vetenvoy.com">www.vetenvoy.com</a>, ' +
                    '<a href="http://www.homeagain.com">www.homeagain.com</a> and ' +
                    '<a href="http://www.akcreunite.org">www.akcreunite.org</a>'),
                '<p><button id="button-vesignup">Signup for VetEnvoy</button></p>',
                '<p><input id="enabledve" type="checkbox" class="asm-checkbox enablecheck" /><label for="enabledve">' + _("Enabled") + '</label></p>',
                '<table>',
                '<tr>',
                '<td><label for="veuserid">VetEnvoy User ID</label></td>',
                '<td><input id="veuserid" type="text" class="asm-doubletextbox cfg" disabled="disabled" data="VetEnvoyUserId" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="veuserpassword">VetEnvoy User Password</label></td>',
                '<td><input id="veuserpassword" type="text" class="asm-doubletextbox cfg" disabled="disabled" data="VetEnvoyUserPassword" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="vehomeagain">Register HomeAgain Microchips</label></td>',
                '<td><select id="vehomeagain" class="asm-selectbox cfg" disabled="disabled" data="VetEnvoyHomeAgainEnabled">',
                '<option>Yes</option><option>No</option></select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="veakc">Register AKC Reunite Microchips</label></td>',
                '<td><select id="veakc" class="asm-selectbox cfg" disabled="disabled" data="VetEnvoyAKCReuniteEnabled">',
                '<option>Yes</option><option>No</option></select></td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render: function() {
            return [
                this.render_vetenvoy_signup_dialog(),
                html.content_header(_("Publishing Options")),
                '<div class="asm-toolbar">',
                '<button id="button-save" title="' + _("Update publishing options") + '">' + html.icon("save") + ' ' + _("Save") + '</button>',
                '</div>',
                '<div id="tabs">',
                this.render_tabs(),
                this.render_animalselection(),
                this.render_allpublishers(),
                this.render_anibase(),
                this.render_pettrac(),
                this.render_petlink(),
                this.render_htmlftp(),
                this.render_petfinder(),
                this.render_petrescue(), 
                this.render_savourlife(), 
                this.render_petslocated(),
                this.render_rescuegroups(),
                this.render_adoptapet(),
                this.render_akcreunite(),
                this.render_foundanimals(),
                this.render_homeagain(),
                this.render_maddiesfund(),
                this.render_petcademy(),
                this.render_helpinglostpets(),
                this.render_smarttag(),
                this.render_vetenvoy(),
                '</div>',
                html.content_footer()
            ].join("\n");
        },

        bind_vetenvoy_signup_dialog: function() {
            let b = { };
            b[_("Signup")] = async function() {
                validate.reset("dialog-vetenvoy");
                if (!validate.notblank([ "vefirstname", "velastname", "vephone", "veemail", "vepracticename", "vezipcode", "veaddress" ])) { return; }
                $("#dialog-vetenvoy").disable_dialog_buttons();
                let formdata = $("#dialog-vetenvoy .asm-textbox, #dialog-vetenvoy .asm-selectbox").toPOST();
                let result = await common.ajax_post("publish_options", "mode=vesignup&" + formdata);
                $("#dialog-vetenvoy").dialog("close");
                $("#dialog-vetenvoy").enable_dialog_buttons();
                // Result should be userid,password
                $("#veuserid").val(result.split(",")[0]);
                $("#veuserpassword").val(result.split(",")[1]);
                $("#enabledve").prop("checked", true);
                $("#enabledve").closest("div").find(".asm-doubletextbox").removeAttr("disabled");
                // Hide the signup button
                $("#button-vesignup").hide();
                // Prompt to save
                validate.dirty(true);
            };
            b[_("Cancel")] = function() {
                $("#dialog-vetenvoy").dialog("close");
            };
            $("#dialog-vetenvoy").dialog({
                autoOpen: false,
                width: 550,
                modal: true,
                dialogClass: "dialogshadow",
                show: dlgfx.edit_show,
                hide: dlgfx.edit_hide,
                buttons: b
            });
        },


        bind: function() {
            const change_checkbox = function() {
                $(".enablecheck").each(function() {
                    let enabled = $(this).is(":checked");
                    if (enabled) {
                        $(this).closest("div").find("select").select("enable");
                        $(this).closest("div").find(".asm-textbox, .asm-doubletextbox").removeAttr("disabled");
                        $(this).closest("div").find("textarea").removeAttr("disabled");
                    }
                    else {
                        $(this).closest("div").find("select").select("disable");
                        $(this).closest("div").find(".asm-textbox, .asm-doubletextbox").attr("disabled", "disabled");
                        $(this).closest("div").find("textarea").attr("disabled", "disabled");
                    }
                });
            };

            const cfg_presets = function() {
                // Read the controls tagged with preset and build an 
                // old style publisher command line string for storing as a
                // configuration option.
                let pr = "";
                $(".preset").each(function() {
                    if ($(this).is(".pbool")) {
                        if ($(this).val() == "1") { pr += " " + $(this).attr("data"); }
                    }
                    else {
                        pr += " " + $(this).attr("data") + "=" + $(this).val();
                    }
                });
                return encodeURIComponent(common.trim(pr));
            };

            const cfg_enabled = function() {
                // Read the enable checkboxes and build a list of enabled publishers 
                // for storing as a configuration option.
                let ep = [];
                $(".enablecheck").each(function() {
                    let c = $(this), k = c.attr("id").replace("enabled", "");
                    // VetEnvoy has two publishers - enable them both if VetEnvoy is on
                    if (c.is(":checked") && k == "ve") { ep.push("veha"); ep.push("vear"); }
                    else if (c.is(":checked")) { ep.push(k); }
                });
                return encodeURIComponent(ep.join(" "));
            };

            // Disable publisher panels when the checkbox says they're disabled
            $(".enablecheck").change(change_checkbox);

            // Toolbar buttons
            $("#button-save").button().click(async function() {
                $("#button-save").button("disable");
                validate.dirty(false);
                let formdata = "mode=save&" + $(".cfg").toPOST();
                formdata += "&PublisherPresets=" + cfg_presets();
                formdata += "&PublishersEnabled=" + cfg_enabled();
                header.show_loading(_("Saving..."));
                await common.ajax_post("publish_options", formdata);
                // Needs to do a full reload to get config.js to update
                common.route_reload(true); 
            });

            $("#button-save").button("disable");

            // Enable services that are only present in certain locales
            $(".localeau").hide();
            $(".localeus").hide();
            $(".localeca").hide();
            $(".localegb").hide();
            $(".localemx").hide();
            $(".english").hide();
            if (asm.locale.indexOf("en") == 0) { $(".english").show(); }
            if (asm.locale == "en") { $(".localeus").show(); }
            if (asm.locale == "en_AU") { $(".localeau").show(); }
            if (asm.locale == "en_GB") { $(".localegb").show(); }
            if (asm.locale == "en_CA" || asm.locale == "fr_CA") { $(".localeca").show(); }
            if (asm.locale == "en_MX" || asm.locale == "es_MX") { $(".localemx").show(); }

            // Disable services that require sitedef setup
            if (!controller.hasakcreunite) { $(".hasakcreunite").hide(); }
            if (!controller.hasfoundanimals) { $(".hasfoundanimals").hide(); }
            if (!controller.hashtmlftp) { $(".hashtmlftp").hide(); }
            if (!controller.hashomeagain) { $(".hashomeagain").hide(); }
            if (!controller.hasmaddiesfund) { $(".hasmaddiesfund").hide(); }
            if (!controller.haspetcademy) { $(".haspetcademy").hide(); }
            if (!controller.haspetlink) { $(".haspetlink").hide(); }
            if (!controller.haspetrescue) { $(".haspetrescue").hide(); }
            if (!controller.haspetslocated) { $(".haspetslocated").hide(); }
            if (!controller.hassavourlife) { $(".hassavourlife").hide(); }
            if (!controller.hasvetenvoy) { $(".hasvetenvoy").hide(); }
            if (!controller.hassmarttag) { $(".hassmarttag").hide(); }

            // Components
            $("#tabs").tabs({ show: "slideDown", hide: "slideUp" });

            // Load default values from the config settings
            $(".cfg").each(function() {
                if ($(this).attr("data")) {
                    let d = $(this).attr("data");
                    if ($(this).is("input:text")) {
                        $(this).val( html.decode(config.str(d)));
                    }
                    else if ($(this).is("input:checkbox")) {
                        $(this).attr("checked", config.bool(d));
                    }
                    else if ($(this).hasClass("asm-bsmselect")) {
                        let n = $(this);
                        n.children().prop("selected", false);
                        $.each(config.str(d).split(/[|,]+/), function(mi, mv) {
                            n.find("[value='" + mv + "']").prop("selected", true);
                        });
                        n.change();
                    }
                    else if ($(this).is("select")) {
                        $(this).select("value", config.str(d));
                    }
                    else if ($(this).is("textarea")) {
                        $(this).val(html.decode(config.str(d)));
                    }
                }
            });

            // Set presets from command line configuration
            let cl = config.str("PublisherPresets");
            $.each(cl.split(" "), function(i, o) {
                // Deal with boolean flags in command line
                $.each( [ "includecase", "includereserved", "includefosters", 
                    "includewithoutdescription", "includewithoutimage", "includenonneutered", 
                    "includecolours", "includeretailer", "includehold", "includequarantine", "includetrial",
                    "bondedassingle", "clearexisting", "uploadall", "forcereupload", 
                    "generatejavascriptdb","thumbnails", "checksocket", "uploaddirectly", 
                    "htmlbychildadult", "htmlbyspecies", "htmlbytype", "outputadopted", 
                    "outputdeceased", "outputrss", "noimportfile" ], 
                function(bi, bo) {
                    if (bo == o) { $("[data='" + bo + "']").select("value", "1"); }
                });
                // Deal with key/value pairs
                $.each( [ "order", "excludeunder", "animalsperpage", "limit", "style", "extension",
                    "scaleimages", "thumbnailsize", "includelocations", "ftproot", "publishdirectory", 
                    "childadultsplit", "outputadopteddays" ],
                function(vi, vo) {
                    if (o.indexOf(vo) == 0) {
                        let v = o.split("=")[1];
                        let node = $("[data='" + vo + "']");
                        if (node.hasClass("asm-selectbox")) {
                            node.select("value", v);
                        }
                        else if (node.hasClass("asm-bsmselect")) {
                            let ls = v.split(",");
                            $.each(ls, function(li, lv) {
                                node.find("[value='" + lv + "']").prop("selected", "selected");
                            });
                            node.change();
                        }
                        else {
                            node.val(v);
                        }
                    }
                });
            });

            // Set enabled checkboxes from enabled publisher list
            let pe = config.str("PublishersEnabled");
            $.each(pe.split(" "), function(i, v) {
                $("#enabled" + v).attr("checked", true);
            });

            // Disable publisher fields for those not active
            change_checkbox();

            // Setup the vetenvoy signup dialog
            this.bind_vetenvoy_signup_dialog();

            // Make the signup button show it
            $("#button-vesignup").button().click(function() {
                $("#dialog-vetenvoy").dialog("open");
            });

            // Only show the VetEnvoy signup button if we no userid set
            if (!config.str("VetEnvoyUserId")) {
                $("#button-vesignup").show();
                // Set default signup values from what we know of the shelter already
                $("#vepraticename").val(config.str("Organisation"));
                $("#vephone").val(config.str("OrganisationTelephone"));
                $("#veemail").val(config.str("EmailAddress"));
                $("#veaddress").val(config.str("OrganisationAddress"));
                $("#button-vesignup").show();
            }
            else {
                $("#button-vesignup").hide();
            }

            // Pushing the AKC generate enrollment id button generates an id
            $("#button-akenroll").button().click(function() {
                $("#akenrollmentid").val( common.generate_uuid() );
                $("#button-akenroll").hide();
            });

            // Only show the AKC enrollment id button if none is set
            if (!config.str("AKCEnrollmentSourceID") || common.trim(config.str("AKCEnrollmentSourceID")) == "") {
                $("#button-akenroll").show();
            }
            else {
                $("#button-akenroll").hide();
            }

            validate.bind_dirty();

        },

        destroy: function() {
            validate.unbind_dirty();
            common.widget_destroy("#dialog-vetenvoy");
        },

        name: "publish_options",
        animation: "options",
        autofocus: "#caseanimals",
        title: function() { return _("Publishing Options"); },
        routes: {
            "publish_options": function() { common.module_loadandstart("publish_options", "publish_options"); }
        }

    };

    common.module_register(publish_options);

});

