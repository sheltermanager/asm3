/*global $, jQuery, _, asm, common, config, controller, dlgfx, format, header, html, validate */
/*global MASK_VALUE */

$(function() {

    "use strict";

    const options = {

        /** Where we have a list of pairs, first is value, second is label */
        two_pair_options: function(o, isflag) {
            let s = [];
            $.each(o, function(i, v) {
                let ds = "";
                if (isflag) {
                    ds = 'data-style="background-image: url(static/images/flags/' + v[0] + '.png)"';
                }
                s.push('<option value="' + v[0] + '" ' + ds + '>' + v[1] + '</option>');
            });
            return s.join("\n");
        },

        /** Sorts a list of pairs by the second element in each list */
        pair_sort_second: function(l) {
            return l.sort(function(a, b) {
                if (a[1] < b[1]) return -1;
                if (a[1] > b[1]) return 1;
                return 0;
            });
        },

        /** Reorders the list l and moves the selected items in configitem to the front */
        pair_selected_to_front: function(l, configitem) {
            let ci = configitem.split(",").reverse();
            $.each(ci, function(i, v) {
                v = String(v).trim();
                $.each(l, function(iv, vl) {
                    if (vl[0] == v) {
                        l.splice(iv, 1); // Remove matching element from the list
                        l.splice(0, 0, [ vl[0], vl[1] ]); // Reinsert it at the front
                        return false; // Break the loop
                    }
                });
            });
            return l;
        },

        /** Renders the list of quicklink options */
        quicklink_options: function() {
            let ql = [];
            $.each(header.QUICKLINKS_SET, function(k, v) {
                ql.push([ k, v[2] ]);
            });
            ql = this.pair_sort_second(ql);
            ql = this.pair_selected_to_front(ql, config.str("QuicklinksID"));
            return this.two_pair_options(ql);
        },

        watermark_colors: [
            "aliceblue", "antiquewhite", "aqua", "aquamarine", "azure", "beige", "bisque", "black", "blanchedalmond", "blue",
            "blueviolet", "brown", "burlywood", "cadetblue", "chartreuse", "chocolate", "coral", "cornflowerblue", "cornsilk",
            "crimson", "cyan", "darkblue", "darkcyan", "darkgoldenrod", "darkgray", "darkgrey", "darkgreen", "darkkhaki",
            "darkmagenta", "darkolivegreen", "darkorange", "darkorchid", "darkred", "darksalmon", "darkseagreen", "darkslateblue",
            "darkslategray", "darkslategrey", "darkturquoise", "darkviolet", "deeppink", "deepskyblue", "dimgray", "dimgrey",
            "dodgerblue", "firebrick", "floralwhite", "forestgreen", "fuchsia", "gainsboro", "ghostwhite", "gold", "goldenrod",
            "gray", "grey", "green", "greenyellow", "honeydew", "hotpink", "indianred", "indigo", "ivory", "khaki", "lavender",
            "lavenderblush", "lawngreen", "lemonchiffon", "lightblue", "lightcoral", "lightcyan", "lightgoldenrodyellow",
            "lightgray", "lightgrey", "lightgreen", "lightpink", "lightsalmon", "lightseagreen", "lightskyblue", "lightslategray",
            "lightslategrey", "lightsteelblue", "lightyellow", "lime", "limegreen", "linen", "magenta", "maroon",
            "mediumaquamarine", "mediumblue", "mediumorchid", "mediumpurple", "mediumseagreen", "mediumslateblue",
            "mediumspringgreen", "mediumturquoise", "mediumvioletred", "midnightblue", "mintcream", "mistyrose", "moccasin",
            "navajowhite", "navy", "oldlace", "olive", "olivedrab", "orange", "orangered", "orchid", "palegoldenrod",
            "palegreen", "paleturquoise", "palevioletred", "papayawhip", "peachpuff", "peru", "pink", "plum", "powderblue",
            "purple", "rebeccapurple", "red", "rosybrown", "royalblue", "saddlebrown", "salmon", "sandybrown", "seagreen",
            "seashell", "sienna", "silver", "skyblue", "slateblue", "slategray", "slategrey", "snow", "springgreen", "steelblue",
            "tan", "teal", "thistle", "tomato", "turquoise", "violet", "wheat", "white", "whitesmoke", "yellow", "yellowgreen",
        ],

        render_tabs: function() {
            return [
                '<ul>',
                '<li><a href="#tab-shelterdetails">' + _("Shelter Details") + '</a></li>',
                '<li><a href="#tab-accounts">' + _("Accounts") + '</a></li>',
                '<li><a href="#tab-adding">' + _("Add Animal") + '</a></li>',
                '<li><a href="#tab-agegroups">' + _("Age Groups") + '</a></li>',
                '<li><a href="#tab-animalcodes">' + _("Animal Codes") + '</a></li>',
                '<li><a href="#tab-animalemblems">' + _("Animal Emblems") + '</a></li>',
                '<li><a href="#tab-boarding">' + _("Boarding") + '</a></li>',
                '<li><a href="#tab-checkout">' + _("Checkout") + '</a></li>',
                '<li><a href="#tab-costs">' + _("Costs") + '</a></li>',
                '<li><a href="#tab-daily-observations">' + _("Daily Observations") + '</a></li>',
                '<li><a href="#tab-data-protection">' + _("Data Protection") + '</a></li>',
                '<li><a href="#tab-defaults">' + _("Defaults") + '</a></li>',
                '<li><a href="#tab-diaryandmessages">' + _("Diary and Messages") + '</a></li>',
                '<li><a href="#tab-display">' + _("Display") + '</a></li>',
                '<li><a href="#tab-documents">' + _("Documents") + '</a></li>',
                '<li><a href="#tab-email">' + _("Email") + '</a></li>',
                '<li><a href="#tab-findscreens">' + _("Find Screens") + '</a></li>',
                '<li><a href="#tab-homepage">' + _("Home page") + '</a></li>',
                '<li><a href="#tab-insurance">' + _("Insurance") + '</a></li>',
                '<li><a href="#tab-lostandfound">' + _("Lost and Found") + '</a></li>',
                '<li><a href="#tab-medical">' + _("Medical") + '</a></li>',
                '<li><a href="#tab-movements">' + _("Movements") + '</a></li>',
                '<li><a href="#tab-onlineforms">' + _("Online Forms") + '</a></li>',
                '<li><a href="#tab-processors">' + _("Payment Processors") + '</a></li>',
                '<li><a href="#tab-quicklinks">' + _("Quicklinks") + '</a></li>',
                '<li><a href="#tab-reminders">' + _("Reminder Emails") + '</a></li>',
                '<li><a href="#tab-unwanted">' + _("Remove") + '</a></li>',
                '<li><a href="#tab-reports">' + _("Reports") + '</a></li>',
                '<li><a href="#tab-search">' + _("Search") + '</a></li>',
                '<li><a href="#tab-security">' + _("Security") + '</a></li>',
                '<li><a href="#tab-shelterview">' + _("Shelter view") + '</a></li>',
                '<li><a href="#tab-waitinglist">' + _("Waiting List") + '</a></li>',
                '<li><a href="#tab-watermark">' + _("Watermark") + '</a></li>',
                '</ul>'
            ].join("\n");
        },

        render_shelterdetails: function() {
            return [
                '<div id="tab-shelterdetails">',
                '<table>',
                '<tr>',
                '<td><label for="organisation">' + _("Organization") + '</label></td>',
                '<td><input id="organisation" type="text" class="asm-doubletextbox" data="Organisation" />',
                '</tr>',
                '<tr>',
                '<td><label for="address">' + _("Address") + '</label></td>',
                '<td><textarea id="address" rows="3" class="asm-textareafixeddouble" data="OrganisationAddress"></textarea>',
                '</tr>',
                '<tr>',
                '<td><label for="city">' + _("City") + '</label></td>',
                '<td><input id="city" type="text" class="asm-textbox" data="OrganisationTown" />',
                '</tr>',
                '<tr>',
                '<td><label for="state">' + _("State") + '</label></td>',
                '<td>',
                common.iif(config.bool("USStateCodes"),
                    '<select id="state" data="OrganisationCounty" class="asm-selectbox">' +
                    html.states_us_options() + '</select>',
                    '<input type="text" id="state" data="OrganisationCounty" maxlength="100" ' + 
                    'class="asm-textbox" />'),
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="zipcode">' + _("Zipcode") + '</label></td>',
                '<td><input id="zipcode" type="text" class="asm-textbox" data="OrganisationPostcode" />',
                '</tr>',
                '<tr>',
                '<td><label for="country">' + _("Country") + '</label></td>',
                '<td><input id="country" type="text" class="asm-textbox" data="OrganisationCountry" />',
                '</tr>',
                '<tr>',
                '<td><label for="telephone">' + _("Telephone") + '</label></td>',
                '<td><input id="telephone" type="text" class="asm-textbox asm-phone" data="OrganisationTelephone" />',
                '</tr>',
                '<tr>',
                '<td><label for="telephone2">' + _("Telephone") + '</label></td>',
                '<td><input id="telephone2" type="text" class="asm-textbox asm-phone" data="OrganisationTelephone2" />',
                '</tr>',
                '<tr>',
                '<td><label for="timezone">' + _("Server clock adjustment") + '</label></td>',
                '<td><select id="timezone" type="text" class="asm-selectbox" data="Timezone">',
                '<option value="-12">-12:00</option>',
                '<option value="-11">-11:00</option>',
                '<option value="-10">-10:00</option>',
                '<option value="-9.5">-09:30</option>',
                '<option value="-9">-09:00</option>',
                '<option value="-8">-08:00 (USA PST)</option>',
                '<option value="-7">-07:00 (USA MST)</option>',
                '<option value="-6">-06:00 (USA CST)</option>',
                '<option value="-5">-05:00 (USA EST)</option>',
                '<option value="-4">-04:00</option>',
                '<option value="-3.5">-03:30</option>',
                '<option value="-3">-03:00</option>',
                '<option value="-2.5">-02:30</option>',
                '<option value="-2">-02:00</option>',
                '<option value="-1">-01:00</option>',
                '<option value="0">' + _("No adjustment") + ' (GMT/UTC)</option>',
                '<option value="1">+01:00 (CET)</option>',
                '<option value="2">+02:00 (EET)</option>',
                '<option value="3">+03:00 (FET)</option>',
                '<option value="3.5">+03:30</option>',
                '<option value="4">+04:00</option>',
                '<option value="4.5">+04:30</option>',
                '<option value="5">+05:00</option>',
                '<option value="5.5">+05:30 (IST)</option>',
                '<option value="5.75">+05:45</option>',
                '<option value="6">+06:00</option>',
                '<option value="6.5">+06:30</option>',
                '<option value="7">+07:00</option>',
                '<option value="8">+08:00 (AWST)</option>',
                '<option value="8.5">+08:30</option>',
                '<option value="8.75">+08:45</option>',
                '<option value="9">+09:00 (JST)</option>',
                '<option value="9.5">+09:30 (ACT)</option>',
                '<option value="10">+10:00 (AET)</option>',
                '<option value="10.5">+10:30</option>',
                '<option value="11">+11:00</option>',
                '<option value="12">+12:00</option>',
                '<option value="12.75">+12:45</option>',
                '<option value="13">+13:00</option>',
                '<option value="13.75">+13:45</option>',
                '<option value="14">+14:00</option>',
                '</select>',
                '<input data="TimezoneDST" id="timezonedst" class="asm-checkbox" type="checkbox" />',
                '<label for="timezonedst">' + _("auto adjust for daylight savings") + '</label>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="olocale">' + _("Locale") + '</label>',
                '<span id="callout-olocale" class="asm-callout">' + _("The locale determines the language ASM will use when displaying text, dates and currencies.") + '</span>',
                '</td>',
                '<td><select id="olocale" type="text" class="asm-doubleselectbox asm-iconselectmenu" data="Locale">',
                this.two_pair_options(controller.locales, true),
                '</select>',
                '</td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_accounts: function() {
            const donmap = function(idx) {
                return [
                    '<tr>',
                    '<td><label for="mapdt' + idx + '">' + _("Payments of type") + '</td>',
                    '<td><select id="mapdt' + idx + '" data-idx="' + idx + '" class="asm-selectbox donmap">',
                    '<option value="-1">' + _("[None]") + '</option>',
                    html.list_to_options(controller.donationtypes, "ID", "DONATIONNAME"),
                    '</select>',
                    '</td>',
                    '<td>' + _("are sent to") + '</td>',
                    '<td><select id="mapac' + idx + '" class="asm-selectbox">',
                    '<option value="-1">' + _("[None]") + '</option>',
                    html.list_to_options(controller.accounts, "ID", "CODE"),
                    '</select>',
                    '</td>',
                    '</tr>'
                ].join("\n");
            };
            return [
                '<div id="tab-accounts">',
                '<p><input data="rc:DisableAccounts" id="disableaccounts" type="checkbox" class="asm-checkbox" />',
                '<label for="disableaccounts">' + _("Enable accounts functionality") + '</label>',
                '<br />',
                '<input data="CreateDonationTrx" id="createdonations" type="checkbox" class="asm-checkbox" />',
                '<label for="createdonations">' + _("Creating payments and payments types creates matching accounts and transactions") + '</label>',
                '<br />',
                '<input data="CreateCostTrx" id="createcost" type="checkbox" class="asm-checkbox" />',
                '<label for="createcost">' + _("Creating cost and cost types creates matching accounts and transactions") + '</label>',
                '<br />',
                '<input data="DonationTrxOverride" id="donationtrxoverride" type="checkbox" class="asm-checkbox" />',
                '<label for="donationtrxoverride">' + _("When receiving payments, allow the deposit account to be overridden") + '</label>',
                '<br />',
                '<input data="DonationQuantities" id="donationquantities" type="checkbox" class="asm-checkbox" />',
                '<label for="donationquantities">' + _("When receiving payments, allow a quantity and unit price to be set") + '</label>',
                '<br />',
                '<input data="DonationFees" id="donationfees" type="checkbox" class="asm-checkbox" />',
                '<label for="donationfees">' + _("When receiving payments, allow a transaction fee to be set") + '</label>',
                '<br />',
                '<input data="VATEnabled" id="vatenabled" type="checkbox" class="asm-checkbox" />',
                '<label for="vatenabled">' + _("When receiving payments, allow recording of sales tax with a default rate of") + '</label>',
                '<input data="VATRate" data-min="0" data-max="100" class="asm-textbox asm-halftextbox asm-numberbox" type="text" />%',
                '<br />',
                '<input data="VATExclusive" id="vatexclusive" type="checkbox" class="asm-checkbox" />',
                '<label for="vatexclusive">' + _("When calculating sales tax, assume the payment amount is net and add it") + '</label>',
                '<br />',
                '<input data="DonationDateOverride" id="donationdateoverride" type="checkbox" class="asm-checkbox" />',
                '<label for="donationdateoverride">' + _("When receiving multiple payments, allow the due and received dates to be set") + '</label>',
                '<br />',
                '<input data="AccountPeriodTotals" id="accountperiodtotals" type="checkbox" class="asm-checkbox" />',
                '<label for="accountperiodtotals">' + _("Only show account totals for the current period, which starts on ") + '</label>',
                '<input data="AccountingPeriod" id="accountingperiod" class="asm-datebox asm-textbox" />',
                '</p>',
                '<table>',
                '<td><label for="defaulttrxview">' + _("Default transaction view") + '</td>',
                '<td><select data="DefaultAccountViewPeriod" id="defaulttrxview" class="asm-selectbox">',
                '<option value="0">' + _("This Month") + '</option>',
                '<option value="1">' + _("This Week") + '</option>',
                '<option value="2">' + _("This Year") + '</option>',
                '<option value="3">' + _("Last Month") + '</option>',
                '<option value="4">' + _("Last Week") + '</option>',
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="csourceaccount">' + _("Default source account for costs") + '</td>',
                '<td><select data="CostSourceAccount" id="csourceaccount" class="asm-selectbox">',
                html.list_to_options(controller.accounts, "ID", "CODE"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="destinationaccount">' + _("Default destination account for payments") + '</td>',
                '<td><select data="DonationTargetAccount" id="destinationaccount" class="asm-selectbox">',
                html.list_to_options(controller.accounts, "ID", "CODE"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="vataccount">' + _("Income account for sales tax") + '</td>',
                '<td><select data="DonationVATAccount" id="vataccount" class="asm-selectbox">',
                html.list_to_options(controller.accountsinc, "ID", "CODE"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="feeaccount">' + _("Expense account for transaction fees") + '</td>',
                '<td><select data="DonationFeeAccount" id="feeaccount" class="asm-selectbox">',
                html.list_to_options(controller.accountsexp, "ID", "CODE"),
                '</select>',
                '</td>',
                '</tr>',
                donmap(1),
                donmap(2),
                donmap(3),
                donmap(4),
                donmap(5),
                donmap(6),
                donmap(7),
                donmap(8),
                donmap(9),
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_adding: function() {
            return [
                '<div id="tab-adding">',
                '<p>',
                '<input data="AddAnimalsShowBreed" id="aashowbreed" class="asm-checkbox" type="checkbox" /> <label for="aashowbreed">' + _("Show the breed fields") + '</label><br />',
                '<input data="UseSingleBreedField" id="singlebreed" class="asm-checkbox" type="checkbox" /> <label for="singlebreed">' + _("Use a single breed field") + '</label>',
                '</p>',
                '<div style="margin-left: 25px;"><span>' + _("OR only show the second breed field for these species of animals") + ':</span> ',
                '<select id="crossbreedspecies" multiple="multiple" class="asm-bsmselect" data="CrossbreedSpecies">',
                html.list_to_options(controller.species, "ID", "SPECIESNAME"),
                '</select>',
                '</div>',
                '<p>',
                '<input data="AddAnimalsShowCoatType" id="aashowcoattype" class="asm-checkbox" type="checkbox" /> <label for="aashowcoattype">' + _("Show the coat type field") + '</label><br />',
                '<input data="AddAnimalsShowColour" id="aashowcolour" class="asm-checkbox" type="checkbox" /> <label for="aashowcolour">' + _("Show the color field") + '</label><br />',
                '<input data="AddAnimalsShowFee" id="aashowfee" class="asm-checkbox" type="checkbox" /> <label for="aashowfee">' + _("Show the adoption fee field") + '</label><br />',
                '<input data="AddAnimalsShowLocation" id="aashowlocation" class="asm-checkbox" type="checkbox" /> <label for="aashowlocation">' + _("Show the internal location field") + '</label><br />',
                '<input data="AddAnimalsShowLocationUnit" id="aashowlocationunit" class="asm-checkbox" type="checkbox" /> <label for="aashowlocationunit">' + _("Show the location unit field") + '</label><br />',
                '<input data="AddAnimalsShowFosterer" id="aashowfosterer" class="asm-checkbox" type="checkbox" /> <label for="aashowfosterer">' + _("Allow a fosterer to be selected") + '</label><br />',
                '<input data="AddAnimalsShowCoordinator" id="aashowcoordinator" class="asm-checkbox" type="checkbox" /> <label for="aashowcoordinator">' + _("Allow an adoption coordinator to be selected") + '</label><br />',
                '<input data="AddAnimalsShowAcceptance" id="aashowacceptance" class="asm-checkbox" type="checkbox" /> <label for="aashowacceptance">' + _("Show the litter ID field") + '</label><br />',
                '<input data="AddAnimalsShowSize" id="aashowsize" class="asm-checkbox" type="checkbox" /> <label for="aashowsize">' + _("Show the size field") + '</label><br />',
                '<input data="AddAnimalsShowWeight" id="aashowweight" class="asm-checkbox" type="checkbox" /> <label for="aashowweight">' + _("Show the weight field") + '</label><br />',
                '<input data="AddAnimalsShowNeutered" id="aashowneutered" class="asm-checkbox" type="checkbox" /> <label for="aashowneutered">' + _("Show the altered fields") + '</label><br />',
                '<input data="AddAnimalsShowMicrochip" id="aashowmicrochip" class="asm-checkbox" type="checkbox" /> <label for="aashowmicrochip">' + _("Show the microchip fields") + '</label><br />',
                '<input data="AddAnimalsShowTattoo" id="aashowtattoo" class="asm-checkbox" type="checkbox" /> <label for="aashowtattoo">' + _("Show the tattoo fields") + '</label><br />',
                '<input data="AddAnimalsShowEntryCategory" id="aashowentrycategory" class="asm-checkbox" type="checkbox" /> <label for="aashowentrycategory">' + _("Show the entry category field") + '</label><br />',
                '<input data="AddAnimalsShowEntryType" id="aashowentrytype" class="asm-checkbox" type="checkbox" /> <label for="aashowentrytype">' + _("Show the entry type field") + '</label><br />',
                '<input data="AddAnimalsShowJurisdiction" id="aashowjurisdiction" class="asm-checkbox" type="checkbox" /> <label for="aashowjurisdiction">' + _("Show the jurisdiction field") + '</label><br />',
                '<input data="AddAnimalsShowPickup" id="aashowpickup" class="asm-checkbox" type="checkbox" /> <label for="aashowpickup">' + _("Show the pickup fields") + '</label><br />',
                '<input data="AddAnimalsShowDateBroughtIn" id="aashowdatebroughtin" class="asm-checkbox" type="checkbox" /> <label for="aashowdatebroughtin">' + _("Show the date brought in field") + '</label><br />',
                '<input data="AddAnimalsShowTimeBroughtIn" id="aashowtimebroughtin" class="asm-checkbox" type="checkbox" /> <label for="aashowtimebroughtin">' + _("Show the time brought in field") + '</label><br />',
                '<input data="AddAnimalsShowOriginalOwner" id="aashoworiginalowner" class="asm-checkbox" type="checkbox" /> <label for="aashoworiginalowner">' + _("Show the original owner field") + '</label><br />',
                '<input data="AddAnimalsShowBroughtInBy" id="aashowbroughtinby" class="asm-checkbox" type="checkbox" /> <label for="aashowbroughtinby">' + _("Show the brought in by field") + '</label><br />',
                '<input data="AddAnimalsShowHold" id="aashowhold" class="asm-checkbox" type="checkbox" /> <label for="aashowhold">' + _("Show the hold fields") + '</label><br />',
                '<input data="WarnSimilarAnimalName" id="warnsimilaranimal" class="asm-checkbox" type="checkbox" /> <label for="warnsimilaranimal">' + _("Warn if the name of the new animal is similar to one entered recently") + '</label>',
                '</p>',
                '</div>'
            ].join("\n");
        },

        render_agegroups: function() {
            return [
                '<div id="tab-agegroups">',
                html.info(_("Age groups are assigned based on the age of an animal. The figure in the left column is the upper limit in years for that group.")),
                '<table>',
                '<tr>',
                '<td>' + _("Age Group 1") + '</td>',
                '<td><input id="agegroup1" type="text" data-max="100" class="asm-numberbox asm-textbox" data="AgeGroup1" /></td>',
                '<td><input id="agegroup1name" type="text" class="asm-textbox" data="AgeGroup1Name" /></td>',
                '</tr>',
                '<tr>',
                '<td>' + _("Age Group 2") + '</td>',
                '<td><input id="agegroup2" type="text" data-max="100" class="asm-numberbox asm-textbox" data="AgeGroup2" /></td>',
                '<td><input id="agegroup2name" type="text" class="asm-textbox" data="AgeGroup2Name" /></td>',
                '</tr>',
                '<tr>',
                '<td>' + _("Age Group 3") + '</td>',
                '<td><input id="agegroup3" type="text" data-max="100" class="asm-numberbox asm-textbox" data="AgeGroup3" /></td>',
                '<td><input id="agegroup3name" type="text" class="asm-textbox" data="AgeGroup3Name" /></td>',
                '</tr>',
                '<tr>',
                '<td>' + _("Age Group 4") + '</td>',
                '<td><input id="agegroup4" type="text" data-max="100" class="asm-numberbox asm-textbox" data="AgeGroup4" /></td>',
                '<td><input id="agegroup4name" type="text" class="asm-textbox" data="AgeGroup4Name" /></td>',
                '</tr>',
                '<tr>',
                '<td>' + _("Age Group 5") + '</td>',
                '<td><input id="agegroup5" type="text" data-max="100" class="asm-numberbox asm-textbox" data="AgeGroup5" /></td>',
                '<td><input id="agegroup5name" type="text" class="asm-textbox" data="AgeGroup5Name" /></td>',
                '</tr>',
                '<tr>',
                '<td>' + _("Age Group 6") + '</td>',
                '<td><input id="agegroup6" type="text" data-max="100" class="asm-numberbox asm-textbox" data="AgeGroup6" /></td>',
                '<td><input id="agegroup6name" type="text" class="asm-textbox" data="AgeGroup6Name" /></td>',
                '</tr>',
                '<tr>',
                '<td>' + _("Age Group 7") + '</td>',
                '<td><input id="agegroup7" type="text" data-max="100" class="asm-numberbox asm-textbox" data="AgeGroup7" /></td>',
                '<td><input id="agegroup7name" type="text" class="asm-textbox" data="AgeGroup7Name" /></td>',
                '</tr>',
                '<tr>',
                '<td>' + _("Age Group 8") + '</td>',
                '<td><input id="agegroup8" type="text" data-max="100" class="asm-numberbox asm-textbox" data="AgeGroup8" /></td>',
                '<td><input id="agegroup8name" type="text" class="asm-textbox" data="AgeGroup8Name" /></td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_animalcodes: function() {
            const animalcodelegend = _("Code format tokens:") + '<br />' +
                    _("T = first letter of animal type") + '<br />' +
                    _("TT = first and second letter of animal type") + '<br />' + 
                    _("E = first letter of animal entry category") + '<br />' +
                    _("EE = first and second letter of animal entry category") + '<br />' + 
                    _("S = first letter of animal species") + '<br />' +
                    _("SS = first and second letter of animal species") + '<br />' + 
                    _("YY or YYYY = current year") + '<br />' +
                    _("MM = current month") + '<br />' +
                    _("DD = current day") + '<br />' + 
                    _("UUUUUUUUUU or UUUU = unique number") + '<br />' +
                    _("XXX or XX = number unique for this year") + '<br />' +
                    _("OOO or OO = number unique for this month") + '<br />' +
                    _("NNN or NN = number unique for this type of animal for this year") + '<br />' +
                    _("Defaults formats for code and shortcode are TYYYYNNN and NNT");
            const incidentcodelegend = _("Code format tokens:") + '<br />' +
                    _("YY or YYYY = current year") + '<br />' +
                    _("MM = current month") + '<br />' +
                    _("DD = current day") + '<br />' + 
                    _("UUUUUUUUUU or UUUU = unique number") + '<br />' +
                    _("XXX or XX = number unique for this year") + '<br />' +
                    _("OOO or OO = number unique for this month") + '<br />' +
                    _("Defaults formats for incident codes are YYMM-XXX");
            return [
                '<div id="tab-animalcodes">',
                '<table>',
                '<tr>',
                '<td><label for="codeformat">' + _("Animal code format") + '</label>',
                '<span id="codeformat-callout" class="asm-callout">' + animalcodelegend + '</span>',
                '</td>',
                '<td><input data="CodingFormat" id="codeformat" type="text" class="asm-textbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="shortformat">' + _("Animal shortcode format") + '</label>',
                '<span id="shortcodeformat-callout" class="asm-callout">' + animalcodelegend + '</span>',
                '</td>',
                '<td><input data="ShortCodingFormat" id="shortformat" type="text" class="asm-textbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="incidentcodeformat">' + _("Incident code format") + '</label>',
                '<span id="incidentcodeformat-callout" class="asm-callout">' + incidentcodelegend + '</span>',
                '</td>',
                '<td><input data="IncidentCodingFormat" id="incidentcodeformat" type="text" class="asm-textbox" /></td>',
                '</tr>',
                '</table>',
                '<p>',
                '<input data="ManualCodes" id="manualcodes" type="checkbox" class="asm-checkbox" /> <label for="manualcodes">' + _("Manually enter codes (do not generate)") + '</label>',
                '<br />',
                '<input data="UseShortShelterCodes" id="shortcodes" type="checkbox" class="asm-checkbox" /> <label for="shortcodes">' + _("Show short shelter codes on screens") + '</label>',
                '<br />',
                '<input data="DisableShortCodesControl" id="disableshortcodes" type="checkbox" class="asm-checkbox" /> <label for="disableshortcodes">' + _("Remove short shelter code box from the animal details screen") + '</label>',
                '<br />',
                '<input data="ShelterViewShowCodes" id="shelterviewshowcodes" type="checkbox" class="asm-checkbox" /> <label for="shelterviewshowcodes">' + _("Show codes on the shelter view screen") + '</label>',
                '<br />',
                '<input data="LockCodes" id="lockcodes" type="checkbox" class="asm-checkbox" /> <label for="lockcodes">' + _("Once assigned, codes cannot be changed") + '</label>',
                '<br />',
                '<input data="AllowDuplicateMicrochip" id="duplicatechip" type="checkbox" class="asm-checkbox" /> <label for="duplicatechip">' + _("Allow duplicate microchip numbers") + '</label>',
                '<br />',
                '<input data="rc:UniqueLicenceNumbers" id="uniquelicence" type="checkbox" class="asm-checkbox" /> <label for="uniquelicence">' + _("Allow duplicate license numbers") + '</label>',
                '</p>',
                '</div>'
            ].join("\n");
        },

        render_animalemblems: function() {
            const emblemvalues = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ@$%^&*!?#",
                emblemglyphs = [
                    8592,  // Left arrow
                    8593,  // Up arrow
                    8594,  // Right arrow
                    8595,  // Down arrow
                    8984,  // Place of interest
                    8987,  // Hourglass
                    8962,  // House
                    9113,  // Print
                    9114,  // Clear screen
                    9200,  // Alarm clock
                    9728,  // Sun
                    9729,  // Cloud
                    9731,  // Snowman
                    9733,  // Star
                    9742,  // Telephone
                    9760,  // Skull/Crossbones
                    9762,  // Radioactive
                    9763,  // Biohazard
                    9774,  // Peace
                    9785,  // Sad face
                    9787,  // Smiley face
                    9792,  // Female
                    9794,  // Male
                    9850,  // Recycling
                    9855,  // Disabled
                    9872,  // White flag
                    9873,  // Black flag
                    9875,  // Anchor
                    9877,  // Medical
                    9878,  // Scales
                    9888,  // Warning
                    9889,  // High Voltage
                    9917,  // Soccer ball
                    9951,  // Truck
                    9983,  // Striped flag
                    9986,  // Scissors
                    9989,  // White heavy check mark (green)
                    9990,  // Telephone location
                    9992,  // Airplane
                    9999,  // Pencil
                    10003, // Tick
                    10004, // Cross
                    10024, // Sparkles
                    10052, // Snowflake
                    10062, // White heavy cross
                    10084, // Heavy heart
                    127798, // Spicy pepper
                    127960, // House - buildings
                    127968, // House - building
                    128008, // Cat
                    128021, // Dog
                    128049, // Cat Face
                    128054, // Dog Face,
                    128137, // Syringe
                    128138, // Pill
                    128169, // Poop
                    128266, // Speaker with high volume
                    128272, // Lock with key
                    128308, // Red circle
                    128309, // Blue circle
                    128992, // Orange circle
                    128993, // Yellow circle
                    128994, // Green circle
                    128995, // Purple circle
                    128996, // Brown circle
                    128997, // Red square
                    128998, // Blue square
                    128999, // Orange square
                    129000, // Yellow square
                    129001, // Green square
                    129002, // Purple square
                    129003, // Brown square
                    128571, // Cat with heart eyes
                    129379, // Bowl and spoon
                    129387, // Can of food
                    129440, // Microbe
                    129460, // Bone
                    129514, // Test tube
                    129516, // DNA
                    129713, // Worm
                    129745  // Bell pepper
                ],
                emblemoptions = [],
                condoptions = '<option></option><option value="has">' + _("if animal has") + 
                    '</option><option value="not">' + _("if animal does not have") + '</option>';
            $.each(emblemglyphs, function(i, v) { emblemoptions.push('<option value="&#' + v + ';">&#' + v + ';</option>'); });
            for (let i = 0; i < emblemvalues.length; i=i+1) { emblemoptions.push('<option>' + emblemvalues[i] + '</option>'); }
            const boxes = function(id) {
                return '<br/>' + 
                '<select data="EmblemsCustomValue' + id + '" class="asm-selectbox asm-halfselectbox decode"><option></option>' + emblemoptions.join("") + '</select> ' + 
                ' <select data="EmblemsCustomCond' + id + '" class="asm-selectbox">' + condoptions + '</select>' + 
                ' <select data="EmblemsCustomFlag' + id + '" class="asm-selectbox"><option></option>' + html.list_to_options(controller.animalflags, "FLAG", "FLAG") + '</select>';
            };
            return [
                '<div id="tab-animalemblems">',
                html.info(_("Animal emblems are the little icons that appear next to animal names in shelter view, the home page and search results.")),
                '<table>',
                '<tr><td>',
                '<p>',
                '<input data="EmblemAlwaysLocation" type="checkbox" id="alwaysshowlocation" class="asm-checkbox" type="checkbox" />',
                    html.icon("location", "On Shelter") + html.icon("person", "Fostered") + html.icon("movement", "Adopted") + 
                    ' <label for="alwaysshowlocation">' + _("Location") + '</label><br />',
                '<input data="EmblemAdoptable" type="checkbox" id="showadoptable" class="asm-checkbox" type="checkbox" />',
                    html.icon("adoptable") + ' <label for="showadoptable">' + _("Adoptable") + '</label><br />',
                '<input data="EmblemBoarding" type="checkbox" id="showboarding" class="asm-checkbox" type="checkbox" />',
                    html.icon("boarding") + ' <label for="showboarding">' + _("Boarding") + '</label><br />',
                '<input data="EmblemBonded" type="checkbox" id="showbonded" class="asm-checkbox" type="checkbox" />',
                    html.icon("bonded") + ' <label for="showbonded">' + _("Bonded") + '</label><br />',
                '<input data="EmblemCourtesy" type="checkbox" id="showcourtesy" class="asm-checkbox" type="checkbox" />',
                    html.icon("share") + ' <label for="showcourtesy">' + _("Courtesy Listing") + '</label><br />',
                '<input data="EmblemCrueltyCase" type="checkbox" id="showcrueltycase" class="asm-checkbox" type="checkbox" />',
                    html.icon("case") + ' <label for="showcrueltycase">' + _("Cruelty Case") + '</label><br />',
                '<input data="EmblemDeceased" type="checkbox" id="showdeceased" class="asm-checkbox" type="checkbox" />',
                    html.icon("death") + ' <label for="showdeceased">' + _("Deceased") + '</label><br />',
                '<input data="EmblemFutureIntake" type="checkbox" id="showfutureintake" class="asm-checkbox" type="checkbox" />',
                    html.icon("animal-add") + ' <label for="showfutureintake">' + _("Future Intake") + '</label><br />',
                '<input data="EmblemFutureAdoption" type="checkbox" id="showfutureadoption" class="asm-checkbox" type="checkbox" />',
                    html.icon("movement") + ' <label for="showfutureadoption">' + _("Future Adoption") + '</label><br />',
                '<input data="EmblemHold" type="checkbox" id="showhold" class="asm-checkbox" type="checkbox" />',
                    html.icon("hold") + ' <label for="showhold">' + _("Hold") + '</label><br />',
                '<input data="EmblemLongTerm" type="checkbox" id="longterm" class="asm-checkbox" type="checkbox" />',
                    html.icon("calendar") + ' <label for="longterm">' + _("Long term") + '</label><br />',
                '<input data="EmblemNeverVacc" type="checkbox" id="shownevervacc" class="asm-checkbox" type="checkbox" />',
                    html.icon("novaccination") + ' <label for="shownevervacc">' + _("Never Vaccinated") + '</label><br />',
                '<input data="EmblemNonShelter" type="checkbox" id="shownonshelter" class="asm-checkbox" type="checkbox" />',
                    html.icon("nonshelter") + ' <label for="shownonshelter">' + _("Non-Shelter") + '</label><br />',
                '<input data="EmblemNotForAdoption" type="checkbox" id="shownotforadoption" class="asm-checkbox" type="checkbox" />',
                    html.icon("notforadoption") + ' <label for="shownotforadoption">' + _("Not For Adoption") + '</label><br />',
                '<input data="EmblemNotMicrochipped" type="checkbox" id="showunmicrochipped" class="asm-checkbox" type="checkbox" />',
                    html.icon("microchip") + ' <label for="showunmicrochipped">' + _("Not Microchipped") + '</label><br />',
                '<input data="EmblemPositiveTest" type="checkbox" id="showpositivetest" class="asm-checkbox" type="checkbox" />',
                    html.icon("positivetest") + ' <label for="showpositivetest">' + _("Positive for Heartworm, FIV or FLV") + '</label><br />',
                '<input data="EmblemQuarantine" type="checkbox" id="showquarantine" class="asm-checkbox" type="checkbox" />',
                    html.icon("quarantine") + ' <label for="showquarantine">' + _("Quarantine") + '</label><br />',
                '<input data="EmblemRabies" type="checkbox" id="showrabies" class="asm-checkbox" type="checkbox" />',
                    html.icon("rabies") + ' <label for="showrabies">' + _("Rabies not given") + '</label><br />',
                '<input data="EmblemReserved" type="checkbox" id="showreserved" class="asm-checkbox" type="checkbox" />',
                    html.icon("reservation") + ' <label for="showreserved">' + _("Reserved") + '</label><br />',
                '<input data="EmblemSpecialNeeds" type="checkbox" id="showspecialneeds" class="asm-checkbox" type="checkbox" />',
                    html.icon("health") + ' <label for="showspecialneeds">' + _("Special Needs") + '</label><br />',
                '<input data="EmblemTrialAdoption" type="checkbox" id="showtrialadoption" class="asm-checkbox" type="checkbox" />',
                    html.icon("trial") + ' <label for="showtrialadoption">' + _("Trial Adoption") + '</label><br />',
                '<input data="EmblemUnneutered" type="checkbox" id="showunneutered" class="asm-checkbox" type="checkbox" />',
                    html.icon("unneutered") + ' <label for="showunneutered">' + _("Unaltered") + '</label><br />',
                '</p>',
                '</td><td>',
                html.info(_("You can assign a custom emblem to your additional animal flags")),
                boxes(1), boxes(2), boxes(3), boxes(4), boxes(5), boxes(6), boxes(7), boxes(8), boxes(9), boxes(10),
                boxes(11), boxes(12), boxes(13), boxes(14), boxes(15), boxes(16), boxes(17), boxes(18), boxes(19), boxes(20),
                '</td></tr></table>',
                '</div>'
            ].join("\n");
        },

        render_boarding: function() {
            return [
                '<div id="tab-boarding">',
                '<table>',
                '<tr>',
                '<td><label for="boardingpaytype">' + _("Boarding payment type") + '</label>',
                '<span id="callout-boardingpaytype" class="asm-callout">' + _("The payment type used when creating payments from boarding records") + '</span>',
                '</td>',
                '<td><select data="BoardingPaymentType" id="boardingpaytype" class="asm-selectbox">',
                html.list_to_options(controller.donationtypes, "ID", "DONATIONNAME"),
                '</select>',
                '</td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_checkout: function() {
            return [
                '<div id="tab-checkout">',
                '<p class="asm-header">' + _("Checkout"),
                '<span id="callout-adcheckout" class="asm-callout">' + _("This feature allows you to email an adopter to have them sign their adoption paperwork, pay the adoption fee and make an optional donation.") + '</span>',
                '</p>',
                '<table>',
                '<tr>',
                '<td><label for="AdoptionCheckoutProcessor">' + _("Payment processor") + '</label></td>',
                '<td>',
                '<select id="AdoptionCheckoutProcessor" data="AdoptionCheckoutProcessor" class="asm-selectbox">',
                '<option value=""></option>',
                '<option value="paypal">' + _("PayPal") + '</option>',
                '<option value="stripe">' + _("Stripe") + '</option>',
                '<option value="cardcom" class="israel">' + _("Cardcom") + '</option>',
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="AdoptionCheckoutTemplateID">' + _("Adoption paperwork template") + '</label></td>',
                '<td>',
                '<select id="AdoptionCheckoutTemplateID" data="AdoptionCheckoutTemplateID" class="asm-selectbox">',
                edit_header.template_list_options(controller.templates),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="AdoptionCheckoutFeeID">' + _("Adoption fee payment type") + '</label></td>',
                '<td>',
                '<select id="AdoptionCheckoutFeeID" data="AdoptionCheckoutFeeID" class="asm-selectbox">',
                html.list_to_options(controller.donationtypes, "ID", "DONATIONNAME"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="LicenceCheckoutFeeID">' + _("License fee payment type") + '</label></td>',
                '<td>',
                '<select id="LicenceCheckoutFeeID" data="LicenceCheckoutFeeID" class="asm-selectbox">',
                html.list_to_options(controller.donationtypes, "ID", "DONATIONNAME"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="AdoptionCheckoutDonationID">' + _("Donation payment type") + '</label></td>',
                '<td>',
                '<select id="AdoptionCheckoutDonationID" data="AdoptionCheckoutDonationID" class="asm-selectbox">',
                html.list_to_options(controller.donationtypes, "ID", "DONATIONNAME"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="AdoptionCheckoutPaymentMethod">' + _("Payment method") + '</label></td>',
                '<td>',
                '<select id="AdoptionCheckoutPaymentMethod" data="AdoptionCheckoutPaymentMethod" class="asm-selectbox">',
                html.list_to_options(controller.paymentmethods, "ID", "PAYMENTNAME"),
                '</select>',
                '</td>',
                '</tr>',

                '</tr>',
                '<tr>',
                '<td><label for="AdoptionCheckoutDonationMsg">' + _("Donation message") + '</label>',
                '<span id="callout-admsg" class="asm-callout">' + _("The text to show adopters when requesting a donation. Simple HTML formatting is allowed.") + '</span>',
                '</td>',
                '<td>',
                '<textarea id="AdoptionCheckoutDonationMsg" data="AdoptionCheckoutDonationMsg" class="asm-textareafixeddouble" rows="3"></textarea>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="AdoptionCheckoutDonationTiers">' + _("Donation tiers") + '</label></td>',
                '<td>',
                '<textarea id="AdoptionCheckoutDonationTiers" data="AdoptionCheckoutDonationTiers" class="asm-textareafixeddouble"  rows="5"></textarea>',
                '</td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_costs: function() {
            return [
                '<div id="tab-costs">',
                '<table>',
                '<tr>',
                '<td><label for="dailyboardingcost">' + _("Default daily boarding cost") + '</label>',
                '<span id="callout-dbc" class="asm-callout">' + _("The daily cost for every day a shelter animal is in care") + '</span>',
                '</td>',
                '<td><input data="DefaultDailyBoardingCost" id="dailyboardingcost" class="asm-currencybox asm-textbox" type="text" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="costtype">' + _("Boarding cost type") + '</label>',
                '<span id="callout-bcosttype" class="asm-callout">' + _("The cost type used when creating a cost record of the total daily boarding cost for adopted animals") + '</span>',
                '</td>',
                '<td><select data="BoardingCostType" id="costtype" class="asm-selectbox">',
                html.list_to_options(controller.costtypes, "ID", "COSTTYPENAME"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td></td>',
                '<td>',
                '<input data="CreateBoardingCostOnAdoption" id="costonadoption" type="checkbox" class="asm-checkbox" /> <label for="costonadoption">' + _("Create boarding cost record when animal is adopted") + '</label><br />',
                '<input data="ShowCostAmount" id="showcostamount" type="checkbox" class="asm-checkbox" /> <label for="showcostamount">' + _("Show a cost field on medical/test/vaccination screens") + '</label><br />',
                '<input data="ShowCostPaid" id="showcostpaid" type="checkbox" class="asm-checkbox" /> <label for="showcostpaid">' + _("Show a separate paid date field with costs") + '</label>',
                '</td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_daily_observations: function() {
            const obsrow = function(i) {
                return '<tr><td><input type="text" class="asm-textbox" data="Behave' + i + 'Name" /></td>' +
                    '<td><input type="text" class="asm-textbox asm-doubletextbox" data="Behave' + i + 'Values" /></td></tr>';
            };
            return [
                '<div id="tab-daily-observations">',
                html.info(_("These are the values that can be recorded for animals on the daily observations screen")),
                '<p class="centered"><label for="behavelogtype">' + _("Log Type") + '</label> ',
                '<select data="BehaveLogType" id="behavelogtype" class="asm-selectbox">',
                html.list_to_options(controller.logtypes, "ID", "LOGTYPENAME"),
                '</select></p>',
                '<table>',
                '<tr><th>' + _("Name") + '</th><th>' + _("Values") + '</th></tr>',
                obsrow(1),
                obsrow(2),
                obsrow(3),
                obsrow(4),
                obsrow(5),
                obsrow(6),
                obsrow(7),
                obsrow(8),
                obsrow(9),
                obsrow(10),
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_data_protection: function() {
            return [
                '<div id="tab-data-protection">',
                '<p>',
                '<input data="AnonymisePersonalData" id="anonymisepersonaldata" type="checkbox" class="asm-checkbox" /> <label for="anonymisepersonaldata">' + _("Anonymize personal data after this many years") + '</label>',
                '<span id="callout-anonymise" class="asm-callout">' + _("This many years after creation of a person record, the name, address and telephone data will be anonymized.") + '</span>',
                '<input data="AnonymiseAfterYears" type="text" class="asm-textbox asm-halftextbox asm-intbox" />', 
                '<br />',
                '<input data="rc:AnonymiseAdopters" id="anonymiseadopters" type="checkbox" class="asm-checkbox" /> <label for="anonymiseadopters">' + _("Never anonymize people who adopted an animal") + '</label>',
                '<br />',
                '<input data="AutoRemoveDocumentMedia" id="autoremovedocumentmedia" type="checkbox" class="asm-checkbox" /> <label for="autoremovedocumentmedia">' + _("Remove HTML and PDF document media after this many years") + '</label>',
                '<input data="AutoRemoveDMYears" type="text" class="asm-textbox asm-halftextbox asm-intbox" />', 
                '<br />',
                '<input data="AutoRemoveAnimalMediaExit" id="autoremoveanimalmediaexit" type="checkbox" class="asm-checkbox" /> <label for="autoremoveanimalmediaexit">' + _("Remove animal media this many years after the animal dies or leaves the shelter") + '</label>',
                '<input data="AutoRemoveAMExitYears" type="text" class="asm-textbox asm-halftextbox asm-intbox" />', 
                '<br />',

                '<input data="AutoRemovePeopleCancResv" id="autoremovepeoplecancresv" type="checkbox" class="asm-checkbox" /> <label for="autoremovepeoplecancresv">' + _("Remove people with a cancelled reservation who have not had any other contact after this many years") + '</label>',
                '<input data="AutoRemovePeopleCRYears" type="text" class="asm-textbox asm-halftextbox asm-intbox" />', 
                '<br />',

                '<input data="ShowGDPRContactOptIn" id="showgdprcontact" type="checkbox" class="asm-checkbox" /> <label for="showgdprcontact">' + _("Show GDPR Contact Opt-In field on person screens") + '</label>',
                '<br />',
                '<input data="GDPRContactChangeLog" id="gdprcontactchangelog" type="checkbox" class="asm-checkbox" /> <label for="gdprcontactchangelog">' + _("When I set a new GDPR Opt-In contact option, make a note of it in the log with this type") + '</label>',
                '<select data="GDPRContactChangeLogType" id="gdprcontactchangelogtype" class="asm-selectbox">',
                html.list_to_options(controller.logtypes, "ID", "LOGTYPENAME"),
                '</select>',
                '</p>',
                '</div>'
            ].join("\n");
        },


        render_defaults: function() {
            const ddrop = function(name, label, cfg, opts) {
                return '<td><label for="' + name + '">' + label + '</label></td>' +
                    '<td><select data="' + cfg + '" id="' + name + '" class="asm-selectbox">' + 
                    opts + '</select></td>';
            };
            const items = [
                ddrop("defaultbreed", _("Breed"), "AFDefaultBreed", html.list_to_options(controller.breeds, "ID", "BREEDNAME")),
                ddrop("defaultclinictype", _("Clinic Appointment"), "AFDefaultClinicType", html.list_to_options(controller.clinictypes, "ID", "CLINICTYPENAME")),
                ddrop("defaultcoattype", _("Coat Type"), "AFDefaultCoatType", html.list_to_options(controller.coattypes, "ID", "COATTYPE")),
                ddrop("defaultcolour", _("Color"), "AFDefaultColour", html.list_to_options(controller.colours, "ID", "BASECOLOUR")),
                ddrop("defaultdeath", _("Death Reason"), "AFDefaultDeathReason", html.list_to_options(controller.deathreasons, "ID", "REASONNAME")),
                ddrop("defaultdiary", _("Diary Person"), "AFDefaultDiaryPerson", '<option value=""></option>' + html.list_to_options(controller.usersandroles, "USERNAME", "USERNAME")),
                ddrop("defaultentry", _("Entry Reason"), "AFDefaultEntryReason", html.list_to_options(controller.entryreasons, "ID", "REASONNAME")),
                ddrop("defaultentry", _("Entry Type"), "AFDefaultEntryType", html.list_to_options(controller.entrytypes, "ID", "ENTRYTYPENAME")),
                ddrop("defaultincident", _("Incident Type"), "DefaultIncidentType", html.list_to_options(controller.incidenttypes, "ID", "INCIDENTNAME")),
                ddrop("defaultjurisdiction", _("Jurisdiction"), "DefaultJurisdiction", html.list_to_options(controller.jurisdictions, "ID", "JURISDICTIONNAME")),
                ddrop("defaultlocation", _("Location"), "AFDefaultLocation", html.list_to_options(controller.locations, "ID", "LOCATIONNAME")),
                ddrop("defaultlog", _("Log Filter"), "AFDefaultLogFilter", '<option value="-1">' + _("(all)") + '</option>' + html.list_to_options(controller.logtypes, "ID", "LOGTYPENAME")),
                ddrop("defaultlogtype", _("Log Type"), "AFDefaultLogType", html.list_to_options(controller.logtypes, "ID", "LOGTYPENAME")),
                ddrop("systemlogtype", _("System Log Type"), "SystemLogType", html.list_to_options(controller.logtypes, "ID", "LOGTYPENAME")),
                ddrop("defaultpaymentmethod", _("Payment Method"), "AFDefaultPaymentMethod", html.list_to_options(controller.paymentmethods, "ID", "PAYMENTNAME")),
                ddrop("defaultdonation", _("Payment Type"), "AFDefaultDonationType", html.list_to_options(controller.donationtypes, "ID", "DONATIONNAME")),
                ddrop("defaultreservation", _("Reservation Status"), "AFDefaultReservationStatus", html.list_to_options(controller.reservationstatuses, "ID", "STATUSNAME")),
                ddrop("defaultreturn", _("Return Reason"), "AFDefaultReturnReason", html.list_to_options(controller.entryreasons, "ID", "REASONNAME")),
                ddrop("defaultsize", _("Size"), "AFDefaultSize", html.list_to_options(controller.sizes, "ID", "SIZE")),
                ddrop("defaultspecies", _("Species"), "AFDefaultSpecies", html.list_to_options(controller.species, "ID", "SPECIESNAME")),
                ddrop("defaulttest", _("Test Type"), "AFDefaultTestType", html.list_to_options(controller.testtypes, "ID", "TESTNAME")),
                ddrop("defaulttransport", _("Transport Type"), "AFDefaultTransportType", html.list_to_options(controller.transporttypes, "ID", "TRANSPORTTYPENAME")),
                ddrop("defaulttype", _("Type"), "AFDefaultType", html.list_to_options(controller.types, "ID", "ANIMALTYPE")),
                ddrop("defaultvaccination", _("Vaccination Type"), "AFDefaultVaccinationType", html.list_to_options(controller.vaccinationtypes, "ID", "VACCINATIONTYPE"))
            ];
            let h = [ "<tr>" ];
            $.each(items, function(i, v) {
                h.push(v);
                if (i % 2 != 0) { h.push("</tr><tr>"); } // Only break after odd items so we get 2 to a row
            });
            h.push("</tr>");
            return [
                '<div id="tab-defaults">',
                html.info(_("These are the default values for these fields when creating new records.")),
                '<table>',
                h.join(""),
                '<tr>',
                '<td><label for="DefaultAnimalAge">' + _("Default Age") + '</label></td>',
                '<td><input id="DefaultAnimalAge" data="DefaultAnimalAge" type="text" class="asm-textbox asm-numberbox" data-min="0" data-max="10" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="DefaultBroughtInBy">' + _("Default Brought In By") + '</label></td>',
                '<td>',
                '<input id="DefaultBroughtInBy" data="DefaultBroughtInBy" type="hidden" class="asm-personchooser" value=\'\' />',
                '</td>',
                '<td><label for="defaultshift">' + _("Default Rota Shift") + '</label></td>',
                '<td>',
                '<input id="defaultshift" data="DefaultShiftStart" type="text" class="asm-textbox asm-halftextbox asm-timebox" />',
                '<input id="defaultshiftend" data="DefaultShiftEnd" type="text" class="asm-textbox asm-halftextbox asm-timebox" />',
                '</td>',
                '</tr>',
                '</table>',
                '<p>',
                '<input data="AutoNotForAdoption" id="autonotadopt" type="checkbox" class="asm-checkbox" /> <label for="autonotadopt">' + _("Mark new animals as not for adoption") + '</label>',
                '<br />',
                '<input data="AutoNewImagesNotForPublish" id="autoimagesnotforpublish" type="checkbox" class="asm-checkbox" /> <label for="autoimagesnotforpublish">' + _("Exclude new animal photos from publishing") + '</label>',
                '<br />',
                '<input data="AutoMediaNotes" id="automedianotes" type="checkbox" class="asm-checkbox" /> <label for="automedianotes">' + _("Prefill new media notes for animal images with animal comments if left blank") + '</label>',
                '<br />',
                '<input data="DefaultMediaNotesFromFile" id="medianotesfile" type="checkbox" class="asm-checkbox" /> <label for="medianotesfile">' + _("Prefill new media notes with the filename if left blank") + '</label>',
                '<br />',
                '<input data="FlagChangeLog" id="flagchangelog" type="checkbox" class="asm-checkbox" /> <label for="flagchangelog">' + _("When I change the flags on an animal or person, make a note of it in the log with this type") + '</label>',
                '<select data="FlagChangeLogType" id="flagchangelogtype" class="asm-selectbox">',
                html.list_to_options(controller.logtypes, "ID", "LOGTYPENAME"),
                '</select>',
                '</br />',
                '<input data="HoldChangeLog" id="holdchangelog" type="checkbox" class="asm-checkbox" /> <label for="holdchangelog">' + _("When I mark an animal held, make a note of it in the log with this type") + '</label>',
                '<select data="HoldChangeLogType" id="holdchangelogtype" class="asm-selectbox">',
                html.list_to_options(controller.logtypes, "ID", "LOGTYPENAME"),
                '</select>',
                '</br />',
                '<input data="LocationChangeLog" id="locationchangelog" type="checkbox" class="asm-checkbox" /> <label for="locationchangelog">' + _("When I change the location of an animal, make a note of it in the log with this type") + '</label>',
                '<select data="LocationChangeLogType" id="locationchangelogtype" class="asm-selectbox">',
                html.list_to_options(controller.logtypes, "ID", "LOGTYPENAME"),
                '</select>',
                '<br />',
                '<input data="WeightChangeLog" id="weightchangelog" type="checkbox" class="asm-checkbox" /> <label for="weightchangelog">' + _("When I change the weight of an animal, make a note of it in the log with this type") + '</label>',
                '<select data="WeightChangeLogType" id="weightchangelogtype" class="asm-selectbox">',
                html.list_to_options(controller.logtypes, "ID", "LOGTYPENAME"),
                '</select>',
                '</p>',
                '</div>'
            ].join("\n");
        },

        render_diaryandmessages: function() {
            return [
                '<div id="tab-diaryandmessages">',
                '<p class="asm-header">' + _("Diary") + '</p>',
                '<p>',
                '<input data="AllDiaryHomePage" id="alldiaryhomepage" class="asm-checkbox" type="checkbox" /> <label for="alldiaryhomepage">' + _("Show the full diary (instead of just my notes) on the home page") + '</label><br />',
                '<input data="DiaryCompleteOnDeath" id="diarycompleteondeath" class="asm-checkbox" type="checkbox" /> <label for="diarycompleteondeath">' + _("Auto complete diary notes linked to animals when they are marked deceased") + '</label><br />',
                '<input data="EmailDiaryNotes" id="emaildiarynotes" class="asm-checkbox" type="checkbox" /> <label for="emaildiarynotes">' + _("Email users their outstanding diary notes once per day") + '</label><br />',
                '<input data="EmailDiaryOnChange" id="emaildiaryonchange" class="asm-checkbox" type="checkbox" /> <label for="emaildiaryonchange">' + _("Email users immediately when a diary note assigned to them is created or updated") + '</label><br />',
                '<input data="EmailDiaryOnComplete" id="emaildiaryoncomplete" class="asm-checkbox" type="checkbox" /> <label for="emaildiaryoncomplete">' + _("Email diary note creators when a diary note is marked complete") + '</label>',
                '</p>',
                '<p class="asm-header">' + _("Messages") + '</p>',
                '<input data="EmailMessages" id="emailmessages" class="asm-checkbox" type="checkbox" /> <label for="emailmessages">' + _("When a message is created, email it to each matching user") + '</label>',
                '</p>',
                '</div>'
            ].join("\n");
        },

        render_display: function() {
            return [
                '<div id="tab-display">',
                '<p>',
                '<input data="rc:DisableEffects" id="disableeffects" class="asm-checkbox" type="checkbox" /> <label for="disableeffects">' + _("Enable visual effects") + '</label><br />',
                '<!-- <input data="FancyTooltips" id="fancytooltips" class="asm-checkbox" type="checkbox" /> <label for="fancytooltips">' + _("Use fancy tooltips") + '</label><br /> -->',
                '<input data="rc:DontUseHTML5Scaling" id="disablehtml5scaling" class="asm-checkbox" type="checkbox" /> <label for="disablehtml5scaling">' + _("Use HTML5 client side image scaling where available to speed up image uploads") + '</label><br />',
                '<input data="PicturesInBooksClinic" id="picsinbooksclinic" class="asm-checkbox" type="checkbox" /> <label for="picsinbooksclinic">' + _("Show animal thumbnails in clinic books") + '</label><br />',
                '<input data="PicturesInBooks" id="picsinbooks" class="asm-checkbox" type="checkbox" /> <label for="picsinbooks">' + _("Show animal thumbnails in movement and medical books") + '</label><br />',
                '<input data="ShowSexBorder" id="sexborder" class="asm-checkbox" type="checkbox" /> <label for="sexborder">' + _("Show pink and blue borders around animal thumbnails to indicate sex") + '</label><br />',
                '<input data="ShowPersonMiniMap" id="minimap" class="asm-checkbox" type="checkbox" /> <label for="minimap">' + _("Show a minimap of the address on person screens") + '</label><br />',
                common.iif(asm.locale == "en", '<input data="USStateCodes" id="usstatecodes" class="asm-checkbox" type="checkbox" /> <label for="usstatecodes">' + _("When entering addresses, restrict states to valid US 2 letter state codes") + '</label><br />', ""),
                '<input data="ShowLatLong" id="latlong" class="asm-checkbox" type="checkbox" /> <label for="latlong">' + _("Allow editing of latitude/longitude with minimaps") + '</label><br />',
                '<input data="MediaTableMode" id="mediatablemode" class="asm-checkbox" type="checkbox" /> <label for="mediatablemode">' + _("Default to table mode when viewing media tabs") + '</label><br />',
                '<input data="ShowWeightInLbs" id="showlbs" class="asm-checkbox" type="checkbox" /> <label for="showlbs">' + _("Show weights as lb and oz") + '</label><br />',
                '<input data="ShowWeightInLbsFraction" id="showlbsf" class="asm-checkbox" type="checkbox" /> <label for="showlbsf">' + _("Show weights as decimal lb") + '</label><br />',
                '<input data="ShowFullCommentsInTables" id="showfullcommentstables" class="asm-checkbox" type="checkbox" /> <label for="showfullcommentstables">' + _("Show complete comments in table views") + '</label><br />',
                '<input data="ShowViewsInAuditTrail" id="showviewsaudittrail" class="asm-checkbox" type="checkbox" /> <label for="showviewsaudittrail">' + _("Show record views in the audit trail") + '</label><br />',
                '<input data="ShowLookupDataID" id="showlookupdataid" class="asm-checkbox" type="checkbox" /> <label for="showlookupdataid">' + _("Show ID numbers when editing lookup data") + '</label><br />',
                '<input data="StickyTableHeaders" id="floatingheaders" class="asm-checkbox" type="checkbox" /> <label for="floatingheaders">' + _("Keep table headers visible when scrolling") + '</label><br />',
                '<input data="TablesReflow" id="tablesreflow" class="asm-checkbox" type="checkbox" /> <label for="tablesreflow">' + _("Tables stack vertically on portrait smartphones") + '</label><br />',
                '<input data="RecordNewBrowserTab" id="recordnewbrowsertab" class="asm-checkbox" type="checkbox" /> <label for="recordnewbrowsertab">' + _("Open records in a new browser tab") + '</label><br />',
                '<input data="ReportNewBrowserTab" id="reportnewbrowsertab" class="asm-checkbox" type="checkbox" /> <label for="reportnewbrowsertab">' + _("Open reports in a new browser tab") + '</label><br />',
                '<input data="LocationFiltersEnabled" id="locationfilters" class="asm-checkbox" type="checkbox" /> <label for="locationfilters">' + _("Enable location filters") + '</label><br />',
                '<input data="MultiSiteEnabled" id="multisite" class="asm-checkbox" type="checkbox" /> <label for="multisite">' + _("Enable multiple sites") + '</label><br />',
                '<input data="FormatPhoneNumbers" id="formatphonenumbers" class="asm-checkbox" type="checkbox" /> <label for="formatphonenumbers">' + _("Format telephone numbers according to my locale") + '</label><br />',
                '<input data="InactivityTimer" id="inactivitytimer" class="asm-checkbox" type="checkbox" /> <label for="inactivitytimer">' + _("Auto log users out after this many minutes of inactivity") + '</label>',
                '<input data="InactivityTimeout" id="inactivitytimeout" data-min="0" data-max="1440" class="asm-textbox asm-numberbox" /><br />',
                '<label for="ownernameformat" style="margin-left: 24px">' + _("When displaying person names, use the format") + '</label> ',
                '<select data="OwnerNameFormat" id="ownernameformat" type="text" class="asm-selectbox">',
                '<option value="{ownertitle} {ownerforenames} {ownersurname}">' + _("Title First Last") + '</option>',
                '<option value="{ownertitle} {ownerinitials} {ownersurname}">' + _("Title Initials Last") + '</option>',
                '<option value="{ownerforenames} {ownersurname}">' + _("First Last") + '</option>',
                '<option value="{ownersurname}, {ownerforenames}">' + _("Last, First") + '</option>',
                '<option value="{ownersurname} {ownerforenames}">' + _("Last First") + '</option>',
                '</select> ',
                '<select data="OwnerNameMarriedFormat" id="ownernamemarriedformat" type="text" class="asm-selectbox">',
                '<option value="{ownerforenames1} & {ownerforenames2} {ownersurname}">' + _("First & First Last") + '</option>',
                '<option value="{ownersurname}, {ownerforenames1} & {ownerforenames2}">' + _("Last, First & First") + '</option>',
                '</select> ',
                '<br />',
                '<label for="ownernameformat" style="margin-left: 24px">' + _("When displaying calendars, the first day of the week is") + '</label> ',
                '<select data="FirstDayOfWeek" id="firstdayofweek" type="text" class="asm-selectbox">',
                '<option value="0">' + _("Sunday") + '</option>',
                '<option value="1">' + _("Monday") + '</option>',
                '</select>',
                '</p>',
                '</div>'
            ].join("\n");
        },

        render_documents: function() {
            return [
                '<div id="tab-documents">',
                '<p>',
                '<input data="AllowODTDocumentTemplates" id="allowodttemp" class="asm-checkbox" type="checkbox" /> <label for="allowodttemp">' + _("Allow use of OpenOffice document templates") + '</label><br />',
                '<input data="JSWindowPrint" id="jswprint" class="asm-checkbox" type="checkbox" /> <label for="jswprint">' + _("Printing word processor documents uses hidden iframe and window.print") + '</label><br />',
                '<input data="PDFInline" id="pdfinline" class="asm-checkbox" type="checkbox" /> <label for="pdfinline">' + _("Show PDF files inline instead of sending them as attachments") + '</label><br />',
                '<input data="IncludeIncompleteMedicalDoc" id="includeincompletemedical" type="checkbox" class="asm-checkbox" /> <label for="includeincompletemedical">' + _("Include incomplete medical records when generating document templates") + '</label><br />',
                '<input data="GenerateDocumentLog" id="generatedocumentlog" type="checkbox" class="asm-checkbox" /> <label for="generatedocumentlog">' + _("When I generate a document, make a note of it in the log with this type") + '</label>',
                '<select data="GenerateDocumentLogType" id="generatedocumentlogtype" class="asm-selectbox">',
                html.list_to_options(controller.logtypes, "ID", "LOGTYPENAME"),
                '</select>',
                '</p>',
                '<p>',
                '<label for="pdfzoom">' + _("Default zoom level when converting documents to PDF") + '</label> ',
                '<input data="PDFZoom" id="pdfzoom" type="text" class="asm-halftextbox asm-numberbox" />%',
                '<br />',
                '</p>',
                '</div>'
            ].join("\n");
        },

        render_email: function() {
            return [
                '<div id="tab-email">',
                '<table>',
                '<tr><td>',
                // inner
                '<table>',
                '<tr>',
                '<td><label for="emailaddress">' + _("Email address") + '</label>',
                '<span id="callout-emailaddress" class="asm-callout">' + _("This email address is the default From address when sending emails") + '</span>',
                '</td>',
                '<td><input data="EmailAddress" id="emailaddress" type="text" class="asm-doubletextbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="emailbcc">' + _("BCC messages to") + '</label>',
                '<span id="callout-emailbcc" class="asm-callout">' + _("BCC this address when sending email. This is useful if you want to archive your emails with another service.") + '</span>',
                '</td>',
                '<td><input data="EmailBCC" id="emailbcc" type="text" class="asm-doubletextbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="emailsig">' + _("Email signature") + '</label>',
                '<span id="callout-emailsignature" class="asm-callout">' + _("This text will be added to the bottom of all send email dialogs") + '</span>',
                '</td>',
                '<td><div data="EmailSignature" id="emailsig" data-margin-top="24px" data-height="200px" data-width="380px" class="asm-richtextarea"></div></td>',
                '</tr>',
                '</table>',
                '</td><td>',
                // next col
                '<table>',
                '<tr>',
                '<td><label for="emailfromadd">' + _("From address book") + '</label>',
                '<span id="callout-fromaddresses" class="asm-callout">' + _("Comma separated list of extra addresses that the From email field of send email dialogs will prompt with") + '</span>',
                '</td>',
                '<td><textarea id="emailfromadd" rows="6" class="asm-textareafixeddouble" data="EmailFromAddresses" title="' + html.title(_("From address book")) + '"></textarea></td>',
                '</tr>',
                '<tr>',
                '<td><label for="emailtoadd">' + _("To address book") + '</label>',
                '<span id="callout-toaddresses" class="asm-callout">' + _("Comma separated list of extra addresses that the To and CC email fields of send email dialogs will prompt with") + '</span>',
                '</td>',
                '<td><textarea id="emailtoadd" rows="6" class="asm-textareafixeddouble" data="EmailToAddresses" title="' + html.title(_("To address book")) + '"></textarea></td>',
                '</tr>',
                '</table>',
                // end
                '</td></tr></table>',
                '<div class="smcom">',
                '<p class="centered"><input id="smtpoverride" type="checkbox" class="asm-checkbox" data="SMTPOverride" /> <label for="smtpoverride">' + _("Specify an SMTP server for sending emails") + '</label>',
                '<span class="asm-callout">' + _("Please do not enable this option if you do not understand what this means.") + '</span></p>',
                '<table>',
                '<tr>',
                '<td><label for="smtpserver">' + _("SMTP Server") + '</label></td>',
                '<td><input id="smtpserver" data="SMTPServer" type="text" class="asm-textbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="smtpport">' + _("Port") + '</label></td>',
                '<td><select id="smtpport" data="SMTPPort" class="asm-selectbox"><option>25</option><option>587</option><option>2525</option></select></td>',
                '</tr>',
                '<tr>',
                '<td></td>',
                '<td><input id="smtptls" type="checkbox" data="SMTPUseTLS" class="asm-checkbox" /> <label for="smtptls">' + _("Use TLS") + '</label></td>',
                '</tr>',
                '<tr>',
                '<td><label for="smtpuser">' + _("Username") + '</label></td>',
                '<td><input id="smtpuser" data="SMTPUsername" class="asm-textbox" type="text" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="smtppass">' + _("Password") + '</label></td>',
                '<td><input id="smtppass" data="SMTPPassword" class="asm-textbox" type="text" /></td>',
                '</tr>',
                '<tr>',
                '<td></td>',
                '<td><input id="smtpreplyasfrom" type="checkbox" class="asm-checkbox" data="SMTPReplyAsFrom" /> ',
                '<label for="smtpreplyasfrom">' + _("Set the FROM header from the email dialog") + '</label>',
                '<span id="callout-smtpreplyasfrom" class="asm-callout">' + _("Allow the user to override the From header. Emails will fail if you try to send email from a domain you do not own.") + '</span>',
                '</td>',
                '</tr>',
                '</table>',
                '</div>',
                '</div>'
            ].join("\n");
        },

        render_findscreens: function() {
            return [
                '<div id="tab-findscreens">',
                html.info(_("These fields determine which columns are shown on the find screens. You can drag and drop to rearrange the order.")),
                '<table>',
                '<tr>',
                '<td><label for="findanimalcols">' + _("Find animal columns") + '</label></td>',
                '<td><select id="searchcolumns" class="asm-bsmselect" data="SearchColumns" multiple="multiple">',
                this.two_pair_options(controller.animalfindcolumns),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="findfoundanimalcols">' + _("Find found animal columns") + '</label></td>',
                '<td>',
                '<select id="findfoundanimalcols" class="asm-bsmselect" data="FoundAnimalSearchColumns" multiple="multiple">',
                this.two_pair_options(controller.foundanimalfindcolumns),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="findlostanimalcols">' + _("Find lost animal columns") + '</label></td>',
                '<td>',
                '<select id="findlostanimalcols" class="asm-bsmselect" data="LostAnimalSearchColumns" multiple="multiple">',
                this.two_pair_options(controller.lostanimalfindcolumns),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="findincidentcols">' + _("Find incident columns") + '</label></td>',
                '<td>',
                '<select id="findincidentcols" class="asm-bsmselect" data="IncidentSearchColumns" multiple="multiple">',
                this.two_pair_options(controller.incidentfindcolumns),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="findpersoncols">' + _("Find person columns") + '</label></td>',
                '<td>',
                '<select id="findpersoncols" class="asm-bsmselect" data="OwnerSearchColumns" multiple="multiple">',
                this.two_pair_options(controller.personfindcolumns),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="findeventcols">' + _("Find event columns") + '</label></td>',
                '<td>',
                '<select id="findeventcols" class="asm-bsmselect" data="EventSearchColumns" multiple="multiple">',
                this.two_pair_options(controller.eventfindcolumns),
                '</select>',
                '</td>',
                '</tr>',

                '</table>',
                '<p>',
                '<input data="AdvancedFindAnimal" id="advancedfindanimal" type="checkbox" class="asm-checkbox" /> <label for="advancedfindanimal">' + _("Default to advanced find animal screen") + '</label>',
                '<br />',
                '<input data="AdvancedFindAnimalOnShelter" id="advancedfindanimalos" type="checkbox" class="asm-checkbox" /> <label for="advancedfindanimalos">' + _("Advanced find animal screen defaults to on shelter") + '</label>',
                '<br />',
                '<input data="AdvancedFindOwner" id="advancedfindperson" type="checkbox" class="asm-checkbox" /> <label for="advancedfindperson">' + _("Default to advanced find person screen") + '</label>',
                '<br />',
                '<input data="AdvancedFindIncidentIncomplete" id="aficomplete" type="checkbox" class="asm-checkbox" /> <label for="aficomplete">' + _("Find an incident screen defaults to incomplete incidents") + '</label>',
                '<br />',
                '<input data="AnimalSearchResultsNewTab" id="animalsearchnewtab" type="checkbox" class="asm-checkbox" /> <label for="animalsearchnewtab">' + _("Open animal find screens in a new tab") + '</label>',
                '<br />',
                '<input data="PersonSearchResultsNewTab" id="personsearchnewtab" type="checkbox" class="asm-checkbox" /> <label for="personsearchnewtab">' + _("Open person find screens in a new tab") + '</label>',
                '</p>',
                '</div>'
            ].join("\n");
        },

        render_homepage: function() {
            return [
                '<div id="tab-homepage">',
                '<p>',
                '<input data="rc:DisableTips" id="disabletips" class="asm-checkbox" type="checkbox" /> <label for="disabletips">' + _("Show tips on the home page") + '</label><br />',
                '<input data="ShowAlertsHomePage" id="showalerts" class="asm-checkbox" type="checkbox" /> <label for="showalerts">' + _("Show alerts on the home page") + '</label><br />',
                '<input data="ShowOverviewHomePage" id="showoverview" class="asm-checkbox" type="checkbox" /> <label for="showoverview">' + _("Show overview counts on the home page") + '</label><br />',
                '<input data="ShowTimelineHomePage" id="showtimeline" class="asm-checkbox" type="checkbox" /> <label for="showtimeline">' + _("Show timeline on the home page") + '</label><br />',
                '<input data="rc:ShowDeceasedHomePage" id="showhdeceased" class="asm-checkbox" type="checkbox" /> <label for="showhdeceased">' + _("Hide deceased animals from the home page") + '</label><br />',
                '<input data="rc:ShowFinancialHomePage" id="showhfinancial" class="asm-checkbox" type="checkbox" /> <label for="showhfinancial">' + _("Hide financial stats from the home page") + '</label><br />',
                '</p>',
                '<p class="asm-header">' + _("Alerts") + '</p>',
                '<table class="asm-left-table">',
                '<tr>',
                '<td>' + _("Show an alert when these species of animals are not microchipped") + '</td>',
                '<td>',
                '<select id="alertmicrochip" multiple="multiple" class="asm-bsmselect" data="AlertSpeciesMicrochip">',
                html.list_to_options(controller.species, "ID", "SPECIESNAME"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>' + _("Show an alert when these species of animals are not altered") + '</td>',
                '<td>',
                '<select id="alertmicrochip" multiple="multiple" class="asm-bsmselect" data="AlertSpeciesNeuter">',
                html.list_to_options(controller.species, "ID", "SPECIESNAME"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>' + _("Show an alert when these species of animals do not have a vaccination of any type") + '</td>',
                '<td>',
                '<select id="alertnevervacc" multiple="multiple" class="asm-bsmselect" data="AlertSpeciesNeverVacc">',
                html.list_to_options(controller.species, "ID", "SPECIESNAME"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<tr>',
                '<td>' + _("Show an alert when these species of animals do not have a rabies vaccination") + '</td>',
                '<td>',
                '<select id="alertrabies" multiple="multiple" class="asm-bsmselect" data="AlertSpeciesRabies">',
                html.list_to_options(controller.species, "ID", "SPECIESNAME"),
                '</select>',
                '</td>',
                '</tr>',
                '</table>',
                '<p class="asm-header">' + _("Stats") + '</p>',
                html.info(_("Stats show running figures for the selected period of animals entering and leaving the shelter on the home page.")),
                '<table class="asm-left-table">',
                '<tr>',
                '<td><label for="statmode">' + _("Stats period") + '</label></td>',
                '<td>',
                '<select id="statmode" class="asm-selectbox" data="ShowStatsHomePage">',
                '<option value="none">' + _("Do not show") + '</option>',
                '<option value="today">' + _("Today") + '</option>',
                '<option value="thisweek">' + _("This week") + '</option>',
                '<option value="thismonth">' + _("This month") + '</option>',
                '<option value="thisyear">' + _("This year") + '</option>',
                '<option value="alltime">' + _("All time") + '</option>',
                '</select>',
                '</td>',
                '</tr>',
                '</table>',
                '<p class="asm-header">' + _("Animal Links") + '</p>',
                '<table class="asm-left-table">',
                '<tr>',
                '<td><label for="linkmode">' + _("Type of animal links to show") + '</label></td>',
                '<td>',
                '<select id="linkmode" class="asm-selectbox" data="MainScreenAnimalLinkMode">',
                '<option value="none">' + _("Do not show") + '</option>',
                '<option value="recentlychanged">' + _("Recently Changed") + '</option>',
                '<option value="recentlyentered">' + _("Recently Entered Shelter") + '</option>',
                '<option value="recentlyadopted">' + _("Recently Adopted") + '</option>',
                '<option value="recentlyfostered">' + _("Recently Fostered") + '</option>',
                '<option value="adoptable">' + _("Up for adoption") + '</option>',
                '<option value="longestonshelter">' + _("Longest On Shelter") + '</option>',
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="linkmax">' + _("Number of animal links to show") + '</label></td>',
                '<td><input type="text" id="linkmax" data-min="0" data-max="200" data="MainScreenAnimalLinkMax" class="asm-textbox asm-numberbox" /></td>',
                '</tr>',
                '</table>',

                '</div>'
            ].join("\n");
        },

        render_insurance: function() {
            return [
                '<div id="tab-insurance">',
                html.info(_("These numbers are for shelters who have agreements with insurance companies and are given blocks of policy numbers to allocate.")),
                '<table>',
                '<tr>',
                '<td></td>',
                '<td><input data="UseAutoInsurance" id="autoinsurance" type="checkbox" class="asm-checkbox" /> <label for="autoinsurance">' + _("Use Automatic Insurance Numbers") + '</label></td>',
                '</tr>',
                '<tr>',
                '<td><label for="insurancestart">' + _("Start at") + '</label></td>',
                '<td><input data="AutoInsuranceStart" id="insurancestart" type="text" class="asm-textbox asm-numberbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="insuranceend">' + _("End at") + '</label></td>',
                '<td><input data="AutoInsuranceEnd" id="insuranceend" type="text" class="asm-textbox asm-numberbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="insurancenext">' + _("Next") + '</label></td>',
                '<td><input data="AutoInsuranceNext" id="insurancenext" type="text" class="asm-textbox asm-numberbox" /></td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_lostandfound: function() {
            return [
                '<div id="tab-lostandfound">',
                '<p>',
                '<input data="rc:DisableLostAndFound" id="disablelostfound" type="checkbox" class="asm-checkbox" /> <label for="disablelostfound">' + _("Enable lost and found functionality") + '</label>',
                '<br />',
                '<input data="MatchIncludeShelter" id="matchshelter" type="checkbox" class="asm-checkbox" /> <label for="matchshelter">' + _("When matching lost animals, include shelter animals") + '</label>',
                '</p>',
                '<table>',
                '<tr>',
                '<td class="bottomborder"><label for="matchpointfloor">' + _("Points required to appear on match report") + '</label></td>',
                '<td class="bottomborder"><input data="MatchPointFloor" id="matchpointfloor" type="text" class="asm-textbox asm-numberbox strong" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="matchmicrochip">' + _("Points for matching microchip") + '</label></td>',
                '<td><input data="MatchMicrochip" id="matchmicrochip" type="text" class="asm-textbox asm-numberbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="matchspecies">' + _("Points for matching species") + '</label></td>',
                '<td><input data="MatchSpecies" id="matchspecies" type="text" class="asm-textbox asm-numberbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="matchbreed">' + _("Points for matching breed") + '</label></td>',
                '<td><input data="MatchBreed" id="matchbreed" type="text" class="asm-textbox asm-numberbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="matchcolour">' + _("Points for matching color") + '</label></td>',
                '<td><input data="MatchColour" id="matchcolour" type="text" class="asm-textbox asm-numberbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="matchagegroup">' + _("Points for matching age group") + '</label></td>',
                '<td><input data="MatchAge" id="matchagegroup" type="text" class="asm-textbox asm-numberbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="matchsex">' + _("Points for matching sex") + '</label></td>',
                '<td><input data="MatchSex" id="matchsex" type="text" class="asm-textbox asm-numberbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="matcharea">' + _("Points for matching lost/found area") + '</label></td>',
                '<td><input data="MatchAreaLost" id="matcharea" type="text" class="asm-textbox asm-numberbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="matchfeatures">' + _("Points for matching features") + '</label></td>',
                '<td><input data="MatchFeatures" id="matchfeatures" type="text" class="asm-textbox asm-numberbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="matchpostcode">' + _("Points for matching zipcode") + '</label></td>',
                '<td><input data="MatchPostcode" id="matchpostcode" type="text" class="asm-textbox asm-numberbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="match2weeks">' + _("Points for being found within 2 weeks of being lost") + '</label></td>',
                '<td><input data="MatchWithin2Weeks" id="match2weeks" type="text" class="asm-textbox asm-numberbox" /></td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_medical: function() {
            return [
                '<div id="tab-medical">',
                '<p>',
                '<input data="IncludeOffShelterMedical" id="includeoffsheltermedical" type="checkbox" class="asm-checkbox" /> <label for="includeoffsheltermedical">' + _("Include off-shelter animals in medical calendar and books") + '</label>',
                '<br />',
                '<input data="MedicalPrecreateTreatments" id="precreatetreat" type="checkbox" class="asm-checkbox" /> <label for="precreatetreat">' + _("Pre-create all treatments when creating fixed-length medical regimens") + '</label>',
                '<br />',
                '<input data="ReloadMedical" id="reloadmedical" type="checkbox" class="asm-checkbox" /> <label for="reloadmedical">' + _("Reload the medical book/tab automatically after adding new medical items") + '</label>',
                '<br />',
                '<input data="AutoDefaultVaccBatch" id="autodefaultvaccbatch" type="checkbox" class="asm-checkbox" /> <label for="autodefaultvaccbatch">' + _("When entering vaccinations, default the last batch number and manufacturer for that type") + '</label>',
                '</p>',
                '<p class="asm-header">' + _("Weekly Fosterer Email") + '</p>',
                '<input data="FostererEmails" id="fostereremails" type="checkbox" class="asm-checkbox" /> <label for="fostereremails">' + _("Send a weekly email to fosterers with medical information about their animals") + '</label><br/>',
                '<input data="FostererEmailSkipNoMedical" id="fostereremailskipnomedical" type="checkbox" class="asm-checkbox" /> <label for="fostereremailskipnomedical">' + _("Do not send an email if there are no medical items due for animals in the care of this fosterer") + '</label>',
                '</p>',
                '<table>',
                '<tr>',
                '<td><label for="femailreplyto">' + _("Replies to the fosterer email should go to"),
                '<span id="callout-femailreplyto" class="asm-callout">' + _("If blank, the address from the Email tab will be used") + '</span> ',
                '</label></td>',
                '<td><input data="FostererEmailsReplyTo" id="femailreplyto" type="text" class="asm-doubletextbox" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="femailsendday">' + _("Send the email on") + '</label></td>',
                '<td><select data="FostererEmailSendDay" id="femailsendday" class="asm-selectbox">',
                '<option value="0">' + _("Monday") + '</option><option value="1">' + _("Tuesday") + '</option>',
                '<option value="2">' + _("Wednesday") + '</option><option value="3">' + _("Thursday") + '</option>',
                '<option value="4">' + _("Friday") + '</option><option value="5">' + _("Saturday") + '</option>',
                '<option value="6">' + _("Sunday"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="femailmsg">' + _("Add an extra message to the fosterer email") + '</label></td>',
                '<td><div data="FostererEmailsMsg" id="femailmsg" data-margin-top="24px" data-height="100px" data-width="380px" class="asm-richtextarea"></div></td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_movements: function() {
            return [
                '<div id="tab-movements">',
                '<p>',
                '<label for="cancelunadopted">' + _("Cancel unadopted reservations after") + '</label>',
                '<span id="callout-cancelunadopted" class="asm-callout">' + _("Cancel unadopted reservations after this many days, or 0 to never cancel") + '</span>',
                '<input data="AutoCancelReservesDays" id="cancelunadopted" type="text" data-min="0" data-max="365" class="asm-textbox asm-halftextbox asm-numberbox" /> ' + _(" days.") + '<br />',
                '<label for="reservesoverdue">' + _("Highlight unadopted reservations after") + '</label>',
                '<input data="ReservesOverdueDays" id="reservesoverdue" type="text" data-min="1" data-max="365" class="asm-textbox asm-halftextbox asm-numberbox" /> ' + _(" days.") + '<br />',
                '<label for="autoremoveholddays">' + _("Remove holds after") + '</label>',
                '<span id="callout-autoremoveholddays" class="asm-callout">' + _("Cancel holds on animals this many days after the brought in date, or 0 to never cancel") + '</span>',
                '<input data="AutoRemoveHoldDays" id="autoremoveholddays" type="text" data-min="0" data-max="365" class="asm-textbox asm-halftextbox asm-numberbox" /> ' + _(" days.") + '<br />',
                '<label for="defaulttriallength">' + _("Trial adoptions last for") + '</label>',
                '<span id="callout-defaulttriallength" class="asm-callout">' + _("When creating trial adoptions, default the end date to this many days from the trial start") + '</span>',
                '<input data="DefaultTrialLength" id="defaulttriallength" type="text" data-min="0" data-max="365" class="asm-textbox asm-halftextbox asm-numberbox" /> ' + _(" days.") + '<br />',
                '<label for="longtermdays">' + _("Animals are long term after") + '</label>',
                '<span id="callout-longtermdays" class="asm-callout">' + _("Show an alert and emblem for animals who have been on shelter for this period") + '</span>',
                '<input data="LongTermDays" id="longtermdays" type="text" data-min="0" data-max="1000" class="asm-textbox asm-halftextbox asm-numberbox" /> ' + _(" days.") + '<br />',
                '</p>',
                '<input data="FutureOnShelter" id="futureonshelter" class="asm-checkbox" type="checkbox" /> <label for="futureonshelter">' + _("Treat animals with a future intake date as part of the shelter inventory") + '</label><br />',
                '<input data="FosterOnShelter" id="fosteronshelter" class="asm-checkbox" type="checkbox" /> <label for="fosteronshelter">' + _("Treat foster animals as part of the shelter inventory") + '</label><br />',
                '<input data="RetailerOnShelter" id="retaileronshelter" class="asm-checkbox" type="checkbox" /> <label for="retaileronshelter">' + _("Treat animals at retailers as part of the shelter inventory") + '</label><br />',
                '<input data="TrialAdoptions" id="trialadoptions" class="asm-checkbox" type="checkbox" /> <label for="trialadoptions">' + _("Our shelter does trial adoptions, allow us to mark these on movement screens") + '</label><br />',
                '<input data="TrialOnShelter" id="trialonshelter" class="asm-checkbox" type="checkbox" /> <label for="trialonshelter">' + _("Treat trial adoptions as part of the shelter inventory") + '</label><br />',
                '<input data="SoftReleases" id="softreleases" class="asm-checkbox" type="checkbox" /> <label for="softreleases">' + _("Our shelter does soft releases, allow us to mark these on movement screens") + '</label><br />',
                '<input data="SoftReleaseOnShelter" id="softreleaseonshelter" class="asm-checkbox" type="checkbox" /> <label for="softreleaseonshelter">' + _("Treat soft releases as part of the shelter inventory") + '</label><br />',
                '<input data="MovementPersonOnlyReserves" id="persononlyreserve" class="asm-checkbox" type="checkbox" /> <label for="persononlyreserve">' + _("Allow reservations to be created that are not linked to an animal") + '</label><br />',
                '<input data="CancelReservesOnAdoption" id="cancelresadopt" class="asm-checkbox" type="checkbox" /> <label for="cancelresadopt">' + _("Automatically cancel any outstanding reservations on an animal when it is adopted") + '</label><br />',
                '<input data="ReturnFostersOnAdoption" id="returnfosteradopt" class="asm-checkbox" type="checkbox" /> <label for="returnfosteradopt">' + _("Automatically return any outstanding foster movements on an animal when it is adopted") + '</label><br />',
                '<input data="ReturnFostersOnTransfer" id="returnfostertransfer" class="asm-checkbox" type="checkbox" /> <label for="returnfostertransfer">' + _("Automatically return any outstanding foster movements on an animal when it is transferred") + '</label><br />',
                '<input data="ReturnRetailerOnAdoption" id="returnretaileradopt" class="asm-checkbox" type="checkbox" /> <label for="returnretaileradopt">' + _("Automatically return any outstanding retailer movements on an animal when it is adopted") + '</label><br />',
                '<input data="MovementDonationsDefaultDue" id="donationsdue" class="asm-checkbox" type="checkbox" /> <label for="donationsdue">' + _("When creating payments from the Move menu screens, mark them due instead of received") + '</label><br />',
                '<input data="DonationOnMoveReserve" id="donationmovereserve" class="asm-checkbox" type="checkbox" /> <label for="donationmovereserve">' + _("Allow creation of payments on the Move{0}Reserve screen").replace("{0}", html.icon("right")) + '</label><br />',
                '<input data="MoveAdoptDonationsEnabled" id="moveadoptdonationsenabled" class="asm-checkbox" type="checkbox" /> <label for="moveadoptdonationsenabled">' + _("Allow editing of payments after creating an adoption on the Move{0}Adopt an animal screen").replace("{0}", html.icon("right")) + '</label><br />',
                '<input data="MoveAdoptGeneratePaperwork" id="moveadoptgeneratepaperwork" class="asm-checkbox" type="checkbox" /> <label for="moveadoptgeneratepaperwork">' + _("Allow requesting signed paperwork when creating an adoption on the Move{0}Adopt an animal screen").replace("{0}", html.icon("right")) + '</label><br />',
                '<input data="MovementNumberOverride" id="movementoverride" class="asm-checkbox" type="checkbox" /> <label for="movementoverride">' + _("Allow overriding of the movement number on the Move menu screens") + '</label><br />',
                '</p>',
                '<p class="asm-header">' + _("Warnings") + '</p>',
                '<p>',
                '<input data="WarnUnaltered" id="warnunaltered" class="asm-checkbox" type="checkbox" /> <label for="warnunaltered">' + _("Warn when adopting an unaltered animal") + '</label><br />',
                '<input data="WarnNoMicrochip" id="warnnomicrochip" class="asm-checkbox" type="checkbox" /> <label for="warnnomicrochip">' + _("Warn when adopting an animal who has not been microchipped") + '</label><br />',
                '<input data="WarnOSMedical" id="warnosmedical" class="asm-checkbox" type="checkbox" /> <label for="warnosmedical">' + _("Warn when adopting an animal who has outstanding medical treatments") + '</label><br />',
                '<input data="WarnNoHomeCheck" id="warnnohomecheck" class="asm-checkbox" type="checkbox" /> <label for="warnnohomecheck">' + _("Warn when adopting to a person who has not been homechecked") + '</label><br />',
                '<input data="WarnBannedAddress" id="warnbaddress" class="asm-checkbox" type="checkbox" /> <label for="warnbaddress">' + _("Warn when adopting to a person who lives at the same address as a banned person") + '</label><br />',
                '<input data="WarnBannedOwner" id="warnbanned" class="asm-checkbox" type="checkbox" /> <label for="warnbanned">' + _("Warn when adopting to a person who has been banned from adopting animals") + '</label><br />',
                '<input data="WarnOOPostcode" id="warnoopostcode" class="asm-checkbox" type="checkbox" /> <label for="warnoopostcode">' + _("Warn when adopting to a person who lives in the same area as the original owner") + '</label><br />',
                '<input data="WarnBroughtIn" id="warnbroughtin" class="asm-checkbox" type="checkbox" /> <label for="warnbroughtin">' + _("Warn when adopting to a person who has previously brought an animal to the shelter") + '</label><br />',
                '<input data="WarnNoReserve" id="warnnoreserve" class="asm-checkbox" type="checkbox" /> <label for="warnnoreserve">' + _("Warn when adopting an animal with reservations and this person is not one of them") + '</label><br />',
                '<input data="WarnMultipleReserves" id="warnmultiplereseves" class="asm-checkbox" type="checkbox" /> <label for="warnmultiplereserves">' + _("Warn when creating multiple reservations on the same animal") + '</label>',
                '</p>',
                '</div>'
            ].join("\n");
        },

        render_onlineforms: function() {
            return [
                '<div id="tab-onlineforms">',
                '<p><label for="autoremoveforms">' + _("Remove incoming forms after") + '</label> <input data="AutoRemoveIncomingFormsDays" id="autoremoveforms" type="text" data-min="7" data-max="56" class="asm-halftextbox asm-textbox asm-numberbox" /> ' + _(" days.") + '<br/>',
                '<input data="OnlineFormDeleteOnProcess" id="deleteonprocess" class="asm-checkbox" type="checkbox" /> <label for="deleteonprocess">' + _("Remove forms immediately when I process them") + '</label><br/>',
                '<input data="rc:DontRemoveProcessedForms" id="removeprocessedforms" class="asm-checkbox" type="checkbox" /> <label for="removeprocessedforms">' + _("Remove processed forms when I leave the incoming forms screens") + '</label><br/>',
                '<input data="AutoHashProcessedForms" id="hashprocessedforms" class="asm-checkbox" type="checkbox" /> <label for="hashprocessedforms">' + _("When storing processed forms as media, apply tamper proofing and make them read only") + '</label><br/>',
                '<input data="OnlineFormSpamHoneyTrap" id="spamhoneytrap" class="asm-checkbox" type="checkbox" /> <label for="spamhoneytrap">' + _("Spambot protection: Invisible checkbox") + '</label><br/>',
                '<input data="OnlineFormSpamUACheck" id="spamuacheck" class="asm-checkbox" type="checkbox" /> <label for="spamuacheck">' + _("Spambot protection: UserAgent check") + '</label><br/>',
                '<input data="OnlineFormSpamFirstnameMixCase" id="spamfirstname" class="asm-checkbox" type="checkbox" /> <label for="spamfirstname">' + _("Spambot protection: First name mixed case") + '</label><br/>',
                '</p>',
                '</div>'
            ].join("\n");
        },

        render_processors: function() {
            return [
                '<div id="tab-processors">',
                html.info(_("ASM can talk to payment processors and request payment from your customers and donors.")),
                '<table>',
                '<tr><td><label for="currencycode">' + _("Request payments in") + '</label></td>',
                '<td><select id="currencycode" class="asm-selectbox asm-doubleselectbox" data="CurrencyCode">',
                html.list_to_options(controller.currencies, "CODE", "DISPLAY"),
                '</select></td><tr>',
                '<tr><td>',
                '<label for="paymentreturn">' + _("Redirect to this URL after successful payment") + '</label></td>',
                '<td><input data="PaymentReturnUrl" id="paymentreturn" type="text" class="asm-textbox asm-doubletextbox" /></td></tr>',
                '</table>',

                '<div id="paypal-options">',
                '<hr/>',
                '<p class="centered"><img height="25px" src="static/images/ui/logo_paypal_100.png" /></p>',
                '<table>',
                '<tr><td><label for="paypalemail">' + _("PayPal Business Email") + '</label></td>',
                '<td><input data="PayPalEmail" id="paypalemail" type="text" class="asm-textbox asm-doubletextbox" /></td></tr>',
                '</table>',
                '<p class="centered">',
                    _("In your PayPal account, enable Instant Payment Notifications with a URL of {0}")
                    .replace("{0}", "<br/><b>" + controller.pp_paypal + "</b>"),
                '</p>',
                '</div>',

                '<div id="stripe-options">',
                '<hr/>',
                '<p class="centered"><img height="25px" src="static/images/ui/logo_stripe_103.png" /></p>',
                '<table>',
                '<tr><td><label for="stripekey">' + _("Stripe Key") + '</label></td>',
                '<td><input data="StripeKey" id="stripekey" type="text" class="asm-textbox asm-doubletextbox" /></td></tr>',
                '<tr><td><label for="stripesecretkey">' + _("Stripe Secret Key") + '</label></td>',
                '<td><input data="StripeSecretKey" id="stripesecretkey" type="text" class="asm-textbox asm-doubletextbox asm-mask" /></td></tr>',
                '</table>',
                '<p class="centered">',
                    _("In the Stripe dashboard, create a webhook to send 'checkout.session.completed' events to {0}")
                    .replace("{0}", "<br/><b>" + controller.pp_stripe + "</b>"),
                '</p>',
                '</div>',

                '<div id="cardcom-options" class="israel">',
                '<hr/>',
                '<p class="centered strong">' + _("Cardcom Payment Gateway")  + '</p>',
                '<table>',
                '<tr><td><label for="CardcomTerminalNumber">' + _("Cardcom Terminal Number") + '</label></td>',
                '<td><input data="CardcomTerminalNumber" id="CardcomTerminalNumber" type="text" class="asm-textbox asm-doubletextbox" /></td></tr>',
                '<tr><td><label for="CardcomUserName">' + _("Cardcom User Name") + '</label></td>',
                '<td><input data="CardcomUserName" id="CardcomUserName" type="text" class="asm-textbox asm-doubletextbox asm-mask" /></td></tr>',

                '<tr><td><label for="CardcomDocumentType">' + _("Cardcom Document Type") + '</label></td>',
                '<td><input data="CardcomDocumentType" id="CardcomDocumentType" type="text" class="asm-textbox asm-doubletextbox" /></td></tr>',


                '<tr><td><label for="CardcomSuccessURL">' + _("Cardcom Success URL") + '</label></td>',
                '<td><input data="CardcomSuccessURL" id="CardcomSuccessURL" type="text" class="asm-textbox asm-doubletextbox" /></td></tr>',

                '<tr><td><label for="CardcomErrorURL">' + _("Cardcom Error URL") + '</label></td>',
                '<td><input data="CardcomErrorURL" id="CardcomErrorURL" type="text" class="asm-textbox asm-doubletextbox" /></td></tr>',

                '<tr><td>&nbsp;</td><td><input data="CardcomUseToken" id="cardcomusetoken" class="asm-checkbox" type="checkbox" /> <label for="cardcomusetoken">' + _("Allow use of tokens") + '</label></td></tr>',
                '</table>',
                '</div>',


                '</div>'
            ].join("\n");
        },

        render_quicklinks: function() {
            return [
                '<div id="tab-quicklinks">',
                '<p>',
                '<input data="QuicklinksHomeScreen" id="disablequicklinkshome" class="asm-checkbox" type="checkbox" /> <label for="disablequicklinkshome">' + _("Show quick links on the home page") + '</label><br />',
                '<input data="QuicklinksAllScreens" id="disablequicklinksall" class="asm-checkbox" type="checkbox" /> <label for="disablequicklinksall">' + _("Show quick links on all pages") + '</label>',
                '<p>',
                html.info(_("Quicklinks are shown on the home page and allow quick access to areas of the system.")),
                '<p style="padding-bottom: 40px">',
                '<select id="quicklinksid" multiple="multiple" class="asm-bsmselect" data="QuicklinksID">',
                this.quicklink_options(),
                '</select>',
                '</p>',
                '</div>'
            ].join("\n");
        },

        render_reminders: function() {
            return [
                '<div id="tab-reminders">',
                html.info(_("Reminder emails can be automatically sent to groups of people a number of days before or after a key event.")),
                '<table>',
                '<thead><tr>',
                '<th></th>',
                '<th>' + _("Days") + '</th>',
                '<th>' + _("Template") + '</th>',
                '<tr>',
                '<td>',
                '<input data="EmailAdopterFollowup" id="adopterfollowup" type="checkbox" class="asm-checkbox" />',
                '<label for="adopterfollowup">' + _("Send a followup email to new adopters after X days") + '</label>',
                '</td>',
                '<td>',
                '<input data="EmailAdopterFollowupDays" id="adopterfollowupdays" data-min="0" data-max="365" class="asm-textbox asm-numberbox" />',
                '</td>',
                '<td>',
                '<select data="EmailAdopterFollowupTemplate" class="asm-selectbox">',
                edit_header.template_list_options(controller.templates),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<label for="adopterfollowupspecies" style="margin-left: 25px;">' + _("Only for these species of adopted animal") + '</label>',
                '</td>',
                '<td colspan="2">',
                '<select id="adopterfollowupspecies" multiple="multiple" class="asm-bsmselect" data="EmailAdopterFollowupSpecies">',
                html.list_to_options(controller.species, "ID", "SPECIESNAME"),
                '</select>',
                '</td>',
                '<tr>',
                '<td>',
                '<input data="EmailClinicReminder" id="clinicreminder" type="checkbox" class="asm-checkbox" />',
                '<label for="clinicreminder">' + _("Send a reminder email to people with clinic appointments in X days") + '</label>',
                '</td>',
                '<td>',
                '<input data="EmailClinicReminderDays" id="clinicreminderdays" data-min="0" data-max="365" class="asm-textbox asm-numberbox" />',
                '</td>',
                '<td>',
                '<select data="EmailClinicReminderTemplate" class="asm-selectbox">',
                edit_header.template_list_options(controller.templatesclinic),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<input data="EmailDuePayment" id="duepayment" type="checkbox" class="asm-checkbox" />',
                '<label for="duepayment">' + _("Send a reminder email to people with payments due in X days") + '</label>',
                '</td>',
                '<td>',
                '<input data="EmailDuePaymentDays" id="duepaymentdays" data-min="0" data-max="365" class="asm-textbox asm-numberbox" />',
                '</td>',
                '<td>',
                '<select data="EmailDuePaymentTemplate" class="asm-selectbox">',
                edit_header.template_list_options(controller.templateslicence),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td>',
                '<input data="EmailLicenceReminder" id="licencereminder" type="checkbox" class="asm-checkbox" />',
                '<label for="licencereminder">' + _("Send a reminder email to people with licenses expiring in X days") + '</label>',
                '</td>',
                '<td>',
                '<input data="EmailLicenceReminderDays" id="licencereminderdays" data-min="0" data-max="365" class="asm-textbox asm-numberbox" />',
                '</td>',
                '<td>',
                '<select data="EmailLicenceReminderTemplate" class="asm-selectbox">',
                edit_header.template_list_options(controller.templateslicence),
                '</select>',
                '</td>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_search: function() {
            return [
                '<div id="tab-search">',
                html.info(_("These options change the behaviour of the search box at the top of the page.")),
                '<p>',
                '<input data="ShowSearchGo" id="showsearchgo" class="asm-checkbox" type="checkbox" /> <label for="showsearchgo">' + _("Display a search button at the right side of the search box") + '</label>',
                '</p>',
                '<table>',
                '<tr>',
                '<td><label for="searchsort">' + _("Search sort order") + '</label></td>',
                '<td><select id="searchsort" class="asm-selectbox" data="SearchSort">',
                '<option value="0">' + _("Alphabetically A-Z") + '</option>',
                '<option value="1">' + _("Alphabetically Z-A") + '</option>',
                '<option value="2">' + _("Least recently changed") + '</option>',
                '<option value="3">' + _("Most recently changed") + '</option>',
                '<option value="6">' + _("Most relevant") + '</option>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_shelterview: function() {
            return [
                '<div id="tab-shelterview">',
                '<table class="asm-left-table">',
                '<tr>',
                '<td><label for="shelterviewdefault">' + _("Default view") + '</label></td>',
                '<td>',
                '<select id="shelterviewdefault" class="asm-selectbox" data="ShelterViewDefault">',
                html.shelter_view_options(),
                '</select>',
                '</td>',
                '</tr>',
                '</table>',
                '<p>',
                '<input data="ShelterViewDragDrop" type="checkbox" id="shelterviewdragdrop" class="asm-checkbox" type="checkbox" /> ',
                    '<label for="shelterviewdragdrop">' + _("Allow drag and drop to move animals between locations") + '</label><br />',
                '<input data="ShelterViewReserves" type="checkbox" id="shelterviewreserves" class="asm-checkbox" type="checkbox" /> ', 
                    '<label for="shelterviewreserves">' + _("Allow units to be reserved and sponsored") + '</label><br />',
                '<input data="ShelterViewShowEmpty" type="checkbox" id="shelterviewempty" class="asm-checkbox" type="checkbox" /> ',
                    '<label for="shelterviewempty">' + _("Show empty locations") + '</label><br />',
                '</p>',
                '</div>'
            ].join("\n");
        },

        render_unwanted: function() {
            return [
                '<div id="tab-unwanted">',
                '<table width="100%">',
                '<tr><td>',
                '<p class="asm-header">' + _("System") + '</p>',
                '<p>',
                '<input data="DisableBoarding" id="disableboarding" class="asm-checkbox" type="checkbox" /> <label for="disableboarding">' + _("Remove boarding functionality from screens and menus") + '</label><br />',
                '<input data="DisableClinic" id="disableclinic" class="asm-checkbox" type="checkbox" /> <label for="disableclinic">' + _("Remove clinic functionality from screens and menus") + '</label><br />',
                '<input data="DisableMovements" id="disablemovements" class="asm-checkbox" type="checkbox" /> <label for="disablemovements">' + _("Remove move menu and the movements tab from animal and person screens") + '</label><br />',
                '<input data="DisableRetailer" id="disableretailer" class="asm-checkbox" type="checkbox" /> <label for="disableretailer">' + _("Remove retailer functionality from the movement screens and menus") + '</label><br />',
                '<input data="DisableDocumentRepo" id="disabledocumentrepo" class="asm-checkbox" type="checkbox" /> <label for="disabledocumentrepo">' + _("Remove the document repository functionality from menus") + '</label><br />',
                '<input data="DisableOnlineForms" id="disableonlineforms" class="asm-checkbox" type="checkbox" /> <label for="disableonlineforms">' + _("Remove the online form functionality from menus") + '</label><br />',
                '<input data="DisableAnimalControl" id="disableanimalcontrol" class="asm-checkbox" type="checkbox" /> <label for="disableanimalcontrol">' + _("Remove the animal control functionality from menus and screens") + '</label><br />',
                '<input data="DisableEvents" id="disableevents" class="asm-checkbox" type="checkbox" /> <label for="disableevents">' + _("Remove the event management functionality from menus and screens") + '</label><br />',
                '<input data="DisableTrapLoan" id="disabletraploan" class="asm-checkbox" type="checkbox" /> <label for="disabletraploan">' + _("Remove the equipment loan functionality from menus and screens") + '</label><br />',
                '<input data="rc:IncidentPermissions" id="incidentpermissions" class="asm-checkbox" type="checkbox" /> <label for="incidentpermissions">' + _("Remove fine-grained animal control incident permissions") + '</label><br />',
                '<input data="DisableRota" id="disablerota" class="asm-checkbox" type="checkbox" /> <label for="disablerota">' + _("Remove the rota functionality from menus and screens") + '</label><br />',
                '<input data="DisableStockControl" id="disablestockcontrol" class="asm-checkbox" type="checkbox" /> <label for="disablestockcontrol">' + _("Remove the stock control functionality from menus and screens") + '</label><br />',
                '<input data="DisableTransport" id="disabletransport" class="asm-checkbox" type="checkbox" /> <label for="disabletransport">' + _("Remove the transport functionality from menus and screens") + '</label><br />',
                '<p class="asm-header">' + _("People") + '</p>',
                '<p>',
                '<input data="HideTownCounty" id="towncounty" class="asm-checkbox" type="checkbox" /> <label for="towncounty">' + _("Remove the city/state fields from person details") + '</label><br />',
                '<input data="HideCountry" id="hcountry" class="asm-checkbox" type="checkbox" /> <label for="hcountry">' + _("Remove the country field from person details") + '</label><br />',
                '<input data="HidePersonDateOfBirth" id="hpdob" class="asm-checkbox" type="checkbox" /> <label for="hpdob">' + _("Remove the date of birth field from person details") + '</label><br />',
                '<input data="HideHomeWorkPhone" id="hidehwphone" class="asm-checkbox" type="checkbox" /> <label for="hidehwphone">' + _("Remove the home and work telephone number fields from person details") + '</label><br />',
                '<input data="HideHomeCheckedNoFlag" id="hhomechecked" class="asm-checkbox" type="checkbox" /> <label for="hhomechecked">' + _("Remove the homechecked/by fields from person type according to the homechecked flag") + '</label><br />',
                '<input data="HideIDNumber" id="hidnumber" class="asm-checkbox" type="checkbox" /> <label for="hidnumber">' + _("Remove the identification number field from person details") + '</label><br />',
                '<input data="DontShowInsurance" id="insuranceno" class="asm-checkbox" type="checkbox" /> <label for="insuranceno">' + _("Remove the insurance number field from the movement screens") + '</label><br />',
                '<input data="HideLookingFor" id="lookingforno" class="asm-checkbox" type="checkbox" /> <label for="lookingforno">' + _("Remove the looking for functionality from the person menus and screens") + '</label><br />',

                '</td><td>',

                '<p class="asm-header">' + _("Animals") + '</p>',
                '<p>',
                '<input data="DisableAsilomar" id="disableasilomar" class="asm-checkbox us" type="checkbox" /> <label for="disableasilomar" class="us">Remove the asilomar fields from the entry/deceased sections</label><br class="us" />',
                '<input data="DisableEntryHistory" id="disableentryhistory" class="asm-checkbox" type="checkbox" /> <label for="disableentryhistory">' + _("Remove the entry history section from animal records") + '</label><br />',
                '<input data="DontShowEntryType" id="entrytype" class="asm-checkbox" type="checkbox" /> <label for="entrytype">' + _("Remove the entry type field from animal entry details") + '</label><br />',
                '<input data="DontShowCoatType" id="coattype" class="asm-checkbox" type="checkbox" /> <label for="coattype">' + _("Remove the coat type field from animal details") + '</label><br />',
                '<input data="DontShowSize" id="size" class="asm-checkbox" type="checkbox" /> <label for="size">' + _("Remove the size field from animal details") + '</label><br />',
                '<input data="DontShowWeight" id="weight" class="asm-checkbox" type="checkbox" /> <label for="weight">' + _("Remove the weight field from animal details") + '</label><br />',
                '<input data="DontShowMicrochip" id="microchip" class="asm-checkbox" type="checkbox" /> <label for="microchip">' + _("Remove the microchip fields from animal identification details") + '</label><br />',
                '<input data="DontShowMicrochipSupplier" id="microchipmf" class="asm-checkbox" type="checkbox" /> <label for="microchipmf">' + _("Remove the microchip supplier info from animal identification details") + '</label><br />',
                '<input data="DontShowTattoo" id="tattoo" class="asm-checkbox" type="checkbox" /> <label for="tattoo">' + _("Remove the tattoo fields from animal identification details") + '</label><br />',
                '<input data="DontShowNeutered" id="neutered" class="asm-checkbox" type="checkbox" /> <label for="neutered">' + _("Remove the neutered fields from animal health details") + '</label><br />',
                '<input data="DontShowDeclawed" id="declawed" class="asm-checkbox" type="checkbox" /> <label for="declawed">' + _("Remove the declawed box from animal health details") + '</label><br />',
                '<input data="DontShowRabies" id="rabiestag" class="asm-checkbox" type="checkbox" /> <label for="rabiestag">' + _("Remove the Rabies Tag field from animal health details") + '</label><br />',
                '<input data="DontShowGoodWith" id="goodwith" class="asm-checkbox" type="checkbox" /> <label for="goodwith">' + _("Remove the good with fields from animal notes") + '</label><br />',
                '<input data="DontShowHeartworm" id="heartworm" class="asm-checkbox" type="checkbox" /> <label for="heartworm">' + _("Remove the heartworm test fields from animal health details") + '</label><br />',
                '<input data="DontShowCombi" id="combitest" class="asm-checkbox" type="checkbox" /> <label for="combitest">' + _("Remove the FIV/L test fields from animal health details") + '</label><br />',
                '<input data="DontShowAdoptionFee" id="fee" class="asm-checkbox" type="checkbox" /> <label for="fee">' + _("Remove the adoption fee field from animal details") + '</label><br />',
                '<input data="DontShowAdoptionCoordinator" id="coordinator" class="asm-checkbox" type="checkbox" /> <label for="coordinator">' + _("Remove the adoption coordinator field from animal entry details") + '</label><br />',
                '<input data="DontShowLitterID" id="litterid" class="asm-checkbox" type="checkbox" /> <label for="litterid">' + _("Remove the Litter ID field from animal details") + '</label><br />',
                '<input data="DontShowLocationUnit" id="subunit" class="asm-checkbox" type="checkbox" /> <label for="subunit">' + _("Remove the location unit field from animal details") + '</label><br />',
                '<input data="DontShowBonded" id="bonded" class="asm-checkbox" type="checkbox" /> <label for="bonded">' + _("Remove the bonded with fields from animal entry details") + '</label><br />',
                '<input data="DontShowJurisdiction" id="jurisdiction" class="asm-checkbox" type="checkbox" /> <label for="jurisdiction">' + _("Remove the jurisdiction field from animal entry details") + '</label><br />',
                '<input data="DontShowPickup" id="pickup" class="asm-checkbox" type="checkbox" /> <label for="pickup">' + _("Remove the picked up fields from animal entry details") + '</label>',
                '</p>',

                '</td></tr></table>',
                '</div>'
            ].join("\n");
        },

        render_reports: function() {
            return [
                '<div id="tab-reports">',
                '<p>',
                '<input data="EmailEmptyReports" id="emptyreports" class="asm-checkbox" type="checkbox" /> <label for="emptyreports">' + _("Email scheduled reports with no data") + '</label><br />',
                '<input data="ReportMenuAccordion" id="reportmenuaccordion" class="asm-checkbox" type="checkbox" /> <label for="reportmenuaccordion">' + _("Show report menu items in collapsed categories") + '</label><br />',
                '</p>',
                '</div>'
            ].join("\n");
        },

        render_security: function() {
            return [
                '<div id="tab-security">',
                '<p>',
                '<input data="Force2FA" id="force2fa" class="asm-checkbox" type="checkbox" /> <label for="force2fa">' + _("Force users to enable 2 factor authentication") + '</label><br />',
                '<input data="ForceStrongPasswords" id="forcestrongpasswords" class="asm-checkbox" type="checkbox" /> <label for="forcestrongpasswords">' + _("Force users to set strong passwords (8+ characters of mixed case and numbers)") + '</label><br />',
                '</p>',
                '</div>'
            ].join("\n");
        },

        render_waitinglist: function() {
            return [
                '<div id="tab-waitinglist">',
                '<p>',
                '<input data="rc:DisableWaitingList" id="disablewl" class="asm-checkbox" type="checkbox" /> <label for="disablewl">' + _("Enable the waiting list functionality") + '</label><br />',
                '<input data="WaitingListRankBySpecies" id="wlrank" class="asm-checkbox" type="checkbox" /> <label for="wlrank">' + _("Separate waiting list rank by species") + '</label>',
                '</p>',
                '<table>',
                '<tr>',
                '<td><label for="wlupdate">' + _("Waiting list urgency update period in days") + '</label>',
                '<span id="callout-wlupdate" class="asm-callout">' + _("Set to 0 to never update urgencies.") + '</span>',
                '</td>',
                '<td>',
                '<input data="WaitingListUrgencyUpdatePeriod" id="wlupdate" data-min="0" data-max="365" class="asm-textbox asm-numberbox" type="text" title="' + _("The period in days before waiting list urgency is increased") + '" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="wldu">' + _("Default urgency") + '</label></td>',
                '<td><select data="WaitingListDefaultUrgency" id="wldu" class="asm-selectbox">',
                html.list_to_options(controller.urgencies, "ID", "URGENCY"),
                '</select>',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="wlremoval">' + _("Default removal after weeks without contact") + '</label>',
                '<span id="callout-wlremoval" class="asm-callout">' + _("Set to 0 to never auto remove.") + '</span>',
                '</td>',
                '<td>',
                '<input data="WaitingListDefaultRemovalWeeks" id="wlremoval" data-min="0" data-max="52" class="asm-textbox asm-numberbox" type="text" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="wlcolumns">' + _("Columns displayed") + '</label></td>',
                '<td>',
                '<select id="wlcolumns" class="asm-bsmselect" data="WaitingListViewColumns" multiple="multiple">',
                this.two_pair_options(controller.waitinglistcolumns),
                '</select>',
                '</tr>',
                '</table>',
                '</div>'
            ].join("\n");
        },

        render_watermark: function() {
            return [
                '<div id="tab-watermark">',
                '<table>',
                '<tr>',
                '<td><label for="watermarkxoffset">' + _("Watermark logo X offset") + '</label>',
                '<span id="callout-watermarkxoffset" class="asm-callout">' + _("Relative to bottom right corner of the image") + '</span>',
                '</td>',
                '<td><input data="WatermarkXOffset" id="watermarkxoffset" data-min="0" data-max="9999" class="asm-textbox asm-numberbox" type="text" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="watermarkyoffset">' + _("Watermark logo Y offset") + '</label>',
                '<span id="callout-watermarkyoffset" class="asm-callout">' + _("Relative to bottom right corner of the image") + '</span>',
                '</td>',
                '<td><input data="WatermarkYOffset" id="watermarkyoffset" data-min="0" data-max="9999" class="asm-textbox asm-numberbox" type="text" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="watermarkfontfillcolor">' + _("Watermark font fill color") + '</label></td>',
                '<td><select data="WatermarkFontFillColor" id="watermarkfontfillcolor" class="asm-selectbox">',
                html.list_to_options_array(this.watermark_colors),
                '</select>',
                '<span id="fontfillcolorsample" style="border: 1px solid black; margin-left: 25px; padding: 0 20px; background: ' + html.decode(config.str('WatermarkFontFillColor')) + '" />',
                '</td>',
                '</tr>',
                '<tr>',
                '<td><label for="watermarkfontshadowcolor">' + _("Watermark font outline color") + '</label></td>',
                '<td><select data="WatermarkFontShadowColor" id="watermarkfontshadowcolor" class="asm-selectbox">',
                html.list_to_options_array(this.watermark_colors),
                '</select>',
                '<span id="fontshadowcolorsample" style="border: 1px solid black; margin-left: 25px; padding: 0 20px; background: ' + html.decode(config.str('WatermarkFontShadowColor')) + '" />',
                '</td>',
                '<tr>',
                '<td><label for="watermarkfontstroke">' + _("Watermark font outline width") + '</label></td>',
                '<td><input data="WatermarkFontStroke" id="watermarkfontstroke" data-min="0" data-max="20" class="asm-textbox asm-numberbox" type="text" /></td>',
                '</tr>',
                '</tr>',
                '<tr>',
                '<td><label for="watermarkfontfile">' + _("Watermark font") + '</label></td>',
                '<td><select data="WatermarkFontFile" id="watermarkfontfile" class="asm-selectbox asm-doubleselectbox">',
                html.list_to_options_array(asm.fontfiles),
                '</select>',
                '<img id="watermarkfontpreview" src="" style="height: 40px; width: 200px; border: 1px solid #000; vertical-align: middle" />',
                '</tr>',
                '<tr>',
                '<td><label for="watermarkfontoffset">' + _("Watermark name offset") + '</label>',
                '<span id="callout-watermarkfontoffset" class="asm-callout">' + _("Offset from left edge of the image") + '</span>',
                '</td>',
                '<td><input data="WatermarkFontOffset" id="watermarkfontoffset" data-min="0" data-max="100" class="asm-textbox asm-numberbox" type="text" /></td>',
                '</tr>',
                '<tr>',
                '<td><label for="watermarkfontmaxsize">' + _("Watermark name max font size") + '</label></td>',
                '<td><input data="WatermarkFontMaxSize" id="watermarkfontmaxsize" data-min="0" data-max="999" class="asm-textbox asm-numberbox" type="text" /></td>',
                '</tr>',
                '</table>',
                '</div>',
            ].join("\n");
        },

        render: function() {
            return [
                html.content_header(_("System Options")),
                '<div class="asm-toolbar">',
                '<button id="button-save" title="' + _("Update system options") + '">' + html.icon("save") + ' ' + _("Save") + '</button>',
                '</div>',
                '<div id="tabs">',
                this.render_tabs(),
                this.render_shelterdetails(),
                this.render_accounts(),
                this.render_adding(),
                this.render_agegroups(),
                this.render_animalcodes(),
                this.render_animalemblems(),
                this.render_boarding(),
                this.render_checkout(),
                this.render_costs(),
                this.render_daily_observations(),
                this.render_data_protection(),
                this.render_defaults(),
                this.render_diaryandmessages(),
                this.render_display(),
                this.render_documents(),
                this.render_email(),
                this.render_findscreens(),
                this.render_homepage(),
                this.render_insurance(),
                this.render_lostandfound(),
                this.render_medical(),
                this.render_movements(),
                this.render_onlineforms(),
                this.render_processors(),
                this.render_quicklinks(),
                this.render_reminders(),
                this.render_search(),
                this.render_shelterview(),
                this.render_unwanted(),
                this.render_reports(),
                this.render_security(),
                this.render_waitinglist(),
                this.render_watermark(),
                '</div>',
                html.content_footer()
            ].join("\n");
        },

        bind: function() {
            const get_donation_mappings = function() {
                let mappings = "";
                $(".donmap").each(function() {
                    let mapname = $(this).val();
                    let idx = $(this).attr("data-idx");
                    let mapvalue = $("#mapac" + idx).val();
                    if (mapname && mapname != "-1" && mapvalue && mapvalue != "-1") {
                        if (mappings != "") { mappings += ","; }
                        mappings += mapname + "=" + mapvalue;
                    }
                });
                return encodeURIComponent(mappings);
            };

            // Toolbar buttons
            $("#button-save").button().click(async function() {
                $("#button-save").button("disable");
                validate.dirty(false);
                let formdata = "mode=save&" + $("input, select, textarea, .asm-richtextarea").not(".chooser").toPOST(true);
                formdata += "&DonationAccountMappings=" + get_donation_mappings();
                header.show_loading(_("Saving..."));
                await common.ajax_post("options", formdata);
                // Needs to do full reload to get updated config.js
                common.route_reload(true); 
            });

            // Components
            $("#tabs").tabs({ show: "slideDown", hide: "slideUp" });

            $("#button-save").button("disable");

            // Load default values from the config settings
            $("input, select, textarea, .asm-richtextarea").each(function() {
                if ($(this).attr("data")) {
                    let d = $(this).attr("data");
                    if ($(this).is(".asm-currencybox")) {
                        $(this).val( html.decode(config.currency(d)));
                    }
                    else if ($(this).is(".asm-richtextarea")) {
                        $(this).richtextarea("value", config.str(d));
                    }
                    else if ($(this).is("input:text")) {
                        if ($(this).is(".asm-mask") && config.str(d)) { $(this).val(MASK_VALUE); }
                        else { $(this).val( html.decode(config.str(d))); }
                    }
                    else if ($(this).is("input:checkbox")) {
                        if (d.indexOf("rc:") != -1) {
                            // it's a reverse checkbox, not it before setting
                            if (!config.bool(d.substring(3))) {
                                $(this).attr("checked", "checked");
                            }
                        }
                        else if (config.bool(d)) {
                            $(this).attr("checked", "checked");
                        }
                    }
                    else if ($(this).is("input:hidden")) {
                        $(this).val( config.str(d));
                    }
                    else if ($(this).is(".asm-selectbox") && $(this).is(".decode")) {
                        $(this).select("value", html.decode(config.str(d)));
                    }
                    else if ($(this).is(".asm-selectbox") || $(this).is(".asm-doubleselectbox")) {
                        $(this).select("value", config.str(d));
                    }
                    else if ($(this).is(".asm-bsmselect")) {
                        let ms = config.str(d).split(",");
                        let bsm = $(this);
                        $.each(ms, function(i, v) {
                            bsm.find("option[value='" + common.trim(v + "']")).attr("selected", "selected");
                        });
                        $(this).change();
                    }
                    else if ($(this).is("textarea")) {
                        $(this).val( html.decode(config.str(d)));
                    }
                    else if ($(this).is(".asm-richtextarea")) {
                        $(this).richtextarea("value", config.str(d));
                    }
                }
            });

            // Set donation type maps from DonationAccountMappings field
            let donmaps = config.str("DonationAccountMappings");
            if (donmaps != "") {
                let maps = donmaps.split(",");
                $.each(maps, function(i, v) {
                    let dt = v.split("=")[0];
                    let ac = v.split("=")[1];
                    let idx = i + 1;
                    $("#mapdt" + idx).select("value", dt);
                    $("#mapac" + idx).select("value", ac);
                });
            }

            // Hide options not applicable for some locales
            if (asm.locale != "en") {
                $(".us").hide();
            }
            if (asm.locale != "he" && asm.locale != "en_IL") {
                $(".israel").hide();
            }

            // Hide other non-relevant options
            if (!controller.haspaypal) {
                $("#paypal-options").hide();
            }
            if (!asm.smcom) {
                $(".smcom").hide();
            }

            // Show sample colours and fonts when selected
            $("#watermarkfontfillcolor").change(function() {
                $("#fontfillcolorsample").css("background-color", $("#watermarkfontfillcolor").select("value"));
            });
            $("#watermarkfontshadowcolor").change(function() {
                $("#fontshadowcolorsample").css("background-color", $("#watermarkfontshadowcolor").select("value"));
            });
            $("#watermarkfontfile").change(function() {
                $("#watermarkfontpreview").prop("src", "options_font_preview?fontfile=" + $("#watermarkfontfile").val());
            });
            $("#watermarkfontfile").change();

            validate.bind_dirty();

        },

        destroy: function() {
            validate.unbind_dirty();
            common.widget_destroy("#DefaultBroughtInBy", "personchooser");
        },

        name: "options",
        animation: "options",
        autofocus: "#organisation",
        title: function() { return _("Options"); },
        routes: {
            "options": function() { common.module_loadandstart("options", "options"); }
        }

    };

    common.module_register(options);

});
