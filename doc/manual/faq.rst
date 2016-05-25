Appendix: Frequently Asked Questions
====================================

How do I add new vaccination types, breeds or internal locations?
-----------------------------------------------------------------

Go to :menuselection:`Settings --> Lookup Data`, and then choose them from the
dropdown list at the upper right side of the screen.

How do I bring an animal back to the shelter after adoption, transfer or fostering?
-----------------------------------------------------------------------------------

Open the animal's record and go the Movements tab. Find the current adoption,
transfer or foster movement, edit it and set a return date.

Where do I get some reports?
----------------------------

Go to :menuselection:`Settings --> Reports`, then click the "Browse
sheltermanager.com" button.  You can choose reports from the list and use the
"Install" button to add them to your database.

Why am I seeing "animal not in location filter/site" when I open a record?
--------------------------------------------------------------------------

You've applied a "location filter" to your account. A location filter is a list
of locations attached to a user account that prohibits the user from seeing
animals who are not in one of those locations. To remove it, go to
:menuselection:`Settings --> System user accounts` and remove the location
filter items from your account.

Why do I get "page 1 of 1" in the header when I print documents?
----------------------------------------------------------------

Your web browser is adding these header and footers. Where you turn them off depends on your
web browser:

* Internet Explorer: Open Page Setup from the printer icon on the toolbar or
  File menu. Delete the header and footer strings in the "Headers and Footers"
  section

* Firefox: Choose Page Setup from the File menu (press ALT if it is not
  visible). Click on the Margins & Header/Footer tab and choose --blank-- from
  all the dropdowns in the Headers and Footers section.

* Chrome: Untick the "Print headers and footers" box in the print preview
  screen.

Why are ASM emails being sent from bounce+account@sheltermanager.com?
---------------------------------------------------------------------

In the early days of email, address spoofing was used by everyone. It was
an easy way ensuring an email came back to you no matter what servers your
message passed through.

Unfortunately, this also made it easy for spammers to fake where their emails
were coming from and to send a lot of backscatter (failure notices) to innocent
victims.

Most large email services today, such as gmail, hotmail and yahoo use
technologies called SPF and DKIM. These allow a domain to state which mail
servers are allowed to relay email on its behalf. For example, the hotmail.com
domain states that nothing but the hotmail servers are allowed to send 
any messages that come from a hotmail.com address.

When a message arrives at an email server using these technologies, it checks
the domain the email is from and then checks to see whether the server it
received that message from is allowed to send email for that domain. If it
isn't, the message is put straight into the spam folder of the recipient or in
some cases, rejected outright.

This is very helpful in filtering spam, but it means that ASM cannot send
emails that appear to come from your address (particularly if you have a
hotmail or gmail address) - otherwise most mail services will either refuse
delivery of your message or put it straight in the spam folder for the
recipient. 

Instead, ASM sends emails from the fixed address you configured in sitedefs and
trusts you know what you're doing.  sheltermanager.com sends emails from a
bounce+account@sheltermanager.com address. Your real email address is set in
the Reply-To email header, which email clients will honour when someone replies
to your message. So while they'll see the message as appearing to come from
bounce+account@sheltermanager.com, when they hit the reply button in their
email client, the email they create will have a to address of you@youremail.com
instead.

In the case of sheltermanager.com, if someone does accidentally reply to a
bounce+account@sheltermanager.com address, the sheltermanager email server will
find your account and send the email through to you, or find a Reply-To header
in the quoted message if one exists and send it to that.

Why has my colour scheme reset?
-------------------------------

Originally, ASM allowed you to set a system-wide theme for all users. It no
longer does this. We decided  to remove that behaviour so that users are all
given a consistent starting point and so that what users see on screen
when they start using the system matches the screenshots in the documentation 
and help videos.

All users can override their theme if they would like something else by
clicking on their username at the top right, and then the "Change User
Settings" menu option.

