/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */

$(function() {

    "use strict";

    const publish_options = {

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
                '<td><input id="vefirstname" data="firstname" type="text" class="asm-text" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="velastname">Last Name</label></td>',
                '<td><input id="velastname" data="lastname" type="text" class="asm-text" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="vephone">Phone</label></td>',
                '<td><input id="vephone" data="phone" type="text" class="asm-text" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="veemail">Email</label></td>',
                '<td><input id="veemail" data="email" type="text" class="asm-text" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="veposition">Position</label></td>',
                '<td><input id="veposition" data="position" type="text" class="asm-text" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="vepracticename">Shelter Name</label></td>',
                '<td><input id="vepracticename" data="practicename" type="text" class="asm-textbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="veaddress">Address</label></td>',
                '<td><input id="veaddress" data="address" type="text" class="asm-textbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="vezipcode">Zipcode</label></td>',
                '<td><input id="vezipcode" data="zipcode" type="text" class="asm-textbox" /></td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");

        },

        render: function() {
            let yesnooptions = '<option value="0">' + _("No") + '</option>' + '<option value="1">' + _("Yes") + '</option>';
            return [
                html.content_header(_("Publishing Options")),
                tableform.buttons_render([
                    { id: "save", icon: "save", text: _("Save") }
                 ], { centered: false }),
                tableform.render_tabs([
                    { id: "tab-animalselection", title: _("Animal Selection"), fields: [
                        { id: "caseanimals", post_field: "includecase", label: _("Include cruelty case animals"), type: "select", options: yesnooptions, classes: 'pbool preset' }, 
                        { id: "nonneutered", post_field: "includenonneutered", label: _("Include unaltered animals"), type: "select", options: yesnooptions, classes: 'pbool preset' }, 
                        { id: "nonmicrochip", post_field: "includenonmicrochip", label: _("Include non-microchipped animals"), type: "select", options: yesnooptions, classes: 'pbool preset' }, 
                        { id: "reservedanimals", post_field: "includereserved", label: _("Include reserved animals"), type: "select", options: yesnooptions, classes: 'pbool preset' }, 
                        { id: "retaileranimals", post_field: "includeretailer", label: _("Include reserved animals"), type: "select", options: yesnooptions, classes: 'pbool preset' }, 
                        { id: "fosteredanimals", post_field: "includefosters", label: _("Include fostered animals"), type: "select", options: yesnooptions, classes: 'pbool preset' }, 
                        { id: "heldanimals", post_field: "includehold", label: _("Include held animals"), type: "select", options: yesnooptions, classes: 'pbool preset' }, 
                        { id: "quarantinedanimals", post_field: "includequarantine", label: _("Include quarantined animals"), type: "select", options: yesnooptions , classes: 'pbool preset'}, 
                        { id: "trialanimals", post_field: "includetrial", label: _("Include animals on trial adoption"), type: "select", options: yesnooptions, classes: 'pbool preset' }, 
                        { id: "nodescription", post_field: "includewithoutdescription", label: _("Include animals who don't have a description"), type: "select", options: yesnooptions, classes: 'pbool preset' }, 
                        { id: "noimage", post_field: "includewithoutimage", label: _("Include animals who don't have a picture"), type: "select", options: yesnooptions, classes: 'pbool preset' }, 
                        { id: "bonded", post_field: "bondedassingle", label: _("Merge bonded animals into a single record"), type: "select", options: yesnooptions, classes: 'pbool preset' }, 
                        { id: "excludeunder", post_field: "excludeunder", label: _("Exclude animals who are aged under"), type: "number", halfsize: true, xattr: 'data-min="1" data-max="52"', xmarkup: ' ' + _("weeks"), classes: 'preset' }, 
                        { id: "excludereserves", post_field: "excludereserves", label: _("Exclude animals with more than"), type: "number", halfsize: true, xattr: 'data-min="0" data-max="50"', xmarkup: ' ' + _("active reservations"), classes: 'preset' }, 
                        { id: "locations", post_field: "includelocations", label: _("Include animals in the following locations"), type: "selectmulti", options: html.list_to_options(controller.locations, "ID", "LOCATIONNAME"), callout: _("If you don't select any locations, publishers will include animals in all locations."), classes: 'preset' }, 
                    ]},
                    { id: "tab-allpublishers", title: _("All Publishers"), fields: [
                        { id: "regmic", post_field: "MicrochipRegisterMovements", label: _("Register microchips after"), type: "selectmulti", options: 
                            '<option value="0">' + _("Intake") + '</option>' + 
                            '<option value="1">' + _("Adoption") + '</option>' + 
                            '<option value="2">' + _("Foster") + '</option>' + 
                            '<option value="3">' + _("Transfer") + '</option>' + 
                            '<option value="5">' + _("Reclaim") + '</option>'+ 
                            '<option value="11">' + _("Trial Adoption") + '</option>'
                        }, 
                        { id: "regfrom", post_field: "MicrochipRegisterFrom", label: _("Register microchips from"), type: "date", callout: _("Only register microchips where the animal moved after this date")
                        }, 
                        { id: "updatefreq", post_field: "PublisherSub24Frequency", label: _("Update adoption websites every"), type: "select", options: 
                        '<option value="2">' + _("{0} hours").replace("{0}", "2") + '</option>' + 
                        '<option value="4">' + _("{0} hours").replace("{0}", "4") + '</option>' + 
                        '<option value="6">' + _("{0} hours").replace("{0}", "6") + '</option>' + 
                        '<option value="8">' + _("{0} hours").replace("{0}", "8") + '</option>' + 
                        '<option value="12">' + _("{0} hours").replace("{0}", "12") + '</option>' + 
                        '<option value="0">' + _("{0} hours").replace("{0}", "24") + '</option>'
                        }, 
                        { id: "forcereupload", post_field: "forcereupload", label: _("Reupload animal images every time"), type: "select", options: yesnooptions, classes: 'pbool preset' }, 
                        { id: "uploadall", post_field: "uploadall", label: _("Upload all available images for animals"), type: "select", options: yesnooptions, classes: 'pbool preset' }, 
                        { id: "publishascrossbreed", post_field: "PublishAsCrossbreed", label: _("Always set the crossbreed/mix flag for these breeds"), type: "selectmulti", options: html.list_to_options(controller.breeds, "ID", "BREEDNAME") }, 
                        { id: "order", post_field: "order", label: _("Order published animals by"), type: "select", options: 
                            '<option value="0">' + _("Entered (oldest first)") + '</option>' + 
                            '<option value="1">' + _("Entered (newest first)") + '</option>' + 
                            '<option value="2">' + _("Animal Name") + '</option>', 
                            classes: 'preset'
                        }, 
                        { id: "thumbnailsize", post_field: "ThumbnailSize", label: _("Thumbnail size"), type: "select", options: 
                            '<option value="100x100">100px</option>' + 
                            '<option value="150x150">150px</option>' + 
                            '<option value="200x200">200px</option>' + 
                            '<option value="250x250">250px</option>' + 
                            '<option value="300x300">300px</option>'
                        }, 
                        { id: "usecomments", post_field: "PublisherUseComments", label: _("Animal descriptions"), type: "select", options: 
                            '<option value="Yes">' + _("Use animal description") + '</option>' + 
                            '<option value="No">' + _("Use notes from preferred photo") + '</option>'
                        }, 
                        { id: "tppublishersig", post_field: "TPPublisherSig", label: _("Add this text to all animal descriptions"), type: "textarea", callout: _("When publishing to third party services, add this extra text to the bottom of all animal descriptions") }
                    ]}, 
                    { id: "tab-htmlftp", title: _("HTML/FTP Publisher"), classes: "hashtmlftp", fields: [
                        { id: "enabledhtml", label: _("Enabled"), type: "check", fullrow: true, classes: 'enablecheck' }, 
                        { id: "generatejavascript", post_field: "generatejavascriptdb", label: _("Generate a javascript database for the search page"), type: "select", options: yesnooptions, classes: 'pbool preset' }, 
                        { id: "thumbnails", post_field: "thumbnails", label: _("Generate image thumbnails as tn_$$IMAGE$$"), type: "select", options: yesnooptions }, 
                        { id: "scalethumb", post_field: "thumbnailsize", label: _("Thumbnail size"), type: "select", options: 
                            '<option value="70x70">70 px</option>' + 
                            '<option value="80x80">80 px</option>' + 
                            '<option value="90x90">90 px</option>' + 
                            '<option value="100x100">100 px</option>' + 
                            '<option value="120x120">120 px</option>' + 
                            '<option value="150x150">150 px</option>', 
                            classes: 'preset'
                        }, 
                        { id: "typesplit", post_field: "htmlbytype", label: _("Output a separate page for each animal type"), type: "select", options: yesnooptions, classes: 'pbool preset' }, 
                        { id: "childadult", post_field: "htmlbychildadult", label: _("Split species pages with a baby/adult prefix"), type: "select", options: yesnooptions, classes: 'pbool preset' }, 
                        { id: "speciessplit", post_field: "htmlbyspecies", label: _("Output a separate page for each species"), type: "select", options: yesnooptions, classes: 'pbool preset' }, 
                        { id: "childsplit", post_field: "childadultsplit", label: _("Split baby/adult age at"), type: "select", options: 
                            '<option value="1">' + _("1 week") + '</option>' + 
                            '<option value="2">' + _("2 weeks") + '</option>' + 
                            '<option value="4">' + _("4 weeks") + '</option>' + 
                            '<option value="8">' + _("8 weeks") + '</option>' + 
                            '<option value="12">' + _("3 months") + '</option>' + 
                            '<option value="26">' + _("6 months") + '</option>' + 
                            '<option value="38">' + _("9 months") + '</option>' + 
                            '<option value="52">' + _("1 year") + '</option>',
                            classes: 'preset'
                        }, 
                        { id: "outputadopted", post_field: "outputadopted", label: _("Output an adopted animals page"), type: "select", options: yesnooptions }, 
                        { id: "outputadopteddays", post_field: "outputadopteddays", label: _("Show animals adopted"), type: "select", options: 
                            '<option value="7">' + _("In the last week") + '</option>' + 
                            '<option value="31">' + _("In the last month") + '</option>' + 
                            '<option value="93">' + _("In the last quarter") + '</option>' + 
                            '<option value="365">' + _("In the last year") + '</option>', 
                            classes: 'preset'
                        }, 
                        { id: "outputdeceased", post_field: "outputdeceased", label: _("Output a deceased animals page"), type: "select", options: yesnooptions, classes: 'pbool preset' }, 
                        { id: "outputforms", post_field: "outputforms", label: _("Output a page with links to available online forms"), type: "select", options: yesnooptions, classes: 'pbool preset' }, 
                        { id: "outputrss", post_field: "outputrss", label: _("Output an rss.xml page"), type: "select", options: yesnooptions, classes: 'pbool preset' }, 
                        { id: "animalsperpage", post_field: "animalsperpage", label: _("Animals per page"), type: "select", options: 
                            '<option value="5">5</option>' + 
                            '<option value="10" selected="selected">10</option>' + 
                            '<option value="15">15</option>' + 
                            '<option value="20">20</option>' + 
                            '<option value="50">50</option>' + 
                            '<option value="100">100</option>' + 
                            '<option value="999999">Unlimited (one page)</option>', 
                            classes: 'preset'
                        }, 
                        { id: "extension", post_field: "extension", label: _("Page extension"), type: "select", options: 
                            '<option value="html">html</option>' + 
                            '<option value="xml">xml</option>' + 
                            '<option value="cgi">cgi</option>' + 
                            '<option value="php">php</option>' + 
                            '<option value="py">py</option>' + 
                            '<option value="rb">rb</option>' + 
                            '<option value="jsp">jsp</option>' + 
                            '<option value="asp">asp</option>' + 
                            '<option value="aspx">aspx</option>', 
                            classes: 'preset'
                        }, 
                        { id: "template", post_field: "style", label: _("Publishing template"), type: "select", options: html.list_to_options(controller.styles), classes: 'preset' }, 
                        { id: "scale", post_field: "scaleimages", label: _("Scale published animal images to"), type: "select", options: 
                            '<option value="">' + _("Don't scale") + '</option>' + 
                            '<option value="300x300">300 px</option>' + 
                            '<option value="320x320">320 px</option>' + 
                            '<option value="400x400">400 px</option>' + 
                            '<option value="500x500">500 px</option>' + 
                            '<option value="600x600">600 px</option>' + 
                            '<option value="800x800">800 px</option>' + 
                            '<option value="1024x1024">1024 px</option>', 
                            classes: 'preset'
                        }, 
                        { id: "publishdir", post_field: "publishdirectory", label: _("Publish to folder"), type: "text", classes: 'preset' }, // To do - the original table row that this replaced had id="publishdirrow" make sure that this has been hooked up to the appropriate mechanism
                        { type: "nextcol"},
                        // To do - the following columns was originally contained in a table with id="ftpuploadtable" make sure that this has been hooked up to the appropriate mechanism
                        { id: "uploaddirectly", post_field: "uploaddirectly", label: _("Enable FTP uploading"), type: "select", options: yesnooptions, classes: 'pbool preset' }, 
                        { id: "ftphost", post_field: "FTPURL", label: _("FTP hostname"), type: "text" }, 
                        { id: "ftpuser", post_field: "FTPUser", label: _("FTP username"), type: "text" }, 
                        { id: "ftppass", post_field: "FTPPassword", label: _("FTP password"), type: "text" }, 
                        { id: "ftproot", post_field: "FTPRootDirectory", label: _("after connecting, chdir to"), type: "text" }, 
                        { id: "clearexisting", post_field: "clearexisting", label: _("Remove previously published files before uploading"), type: "select", options: yesnooptions, classes: 'pbool preset' }, 
                    ]}, 
                    { id: "tab-adoptapet", title: "AdoptAPet.com", classes: "localeus localeca localemx", info: 'Signup at <a target="_blank" href="http://www.adoptapet.com">www.adoptapet.com</a>.<br />' +
                    'Use the Shelter/Rescue menu after logging in to adoptapet to manage/setup your autoupload account for ASM', fields: [
                        { id: "enabledap", label: _("Enabled"), type: "check", classes: 'enablecheck' }, 
                        { id: "apftpuser", post_field: "SaveAPetFTPUser", label: 'Autoupload FTP username', type: "text" }, 
                        { id: "apftppass", post_field: "SaveAPetFTPPassword", label: 'Autoupload FTP password', type: "text" }, 
                        { id: "includecolours", post_field: "includecolours", label: 'Colors', type: "select", options:
                            '<option value="0">Do not send colors</option>' + 
                            '<option value="1">Send colors (not recommended, requires mapping)</option>', 
                            classes: 'pbool preset'
                        }, 
                        { id: "noimportfile", post_field: "noimportfile", label: 'import.cfg', type: "select", options:
                            '<option value="0">Auto-generate and upload</option>' + 
                            '<option value="1">Do not generate and upload (not recommended)</option>', 
                            classes: 'pbool preset'
                        }
                    ]}, 
                    { id: "tab-findpet", title: "FindPet.com", 
                        info: 'Find out more at <a target="_blank" href="https://findpet.com">www.findpet.com</a> ' +
                        'or contact hello@findpet.com for more information.<br>' +
                        'Sign up by filling out form <a target="_blank" href="https://forms.gle/EA4jbPZEK1UKWWdy8">https://forms.gle/EA4jbPZEK1UKWWdy8</a> ' +
                        'to get a Findpet Organization ID for:<br>' +
                        '<ul><li>automatic microchip registration</li>' +
                        '<li>automatic pet tag activation</li>' +
                        '<li>to report your pets as found to facilitate lost pet reunification</li></ul>', 
                        classes: 'localeus hasfindpet', fields: [
                            { id: "enabledmf", label: _("Enabled"), type: "check", classes: 'enablecheck' }, 
                            { id: "fporgid", post_field: "FindPetOrgID", label: "FindPet Organization ID", type: "text" }, 
                            { id: "fpintlevel", post_field: "FindPetIntLevel", label: "Integration Level", type: "select", options: 
                                '<option value="0">Send stray/found pets and register microchips</option>' + 
                                '<option value="1">Send stray/found pets only</option>'
                            }, 
                    ]}, 
                    { id: "tab-maddiesfund", title: "Maddie's Fund", info: 'Signup at <a target="_blank" href="http://www.maddiesfund.org/mpa.htm">http://www.maddiesfund.org/mpa.htm</a>', classes: 'english hasmaddiesfund', fields: [
                        { id: "enabledfip", label: _("Enabled"), type: "check", classes: 'enablecheck' }, 
                        { id: "mfemail", post_field: "MaddiesFundUsername", label: "MPA API Username", type: "text" }, 
                        { id: "mfpassword", post_field: "MaddiesFundPassword", label: "MPA API Password", type: "text" }
                    ]}, 
                    { id: "tab-petcademy", title: "Petcademy", info: 'Signup at <a target="_blank" href="https://petcademy.org/rescues-and-shelters/">https://petcademy.org/rescues-and-shelters/</a>', classes: 'english haspetcademy', fields: [
                        { id: "enabledpc", label: _("Enabled"), type: "check", classes: 'enablecheck' }, 
                        { id: "pctoken", post_field: "PetcademyToken", label: "MPA API Username", type: "text" }, 
                    ]}, 
                    { id: "tab-petfbi", title: "PetFBI.com", info: 'Signup at <a target="_blank" href="https://petfbi.org/info-for-shelters/sheltermanager/">https://petfbi.org/info-for-shelters/sheltermanager/</a>', fields: [
                        { id: "enabledfbi", label: _("Enabled"), type: "check", classes: 'enablecheck' }, 
                        { id: "fbiftpuser", post_field: "PetFBIFTPUser", label: 'PetFBI FTP username', type: "text" }, 
                        { id: "fbiftppass", post_field: "PetFBIFTPPassword", label: 'PetFBI FTP password', type: "text" }, 
                        { id: "fbiorgid", post_field: "PetFBIOrgID", label: 'PetFBI Organisation ID', type: "text" }, 
                    ]}, 
                    { id: "tab-petfinder", title: "PetFinder.com", info: 'Signup at <a target="_blank" href="http://www.petfinder.com/register/">www.petfinder.com/register/</a>', fields: [
                        { id: "enabledpf", label: _("Enabled"), type: "check", classes: 'enablecheck' }, 
                        { id: "pfftpuser", post_field: "PetFinderFTPUser", label: 'PetFinder shelter ID', type: "text" }, 
                        { id: "pfftppass", post_field: "PetFinderFTPPassword", label: 'PetFinder FTP password', type: "text" }, 
                        { id: "pfsendstrays", post_field: "PetFinderSendStrays", label: 'Stray shelter animals', type: "select", options:
                            '<option value="No">Do not send</option>' + 
                            '<option value="Yes">Send with status "F"</option>'
                        }, 
                        { id: "pfsendholds", post_field: "PetFinderSendHolds", label: 'Held shelter animals', type: "select", options:
                            '<option value="No">Do not send</option>' + 
                            '<option value="Yes">Send with status "H"</option>'
                        }, 
                        { id: "pfsendadopted", post_field: "PetFinderSendAdopted", label: 'Previously adopted animals', type: "select", options:
                            '<option value="No">Do not send</option>' + 
                            '<option value="Yes">Send with status "X"</option>'
                        }, 
                        { id: "pfsendadoptedphoto", post_field: "PetFinderSendAdoptedPhoto", label: 'Photo for adopted animals', type: "select", options:
                            '<option value="No">No photo</option>' + 
                            '<option value="Yes">Send the preferred photo</option>'
                        }, 
                        { type: "raw", markup: '<tr><td colspan="2">' + html.info('Make sure to notify the PetFinder helpdesk that you are using ASM to upload animals so that they can give you your FTP password.<br/>It is <b>not</b> the same as your password for the members area.') + '</td></tr>' }
                    ]},
                    { id: "tab-petslocated", title: "PetsLocated", info: 'Signup at <a target="_blank" href="http://www.petslocated.com">www.petslocated.com</a>', fields: [
                            { id: "enabledrg", label: _("Enabled"), type: "check", classes: 'enablecheck' }, 
                            { id: "pcukcustid", post_field: "PetsLocatedCustomerID", label: 'petslocated.com customer number', type: "text" }, 
                            { id: "pcukincludeshelter", post_field: "PetsLocatedIncludeShelter", label: 'Include shelter animals', type: "select", options: yesnooptions }, 
                            { id: "pcukanimalflag", post_field: "PetsLocatedAnimalFlag", label: 'Only shelter animals with this flag', type: "select", options: html.list_to_options(controller.flags, "FLAG", "FLAG") }
                    ]}, 
                    { id: "tab-petrescue", title: "PetRescue.com.au", classes: 'localeau haspetrescue', info: 'Signup at <a target="_blank" href="http://petrescue.com.au">petrescue.com.au</a>', fields: [
                        { id: "enabledpr", label: _("Enabled"), type: "check", classes: 'enablecheck' }, 
                        { id: "prtoken", post_field: "PetRescueToken", label: 'PetRescue Token', type: "text", doublesize: true }, 
                        { id: "prdesex", post_field: "PetRescueAllDesexed", label: 'Send all animals as desexed', type: "select", options: yesnooptions, callout: 'PetRescue will not accept listings for non-desexed animals. Setting this to "Yes" will send all animals as if they are desexed.' }, 
                        { id: "breederid", post_field: "PetRescueBreederID", label: 'Breeder ID', type: "text", callout: 'Your organisation breeder number if applicable. Mandatory for dog listings in QLD. Mandatory for dog listings in South Australia where "bredincareofgroup" is selected.' }, 
                        { id: "nswrehomingorgid", post_field: "PetRescueNSWRehomingOrgID", label: 'NSW Rehoming Organisation ID', type: "text", callout: 'For cats and dogs being rehomed in NSW, a rehoming organisation ID is required OR microchip number OR breeder id' }, 
                        { id: "vicpicnumber", post_field: "PetRescueVICPICNumber", label: 'VIC PIC Number', type: "text", callout: 'Property Identification Code for livestock listings in Victoria' }, 
                        { id: "vicsourcenumber", post_field: "PetRescueVICSourceNumber", label: 'VIC Source Number', type: "text", callout: 'Source Number for the Victoria Pet Exchange Register. Mandatory for cat and dog listings in VIC.' }, 
                        { id: "pradoptablein", post_field: "PetRescueAdoptableIn", label: 'Adoptable in states', type: "selectmulti", 
                            options: '<option value="ACT">Australian Capital Territory</option>' + 
                            '<option value="NSW">New South Wales</option>' + 
                            '<option value="NT">Northern Territory</option>' + 
                            '<option value="QLD">Queensland</option>' + 
                            '<option value="SA">South Australia</option>' + 
                            '<option value="TAS">Tasmania</option>' + 
                            '<option value="VIC">Victoria</option>' + 
                            '<option value="WA">Western Australia</option>', 
                            callout: 'Choose the states your animals will be adoptable in. The state the animal is currently located in will be implicitly included.' 
                        }, 
                        { id: "premail", post_field: "PetRescueEmail", label: 'Contact email', type: "text", 
                            callout: 'This is the contact email for PetRescue listings. If you do not set it, the option from Settings &#8594; Options &#8594; Email is used.' 
                        }, 
                        { id: "prphone", post_field: "PetRescuePhoneType", label: 'Contact phone', type: "select", 
                            options: '<option value="org">Use organisation number</option>' + 
                            '<option value="spec">Specify a number &#8594;</option>' + 
                            '<option value="none">Do not send a number</option>', 
                            callout: 'This controls the phone number included as a secondary contact with your listings', 
                            xmarkup: ' <input type="text" class="asm-textbox cfg" title="The phone number to use" data="PetRescuePhoneNumber" />'
                        }, 
                        { id: "usecoord", post_field: "PetRescueUseCoordinator", label: 'Use adoption coordinator as contact', type: "select", 
                            options: '<option value="0">No</option>' + 
                            '<option value="1">Use coordinator\'s phone number and email address</option>' + 
                            '<option value="2">Use coordinator\'s email address only</option>', 
                            callout: 'Use the adoption coordinator\'s contact information instead of the options above if the animal has an adoption coordinator assigned.' ,
                            doublesize: true
                        }
                    ]}, 

                    { id: "tab-savourlife", title: "SavourLife.com.au", classes: 'localeau hassavourlife', info: 'Signup at <a target="_blank" href="http://savourlife.com.au">savour-life.com.au</a>', fields: [
                        { id: "enabledsl", label: _("Enabled"), type: "check", classes: 'enablecheck' }, 
                        { id: "sltoken", post_field: "SavourLifeToken", label: 'Authentication Token', type: "text" }, 
                        { id: "slinterstate", post_field: "SavourLifeInterstate", label: 'Mark as interstate', type: "select", callout: 'Set to yes if you will fly adoptable animals to other states', 
                            options: yesnooptions
                        }, 
                        { id: "slradius", post_field: "SavourLifeRadius", label: 'Distance restriction', type: "select",
                            options: '<option value="0">No restriction</option>' + 
                            '<option value="20">20 km</option>' + 
                            '<option value="40">40 km</option>' + 
                            '<option value="60">60 km</option>' + 
                            '<option value="100">100 km</option>' + 
                            '<option value="200">200 km</option>' + 
                            '<option value="500">500 km</option>'
                        }, 
                        { id: "slmicrochips", post_field: "SavourLifeAllMicrochips", label: 'Send microchip numbers for all animals', type: "select", options: yesnooptions, callout: 'By default we only send microchip numbers for animals listed in a VIC or NSW postcode. Settings this to "Yes" will send the microchip number for all animals'
                        }, 
                    ]}, 
                    { id: "tab-rescuegroups", title: "RescueGroups.org", info: 'RescueGroups offer a service called Pet Adoption Portal that allows you to upload adoptable animals ' +
                    'to them for republishing on to many other sites. Find out more at ' +
                    '<a target="_blank" href="http://www.rescuegroups.org/services/pet-adoption-portal/">www.rescuegroups.org</a>', fields: [
                        { id: "enabledrg", label: _("Enabled"), type: "check", classes: 'enablecheck' }, 
                        { id: "rgftpuser", post_field: "RescueGroupsFTPUser", label: 'RescueGroups FTP username', type: "text" }, 
                        { id: "rgftppass", post_field: "RescueGroupsFTPPassword", label: 'RescueGroups FTP password', type: "text" }
                    ]}, 
                    { id: "tab-sac", title: "ShelterAnimalsCount.org", classes: 'localeus localeca hassac', 
                        info: 'Signup at <a target="_blank" href="http://shelteranimalscount.org">shelteranimalscount.org</a><br>' + 
                        'You will need to give SAC your account number of "' + asm.useraccount + '" in order for them to accept uploads from you.', 
                        fields: [
                            { id: "enabledsac", label: _("Enabled"), type: "check", classes: 'enablecheck' }
                        ]
                    }, 
                    { id: "tab-pettrac", title: "AVID UK Microchips", classes: 'localeus', 
                        info: 'These settings are for registering microchips with new owner information to the AVID PETtrac UK database. <br/>' + 
                        'Find out more at <a target="_blank" href="http://www.pettrac.co.uk">www.pettrac.co.uk</a>', 
                        fields: [
                            { id: "enabledptuk", label: _("Enabled"), type: "check", classes: 'enablecheck' }, 
                            { id: "avidorgname", post_field: "AvidOrgName", label: "Organisation Name", type: "text", doublesize: true }, 
                            { id: "avidorgserial", post_field: "AvidOrgSerial", label: "Serial Number", type: "text", doublesize: true }, 
                            { id: "avidorgpostcode", post_field: "AvidOrgPostcode", label: "Postcode", type: "text", doublesize: true }, 
                            { id: "avidorgpassword", post_field: "AvidOrgPassword", label: "Password", type: "text", doublesize: true }, 
                            { id: "avidrereg", post_field: "AvidReRegistration", label: "Re-register previously registered microchips", type: "select", options: yesnooptions }, 
                            { id: "avidauthuser", post_field: "AvidAuthUser", label: "Password", type: "select", options: html.list_to_options(controller.users, "USERNAME", "USERNAME"), 
                                callout: "An authorised user must be chosen and they must have an electronic signature on file.<br/>" + 
                                "Their details will be used on an authorisation document transmitted to AVID when " +
                                "re-registering previously registered microchips.<br/>Please also make sure the authorised " +
                                "user has a real name on file."

                            }
                        ]
                    }, 
                    { id: "tab-anibase", title: "Identibase UK Microchips", classes: 'localegb', 
                        info: 'These settings are for uploading new owner information to the Identibase/Anibase UK microchip database. <br/>' + 
                        'Find out more at <a target="_blank" href="http://www.animalcare.co.uk">www.animalcare.co.uk</a>', 
                        fields: [
                            { id: "enabledabuk", label: _("Enabled"), type: "check", classes: 'enablecheck' }, 
                            { id: "anibasepinno", post_field: "AnibasePinNo", label: "Vet Code", type: "text", doublesize: true }
                        ]
                    }, 
                    { id: "tab-mypet", title: "MyPet UK Microchips", classes: 'localegb',
                        info: 'These settings are for uploading new owner information to the MyPet UK microchip database. <br/>' + 
                        'Find out more at <a target="_blank" href="http://www.mypethq.io">www.mypethq.io</a>', 
                        fields: [
                            { id: "enabledmpuk", label: _("Enabled"), type: "check", classes: 'enablecheck' }, 
                            { id: "mypetpracticeid", post_field: "AnibaseMyPetUKPracticeIDPinNo", label: "Practice ID", type: "text", doublesize: true }
                        ]
                    }, 
                    { id: "tab-akcreunite", title: "AKC Reunite Microchips", classes: 'localeus hasakcreunite',
                        info: 'Learn about AKC Reunite microchips and auto-uploading pet enrollment information at ' +
                        '<a target="_blank" href="https://www.akcreunite.org/shelters">https://www.akcreunite.org/shelters</a>.<br/>' +
                        'Request auto-uploads of pet microchip information to AKC Reunite at ' +
                        '<a target="_blank" href="https://www.akcreunite.org/auto-upload/">https://www.akcreunite.org/auto-upload</a>.', 
                        fields: [
                            { id: "enabledak", label: _("Enabled"), type: "check", classes: 'enablecheck' }, 
                            { type: "raw", markup: '<tr><td colspan="2"><button id="button-akenroll">Generate an Enrollment Source Id for AKC Reunite</button></td></tr>' }, // To do - check that this button is doing what it should
                            { id: "akenrollmentid", post_field: "AKCEnrollmentSourceID", label: "AKC Reunite Enrollment Source ID", type: "text", doublesize: true }, 
                            { id: "akregisterall", post_field: "AKCRegisterAll", label: "Register", type: "select", 
                                options: '<option value="No">Only AKC Microchips</option>' + 
                                '<option value="Yes">All Microchips</option>'
                            }
                        ]
                    }, 
                    { id: "tab-buddyid", title: "BuddyID Microchips", classes: 'localeus hasbuddyid',
                        info: 'Find out more at ' + 
                        '<a target="_blank" href="https://buddyid.com/pet-microchips-and-registration/">https://buddyid.com/pet-microchips-and-registration/</a>', 
                        fields: [
                            { id: "enabledbd", label: _("Enabled"), type: "check", classes: 'enablecheck' }, 
                            { id: "bdprovidercode", post_field: "BuddyIDProviderCode", label: "BuddyID Provider Code", type: "text", doublesize: true }
                        ]
                    }, 
                    { id: "tab-foundanimals", title: "Found/24Pet Microchips", classes: 'localeus localeca hasfoundanimals',
                        info: 'Find out more at <a target="_blank" href="http://www.my24pet.com">www.my24pet.com</a><br/>' +
                        'Contact clientcare@pethealthinc.com to get a folder for automatic batch registrations of microchips.', 
                        fields: [
                            { id: "enabledfa", label: _("Enabled"), type: "check", classes: 'enablecheck' }, 
                            { id: "fafolder", post_field: "FoundAnimalsFolder", label: "Folder name", type: "text", doublesize: true }, 
                            { id: "faemail", post_field: "FoundAnimalsEmail", label: "Rescue group email", type: "text", doublesize: true, 
                                callout: 'To stay on record for every pet you register as the permanent rescue contact, enter your group\'s registry ' + 
                                'account email in this field.'
                            }
                        ]
                    }, 
                    { id: "tab-homeagain", title: "HomeAgain Microchips", classes: 'localeus hashomeagain',
                        info: 'Signup at <a target="_blank" href="http://homeagain.4act.com">http://homeagain.4act.com</a> or contact HomeAgain Customer Service on <a target="_blank" href="tel:1-800-341-5785">(800) 341-5785</a> for more information.', 
                        fields: [
                            { id: "enabledha", label: _("Enabled"), type: "check", classes: 'enablecheck' }, 
                            { id: "hauserid", post_field: "HomeAgainUserId", label: "HomeAgain User ID", type: "text", doublesize: true }, 
                            { id: "hauserpassword", post_field: "HomeAgainUserPassword", label: "HomeAgain User Password", type: "text", doublesize: true }
                        ]
                    }, 
                    { id: "tab-petlink", title: "PetLink Microchips", classes: 'localeus localeca localemx haspetlink',
                        info: 'These settings are for uploading new owner information to the PetLink/DataMARS microchip database.<br />' +
                        'Find out more at <a target="_blank" href="http://www.petlink.net/us/">www.petlink.net</a>', 
                        fields: [
                            { id: "enabledpl", label: _("Enabled"), type: "check", classes: 'enablecheck' }, 
                            { id: "plemail", post_field: "PetLinkEmail", label: "Professional/Vet Account Email", type: "text", 
                                callout: 'This is the email address you use to log into the PetLink site as a professional/vet'
                            }, 
                            { id: "plpass", post_field: "PetLinkPassword", label: "Password", type: "text" }, 
                            { id: "plowneremail", post_field: "PetLinkOwnerEmail", label: "Owner Account Email (Optional)", type: "text", 
                                callout: 'If you are registering animals to the shelter on intake, ' + 
                                'this is the email address of the PetLink owner account to register shelter animals to.'
                            }, 
                            { id: "plregisterall", post_field: "PetLinkRegisterAll", label: "Register", type: "select", 
                                options: '<option value="No">PetLink pre-paid microchips (98102*)</option>' + 
                                '<option value="Yes">ALL microchips (*)</option>'
                            }
                        ]
                    }, 
                    { id: "tab-smarttag", title: "SmartTag Tags/Microchips", classes: 'localeus hassmarttag',
                        info: 'Find out more at <a target="_blank" href="http://www.idtag.com">www.idtag.com</a><br/>' +
                        'Contact SmartTag to get your account ID for automatic registration of chips and tags ' +
                        '212-868-2559 x136 (Mike Cotti) or email mikec@idtag.com', 
                        fields: [
                            { id: "enabledst", label: _("Enabled"), type: "check", classes: 'enablecheck' }, 
                            { id: "stuser", post_field: "SmartTagFTPUser", label: "SmartTag Account ID", type: "text" }
                        ]
                    }, 
                    { id: "tab-vetenvoy", title: "VetEnvoy Microchips", classes: 'localeus hasvetenvoy',
                        info: 'VetEnvoy allow ASM to automatically register microchips provided by HomeAgain and AKC Reunite<br />' +
                        'Find out more at <a target=_"blank" href="http://www.vetenvoy.com">www.vetenvoy.com</a>, ' +
                        '<a target="_blank" href="http://www.homeagain.com">www.homeagain.com</a> and ' +
                        '<a target="_blank" href="http://www.akcreunite.org">www.akcreunite.org</a>', 
                        fields: [
                            { type: "raw", markup: '<tr><td colspan="2"><button id="button-vesignup">Signup for VetEnvoy</button></td></tr>' }, // To do - check that this button is doing what it should
                            { id: "enabledve", label: _("Enabled"), type: "check", classes: 'enablecheck' }, 
                            { id: "veuserid", post_field: "VetEnvoyUserId", label: "VetEnvoy User ID", type: "text", doublesize: true }, 
                            { id: "veuserpassword", post_field: "VetEnvoyUserPassword", label: "VetEnvoy User Password", type: "text", doublesize: true }, 
                            { id: "vehomeagain", post_field: "VetEnvoyHomeAgainEnabled", label: "Register HomeAgain Microchips", type: "select", options: yesnooptions }, // To do - the original widget had no ids for the options and the options were not in the same order as other yesno selects, check that this is plumbed in correctly
                            { id: "veakc", post_field: "VetEnvoyAKCReuniteEnabled", label: "Register AKC Reunite Microchips", type: "select", options: yesnooptions }, // To do - the original widget had no ids for the options and the options were not in the same order as other yesno selects, check that this is plumbed in correctly
                        ]
                    }
                ], {full_width: false}),
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
                        $(this).closest("div").find("button").show();
                        $(this).closest("div").find(".asm-textbox, .asm-doubletextbox").removeAttr("disabled");
                        $(this).closest("div").find("textarea").removeAttr("disabled");
                    }
                    else {
                        $(this).closest("div").find("select").select("disable");
                        $(this).closest("div").find("button").hide();
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
                        if ($(this).val() == "1") { pr += " " + $(this).attr("data-post"); }
                    }
                    else {
                        pr += " " + $(this).attr("data-post") + "=" + $(this).val();
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
                let formdata = "mode=save&" + $("input, select, textarea, .asm-richtextarea").not(".chooser").toPOST(true);
                formdata += "&PublisherPresets=" + cfg_presets();
                formdata += "&PublishersEnabled=" + cfg_enabled();
                header.show_loading(_("Saving..."));
                await common.ajax_post("publish_options", formdata);
                // Needs to do a full reload to get config.js to update
                common.route_reload(true); 
            });

            $("#button-save").button("disable");
            /*
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
            if (!controller.hasbuddyid) { $(".hasbuddyid").hide(); }
            if (!controller.hasfindpet) { $(".hasfindpet").hide(); }
            if (!controller.hasfoundanimals) { $(".hasfoundanimals").hide(); }
            if (!controller.hashtmlftp) { $(".hashtmlftp").hide(); }
            if (!controller.hashomeagain) { $(".hashomeagain").hide(); }
            if (!controller.hasmaddiesfund) { $(".hasmaddiesfund").hide(); }
            if (!controller.haspetcademy) { $(".haspetcademy").hide(); }
            if (!controller.haspetlink) { $(".haspetlink").hide(); }
            if (!controller.haspetrescue) { $(".haspetrescue").hide(); }
            if (!controller.haspetslocated) { $(".haspetslocated").hide(); }
            if (!controller.hassac) { $(".hassac").hide(); }
            if (!controller.hassavourlife) { $(".hassavourlife").hide(); }
            if (!controller.hasvetenvoy) { $(".hasvetenvoy").hide(); }
            if (!controller.hassmarttag) { $(".hassmarttag").hide(); }
            */
            // Load default values from the config settings
            $("input, select, textarea, .asm-richtextarea").not(".chooser").each(function() {
                if ($(this).attr("data-post")) {
                    let d = $(this).attr("data-post");
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
                    "includewithoutdescription", "includewithoutimage", "includenonneutered", "includenonmicrochip", 
                    "includecolours", "includeretailer", "includehold", "includequarantine", "includetrial",
                    "bondedassingle", "clearexisting", "uploadall", "forcereupload", 
                    "generatejavascriptdb","thumbnails", "checksocket", "uploaddirectly", 
                    "htmlbychildadult", "htmlbyspecies", "htmlbytype", "outputadopted", 
                    "outputdeceased", "outputrss", "noimportfile" ], 
                function(bi, bo) {
                    if (bo == o) { $("[data='" + bo + "']").select("value", "1"); }
                });
                // Deal with key/value pairs
                $.each( [ "order", "excludeunder", "excludereserves", "animalsperpage", "limit", "style", "extension",
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

