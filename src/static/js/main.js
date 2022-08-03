/*global $, jQuery, _, asm, common, config, controller, dlgfx, edit_header, format, header, html, validate, Path */

$(function() {

    "use strict";

    const main = {

        render_active_users: function() {
            let s = "", loggedin = _("Active users: {0}"), userlist = [];
            $.each(controller.activeusers.split(","), function(i, u) {
                let since = u.split("=")[1], user = u.split("=")[0];
                userlist.push("<a class='activeuser' title='" + html.title(since) + "' href='#'>" + user + "</a>");
            });
            s += '<div id="footer">';
            s += '<div class="asm-footer-users">' + common.substitute(loggedin, { "0": userlist.join(", ")}) + '</div>';
            s += '<div class="asm-footer-version">';
            s += common.substitute('<a id="link-about" href="#">{asm} {version} {user}@{org}</a>', {
                "asm":      _("ASM"),
                "version":  controller.version.substring(0, controller.version.indexOf(" ")),
                "user":     asm.user,
                "org":      config.str("Organisation")});
            s += '</div>';
            s += '</div>';
            return s;
        },

        tip: function() {
            const tips = [ 
                _("You can middle click a link to open it in a new browser tab (push the wheel on most modern mice)."),
                _("You can bookmark search results, animals, people and most data entry screens."),
                _("Most browsers will let you visit a record you have been to in this session by typing part of its name in the address bar."),
                _("Most browsers let you search in dropdowns by typing the first few letters of the item you want."),
                _("Entering 'deceased' in the search box will show you recently deceased animals."),
                _("Entering 'os' in the search box will show you all shelter animals."),
                _("Entering 'notforadoption' in the search box will show you all shelter animals with the not for adoption flag set."),
                _("Entering 'fosterers', 'homecheckers', 'staff', 'volunteers', 'aco' or 'members' in the search box will show you those groups of people."),
                _("You can sort tables by clicking on the column headings."),
                _("Some browsers allow shortcut keys, press SHIFT+ALT+A in Chrome or Firefox to jump to the animal adoption screen."),
                _("Use the icon in the lower right of notes fields to view them in a separate window."),
                _("You can prefix your term in the search box with a: to search only animals, p: to search only people, wl: to search waiting list entries, la: to search lost animals and fa: to search found animals."),
                _("ASM 3 is compatible with your iPad and other tablets."),
                _("Entering 'activelost' or 'activefound' in the search box will show you lost and found animals reported in the last 30 days."),
                _("You can override the search result sort by adding one of the following to the end of your search - sort:az, sort:za, sort:mr, sort:lr"),
                _("When you use Move > Adopt an animal, ASM will automatically return any open foster or retailer movement before creating the adoption."),
                _("When you use Move > Foster an animal, ASM will automatically return any open foster movement before moving the animal to its new home."),
                _("When entering dates, hold down CTRL and use the cursor keys to move around the calendar. Press t to go to today."),
                _("You can upload images called logo.jpg and splash.jpg to the Settings, Reports, Extra Images screen to override the login splash screen and logo in the upper left corner of the application."),
                _("ASM can track detailed monthly and annual figures for your shelter. Install the Monthly Figures and Annual Figures reports from Settings-Reports-Browse sheltermanager.com"),
                _("ASM comes with a dictionary of 4,000 animal names. Just click the generate random name button when adding an animal."),
                _("You can set a default amount for different payment types in the Settings, Lookup Data screen. Very handy when creating adoptions."),
                _("You can drag and drop animals in shelter view to change their locations."),
                _("Lots of reports installed? Clean up the Reports menu with Settings, Options, Display, Show report menu items in collapsed categories."),
                _("Press F11 in HTML or SQL code editing boxes to edit in fullscreen mode")
            ];
            return tips[Math.floor(Math.random() * tips.length)];
        },

        render_alerts: function() {
            let s = "", alerts;
            if (!config.bool("ShowAlertsHomePage")) { return; }
            if (!controller.alerts || controller.alerts.length == 0) { return; }
            alerts = controller.alerts[0];
            let totalalerts = 0;
            s += '<p class="asm-menu-category">' + _("Alerts") + ' (<span id="totalalerts"></span>)</p><p>';
            if (alerts.DUEVACC > 0 && common.has_permission("vav")) {
                totalalerts += alerts.DUEVACC;
                s += '<a href="vaccination">' + html.icon("vaccination") + ' ' + 
                    common.ntranslate(alerts.DUEVACC, [ 
                        _("{plural0} vaccination needs to be administered today"), 
                        _("{plural1} vaccinations need to be administered today"),
                        _("{plural2} vaccinations need to be administered today"),
                        _("{plural3} vaccinations need to be administered today")
                    ]) + '</a><br />';
            }
            if (alerts.EXPVACC > 0 && common.has_permission("vav")) {
                totalalerts += alerts.EXPVACC;
                s += '<a href="vaccination?offset=xm365">' + html.icon("vaccination") + ' ' + 
                    common.ntranslate(alerts.EXPVACC, [ 
                        _("{plural0} vaccination has expired"), 
                        _("{plural1} vaccinations have expired"),
                        _("{plural2} vaccinations have expired"),
                        _("{plural3} vaccinations have expired")
                    ]) + '</a><br />';
            }
            if (alerts.DUETEST > 0 && common.has_permission("vat")) {
                totalalerts += alerts.DUETEST;
                s += '<a href="test">' + html.icon("test") + ' ' + 
                    common.ntranslate(alerts.DUETEST, [ 
                        _("{plural0} test needs to be performed today"), 
                        _("{plural1} tests need to be performed today"),
                        _("{plural2} tests need to be performed today"),
                        _("{plural3} tests need to be performed today")
                    ]) + '</a><br />';
            }
            if (alerts.DUEMED > 0 && common.has_permission("mvam")) {
                totalalerts += alerts.DUEMED;
                s += '<a href="medical">' + html.icon("medical") + ' ' + 
                    common.ntranslate(alerts.DUEMED, [
                        _("{plural0} medical treatment needs to be administered today"),
                        _("{plural1} medical treatments need to be administered today"),
                        _("{plural2} medical treatments need to be administered today"),
                        _("{plural3} medical treatments need to be administered today")
                    ]) + '</a><br />';
            }
            if (alerts.DUECLINIC > 0 && common.has_permission("vcl")) {
                totalalerts += alerts.DUECLINIC;
                s += '<a href="clinic_waitingroom">' + html.icon("health") + ' ' + 
                    common.ntranslate(alerts.DUECLINIC, [
                        _("{plural0} clinic appointment today"),
                        _("{plural1} clinic appointments today"),
                        _("{plural2} clinic appointments today"),
                        _("{plural3} clinic appointments today")
                    ]) + '</a><br />';
            }

            if (alerts.URGENTWL > 0 && common.has_permission("vwl")) {
                totalalerts += alerts.URGENTWL;
                s += '<a href="waitinglist_results?priorityfloor=1">' + html.icon("waitinglist") + ' ' + 
                    common.ntranslate(alerts.URGENTWL, [
                        _("{plural0} urgent entry on the waiting list"),
                        _("{plural1} urgent entries on the waiting list"),
                        _("{plural2} urgent entries on the waiting list"),
                        _("{plural3} urgent entries on the waiting list")
                    ]) + '</a><br />';
            }
            if (alerts.RSVHCK > 0 && config.bool("WarnNoHomeCheck") && common.has_permission("vo")) {
                totalalerts += alerts.RSVHCK;
                s += '<a href="search?q=reservenohomecheck">' + html.icon("person") + ' ' + 
                    common.ntranslate(alerts.RSVHCK, [
                        _("{plural0} person with an active reservation has not been homechecked"),
                        _("{plural1} people with active reservations have not been homechecked"),
                        _("{plural2} people with active reservations have not been homechecked"),
                        _("{plural3} people with active reservations have not been homechecked")
                    ]) + '</a><br />';
            }
            if (alerts.LONGRSV > 0 && common.has_permission("vamv")) {
                totalalerts += alerts.LONGRSV;
                s += '<a href="move_book_reservation">' + html.icon("reservation") + ' ' + 
                    common.ntranslate(alerts.LONGRSV, [
                        _("{plural0} reservation has been active over a week without adoption"),
                        _("{plural1} reservations have been active over a week without adoption"),
                        _("{plural2} reservations have been active over a week without adoption"),
                        _("{plural3} reservations have been active over a week without adoption")
                    ]) + '</a><br />';
            }
            if (alerts.NOTNEU > 0 && common.has_permission("va") && config.bool("EmblemUnneutered") ) {
                totalalerts += alerts.NOTNEU;
                s += '<a href="move_book_unneutered">' + html.icon("unneutered") + ' ' + 
                    common.ntranslate(alerts.NOTNEU, [
                        _("{plural0} unaltered animal has been adopted in the last month"),
                        _("{plural1} unaltered animals have been adopted in the last month"),
                        _("{plural2} unaltered animals have been adopted in the last month"),
                        _("{plural3} unaltered animals have been adopted in the last month")
                    ]) + '</a><br />';
            }
            if (alerts.NOTRAB > 0 && common.has_permission("va") && config.bool("EmblemRabies") ) {
                totalalerts += alerts.NOTRAB;
                s += '<a href="search?q=norabies">' + html.icon("rabies") + ' ' + 
                    common.ntranslate(alerts.NOTRAB, [
                        _("{plural0} animal has not had a rabies vaccination"),
                        _("{plural1} animals have not had a rabies vaccination"),
                        _("{plural2} animals have not had a rabies vaccination"),
                        _("{plural3} animals have not had a rabies vaccination")
                    ]) + '</a><br />';
            }
            if (alerts.NOTCHIP > 0 && common.has_permission("va") && config.bool("EmblemNotMicrochipped") ) {
                totalalerts += alerts.NOTCHIP;
                s += '<a href="search?q=notmicrochipped">' + html.icon("microchip") + ' ' + 
                    common.ntranslate(alerts.NOTCHIP, [
                        _("{plural0} shelter animal has not been microchipped"),
                        _("{plural1} shelter animals have not been microchipped"),
                        _("{plural2} shelter animals have not been microchipped"),
                        _("{plural3} shelter animals have not been microchipped")
                    ]) + '</a><br />';
            }
            if (alerts.DUEDON > 0 && common.has_permission("ovod")) {
                totalalerts += alerts.DUEDON;
                s += '<a href="donation?offset=d0">' + html.icon("donation") + ' ' + 
                    common.ntranslate(alerts.DUEDON, [
                        _("{plural0} person has an overdue payment"),
                        _("{plural1} people have overdue payments"),
                        _("{plural2} people have overdue payments"),
                        _("{plural3} people have overdue payments")
                    ]) + '</a><br />';
            }
            if (alerts.ENDTRIAL > 0 && common.has_permission("vamv")) {
                totalalerts += alerts.ENDTRIAL;
                s += '<a href="move_book_trial_adoption">' + html.icon("trial") + ' ' + 
                    common.ntranslate(alerts.ENDTRIAL, [
                        _("{plural0} trial adoption has ended"),
                        _("{plural1} trial adoptions have ended"),
                        _("{plural2} trial adoptions have ended"),
                        _("{plural3} trial adoptions have ended")
                    ]) + '</a><br />';
            }
            if (alerts.DOCUNSIGNED > 0 && common.has_permission("vo")) {
                totalalerts += alerts.DOCUNSIGNED;
                s += '<a href="search?q=unsigned">' + html.icon("signature") + ' ' + 
                    common.ntranslate(alerts.DOCUNSIGNED, [
                        _("{plural0} document signing request issued in the last month is unsigned"),
                        _("{plural1} document signing requests issued in the last month are unsigned"),
                        _("{plural2} document signing requests issued in the last month are unsigned"),
                        _("{plural3} document signing requests issued in the last month are unsigned")
                    ]) + '</a><br />';
            }
            if (alerts.DOCSIGNED > 0 && common.has_permission("vo")) {
                totalalerts += alerts.DOCSIGNED;
                s += '<a href="search?q=signed">' + html.icon("signature") + ' ' + 
                    common.ntranslate(alerts.DOCSIGNED, [
                        _("{plural0} document signing request has been received in the last week"),
                        _("{plural1} document signing requests have been received in the last week"),
                        _("{plural2} document signing requests have been received in the last week"),
                        _("{plural3} document signing requests have been received in the last week")
                    ]) + '</a><br />';
            }
            if (alerts.NOTADOPT > 0 && common.has_permission("va") && config.bool("EmblemNotForAdoption")) {
                totalalerts += alerts.NOTADOPT;
                s += '<a href="search?q=notforadoption">' + html.icon("notforadoption") + ' ' + 
                    common.ntranslate(alerts.NOTADOPT, [
                        _("{plural0} animal is not available for adoption"),
                        _("{plural1} animals are not available for adoption"),
                        _("{plural2} animals are not available for adoption"),
                        _("{plural3} animals are not available for adoption")
                    ]) + '</a><br />';
            }
            if (alerts.LNGTERM > 0 && common.has_permission("va") && config.bool("EmblemLongTerm")) {
                totalalerts += alerts.LNGTERM;
                s += '<a href="search?q=longterm">' + html.icon("calendar") + ' ' + 
                    common.ntranslate(alerts.LNGTERM, [
                        _("{plural0} animal has been on the shelter longer than {0} months").replace("{0}", config.integer("LongTermMonths")),
                        _("{plural1} animals have been on the shelter longer than {0} months").replace("{0}", config.integer("LongTermMonths")),
                        _("{plural2} animals have been on the shelter longer than {0} months").replace("{0}", config.integer("LongTermMonths")),
                        _("{plural3} animals have been on the shelter longer than {0} months").replace("{0}", config.integer("LongTermMonths"))
                    ]) + '</a><br />';
            }

            if (alerts.HOLDTODAY > 0 && common.has_permission("va") && config.bool("EmblemHold")) {
                totalalerts += alerts.HOLDTODAY;
                s += '<a href="search?q=holdtoday">' + html.icon("hold") + ' ' + 
                    common.ntranslate(alerts.HOLDTODAY, [
                        _("{plural0} animal has a hold ending today"),
                        _("{plural1} animals have holds ending today"),
                        _("{plural2} animals have holds ending today"),
                        _("{plural3} animals have holds ending today")
                    ]) + '</a><br />';
            }
            if (alerts.INFORM > 0 && common.has_permission("vif")) {
                totalalerts += alerts.INFORM;
                s += '<a href="onlineform_incoming">' + html.icon("forms") + ' ' + 
                    common.ntranslate(alerts.INFORM, [
                        _("{plural0} new online form submission"),
                        _("{plural1} new online form submissions"),
                        _("{plural2} new online form submissions"),
                        _("{plural3} new online form submissions")
                    ]) + '</a><br />';
            }
            if (alerts.LOOKFOR > 0 && common.has_permission("vcr")) {
                totalalerts += alerts.LOOKFOR;
                s += '<a href="person_lookingfor">' + html.icon("animal-find") + ' ' + 
                    common.ntranslate(alerts.LOOKFOR, [
                        _("{plural0} shelter animal has people looking for them"),
                        _("{plural1} shelter animals have people looking for them"),
                        _("{plural2} shelter animals have people looking for them"),
                        _("{plural3} shelter animals have people looking for them")
                    ]) + '</a><br />';
            }
            if (alerts.LOSTFOUND > 0 && common.has_permission("mlaf")) {
                totalalerts += alerts.LOSTFOUND;
                s += '<a href="lostfound_match">' + html.icon("match") + ' ' + 
                    common.ntranslate(alerts.LOSTFOUND, [
                        _("{plural0} potential match for a lost animal"),
                        _("{plural1} potential matches for lost animals"),
                        _("{plural2} potential matches for lost animals"),
                        _("{plural3} potential matches for lost animals")
                    ]) + '</a><br />';
            }
            if (alerts.PUBLISH > 0 && common.has_permission("uipb")) {
                totalalerts += alerts.PUBLISH;
                s += '<a href="publish_logs">' + html.icon("web") + ' ' + 
                    common.ntranslate(alerts.PUBLISH, [
                        _("{plural0} recent publisher run had errors"),
                        _("{plural1} recent publisher runs had errors"),
                        _("{plural2} recent publisher runs had errors"),
                        _("{plural3} recent publisher runs had errors")
                    ]) + '</a><br />';
            }
            if (alerts.ACUNFINE > 0 && common.has_permission("vaci")) {
                totalalerts += alerts.ACUNFINE;
                s += '<a href="citations?filter=unpaid">' + html.icon("donation") + ' ' + 
                    common.ntranslate(alerts.ACUNFINE, [
                        _("{plural0} unpaid fine"),
                        _("{plural1} unpaid fines"),
                        _("{plural2} unpaid fines"),
                        _("{plural3} unpaid fines")
                    ]) + '</a><br />';
            }
            if (alerts.ACUNDISP > 0 && common.has_permission("vaci")) {
                totalalerts += alerts.ACUNDISP;
                s += '<a href="incident_find_results?filter=undispatched">' + html.icon("call") + ' ' + 
                    common.ntranslate(alerts.ACUNDISP, [
                        _("{plural0} undispatched animal control call"),
                        _("{plural1} undispatched animal control calls"),
                        _("{plural2} undispatched animal control calls"),
                        _("{plural3} undispatched animal control calls")
                    ]) + '</a><br />';
            }
            if (alerts.ACFOLL > 0 && common.has_permission("vaci")) {
                totalalerts += alerts.ACFOLL;
                s += '<a href="incident_find_results?filter=requirefollowup">' + html.icon("call") + ' ' + 
                    common.ntranslate(alerts.ACFOLL, [
                        _("{plural0} animal control call due for followup today"),
                        _("{plural1} animal control calls due for followup today"),
                        _("{plural2} animal control calls due for followup today"),
                        _("{plural3} animal control calls due for followup today")
                    ]) + '</a><br />';
            }
            if (alerts.ACUNCOMP > 0 && common.has_permission("vaci")) {
                totalalerts += alerts.ACUNCOMP;
                s += '<a href="incident_find_results?filter=incomplete">' + html.icon("call") + ' ' + 
                    common.ntranslate(alerts.ACUNCOMP, [
                        _("{plural0} incomplete animal control call"),
                        _("{plural1} incomplete animal control calls"),
                        _("{plural2} incomplete animal control calls"),
                        _("{plural3} incomplete animal control calls")
                    ]) + '</a><br />';
            }
            if (alerts.TLOVER > 0 && common.has_permission("vatl")) {
                totalalerts += alerts.TLOVER;
                s += '<a href="traploan?filter=active">' + html.icon("traploan") + ' ' + 
                    common.ntranslate(alerts.TLOVER, [
                        _("{plural0} trap is overdue for return"),
                        _("{plural1} traps are overdue for return"),
                        _("{plural2} traps are overdue for return"),
                        _("{plural3} traps are overdue for return")
                    ]) + '</a><br />';
            }
            if (alerts.STEXP > 0 && common.has_permission("vsl")) {
                totalalerts += alerts.STEXP;
                s += '<a href="stocklevel?sortexp=1">' + html.icon("stock") + ' ' + 
                    common.ntranslate(alerts.STEXP, [
                        _("{plural0} item of stock has expired"),
                        _("{plural1} items of stock have expired"),
                        _("{plural2} items of stock have expired"),
                        _("{plural3} items of stock have expired")
                    ]) + '</a><br />';
            }
            if (alerts.STEXPSOON > 0 && common.has_permission("vsl")) {
                totalalerts += alerts.STEXPSOON;
                s += '<a href="stocklevel?sortexp=1">' + html.icon("stock") + ' ' + 
                    common.ntranslate(alerts.STEXPSOON, [
                        _("{plural0} item of stock expires in the next month"),
                        _("{plural1} items of stock expire in the next month"),
                        _("{plural2} items of stock expire in the next month"),
                        _("{plural3} items of stock expire in the next month")
                    ]) + '</a><br />';
            }
            if (alerts.TRNODRV > 0 && common.has_permission("vtr")) {
                totalalerts += alerts.TRNODRV;
                s += '<a href="transport">' + html.icon("transport") + ' ' + 
                    common.ntranslate(alerts.TRNODRV, [
                        _("{plural0} transport does not have a driver assigned"),
                        _("{plural1} transports do not have a driver assigned"),
                        _("{plural2} transports do not have a driver assigned"),
                        _("{plural3} transports do not have a driver assigned")
                    ]) + '</a><br />';
            }
            s += '</p>';
            main.total_alerts = totalalerts;
            return s;
        },

        render_animal_links: function() {
            let s = [];
            let callout = '<span class="asm-callout" id="callout-linkstale">';
            callout +=  _("Animal links, Timeline, Stats and Alerts shown on this screen may be upto {0} minutes out of date due to caching.").replace("{0}", (controller.age / 60));
            callout += '</span>';
            if (controller.linkname != "none" && controller.animallinks.length > 0) {
                s.push('<p class="asm-menu-category">' + controller.linkname + ' ' + callout + '</p>');
                $.each(controller.animallinks, function(i, a) {
                    // Skip this one if the animal is deceased and we aren't showing them
                    if (!config.bool("ShowDeceasedHomePage") && a.DECEASEDDATE) { return; }
                    s.push('<div class="asm-shelterview-animal">');
                    s.push(html.animal_link_thumb(a, { showlocation: true }));
                    s.push("</div>");
                });
            }
            return s.join("\n");
        },

        render_diary: function() {
            let s = "";
            s += '<p class="asm-menu-category"><a href="diary_edit_my">' + common.substitute(_("Diary for {0}"), {"0": asm.user }) + '</a> ';
            s += '<button id="button-adddiary">' + _("Add a diary note") + '</button>';
            s += '<button id="button-diarycal">' + _("Calendar view") + '</button></p>';
            s += '<table class="asm-main-table asm-underlined-rows">';
            s += '<tbody>';
            $.each(controller.diary, function(i, d) {
                let link = "#";
                if (d.LINKTYPE == 1) { link = "animal?id=" + d.LINKID; }
                if (d.LINKTYPE == 2) { link = "person?id=" + d.LINKID; }
                if (d.LINKTYPE == 3) { link = "lostanimal?id=" + d.LINKID; }
                if (d.LINKTYPE == 4) { link = "foundanimal?id=" + d.LINKID; }
                if (d.LINKTYPE == 5) { link = "waitinglist?id=" + d.LINKID; }
                if (d.LINKTYPE == 7) { link = "incident?id=" + d.LINKID; }
                s += '<tr title="' + html.title(common.substitute(_("Added by {0} on {1}"), { "0": d.CREATEDBY, "1": format.date(d.CREATEDDATE) })) + '">';
                s += '<td>' + format.date(d.DIARYDATETIME);
                if (d.DIARYFORNAME != asm.user) {
                    s += " <i>(" + d.DIARYFORNAME + ")</i>";
                }
                s += '</td>';
                s += '<td style="width: 20%">' + d.SUBJECT + '</td>';
                s += '<td>';
                if (d.LINKINFO != null && d.LINKINFO != "") {
                    s += '<a href="' + link + '">' + d.LINKINFO + '</a><br />';
                }
                s += d.NOTE + '</td></tr>';
            });
            s += '</tbody></table>';
            return s;
        },

        render_messages: function() {
            let s = "";

            s += '<p class="asm-menu-category">' + _("Message Board") + ' <button id="button-addmessage">' + _("Add Message") + '</button></p>';
            s += '<table id="asm-messageboard" class="asm-main-table asm-underlined-rows"><tbody>';

            $.each(controller.mess, function(i, m) {
                s += '<tr><td><span style="white-space: nowrap; padding-right: 5px;">';
                if (m.CREATEDBY == asm.user || m.FORNAME == asm.user || asm.superuser == 1) {
                    s += '<button class="messagedelete" data="' + m.ID + '">' + _("Delete") + '</button>';
                }
                s += '<a href="#" class="activeuser">' + m.CREATEDBY + '</a>';
                if (m.FORNAME != "*") {
                    s += html.icon("right") + m.FORNAME;
                }
                s += '</span></td>';
                s += '<td><span style="white-space: nowrap; padding-right: 5px;">';
                if (m.PRIORITY == 1) {
                    s += '<span class="ui-icon ui-icon-alert" title="' + html.title(_('Important')) + '"></span>';
                }
                else {
                    s += '<span class="ui-icon ui-icon-info" title="' + html.title(_('Information')) + '"></span>';
                }
                s += format.date(m.ADDED);
                s += '</span></td>';
                if (m.PRIORITY == 1) {
                    s += '<td id="mt' + m.ID + '">';
                    s += '<span class="mtext" style="font-weight: bold !important">' + html.truncate(m.MESSAGE) + '</span>';
                    s += '<a class="messagetoggle" href="#" data="' + m.ID + '"></a>';
                    s += '</td>';
                }
                else {
                    s += '<td id="mt' + m.ID + '">';
                    s += '<span class="mtext">' + html.truncate(m.MESSAGE) + '</span>';
                    s += '<a class="messagetoggle" href="#" data="' + m.ID + '"></a>';
                    s += '</td>';
                }
            });
            s += '</tr></tbody></table>';

            $.each(controller.mess, function(i, m) {
                s += '<input id="long' + m.ID + '" type="hidden" value="' + html.title(common.replace_all(m.MESSAGE, "\n", "<br/>")) + '" />';
                s += '<input id="short' + m.ID + '" type="hidden" value="' + html.title(html.truncate(m.MESSAGE)) + '" />';
            });
            return s;
        },

        render_stats: function() {
            let s = "", stats, displayname;
            if (config.str("ShowStatsHomePage") == "none") { return; }
            if (!controller.stats || controller.stats.length == 0) { return; }
            stats = controller.stats[0];
            if (config.str("ShowStatsHomePage") == "today") {
                displayname = _("Shelter stats (today)");
            }
            else if (config.str("ShowStatsHomePage") == "thisweek") {
                displayname = _("Shelter stats (this week)");
            }
            else if (config.str("ShowStatsHomePage") == "thismonth") {
                displayname = _("Shelter stats (this month)");
            }
            else if (config.str("ShowStatsHomePage") == "thisyear") {
                displayname = _("Shelter stats (this year)");
            }
            else if (config.str("ShowStatsHomePage") == "alltime") {
                displayname = _("Shelter stats (all time)");
            }
            s += '<p class="asm-menu-category">' + displayname + '</p><p>';
            if (stats.ENTERED > 0 && common.has_permission("va")) {
                s += html.icon("animal") + ' ' + common.ntranslate(stats.ENTERED, [
                    _("{plural0} animal entered the shelter"),
                    _("{plural1} animals entered the shelter"),
                    _("{plural2} animals entered the shelter"),
                    _("{plural3} animals entered the shelter")
                    ]) + '<br />';
            }
            if (stats.ADOPTED > 0 && common.has_permission("vamv")) {
                s += html.icon("movement") + ' ' + common.ntranslate(stats.ADOPTED, [
                    _("{plural0} animal was adopted"),
                    _("{plural1} animals were adopted"),
                    _("{plural2} animals were adopted"),
                    _("{plural3} animals were adopted")
                    ]) + '<br />';
            }
            if (stats.RECLAIMED > 0 && common.has_permission("vamv")) {
                s += html.icon("person") + ' ' + common.ntranslate(stats.RECLAIMED, [
                    _("{plural0} animal was reclaimed by its owner"),
                    _("{plural1} animals were reclaimed by their owners"),
                    _("{plural2} animals were reclaimed by their owners"),
                    _("{plural3} animals were reclaimed by their owners")
                    ]) + '<br />';
            }
            if (stats.TRANSFERRED > 0 && common.has_permission("vamv")) {
                s += html.icon("book") + ' ' + common.ntranslate(stats.TRANSFERRED, [
                    _("{plural0} animal was transferred to another shelter"),
                    _("{plural1} animals were transferred to other shelters"),
                    _("{plural2} animals were transferred to other shelters"),
                    _("{plural3} animals were transferred to other shelters")
                    ]) + '<br />';
            }
            if (stats.RELEASED > 0 && common.has_permission("vamv")) {
                s += html.icon("book") + ' ' + common.ntranslate(stats.RELEASED, [
                    _("{plural0} animal was released to wild"),
                    _("{plural1} animals were released to wild"),
                    _("{plural2} animals were released to wild"),
                    _("{plural3} animals were released to wild")
                    ]) + '<br />';
            }
            if (stats.TNR > 0 && common.has_permission("vamv")) {
                s += html.icon("book") + ' ' + common.ntranslate(stats.TNR, [
                    _("{plural0} animal was TNR"),
                    _("{plural1} animals were TNR"),
                    _("{plural2} animals were TNR"),
                    _("{plural3} animals were TNR")
                    ]) + '<br />';
            }
            if (stats.PTS > 0 && common.has_permission("va") && config.bool("ShowDeceasedHomePage")) {
                s += html.icon("death") + ' ' + common.ntranslate(stats.PTS, [
                    _("{plural0} animal was euthanized"),
                    _("{plural1} animals were euthanized"),
                    _("{plural2} animals were euthanized"),
                    _("{plural3} animals were euthanized")
                    ]) + '<br />';
            }
            if (stats.DIED > 0 && common.has_permission("va") && config.bool("ShowDeceasedHomePage")) {
                s += html.icon("death") + ' ' + common.ntranslate(stats.DIED, [
                    _("{plural0} animal died"),
                    _("{plural1} animals died"),
                    _("{plural2} animals died"),
                    _("{plural3} animals died")
                    ]) + '<br />';
            }
            if (stats.DOA > 0 && common.has_permission("va") && config.bool("ShowDeceasedHomePage")) {
                s += html.icon("death") + ' ' + common.ntranslate(stats.DOA, [
                    _("{plural0} animal was dead on arrival"),
                    _("{plural1} animals were dead on arrival"),
                    _("{plural2} animals were dead on arrival"),
                    _("{plural3} animals were dead on arrival")
                    ]) + '<br />';
            }

            if (stats.DONATIONS > 0 && common.has_permission("ovod") && config.bool("ShowFinancialHomePage")) {
                s += html.icon("donation") + ' ' + 
                    _("{0} received").replace("{0}", format.currency(stats.DONATIONS))
                    + '<br />';
            }
            if (stats.COSTS > 0 && common.has_permission("cvad") && config.bool("ShowFinancialHomePage")) {
                s += html.icon("cost") + ' ' + 
                    _("{0} incurred in costs").replace("{0}", format.currency(stats.COSTS))
                    + '<br />';
            }
            s += '</p>';
            return s;
        },

        render_timeline: function() {
            let h = [];
            if (!config.bool("ShowTimelineHomePage") || !common.has_permission("va")) { return; }
            h.push('<p class="asm-menu-category"><a href="timeline">' + _("Timeline ({0})").replace("{0}", controller.recent.length) + '</a></p><p>');
            $.each(controller.recent, function(i, v) {
                // Skip this entry if it's for a deceased animal and we aren't showing them
                if (!config.bool("ShowDeceasedHomePage") && (v.CATEGORY == "DIED" || v.CATEGORY == "EUTHANISED")) { return; }
                h.push(html.event_text(v, { includedate: true }) + '<br/>');
            });
            return h.join("\n");
        },

        render: function() {
            let h = [
            '<div id="dialog-welcome" title="' + _('Welcome!') + '" style="display: none">',
            '<h2 class="centered">' + _("Welcome!") + '</h2>',
            '<div class="ui-state-highlight ui-corner-all" style="margin-top: 5px; padding: 5px;">',
            '<p><span class="ui-icon ui-icon-info"></span>',
            _("Thank you for choosing Animal Shelter Manager for your shelter!") + '<br/>',
            _("Here are some things you should do before you start adding animals and people to your database."),
            '</p>',
            '</div>',
            '<div class="ui-state-highlight ui-corner-all" style="margin-top: 5px; padding: 5px;">',
            '<p><span class="ui-icon ui-icon-gear"></span>',
            '<a href="options" target="_blank"><b>',
            _("Settings") + html.icon("right") + _("Options") + '</b></a>',
            _("Go to the options screen and set your shelter's contact details and other settings."),
            '</p>',
            '</div>',
            '<div class="ui-state-highlight ui-corner-all" style="margin-top: 5px; padding: 5px;">',
            '<p><span class="ui-icon ui-icon-note"></span>',
            '<a href="lookups" target="_blank"><b>',
            _("Settings") + html.icon("right") + _("Lookup data") + '</b></a>',
            _("Go to the lookup data screen and add/remove breeds, species and animal types according to the animals your shelter deals with."),
            '</p>',
            '</div>',
            '<div class="ui-state-highlight ui-corner-all" style="margin-top: 5px; padding: 5px;">',
            '<p><span class="ui-icon ui-icon-person"></span>',
            '<a href="systemusers" target="_blank"><b>',
            _("Settings") + html.icon("right") + _("System user accounts") + '</b></a>',
            _("Go to the system users screen and add user accounts for your staff."),
            '</p>',
            '</div>',
            '<div class="ui-state-highlight ui-corner-all" style="margin-top: 5px; padding: 5px;">',
            '<p><span class="ui-icon ui-icon-print"></span>',
            '<a href="reports?browse=true" target="_blank"><b>',
            _("Settings") + html.icon("right") + _("Reports") + '</b></a>',
            _("Browse sheltermanager.com and install some reports, charts and mail merges into your new system."),
            '</p>',
            '</div>',
            '<div class="ui-state-highlight ui-corner-all" style="margin-top: 5px; padding: 5px;">',
            '<p><span class="ui-icon ui-icon-star"></span>',
            '<a href="static/pages/manual/index.html" target="_blank"><b>' + _("Manual") + '</b></a>',
            _("Read the manual for more information about Animal Shelter Manager."),
            '</p>',
            '</div>',
            '</div> ',

            '<div id="dialog-about" style="display: none" title="' + _("About") + '">',
            '<p class="asm-main-about-version">',
            '<img src="static/images/logo/icon-128.png" />',
             _("ASM") + ' ' + controller.version + '</p>',
             '<p class="asm-main-about-browser">', 
             common.substitute(_("{browser} version {version}, running on {os}."), {
                 "browser": "<b>" + common.browser_info().name + "</b>",
                 "version": "<b>" + common.browser_info().version + "</b>",
                 "os": "<b>" + navigator.platform + "</b>"
            }),
            '</p>',
            '<div id="changelog">',
                '<textarea class="asm-textarea" readonly="readonly" style="width: 650px; height: 400px;"></textarea>',
            '</div>',
            '</div>',

            '<div id="dialog-addmessage" style="display: none" title="' + _("Add message") + '">',
            '<div class="ui-state-highlight ui-corner-all" style="margin-top: 20px; padding: 0 .7em">',
            '<p><span class="ui-icon ui-icon-info"></span>',
            _("All fields should be completed."),
            '</p>',
            '</div>',
            '<table width="100%">',
            '<tr>',
            '<td><label for="forname">' + _("For") + '</label></td>',
            '<td><select id="forname" class="asm-selectbox" data="forname" type="textbox">',
            '<option value="*">' + _("(everyone)") + '</option>',
            html.list_to_options(controller.usersandroles, "USERNAME", "USERNAME"),
            '</select></td>',
            '</tr>',
            '<tr>',
            '<td><label for="priority">' + _("Priority") + '</label></td>',
            '<td><select id="priority" class="asm-selectbox" data="priority" type="textbox">',
            '<option value="0">' + _("Information") + '</option>',
            '<option value="1">' + _("Important") + '</option>',
            '</select></td>',
            '</tr>',
            '<tr>',
            '<td><label for="expires">' + _("Expires") + '</label></td>',
            '<td><input id="expires" class="asm-textbox asm-datebox" data="expires" type="textbox" title="' + _("When ASM should stop showing this message") + '" /></td>',
            '</tr>',
            '<tr>',
            '<td></td>',
            '<td><input id="email" class="asm-checkbox" data="email" type="checkbox" title="' + _("Email this message to all matching users") + '" /><label for="email">' + _("Send via email") + '</label></td>',
            '</tr>',
            '<tr>',
            '<td><label for="message">' + _("Message") + '</label></td>',
            '<td><textarea id="message" class="asm-textarea" rows="4" data="message"></textarea></td>',
            '</tr>',
            '</table>',
            '</div>',

            '<div id="asm-content" class="ui-helper-reset ui-widget-content ui-corner-all" style="padding: 10px;">',
            this.render_animal_links(),
            '<div class="asm-main-columns">',
            '<div id="asm-main-diary" class="asm-main-column">',
            this.render_diary(),
            controller.diary.length < 3 ? this.render_timeline() : "",
            '</div>',
            '<div class="asm-main-column">',
            this.render_alerts(),
            this.render_messages(),
            controller.diary.length >= 3 ? this.render_timeline() : "",
            this.render_stats(),
            '<p class="asm-menu-category">',
            '<a id="newstoggle" href="#">',
            '<span id="newsnav" class="ui-icon ui-icon-triangle-1-e"></span>',
            _("ASM News"),
            '<span id="newsunread"></span>',
            '</a>',
            '</p>',
            '<span id="newswrapper" style="display: none">',
            controller.news,
            '</span>',
            '</div>',
            '</div>',
            this.render_active_users(),
            '</div>'
            ];
            return h.join("\n");
        },

        bind: function () {

            if (controller.dbmessage != "") {
                header.show_info(controller.dbmessage);
            }

            if (asm.smcom && asm.smcomexpiry) {
                let warnat = new Date(format.date_js(asm.smcomexpiry).getTime() - (1000 * 60 * 60 * 24 * 5)),
                    stopwarnat = format.date_js(asm.smcomexpiry),
                    now = new Date();
                if (now >= warnat && now < stopwarnat) {
                    header.show_info(_("Your sheltermanager.com account is due to expire on {0}, please renew {1}")
                        .replace("{0}", asm.smcomexpirydisplay).replace("{1}", asm.smcompaymentlink), 20000);
                }
            }

            if (!common.has_permission("vdn")) { $("#asm-main-diary").hide(); }

            let message_buttons = {}; 
            message_buttons[_("Create this message")] = async function() { 
                if (!validate.notblank(["expires", "message"])) { return; }
                $("#dialog-addmessage").disable_dialog_buttons();
                let formdata = "mode=addmessage&" + $("#dialog-addmessage .asm-textbox, #dialog-addmessage textarea, #dialog-addmessage select, #dialog-addmessage .asm-checkbox").toPOST();
                try {
                    await common.ajax_post("main", formdata);
                    let h = "<tr>\n";
                    h += "<td>\n";
                    h += "<span style=\"white-space: nowrap; padding-right: 5px;\">" + asm.user + "</span>\n";
                    h += "</td><td>";
                    h += "<span style=\"white-space: nowrap; padding-right: 5px;\">";
                    if ($("#priority").val() == 1) {
                        h += '<span class="ui-icon ui-icon-alert"></span>\n';
                    }
                    else {
                        h += '<span class="ui-icon ui-icon-info"></span>\n';
                    }
                    h += $("#expires").val();
                    h += "</span></td>";
                    if ($("#priority").val() == 1) {
                        h += '<td><span class="mtext" style="font-weight: bold !important">' + $("#message").val() + '</span></td>\n';
                    }
                    else {
                        h += '<td><span class="mtext">' + $("#message").val() + '</span></td>\n';
                    }
                    h += "</tr>";
                    $("#asm-messageboard > tbody:first").prepend(h);
                }
                finally {
                    $("#dialog-addmessage").enable_dialog_buttons();
                    $("#dialog-addmessage").dialog("close");
                }
            };
            message_buttons[_("Cancel")] = function() { $(this).dialog("close"); };

            $("#dialog-addmessage").dialog({
                autoOpen: false,
                width: 750,
                modal: true,
                dialogClass: "dialogshadow",
                show: dlgfx.add_show,
                hide: dlgfx.add_hide,
                buttons: message_buttons,      
                close: function() {
                    $("#dialog-addmessage .asm-textbox").val("");
                    validate.reset("dialog-addmessage");
                }
            });

            let welcome_buttons = {};
            welcome_buttons[_("I've finished, Don't show me this popup again.")] = {
                text: _("I've finished, Don't show me this popup again."),
                "class": "asm-dialog-actionbutton",
                click: function() {
                    let formdata = "mode=showfirsttimescreen";
                    common.ajax_post("main", formdata);
                    $(this).dialog("close");
                }
            };
            welcome_buttons[_("Close")] = function() { $(this).dialog("close"); };

            $("#dialog-welcome").dialog({
                autoOpen: false,
                width: 750,
                modal: true,
                dialogClass: "dialogshadow",
                show: dlgfx.add_show,
                hide: dlgfx.add_hide,
                buttons: welcome_buttons
            });

            let about_buttons = {};
            about_buttons[_("Close")] = function() {
                $(this).dialog("close");
            };

            $("#dialog-about").dialog({
                autoOpen: false,
                width: 680,
                modal: true,
                dialogClass: "dialogshadow",
                show: dlgfx.zoom_show,
                hide: dlgfx.zoom_hide,
                buttons: about_buttons
            });

            $("#link-about").click(async function() {
                header.show_loading();
                let changelog = await common.ajax_get("static/pages/changelog.txt");
                $("#changelog>textarea").text(changelog);
                $("#dialog-about").dialog("open");
                return false; // squash href #
            });

            $(".activeuser").each(function() {
               let t = $(this);
               t.click(function() {
                   $("#forname").select("value", t.text());
                   $("#dialog-addmessage").dialog("open");
                   return false; // squash href #
               });
            });

            $("#button-adddiary")
                .button({ icons: { primary: "ui-icon-circle-plus" }, text: false })
                .click(function() {
                common.route("diary_edit_my?newnote=1");
            });

            $("#button-diarycal")
                .button({ icons: { primary: "ui-icon-calendar" }, text: false })
                .click(function() {
                common.route("calendarview?ev=d");
            });

            $("#button-addmessage")
                .button({ icons: { primary: "ui-icon-circle-plus" }, text: false })
                .click(function() {
                if (config.bool("EmailMessages")) { $("#email").attr("checked", true); }
                $("#dialog-addmessage").dialog("open");
            });

            $(".messagedelete")
                .button({ icons: { primary: "ui-icon-trash" }, text: false })
                .click(async function() {
                    let t = $(this), formdata = "mode=delmessage&id=" + String(t.attr("data"));
                    await common.ajax_post("main", formdata);
                    t.closest("tr").fadeOut(); 
                });

            $(".messagetoggle").each(function() {
                let data = $(this).attr("data");
                let moretext = " " + _("more");
                let ldv = $("#long" + data).val();
                let sdv = $("#short" + data).val();
                if (ldv.length != sdv.length) {
                    $(this).html(moretext);
                }
            });

            $(".messagetoggle").click(function() {
                let data = $(this).attr("data");
                let moretext = " " + _("more");
                let lesstext = " " + _("less");
                let mt = $("#mt" + data + " .mtext");
                let ldv = $("#long" + data).val();
                let sdv = $("#short" + data).val();
                let ar = $(this);
                if (ldv.length != sdv.length) {
                    if (ar.text() == moretext) {
                        mt.fadeOut(function() {
                            mt.html(ldv);
                            mt.fadeIn();
                            ar.html(lesstext);
                        });
                    }
                    else {
                        mt.fadeOut(function() {
                            mt.html(sdv);
                            mt.fadeIn();
                            ar.html(moretext);
                        });
                    }
                }
                return false;
            });

            $("#newstoggle").click(function() {
                if ($("#newsnav").hasClass("ui-icon-triangle-1-e")) {
                    $("#newsnav").removeClass("ui-icon-triangle-1-e");
                    $("#newsnav").addClass("ui-icon-triangle-1-s");
                    $("#newswrapper").fadeIn();
                    // Mark all news seen for this user
                    main.max_news_user = main.max_news_story;
                    common.local_set(asm.user + "_news", main.max_news_story);
                    $("#newsunread").html("(0)");
                }
                else {
                    $("#newsnav").removeClass("ui-icon-triangle-1-s");
                    $("#newsnav").addClass("ui-icon-triangle-1-e");
                    $("#newswrapper").fadeOut();
                }
                return false;
            });

            // Put a random tip in the box
            $("#tip").html(this.tip());

            if (controller.showwelcome) {
                $("#dialog-welcome").dialog("open");
            }
        },

        /** The highest story number from the news feed */
        max_news_story: 0,

        /** The highest story number the current user has seen */
        max_news_user: 0,

        /** The calculated total number of visible alerts */
        total_alerts: 0,

        sync: function() {

            // add a class to the html element for desktop or mobile
            if (typeof asm !== "undefined" && asm.mobileapp) { 
                $("html").removeClass("desktop");
                $("html").addClass("mobile"); 
            }
            else { 
                $("html").removeClass("mobile");
                $("html").addClass("desktop"); 
            }

            // If there's been a new deployment of ASM since we last
            // downloaded it to the browser, reload the page using the
            // new build number to invalidate the cache (passing a b
            // parameter also triggers the backend to invalidate config
            // and sets noreload to prevent any potential reload loops)
            if (asm.build != controller.build && !controller.noreload) {
                common.route("main?b=" + controller.build, true);
            }

            // What's the highest news story available in the DOM/newsfeed?
            $("#newswrapper p").each(function() {
                let t = $(this), ds = format.to_int(t.attr("data-story"));
                if (ds > main.max_news_story) { main.max_news_story = ds; }
            });

            // What's the highest news story this person has seen?
            main.max_news_user = format.to_int(common.local_get(asm.user + "_news"));
            $("#newsunread").html( "(" + (main.max_news_story - main.max_news_user) + ")" );

            // Set the total alerts
            $("#totalalerts").text( main.total_alerts );

        },

        destroy: function() {
            common.widget_destroy("#dialog-addmessage");
            common.widget_destroy("#dialog-welcome");
        },

        name: "main",
        animation: "main",
        title: function() { return _("Animal Shelter Manager") + " - " + config.str("Organisation"); },

        routes: {
            "main": function() {
                common.module_loadandstart("main", "main?" + this.rawqs);
            }
        }


    };

    common.module_register(main);

});
