Options
=======

The main :menuselection:`Settings --> Options` page allows configuring of the
general preferences within Animal Shelter Manager. 

Shelter Details
---------------

The shelter details tab allows you to enter contact information for your
shelter. This is used with reporting and internet publishing.

The “Server Adjustment” box allows you to set a time offset in hours from the
server clock. This is only necessary if your client is in a different timezone
from the server. For example, the main sheltermanager.com servers are in the
UK. East coast Americans will want to adjust the time by -5 hours to make sure
alerts appear at the correct time and reports are shown correctly.

Accounts
--------

ASM contains a full double entry accounting package. The options here are: 

* Enable Accounts Functionality: Unticking this box will cause ASM to remove
  all accounts related menu entries/buttons so that users do not see it, and
  you will not be using ASM to manage your accounts. 

* Creating payments and payments types creates matching accounts and
  transactions: When you create a new payment type, or log a new payment
  against an owner/animal, ASM will automatically create a matching account in
  the accounts system if one does not exist, and a matching transaction. 

* Creating costs and cost types creates matching accounts and
  transactions: When you create a new cost type, or log a new cost
  against an animal, ASM will automatically create a matching account in
  the accounts system if one does not exist, and a matching transaction.

* When receiving payments, allow the deposit account to be overridden: When
  adding payments to the system, if you have the create matching transactions
  option on as well as this one, a destination account dropdown will be shown
  on payment screens allowing you to override the deposit account that the
  donation will be applied to (the withdrawal account is always the donation
  type's matching income account).

* When receiving payments, allow a quantity and unit price to be set: When
  adding payments to the system, allow a quantity and unit price to be included
  for multiple item purchases/payments.

* When receiving payments, allow a transaction fee to be set: Allows a 
  transaction fee to be recorded with the payment (eg: The cut taken by
  services like PayPal, Amazon Payments, Google Wallet, Stripe, etc).

* When receiving payments, allow recording of sales tax with a default rate of %:
  ASM can calculate and store sales tax/VAT/GST amounts on payments you receive
  for taxable goods. Enabling this option will add a tickbox to all payment
  screens allowing you to calculate the taxable value (assumes your amount is
  gross and inclusive of tax/VAT/GST).

* When calculating sales tax, assume the payment amount is net and add it:
  Not everyone charges for items that are inclusive of tax and don't have the 
  full amount to hand. With this option on, when the system calculates the sales
  tax/VAT/GST on your payment amount, it will calculate it as if the amount was
  exclusive of tax and then add it to the amount so that it becomes a gross
  amount, inclusive of tax. Eg: $50 at 20% will produce $10 tax and the amount
  will become $60 with this option on. With it off, tax will be calculated
  as $8.33 for $50.

* When receiving multiple payments, allow the due and received dates to be set:
  If this option is on, due and received date columns will be shown when taking
  payments from the Move screens and Receive a Payment screen.

* Only show account totals for the current period, which starts on: If you wish
  to use accounting periods, put the start date in here. By enabling the show
  account totals for current period option, the totals shown on the account
  screen will only include transactions from this date or later. 

* Default transaction view: When viewing transactions for an account, ASM will
  show transactions matching this time period. The default is the current
  month.

* Default source account for costs: When ASM creates a matching cost
  transaction, it will use the cost type to find the expense account to use.
  The source account here denotes where the money will be moved from. If you do
  not set one, ASM will use the first bank account on file. 

* Default destination account for payments: When ASM creates a matching
  payment transaction, it will use the payment type to find the income
  account to use. The destination account here denotes where the money will be
  moved to. If you do not set one, ASM will use the first bank account on file. 

* Income account for sales tax: If you are creating matching transactions from
  payment records and there is a tax/VAT/GST value present, the system will
  write a transaction to deposit the tax into the target bank account from the
  income account you nominate here, giving you an easy way to track your
  tax burden while keeping your bank balances correct.

* Expense account for transaction fees: If you are creating matching
  transactions from payment records and there is a fee present, the system will
  write a transaction to deduct the fee from the target bank account and send
  it to the expense account you nominate here.

* Donations of type … are sent to ...: In addition to the default payment
  destination account, you can specify optional mappings, so that when ASM
  receives a payment of a particular type, it uses the specified destination
  account for it when creating the matching accounting transaction. 

Add Animal
----------

ASM allows you to bulk add more than one animal at a time by just hitting the
“Create” button on the new animal screen instead of “Create and Edit” - this is
useful if booking in a litter of kittens and puppies for example. Here, you can
choose some extra fields for the new animal screen.

* Show breed field(s): Allow entry of a breed

* Use a single breed field for animals: Setting this option will make ASM only
  display a single breed field on the animal details screen. This is the norm
  for UK shelters, where animals are either pedigree or a crossbreed (a
  “Crossbreed” breed can be added to the lookup). Without this option set, ASM
  allows for two breed fields and a crossbreed indicator so that mixed breed
  type animals can be recorded (this is typical for US shelters). 

* OR only show the second breed field for these species of animals: If the
  "use a single breed field for animals" option is not enabled, restrict
  display of the second breed field to only these species of animals. 

* Show the color field: Allow entry of a specific colour

* Show the adoption fee field: Allow entry of an adoption fee

* Show the internal location field: Allow entry of an internal location 

* Show the location unit field: Allow a cage/pen/kennel/hutch number to be set

* Allow a fosterer to be selected: Allow new animals to be fostered straight
  away

* Allow an adoption coordinator to be selected: Allow assignment of an adoption
  coordinator

* Show the litter ID field: Allow a litter ID

* Show the size field: Allow entry of the size

* Show the weight field: Allow entry of the weight

* Show the altered fields: Allow an altered date to be set 

* Show the microchip fields: Allow a microchip date/number to be set 

* Show the entry category field: Allow an entry category to be set 

* Show the original owner field: Allow original owner to be set

* Show the pickup fields: Allow pickup location/address to be set

* Show the brought in by field: Allow brought in by to be set

* Show the transfer in field: Allow incoming transfers to be set

* Show the hold fields: Allow hold and hold until date to be set

* Warn if the animal is similar to one entered recently: Pop up a warning
  dialog if the animal's name is the same as one entered recently to help
  prevent possible duplicates.

Age Groups
----------

It is possible to categorise your animals by their age in ASM. This is useful
when generating adoption paperwork and you don't have an exact date of birth
for the animal. Instead, ASM can specify one if its groups, using the AgeGroup
wordkey (or animal.AgeGroup field in custom reports).

This tab allows you to choose the threshold for each grouping, as well as the
grouping name. By default, anything under 6 months (0.5 years) is classed as a
Baby, anything under 2 years is Young Adult, under 7 years is Adult and over
that is Senior. 

Animal Codes
------------

ASM allows you to choose the format that animal codes will be automatically
generated in. ASM internally stores two codes for each animal, the “normal”
code, unique among all animals and the “short” code. The short code does not
have to be unique and is used by staff wanting to quickly identify animals in
conversation.

The defaults are TYYYYNNN (the first letter of the animal type, followed by the
year it was brought to the shelter, followed by a number unique within that
year for that type of animal) for the normal code and NNT for the shortcode (a
unique number within the year for the animal's type, followed by the type). 

You can build and use any format string you like, using the following tokens: 

* YYYY - The year the animal was brought into the shelter (4 digits) 

* YY - The year the animal was brought into the shelter (2 digits) 

* MM - The month the animal was brought into the shelter 

* DD - The day the animal was brought into the shelter 

* E - The first letter of the animal's entry category

* EE - The first and second letters of the animal's entry category

* S - The first letter of the animal's species

* SS - The first and second letters of the animal's species 

* T - The first letter of the animal's type 

* TT – The first and second letters of the animal's type

* UUUUUUUUUU - (10 digits) a unique number representing the animal (this number
  will never be used for another animal), padded to 10 digits. If the number
  overflows, more digits will be used. 

* UUUU - (4 digits) a unique number representing the animal (this number will
  never be used for another animal), padded to 4 digits. If the number
  overflows, more digits will be used. 

* XXX - (3 digits) a number which is unique for all animals within the year

* XX - A number which is unique for all animals within the year, no padding is
  done.

* NNN - (3 digits) a number representing the animal, which is unique within the
  year brought in for the animal's type and padded to 3 digits. If the number
  overflows, more digits will be used. 

* NN - A number representing the animal, which is unique within the year
  brought in for the animal's type. No padding is done. 

Here are some examples: 

* YYYYMMDD-NNN-T (an ISO date, followed by a unique number/type within the
  year). Eg: 20080520-001-D 

* TUUUUUUUUUU (the animal's type, followed by a unique number for the animal) -
  Eg: U0000003412 

If you change the coding formats when you already have animals on file using a
different format, those animals will be ignored when creating new codes and
multiple codes can co-exist.

Any values you put in your codes other than these tokens (such as punctuation
or other letters) will not be substituted and will be retained in generated
codes. For example, the format NNN:21:T will produce 001:21:D for the first dog
of the year. 

* Manually enter codes (do not generate): This option tells ASM that you don't
  want it to generate any codes. A code field will appear on the add animal
  screen and apart from enforcing that codes are unique, ASM will do nothing
  with the values entered by the user. Shortcodes can also be manually entered
  unless the option to remove the box below is ticked.

* Show short shelter codes on screens: This option tells ASM to display the
  short code throughout the application instead of the main shelter code. 

* Remove short shelter code box from the animal details screen: Setting this
  option will make ASM hide the short shelter code field at the top left of the
  animal details screen. It does not stop ASM generating short codes behind the
  scenes, it just stops them being visible on the screen. 

* Show codes on the shelter view screen: This option tells ASM to display the
  code with the animal's name on the shelter view screen and animal links on
  the home page.

* Once assigned, codes cannot be changed: Setting this option will make ASM
  lock the shelter code fields, as well as the type and brought in date once an
  animal record has been saved for the first time. This is to guarantee that
  once an animal code has been handed out, it cannot be changed.

* Allow duplicate microchip numbers: By default, the system will prevent you
  entering or saving animals with a microchip number that has already been
  allocated. In some situations this is desirable (for example, for figures
  purposes some shelters prefer to create new animal records every time they
  see an animal regardless of whether it has been through the shelter before). 

* Allow duplicate license numbers: By default, the system will prevent you
  entering or saving licenses with a number that has already been used.
  Some licensing regions use a tag number that stays with the animal for
  life and need to allow duplicate licenses as a result.

Boarding
--------

The boarding tab allows configuration of the boarding tab that appears on
person records, and animals who are not in care.

* Boarding payment type: The payment type to use when creating due payments
  from a boarding record with the "Create Payment" toolbar button.

Checkout
--------

The checkout tab allows you to configure automated checkouts that take payment
from members of the public (eg: for adoptions and license renewals).

* Payment Processor: The payment processor to use for taking checkout payments.

* Adoption paperwork template: A document template to use for generating
  adoption paperwork.

* Adoption fee payment type: The payment type to use when creating a payment
  record for the adoption fee.

* Donation payment type: The payment type to use when creating a payment record
  for a donation during adoption checkout.

* Payment method: The payment method to assign to the fee/donation payment
  records.

* Donation message: The message shown at the top of the adoption checkout
  donate screen. Limited HTML formatting tags can be used here, such as <b>,
  <u>, <i> and <br/>

* Donation tiers: The available options adopters have for making a donation.
  They are in the form amount=description. Currency symbols should be included
  in the amount. You should include a zero/0 donation tier unless you want to
  force your adopters to leave a donation. 

Costs
-----

The costs tab allows you to specify a default daily boarding cost for new
animals (this value can be modified on the animal's cost tab). 

* Create boarding cost record when animal is adopted: If set, then during
  adoption the total daily boarding cost for the animal will be converted to a
  cost a record and given the boarding cost type.

* Show a cost field on medical/test/vaccination screens: If set, a cost amount
  box will be shown on medical, test and vaccination screens to store the cost
  of treatments the animal received (this can then be reported on).

* Show a separate paid date field with costs: If you would like to track the
  date a cost was paid separately from the date a cost was incurred, tick this
  box.

Daily Observations
------------------

This tab allows you to configure the values that are requested on the
:ref:`dailyobservations` screen, along with the log type used for the 
records written.

The left column contains the name of the value, and the right the available
values. If the right column is empty, the user will be given a free text box to
enter a value. Otherwise, the right column should contain a pipe-separated list
of the values available to show in a dropdown. 

Data Protection
---------------

This tab allows configuration of how long ASM should keep certain types of data
before removing them. These settings can be used to enforce data retention
policies instigated as part of data protection compliance.

* Anonymize personal data after this many years: If this option is on, the 
  system will automatically anonymize person records this many years after
  their creation. Anonymizing will blank the name, email, address and telephone 
  fields. The city, state and zipcode (town, county and postcode for other locales)
  will be retained along with the rest of the person data for statistics
  and reporting. This option helps organisations in the EU to comply with 
  data retention policies and the GDPR by removing identifiable personal data.

  To be anonymized, a record needs to be older than the retention period, and
  all payments, clinic appointments, boarding records, vouchers, licenses,
  movements or log entries attached to the person must be older than the
  retention period.  The person record cannot have any flag that indicates an
  ongoing relationship with the shelter. These flags are: 

   aco, adoptioncoordinator, driver, retailer, homechecker, member, shelter, foster, staff, vet, volunteer

.. warning:: Once anonymized, personal data is gone forever and cannot be recovered.

* Never anonymize people who adopted an animal: If this option is set, people
  with the adopter flag are included in the list of people who will never be
  anonymized.

* Remove HTML and PDF document media after this many years: If this option is
  on, the system will automatically delete HTML and PDF document media this
  many years after its creation.

.. warning:: Once deleted, documents are gone forever and cannot be recovered.

* Remove animal media this many years after the animal dies or leaves the shelter:
  If this option is on, the system will automatically remove animal media a 
  set number years after the animal dies or leaves the shelter. 

.. warning:: Once deleted, media is gone forever and cannot be recovered.

* Remove people with a cancelled reservation who have not had any other contact
  after this many years: Shelters receive many applications to adopt animals,
  many of which can be unsuccessful. This option will completely delete (not
  anonymise) people records where their only contact with the shelter is a
  cancelled reservation that is X years old. The same rules as above for
  anonymization apply in that anyone with an ongoing relationship with the
  shelter or a previous adoption will be excluded. 

* Show GDPR Contact Opt-In field on person screens: If this option is on, the
  system will show a contact opt-in field on person records. You can use it to
  specify which forms of communication a person prefers. When saving the
  record, if "Email" is not in the list of preferred communication methods, the
  "Exclude from bulk email" flag will automatically be set on the person's
  record.

* When I set a new GDPR Opt-In contact option, make a note of it in the log
  with this type: This option will automatically log any changes to the contact
  opt-in field so that the person who changed it along with the date and time
  are recorded in the log.

Defaults
--------

This screen allows configuration of the system defaults. These defaults are
used to select starting values when finding and creating animals and other
records.

* Mark new animals as not for adoption: Setting this option will cause ASM to
  automatically tick the “not for adoption” box when creating new animals. This
  is an extra precaution - by forcing users to untick the box when necessary,
  no animal can be accidentally published. 

* Exclude new animal photos from publishing: Setting this option will make
  any photos uploaded to the media tab not sent by the publishers or included
  in any websites. If an animal does not have any other photos, they will
  continue to have the "No photo available" picture until the picture is
  made available for publishing (by ticking the red cross to the lower right
  of it on the media tab). This allows new photos to be vetted before
  being sent to adoption sites or used anywhere.

* Prefill new media notes for animal images with animal comments if left blank:
  If no notes are given when adding images as media, ASM will default the
  animal's comments field.

* Prefill new media notes with the filename if left blank: If the media being
  added is not an image and the notes are blank, use the original filename as
  the notes.

* When I change the flags on an animal/person, make a note of it in the log
  with this type:  If this option is on a log record is created when you add
  or remove a person or animal flag. 

* When I mark an animal held, make a note of it in the log: If this option is on,
  a log record is created when you mark an animal held along with the hold
  until date.

* When I change the location of an animal, make a note of it in the log: If
  this option is on, a log record is created every time you change an animal's
  internal location with the new location so you can track the history of where
  the animal has moved within your shelter.

* When I change the weight of an animal, make a note of it in the log: If
  this option is on, a log record is created every time you change an animal's
  weight so you can track the history of an animal's wieght with reports and
  graphs.

Diary and Messages
------------------

* Show the full diary (instead of just my notes) on the home page: If this option
  is on, all users will see the full list of outstanding diary notes on their home page.

* Auto complete diary notes linked to animals when they are marked deceased: If
  this option is enabled, diary notes linked to animals are completed when the
  animal is given a deceased date.

* Email users their outstanding diary notes once per day: This option will cause
  the system to send users an email containing their outstanding diary notes. 
  The system will send it as part of the overnight batch, which depending on
  your recommended locale/cron times will be between midnight and 4am.
  For this option to work, you must have configured the system email in
  the Email tab of this screen and your users must have email addresses set.

* Email users immediately when a diary note assigned to them is created or
  updated: This option will cause an email be sent to any users a diary note is
  assigned to as soon as you create or make a change to it. 

* Email diary note creators when a diary note is marked complete: This option
  will have an email sent to the person who created a diary note the moment
  that it is marked complete by a user.

* When a message is created, email it to each matching user: In addition to
  showing messages on the home page for a user, send it via email. The message
  is sent immediately as soon as the message is created.

Display
-------

* Enable Visual Effects: Enables visual sliding effects. Turn this off to speed
  up the UI.

* Use Fancy Tooltips: If your browser supports it (all but IE8), ASM can use
  modern callout style tooltips in the interface.

* Use HTML5 client side image scaling: If your browser supports it, media will
  be scaled on your PC before being uploaded to the server to save time.

* Show animal thumbnails in clinic books: Show animal pictures in the rows of
  the clinic waiting and consulting room screens. This option is off by default
  to save screen space and because clinics are normally person-focused.

* Show animal thumbnails in movement and medical books: Show animal pictures in
  the rows of the movement and medical books (foster book, reservation book,
  vaccination book, etc.)

* Show pink and blue borders around animal thumbnails to indicate sex: Makes
  the border around thumbnails pink for girls and blue for boy animals.

* Show a minimap of the address on person screens: Show an embedded map next to the
  person's address on the details screen. Also shows a minimap on the dispatch
  slider of incidents.

* When entering addresses, restrict states to valid US 2 letter state codes:
  When this option is on, the state field will switch to a dropdown that only
  allows valid US states to be selected. The default state for screens will be
  auto selected from the state chosen on the shelter details options tab.

* Allow editing of latitude/longitude with minimaps: Allow the latitude/longitude
  geocodes to be hand edited in fields near the minimap and address. Right clicking
  on the minimap will add a new pin and update the fields.

* Default to table mode when viewing media tabs: When accessing the media tab
  of records, show the media records in a sortable table with metadata
  information. You can toggle the view mode of media tabs with the button on
  the right side of the toolbar.

* Show weights as lb and oz: Enter and show weights with separate pounds and
  ounces. eg: 5 lbs and 6 oz

* Show weights as decimal lb: Enter and show weights in lbs, allowing decimal
  fractions, eg: 5.50 lbs
  If neither this or the previous show weights option is set, weights are shown
  in kg, eg: 20.1 kg

* Show complete comments in table views: When viewing comments or log notes in
  tables, show the complete text instead of truncating it to 80 characters and
  fitting the text onto one line.

* Show record views in the audit trail: When viewing the audit trail slider of
  a record, include audit records that show when users viewed this record.

* Show ID numbers when editing lookup data: When browsing lookup data under
  :menuselection:`Settings --> Lookup Data`, show the internal system ID numbers.
  This is handy for looking up IDs when writing reports.

* Keep table headers visible when scrolling: If selected, when scrolling down
  long tables their headers will float at the top of the screen to remind you
  of the column headings.

* Open records in a new browser tab: Open all records in their own browser
  tabs.

* Open reports in a new browser tab: Open all reports in their own browser
  tabs.

* Auto log users out after this many minutes of activity: If a user leaves
  their browser open and idle for this many minutes, the system will
  automatically log them out.

* Enable location filters: Location filters allow a user account to be
  restricted to only viewing animals in set internal locations. With this
  option enabled, a location filter field will appear on the system users
  screen allowing you to set the locations a user account is restricted to
  viewing.

* Enable multiple sites: Once enabled, sites can be created in the lookup data
  section. Sites can be assigned to locations, user accounts, incidents  and
  people records. User accounts with a particular site assigned can only see
  animals in locations belonging to their site, along with people and incidents
  at their site. Leaving a person, location or incident with no site allows
  anyone to see it. Leaving a user account without a site allows it to see all
  sites.  This allows you to handle multiple sites with one ASM database. A
  number of site-specific reports are available in the repository.

* Format telephone numbers according to my locale: When leaving fields containing
  phone numbers, if the numeric portion is the correct length, format them
  according to your locale. Eg: US numbers become (XXX) XXX-XXXX

* When displaying person names in lists, use the format: In movement books,
  donation books, the waiting list, etc. when showing person names, ASM can use
  different formats if you want surname first for sorting, etc.

* When displaying calendars, the first day of the week is: For date choosers
  and calendar view, select which day the week should start on. For the US
  and some Jewish cultures, it's generally Sunday, for the rest of the world,
  Monday.


Documents
---------

The documents tab allows you to change various settings related to generating
documents from templates.

* Allow use of OpenOffice document templates: Browser based applications cannot
  support native applications like OpenOffice as well as the browser-based word
  processor built into ASM, however with this option on you can continue to use
  OpenOffice templates. With this option enabled, the document template screen
  will also allow you to upload OpenOffice documents as templates. When
  generating a document from an OpenOffice template, ASM will substitute the
  correct tags in the OpenOffice template and send the constructed document to
  the web browser as a binary file with the correct mime type for display in
  OpenOffice or download.

* Printing word processor docuemnts uses hidden iframe and window.print:By
  default when printing documents in the built-in wordprocessor, an iframe is
  used to display and print only the document. This works fine for desktop web
  browsers, but if you use mobile devices where the print command sends the URL
  to a separate printing service, this will not work and you should untick this
  option. Unticking this option will cause the print button to redirect to a
  separate copy of the document by itself for use by mobile printing services.

* Send PDF files inline instead of as attachments: If this option is on, ASM
  will tell the browser to show PDF documents in the main page. Otherwise, it
  will send them as attachments for you to download.
  
* Include incomplete medical records when generating document templates: If
  set, vaccinations, tests and medical regimens will be included that are incomplete 
  when accessing them via LastX, Due and Recent wordkeys. 
  
* When I generate a document, make a note of it in the log: If this option is
  on, a log record is created every time you generate a document.

* Default zoom level when converting documents to PDF: This setting controls how
  the text is scaled when converting a document to PDF. Older versions of the
  PDF converter used by SM would to scale to the widest element on the page,
  however newer versions do not do this. To get back the behaviour that older 
  versions of SM had with wkhtmltopdf <= 0.12.3, set this value to 130.

Email
-----

Configure the email address used as the FROM address when sending from ASM. You
can also configure autocomplete items for the from, to and cc address boxes.

(sheltermanager.com only) You can override the use of smtp.sheltermanager.com
and use your own SMTP server to send email if you wish. This is an advanced
option for experienced users, if you do not understand what you are doing, do
not enable the option to use your own SMTP server as you will likely break
the email sending functionality for your database.

Find Screens
------------

This tab allows you to configure which columns are present on all the find
screens and in which order they are displayed.

* Default to advanced find animal screen: If ticked, the find animal screen
  will appear in advanced mode by default. 

* Advanced find animal screen defaults to on shelter: If ticked, the advanced
  find animal screen will automatically select “On Shelter” as the logical
  location when the screen is opened.

* Default to advanced find person screen: If ticked, the find person screen
  will appear in advanced mode by default. 

Home page
---------

The home page tab allows configuration of the home page. If selected, some
shelter stats can be displayed for the current period on the home page as 
well as links to a chosen set of animals (eg: Recently changed or Up
for adoption).

* Show tips on the home page: Shows tips at the top of the home page.

* Show alerts on the home page: Shows alerts about outstanding vaccinations,
  medical treatments, donations, etc.

* Show overview counts on the home page: Shows totals for animals in care.

* Show timeline on the home page: Shows the last 10 things that happened at the
  shelter on the home page (intake, adoptions, euthanasia, etc)

* Hide deceased animals from the home page: If this option is on, any deceased
  animals on the animal links or timeline sections of the home page will be
  hidden.  This option does not apply to the full timeline view, accessed by
  clicking the Timeline heading on the home page or from the
  :menuselection:`ASM --> Timeline` menu option.

* Hide financial stats from the home page: If this option is on, the stats
  lines showing how much money has been received in payments or spent in
  costs will be hidden from the home page.

* Show an alert when these species of animals are not microchipped: The microchip
  alerts on the home page and emblems will only be shown for these species of
  animals (by default, dogs and cats)

* Show an alert when these species of animals are not altered: The recently
  adopted/unneutered animal alerts on the home page and emblems will only be 
  shown for these species of animals (by default, dogs and cats)

* Show an alert when these species of animals do not have a rabies vaccination:
  The alert for animals without a rabies vaccination will only be shown for these
  species (by default dogs)

* Show an alert when these species of animals do not have a vaccination of any
  type: The alert for animals that have never been vaccinated will only be
  shown for these species (by default dogs and cats)


Insurance
---------

If you have an agreement with a pet insurer, Animal Shelter Manager can accept
a range of numbers under this tab and allow you to assign them to adoptions as
they are made. 

Simply fill in the start/end/next values and tick the box to ensure you are
using automatic numbers. When you next adopt an animal, a button will appear at
the side of the insurance number on the movement screen, allowing you to assign
an insurance number to that adoption. 

Lost and Found
--------------

The lost and found tab allows you to assign your own point weightings to the
different kinds of matches used when generating the lost and found match
report, as well as determine how many points are need for a match to be
included.

Medical
-------

* Include off-shelter animals in medical calendar and books: If ticked, animals
  with outstanding medical/vacc/tests that have left the shelter will be shown
  in medical books and the medical calendar.

* Pre-create all treatments when creating fixed-length medical regimens:
  Enabling this option will have creation of a new medical regimen create all
  of its treatments up-front. If the new regimen has a "Completed" status, all
  the treatments will be marked as given. This can be useful when entering
  historic records.  The default behaviour without this option is to create
  treatments incrementally as each previous treatment is given. This is done to
  prevent staff accidentally overdosing animals or having to "catch up" when a
  treatment is missed. 

* Reload the medical book/tab automatically after adding new medical items: If
  selected, reloads the screen automatically after adding a new medical
  regimen. If this option is not enabled, a placeholder row will be shown for
  the new medical item instead and the status column will show a link to reload
  the screen. This option is useful if you have a full medical book or animals
  with a lot of medical items who are frequently treated and reload times are
  long.

* When entering vaccinations, default the last batch number and manufacturer
  for that type: If ticked, when entering a given vaccination, the batch number
  and manufacturer will be copied from the last vaccination on record of the
  vaccination type.

* Send a weekly email to fosterers with medical information about their
  animals: If set, an email will be sent to all active fosterers containing
  info of overdue medications and medications/clinic appointments that fall due
  in the coming week. The email is sent as part of the overnight batch, early
  on Monday mornings by default. A day other than Monday can be chosen from the
  dropdown below if needed.

* Do not send an email if there are no medical items due for animals in the
  care of this fosterer: If set, fosterers will be skipped if there are no
  medical items due for animals in their care.

  An example of the email fosterers will receive looks like this:

.. image:: images/fosterer_email.png

Movements
---------

* Cancel unadopted reservations after: If an animal is reserved for this period
  of time and it does not result in an adoption (or any kind of movement), ASM
  will automatically cancel the reservation for you after this time.

* Highlight unadopted reservations on screen after: If an animal
  is reserved for this period of time, the system will highlight the reservation
  on screen (typically in red italics).

* Remove holds after: This value is used to set a default in the "Hold until date"
  field of new animals. When the date is reached, the hold flag is automatically
  removed.

* Trial adoptions last for: This value is used to set the default "trial end date"
  field when marking adoptions as a trial.

* Animals are long term after: This value controls the long term alert, search
  and emblem. The default is 182 days (6 months). 

* Treat animals with a future intake date as part of the shelter inventory: This
  option will treat animals who have not arrived yet (Date Brought In > Today)
  as on shelter so that they are visible in shelter view etc.

* Treat foster animals as part of the shelter inventory: Setting this option
  will make ASM treat fostered animals as if they are on the shelter (with
  appropriate visual output to show they are fostered). 

.. note:: You should use :menuselection:`Settings --> Trigger Batch Processes` and recalculate animal locations after changing this option.

* Treat animals at retailers as part of the shelter inventory: Setting this 
  option will make ASM treat animals at a retailer as if they are on the
  shelter (with indications that they are at a retailer).

* Our shelter does trial adoptions, allow us to mark these on movement screens:
  When creating an adoption from :menuselection:`Move --> Adopt an animal`, or
  in any of the movement tabs/screens, show a “trial” tickbox and trial end
  date. This allows for trial adoptions (some shelters call this “Foster to
  Adopt”), which can then be reported on by installing the “Active Trial
  Adoptions” and “Expired Trial Adoptions” reports.

* Treat Trial Adoptions as shelter inventory: As with the Foster as inventory
  option, trial adoptions are still shown in the Shelter View and on shelter
  searches/reports.

* Our shelter does soft releases, allow us to mark these on movement screens:
  When creating a released to wild movement, this allows for a soft release
  to be made. A soft release is one where the animal is monitored for some
  time after release.

* Treat Soft Releases as shelter inventory: Animals on soft release will be 
  kept in the shelter's inventory.

* Allow reservations to be created that are not linked to an animal: This
  option lets you create a reservation without specifying the animal. It also
  applies to using :menuselection:`Create --> Person` on the incoming forms
  screen with a reserveanimalname field in the form to allow the person's
  application to still be tracked through the reservation book even if the
  person is not interested in a specific animal yet.

* Automatically cancel any outstanding reservations on an animal when it is
  adopted: Self explanatory.

* Automatically return any outstanding foster movements on an animal when it is
  adopted: Applies to movement tabs/books. If an adoption record is created for
  an animal that still has an open foster movement, the foster movement will be
  returned with the adoption date so that the adoption can proceed.

* Automatically return any outstanding retailer movements on an animal when it is
  adopted: Applies to movement tabs/books. If an adoption record is created for
  an animal that still has an open retailer movement, the retailer movement will be
  returned with the adoption date so that the adoption can proceed. The adoption
  will be linked to the previous retailer and movement for reporting purposes.

* When creating payments from the Move menu screens, mark them due instead of
  received: Creating adoptions and reservations from :menuselection:`Move -->
  Adopt an animal` lets you receive a payment at the same time. If this option
  is ticked, the payment will be marked as due to be paid, but not actually
  received. 
  
* Allow creation of payments on the Move-Reserve screen: Allow payments to be
  taken on the :menuselection:`Move --> Reserve an animal` screen.

* Allow editing of payments after creating an adoption on the Move-Adopt an
  animal screen: After the adopt button is clicked, take the user to a screen
  that allows editing of the payments that were just created. This allows the
  user to generate an invoice/receipt or request payment by email, etc.

* Allow requesting of signed paperwork when creating an adoption on the
  Move-Adopt an animal screen: If this option is enabled, a section will appear
  on the adopt an animal screen (after choosing a person) to allow a document
  template to be chosen and an email address. After the adopt button is
  clicked, the document will be generated and sent to that email for signature.

* Allow overriding of the movement number on the Move menu screens: If turned
  on, the movement number field will be visible on all Move menu screens for
  the user to override.

* Warn when adopting an unaltered animal: If the animal has not been 
  neutered/spayed, show a warning when trying to adopt it. 

* Warn when adopting an animal who has not been microchipped: If the animal
  has not been microchipped, show a warning when trying to adopt it.

* Warn when adopting an animal who has outstanding medical treatments: If the
  animal has ungiven medical treatments, show a warning when trying to adopt it.

* Warn when adopting to a person who has not been homechecked: If the person
  record does not have them down as homechecked, the system can warn you if you
  try to adopt an animal to them. 
 
* Warn when adopting to a person who lives at the same address as a banned person:
  If the adopter has the same address as someone previously banned, show a warning.

* Warn when adopting to a person who has been banned from adopting animals: The
  system can warn you if you try to adopt an animal to a person who has been
  marked as banned. 

* Warn when adopting to an owner in the same postcode as the original owner:
  Self explanatory. 

* Warn when adopting an animal with reservations and this person is not one of
  them: Self explanatory.

* Warn when creating multiple reservations on the same animal: If set, the
  system will warn you if you attempt to reserve the same animal to different
  people.  

* Warn when adopting to a person who has previously brought an animal to the
  shelter: The system can check and warn you if you attempt to adopt an animal
  to an owner who looks like an owner who brought an animal in. This is a loose
  check based on name and address. 

Online Forms
------------

* Remove incoming forms after: Automatically remove forms from the incoming queue
  after this many days.

* Remove forms immediately when I process them: When creating or attaching forms
  to records in the incoming forms list, delete the form as soon as it is 
  successfully processed.

* Remove processed forms when I leave the incoming forms screen: When navigating
  away from the incoming forms screen, any forms that have been processed (have
  a link shown in the rightmost column) will be deleted automatically.

* When storing processed forms as media, apply tamper proofing and make them read
  only: If this option is on, form submissions will be hashed and read only 
  (in the same way as signed documents) and the user who processed the form
  recorded. This prevents anyone from editing form submissions after they have been
  stored.

.. _paymentprocessors:

Payment Processors
------------------

ASM can be configured to request due payments from your customers via payment
processors.

* Request payments in: A currency code to request payments in. This should match
  the currency that you are using in your database as ASM does not perform
  any kind of currency exchange calculations.

* Redirect to this URL after successful payment: When a customer succesfully
  completes a payment, this is the page they will be redirected to. If you do not 
  set a page, the payment processor will show their own payment successful page.

PayPal
^^^^^^

* PayPal Business Email: The address for your PayPal account where payments will 
  be sent to.

It should not be necessary, but some users have reported problems receiving
IPN notifications from PayPal. As a "just in case" measure, click on the Settings/Gear
icon at the top right of your PayPal account, choose "Account Settings", then 
"Notifications" and the "Update" link next to "Instant Payment Notifications".
You can now choose a URL and to enable IPN messages. Use the URL shown on screen.

Stripe
^^^^^^

* Stripe Key: Your stripe key. This is usually prefixed with pk

* Stripe Secret Key: Your stripe secret key, usually prefixed with sk

In order for ASM to receive notification that payments have been received, a
Webhook needs to be created in the Stripe dashboard to receive
"checkout.session.completed" events under :menuselection:`Developers -->
Webhooks`

The Payment Processors option tab in ASM will display the URL you need to
configure for your webhook below the key fields.

Quicklinks
----------

Quicklinks can be configured here and shown on the home page and optionally
all screens (at the cost of some vertical space). Quicklinks allow you to
quickly get to some of ASM's screens without having to open the menus.

Reminder Emails
---------------

Reminder emails can be configured to be sent to people before or after certain events and
interactions with the shelter. In all cases, a number of days and an email template can be chosen. 

* Send a followup email to new adopters after days: This option will
  automatically send a followup email to people who recently adopted an animal.
  The system will make sure the animal is not dead or returned before sending
  the email. The template must be suitable for movement data.

* Send a reminder email to people with clinic appointments in days: This option
  will automatically send a reminder email to everyone who has a clinic
  appointment in the number of days chosen. The template chosen must be
  suitable for clinic data.

* Send a reminder email to people with due payments in days: This option
  will automatically send a reminder email to everyone who has a non-received payment
  with a due date in the number of days chosen. The template chosen must be
  suitable to receive payment data.

* Send a reminder email to people with licenses expiring in days: This option
  will automatically send a reminder email to everyone with an expiring license
  in the number of days entered. The template chosen must be suitable for
  license data. A forthcoming expansion to this area will allow inclusion of a
  renewal link to allow the license holder to renew and pay online.

Remove
------

System
^^^^^^

* Remove boarding functionality from screens and menus: If your shelter does
  not board animals for the public, this option will disable the system's boarding
  functionality from the financial menu and animal/person screens.

* Remove clinic functionality from screens and menus: If your shelter does
  not run a clinic, this option will disable the system's clinic appointment
  and invoicing functionality from the medical menu and animal/person screens.

* Remove move menu and the movements tab from animal and person screens: If
  your shelter does not do adoptions and animals never leave, this option will
  disable the system's movement functionality.

* Remove retailer functionality from the movement screens and menus: Setting
  this option removes the retailer fields from the movement screens and
  retailer specific options from the menu.

* Remove the document repository functionality from menus: Setting this option
  removes the central document repository from the menu.

* Remove the online form functionality from menus: Setting this option removes
  the online form screens from the menu.

* Remove the animal control functionality from menus: Setting this option
  removes the animal control screens from the menu.

* Remove fine-grained animal control incident permissions: Setting this option
  removes the "View Roles" control from the new incident and edit incident
  screens. The "View Roles" control allows a user to specify exactly which
  users can see the incident.

* Remove the rota functionality from menus: Setting this option removes
  the staff rota from the menu and person screens.

* Remove the stock control functionality from menus: Setting this option
  removes the stock control screens from the financial menu and
  medical/vaccination dialogs.

* Remove the transport functionality from menus: Setting this option removes
  the transport book from the menu and the tab from animal records.

* Remove the trap loan functionality from menus: Setting this option removes
  the trap loan link from the menu and the trap loan tab on the person screen.

People
^^^^^^

* Remove the city/state fields from person details: Setting this option will
  prevent ASM from presenting the user with additional fields to store the city
  and state information. These are handy for group owner searches, but not all
  shelters want or need them and prefer to keep the complete address in the
  address box. 

* Remove the country field from person details: Setting this option will 
  hide the country field from person addresses. This option is on by default 
  since most shelters only deal with one country.

* Remove the home and work telephone fields from person details: Setting this option
  will hide the home and work telephone fields from person records. 

* Remove the homechecked/by fields from person type according to the homechecked 
  flag: This option is on by default and will hide the homechecked by and date
  fields from the person type slider if they don't have the homechecked flag.
  This option exists because some users prefer to assign the person doing the
  homecheck before the flag to confirm the person is homechecked.

* Remove the insurance number field from the movement screens: Setting this
  option hides the insurance number field and button from :menuselection:`Move
  --> Adopt an animal` and all movement tabs/books.

Animals
^^^^^^^

* Remove the asilomar fields from the entry/deceased section: (US locales only)
  This option hides the asimilor intake and death category fields from the
  Entry and Deceased sliders.

* Remove the coat type field from the animal screen: If ticked, ASM won't
  display the coat type dropdown on the animal editing screen. For some
  shelters, keeping coat types is unnecessary (particularly for those that keep
  reptiles and birds!), so you can disable it here. 

* Remove the microchip fields from the animal screen: If ticked, ASM won't
  display the microchip indicator, number and date fields. For shelters that
  don't keep microchipped animals (eg: Reptiles and birds). 

* Remove the tattoo fields from the animal screen: If ticked, ASM won't display
  the tattoo indicator, number and date fields. Useful for shelters that don't
  keep animals with ear tattoos. 

* Remove the spay/neutered fields from the animal screen: If ticked, ASM won't
  display the neutered/spayed flag and date. Useful for shelters that keep
  animals that do not require neutering (small mammals, birds, reptiles,
  horses, etc). 

* Remove the declawed field from the animal screen: If ticked, ASM won't
  display the declawed flag. Useful for shelters that don't keep cats, or for
  countries where declawing is illegal (such as the UK). 

* Remove the heartworm test fields from the animal screen: If ticked, ASM won't
  display the heartworm test fields. Useful for shelters with animals that do
  not require heartworm tests. 

* Remove the FIV/L test fields from the animal screen: If ticked, ASM won't
  display the Combi test or FIV/FLV test fields (depending on your locale). 

* Remove the “Good With...” and Housetrained fields from the animal screen: If
  ticked, ASM won't display the good with cats/dogs/children and housetrained
  fields. Useful for shelters that don't keep cats and dogs. 

* Remove the adoption fee field from the animal screen: If ticked, ASM won't
  show the adoption fee field on the animal details. If this option is not on
  and an animal has a fee set, it will override the donation amount in the
  :menuselection:`Move --> Adopt an animal` and :menuselection:`Move -->
  Reserve an animal` screens.

* Remove the adoption coordinator field from the animal entry screeen: If ticked,
  ASM won't show the adoption coordinator field on the entry slider. Adoption
  coordinators are generally used by smaller, distributed rescues.

* Remove the Litter ID/Acceptance Number field from the animal screen: If
  ticked, ASM won't display the Litter ID or Acceptance Number field at the top
  of the details screen. If your shelter does not track litters, or is not a UK
  RSPCA shelter, you can turn this off and save some space on the screen. 

* Remove the location unit field from animal details: If ticked, ASM won't
  display the location unit field (this is the cage or pen number if your
  shelter uses those).

* Remove the Bonded With fields from the entry details screen: If ticked, ASM
  won't display the fields that allow an animal to be marked as bonded with
  other animals (bonding is particularly common with rescues that deal with
  rabbits and is the recommendation that pairs of animals are adopted
  together). 

* Remove the picked up fields from the entry details screen: If ticked, ASM
  won't display the fields that allow an animal to be marked as picked up in a
  particular location or by an ACO (useful for shelters who do not have staff
  picking up animals).

Reports
-------

* Email scheduled reports with no data: If you have set reports to be
  automatically emailed at a time of day, empty reports with "No data to show"
  will be emailed if this box is ticked. 

* Show report menu items in collapsed categories: If you have a lot of reports
  installed, this option allows you to just show the categories in the reports
  menu. Clicking a category expands it.

Shelter View
------------

The shelter view tab allows the default grouping to be set.

* Allow drag and drop to move animals between locations: If set, you can drag animal
  thumbnails between locations in shelter view to move them.

* Allow units to be reserved and sponsored: If set, and the user has the appropriate
  "Reserve/Sponsor Unit" permission, an edit icon will appear to the right of units
  in "Location and Unit" mode. This edit icon allows a reservation to be placed on
  a unit so that it appears with a red background and shows as occupied when 
  adding/editing animals. Any sponsor text will be included with the animal occupying
  that unit when it is published to your website so that the sponsor of the unit
  can be shown publicly.

* Show empty locations: If set, headings for all internal locations will be shown, 
  even if there are no animals in them.

Waiting List
------------

The waiting list tab allows an update period to be configured here. Simply
specify in days the interval between updates (how often a waiting list entry is
bumped up the urgency ratings until it reaches “High”). Another option is
available to select the default waiting list urgency - this is the default
start value given to new waiting list entries. You can also choose hold
separate rankings for species on the waiting list. This makes sense if your
shelter takes dogs and cats for example and whether you can take a cat is
independent of how many dogs are on the shelter. 

Watermark
---------

Watermarking is a feature available under the media tab of animal records. It
allows you to embed a logo and the animal's name within a photo.

By default, the watermark image is added to the bottom right corner of the
photo and the name in the bottom left.

Note that the original image will be changed, so you will need to upload the
same image twice if you want to retain a copy without the watermark.

The options on this tab allow you to control the placement of the watermark
image and animal name, along with the colours used for the text of the name. 

For this feature to be available, you need to upload your watermark image,
named "watermark.png" to :menuselection:`Settings --> Reports --> Extra Images`
- note that the image must be a PNG file, so that an alpha channel for
transparency can be included.

