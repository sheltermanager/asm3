/*jslint browser: true, forin: true, eqeq: true, white: true, sloppy: true, vars: true, nomen: true */
/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    var publish_options = {

        render_tabs: function() {
            return [
                '<ul>',
                '<li><a href="#tab-animalselection">' + _("Animal Selection") + '</a></li>',
                '<li><a href="#tab-allpublishers">' + _("All Publishers") + '</a></li>',
                '<li><a href="#tab-htmlftp">' + _("HTML/FTP Publisher") + '</a></li>',
                '<li class="localeus"><a href="#tab-adoptapet">AdoptAPet Publisher</a></li>',
                '<li><a href="#tab-helpinglostpets">HelpingLostPets Publisher</a></li>',
                '<li class="localeus localeca localemx"><a href="#tab-meetapet">MeetAPet Publisher</a></li>',
                '<li class="localeus localeca localemx"><a href="#tab-petfinder">PetFinder Publisher</a></li>',
                '<li class="localeau"><a href="#tab-petrescue">PetRescue Publisher</a></li>',
                '<li class="localeus"><a href="#tab-rescuegroups">RescueGroups Publisher</a></li>',
                '<li class="localegb"><a href="#tab-anibase">Anibase UK Microchips</a></li>',
                '<li class="localegb"><a href="#tab-pettrac">AVID/PETtrac UK Microchips</a></li>',
                '<li class="localeus localeca localemx"><a href="#tab-petlink">PetLink Microchips</a></li>',
                '<li class="localeus hassmarttag"><a href="#tab-smarttag">SmartTag Tags/Microchips</a></li>',
                '<li class="localeus hasvevendor"><a href="#tab-vetenvoy">VetEnvoy Microchips</a></li>',
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
                '<td><select id="excludeunder" class="asm-selectbox preset" data="excludeunder">',
                '<option value="1">' + _("1 week") + '</option>',
                '<option value="2">' + _("2 weeks") + '</option>',
                '<option value="4">' + _("4 weeks") + '</option>',
                '<option value="6">' + _("6 weeks") + '</option>',
                '<option value="8">' + _("8 weeks") + '</option>',
                '<option value="12">' + _("3 months") + '</option>',
                '<option value="26">' + _("6 months") + '</option>',
                '<option value="38">' + _("9 months") + '</option>',
                '<option value="52">' + _("1 year") + '</option>',
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="locations">' + _("Include animals in the following locations") + '</label></td>',
                '<td><select id="locations" class="asm-bsmselect preset" multiple="multiple" data="includelocations">',
                html.list_to_options(controller.locations, "ID", "LOCATIONNAME"),
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td></td>',
                '<td>',
                '<div class="ui-state-highlight ui-corner-all" style="padding: 0 .7em;">',
                '<p><span class="ui-icon ui-icon-info" style="float: left; margin-right: .3em;"></span>',
                _("If you don't select any locations, publishers will include animals in all locations."),
                '</p>',
                '</div>',
                '</td>',
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
                '<td><label for="limit">' + _("Only publish a set number of animals") + '</label></td>',
                '<td valign="middle"><input id="limit" type="text" class="asm-textbox asm-numberbox preset" data="limit" value="0" />',
                '<div class="ui-state-highlight ui-corner-all" style="padding: 0 .7em; display: inline-block; vertical-align: middle;">',
                '<p><span class="ui-icon ui-icon-info" style="float: left; margin-right: .3em;"></span>',
                _("Set to 0 for no limit."),
                '</p>',
                '</div>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="regmic">' + _("Register microchips after") + '</label></td>',
                '<td><select id="regmic" class="asm-bsmselect cfg" multiple="multiple" data="MicrochipRegisterMovements">',
                '<option value="1">' + _("Adoption") + '</option>',
                '<option value="2">' + _("Foster") + '</option>',
                '<option value="3">' + _("Transfer") + '</option>',
                '<option value="5">' + _("Reclaim") + '</option>',
                '<option value="11">' + _("Trial Adoption") + '</option>',
                '</select></td>',
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
                '<td><label for="usecomments">' + _("Animal descriptions") + '</label></td>',
                '<td><select id="usecomments" class="asm-selectbox cfg" data="PublisherUseComments">',
                '<option value="Yes">' + _("Use animal comments") + '</option>',
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
                html.info('These settings are for uploading new owner information to the AVID PETtrac UK microchip database. <br/>' + 
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
                '<td><label for="plemail">Login Email</label></td>',
                '<td><input id="plemail" type="text" class="asm-textbox cfg" data="PetLinkEmail" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="plpass">Password</label></td>',
                '<td><input id="plpass" type="text" class="asm-textbox cfg" data="PetLinkPassword" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="plchippass">Chip Password</label></td>',
                '<td><input id="plchippass" type="text" class="asm-textbox cfg" data="PetLinkChipPassword" /></td>',
                '</tr>',
                '<tr>',
                '<td></td>',
                '<td>',
                html.info('The chip password is the password that allows owners to update their own information on the PetLink' +
                  'website in combination with their email address.'),
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
                '<td><label for="scale">' + _("Thumbnail size") + '</label></td>',
                '<td><select id="scale" class="asm-selectbox preset" data="thumbnailsize">',
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
                '<tr id="publishdiroverride" style="display: none">',
                '<td>' + _("Publish to folder") + '</td>',
                '<td><a href="#"></a></td>',
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
                '<td><label for="prftpuser">PetRescue account ID</label></td>',
                '<td><input id="prftpuser" type="text" class="asm-textbox cfg" data="PetRescueFTPUser" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="prftppass">PetRescue password</label></td>',
                '<td><input id="prftppass" type="text" class="asm-textbox cfg" data="PetRescueFTPPassword" /></td>',
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
                html.info('Signup at <a href="http://www.adoptapet.com">www.adoptapet.com</a>'),
                '<p><input id="enabledap" type="checkbox" class="asm-checkbox enablecheck" /><label for="enabledap">' + _("Enabled") + '</label></p>',
                '<table>',
                '<tr>',
                '<td><label for="apftpuser">AdoptAPet FTP username</label></td>',
                '<td><input id="apftpuser" type="text" class="asm-textbox cfg" data="SaveAPetFTPUser" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="apftppass">AdoptAPet FTP password</label></td>',
                '<td><input id="apftppass" type="text" class="asm-textbox cfg" data="SaveAPetFTPPassword" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="includecolours">Include colors in column 9</label></td>',
                '<td><select id="includecolours" class="asm-selectbox pbool preset" data="includecolours">',
                '<option value="0">' + _("No") + '</option>',
                '<option value="1">' + _("Yes") + '</option>',
                '</select></td>',
                '</tr>',
                '<tr>',
                '<td><label for="noimportfile">Don\'t upload import.cfg</label></td>',
                '<td><select id="noimportfile" class="asm-selectbox pbool preset" data="noimportfile">',
                '<option value="0">' + _("No") + '</option>',
                '<option value="1">' + _("Yes") + '</option>',
                '</select></td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_anibase: function() {
            return [
                '<div id="tab-anibase">',
                html.info('These settings are for uploading new owner information to the idENTIPCHIP/Anibase UK microchip database. <br/>' + 
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

        render_meetapet: function() {
            return [
                '<div id="tab-meetapet">',
                html.info('Signup at <a href="http://www.meetapet.com">www.meetapet.com</a>'),
                '<p><input id="enabledmp" type="checkbox" class="asm-checkbox enablecheck" /><label for="enabledmp">' + _("Enabled") + '</label></p>',
                '<table>',
                '<tr style="display: none">',
                '<td><label for="mpkey">MeetAPet Key</label></td>',
                '<td><input id="mpkey" type="text" class="asm-textbox cfg" data="MeetAPetKey" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="mpsecret">MeetAPet Secret</label></td>',
                '<td><input id="mpsecret" type="text" class="asm-textbox cfg" data="MeetAPetSecret" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="mpuserkey">MeetAPet Shelter Key</label></td>',
                '<td><input id="mpuserkey" type="text" class="asm-textbox cfg" data="MeetAPetUserKey" /></td>',
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
                '<td><input id="veuserid" type="text" class="asm-doubletextbox cfg" data="VetEnvoyUserId" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="veuserpassword">VetEnvoy User Password</label></td>',
                '<td><input id="veuserpassword" type="text" class="asm-doubletextbox cfg" data="VetEnvoyUserPassword" /></td>',
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
                this.render_rescuegroups(),
                this.render_adoptapet(),
                this.render_meetapet(),
                this.render_helpinglostpets(),
                this.render_smarttag(),
                this.render_vetenvoy(),
                '</div>',
                html.content_footer()
            ].join("\n");
        },

        bind_vetenvoy_signup_dialog: function() {
            var b = { };
            b[_("Signup")] = function() {
                $("#dialog-vetenvoy label").removeClass("ui-state-error-text");
                if (!validate.notblank([ "vefirstname", "velastname", "vephone", "veemail", "vepracticename", "vezipcode", "veaddress" ])) { return; }
                $("#dialog-vetenvoy").disable_dialog_buttons();
                var formdata = $("#dialog-vetenvoy .asm-textbox, #dialog-vetenvoy .asm-selectbox").toPOST();
                common.ajax_post("publish_options", "mode=vesignup&" + formdata)
                    .then(function(result) {
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
                    });
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
            var change_checkbox = function() {
                $(".enablecheck").each(function() {
                    var enabled = $(this).is(":checked");
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

            var cfg_presets = function() {
                // Read the controls tagged with preset and build an 
                // old style publisher command line string for storing as a
                // configuration option.
                var pr = "";
                $(".preset").each(function() {
                    if ($(this).is(".pbool")) {
                        if ($(this).val() == "1") { pr += " " + $(this).attr("data"); }
                    }
                    else {
                        pr += " " + $(this).attr("data") + "=" + $(this).val();
                    }
                });
                return encodeURIComponent($.trim(pr));
            };

            var cfg_enabled = function() {
                // Read the enable checkboxes and build a list of enabled publishers 
                // for storing as a configuration option.
                var ep = "";
                if ($("#enabledhtml").is(":checked")) { ep += " html"; }
                if ($("#enabledpf").is(":checked")) { ep += " pf"; }
                if ($("#enabledabuk").is(":checked")) { ep += " abuk"; }
                if ($("#enabledap").is(":checked")) { ep += " ap"; }
                if ($("#enabledrg").is(":checked")) { ep += " rg"; }
                if ($("#enabledmp").is(":checked")) { ep += " mp"; }
                if ($("#enabledhlp").is(":checked")) { ep += " hlp"; }
                if ($("#enabledpl").is(":checked")) { ep += " pl"; }
                if ($("#enabledpr").is(":checked")) { ep += " pr"; }
                if ($("#enabledptuk").is(":checked")) { ep += " ptuk"; }
                if ($("#enabledst").is(":checked")) { ep += " st"; }
                if ($("#enabledve").is(":checked")) { ep += " ve"; }
                return encodeURIComponent($.trim(ep));
            };

            // Disable publisher panels when the checkbox says they're disabled
            $(".enablecheck").change(change_checkbox);

            // Disable publishing to a folder if it was overridden
            if (controller.publishurl != "") {
                $("#publishdirrow").hide();
                $("#publishdiroverride").show();
                var url = controller.publishurl;
                url = url.replace("{alias}", asm.useraccountalias);
                url = url.replace("{database}", asm.useraccount);
                url = url.replace("{username}", asm.user);
                $("#publishdiroverride a").attr("href", url).text(url);
            }

            // Disable ftp upload controls if ftp has been overridden
            if (controller.hasftpoverride) {
                $("#ftpuploadtable").hide();
            }

            // Toolbar buttons
            $("#button-save").button().click(function() {
                $("#button-save").button("disable");
                validate.dirty(false);
                var formdata = "mode=save&" + $(".cfg").toPOST();
                formdata += "&PublisherPresets=" + cfg_presets();
                formdata += "&PublishersEnabled=" + cfg_enabled();
                common.ajax_post("publish_options", formdata)
                    .then(function() { 
                        // Needs to do a full reload to get config.js to update
                        common.route_reload(true); 
                    });
            });
            $("#button-save").button("disable");

            $(".localeau").hide();
            $(".localeus").hide();
            $(".localeca").hide();
            $(".localegb").hide();
            $(".localemx").hide();

            // Enable tabs for US only publishers
            if (asm.locale == "en") {
                $(".localeus").show();
            }

            // Enable tab sections for Australian publishers
            if (asm.locale == "en_AU" && controller.haspetrescue) {
                $(".localeau").show();
            }

            // Enable tab sections for British publishers
            if (asm.locale == "en_GB") {
                $(".localegb").show();
            }

            // Enable tab sections for Canadian publishers
            if (asm.locale == "en_CA") {
                $(".localeca").show();
            }

            // Enable tab sections for Mexican publishers
            if (asm.locale == "en_MX" || asm.locale == "es_MX") {
                $(".localemx").show();
            }

            // Disable VetEnvoy if there's no vendor password
            if (!controller.hasvevendor) {
                $(".hasvevendor").hide();
            }

            // Disable SmartTag if it's not setup in sitedefs
            if (!controller.hassmarttag) {
                $(".hassmarttag").hide();
            }

            // Components
            $("#tabs").tabs({ show: "slideDown", hide: "slideUp" });

            // Load default values from the config settings
            $(".cfg").each(function() {
                if ($(this).attr("data")) {
                    var d = $(this).attr("data");
                    if ($(this).is("input:text")) {
                        $(this).val( html.decode(config.str(d)));
                    }
                    else if ($(this).is("input:checkbox")) {
                        $(this).attr("checked", config.bool(d));
                    }
                    else if ($(this).hasClass("asm-bsmselect")) {
                        var n = $(this);
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
                        $(this).val(config.str(d));
                    }
                }
            });

            // Set presets from command line configuration
            var cl = config.str("PublisherPresets");
            $.each(cl.split(" "), function(i, o) {
                // Deal with boolean flags in command line
                $.each( [ "includecase", "includereserved", "includefosters", "includewithoutimage", 
                    "includecolours", "includeretailer", "includehold", "includequarantine", "includetrial",
                    "bondedassingle", "clearexisting", "uploadall", "forcereupload", 
                    "generatejavascriptdb","thumbnails", "checksocket", "uploaddirectly", 
                    "htmlbychildadult", "htmlbyspecies", "outputadopted", "outputrss", "noimportfile" ], 
                function(bi, bo) {
                    if (bo == o) { $("[data='" + bo + "']").select("value", "1"); }
                });
                // Deal with key/value pairs
                $.each( [ "order", "excludeunder", "animalsperpage", "limit", "style", "extension",
                    "scaleimages", "thumbnailsize", "includelocations", "ftproot", "publishdirectory", 
                    "childadultsplit", "outputadopteddays" ],
                function(vi, vo) {
                    if (o.indexOf(vo) == 0) {
                        var v = o.split("=")[1];
                        var node = $("[data='" + vo + "']");
                        if (node.hasClass("asm-selectbox")) {
                            node.select("value", v);
                        }
                        else if (node.hasClass("asm-bsmselect")) {
                            var ls = v.split(",");
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

            // Set enabled from enabled list
            var pe = config.str("PublishersEnabled");
            if (pe.indexOf("html") != -1) { $("#enabledhtml").attr("checked", true); }
            if (pe.indexOf("pf") != -1) { $("#enabledpf").attr("checked", true); }
            if (pe.indexOf("ap") != -1) { $("#enabledap").attr("checked", true); }
            if (pe.indexOf("rg") != -1) { $("#enabledrg").attr("checked", true); }
            if (pe.indexOf("mp") != -1) { $("#enabledmp").attr("checked", true); }
            if (pe.indexOf("hlp") != -1) { $("#enabledhlp").attr("checked", true); }
            if (pe.indexOf("pl") != -1) { $("#enabledpl").attr("checked", true); }
            if (pe.indexOf("pr") != -1) { $("#enabledpr").attr("checked", true); }
            if (pe.indexOf("ptuk") != -1) { $("#enabledptuk").attr("checked", true); }
            if (pe.indexOf("abuk") != -1) { $("#enabledabuk").attr("checked", true); }
            if (pe.indexOf("st") != -1) { $("#enabledst").attr("checked", true); }
            if (pe.indexOf("ve") != -1) { $("#enabledve").attr("checked", true); }

            // Disable publisher fields for those not active
            change_checkbox();

            // Setup the vetenvoy signup dialog
            this.bind_vetenvoy_signup_dialog();

            // Make the signup button show it
            $("#button-vesignup").button().click(function() {
                $("#dialog-vetenvoy").dialog("open");
            });

            // Only show the VetEnvoy signup button if we have
            // a System Vendor user/password and no userid set
            if (controller.hasvesys && !config.str("VetEnvoyUserId")) {
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

