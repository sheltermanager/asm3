Configuration
=============

To configure all areas of the system, you need to look under the top-level Settings menu. 

Additional Fields
-----------------

.. image:: images/additional_fields.png

This screen allows you to declare additional fields that will appear on the
animal, person, lost animal, found animal and waiting list screens.

Fields have a name, a label, a tooltip, a location and a display index. 

The name cannot contain spaces and is used for referencing the data in document
generation - you can use a <<FIELDNAME>> tag to add these additional values to
your documents. The label is what will appear on the screen at the side of the
field, the tooltip text will appear when you hover your mouse over the control
on screen. The display index determines the order your fields are output to the
tab and which field the cursor moves to when you press the TAB key on the
screen.

If you selected a field type of “lookup” or “multi-lookup”, then the use the
“Lookup Items” field to supply some values for the dropdown list. These should
be pipe-separated, eg: Item 1 | Item 2 | Item 3 

If you selected a field type of “Yes/No” then “Lookup Items” can optionally
hold a pair of values that ASM will use. You can use this to supply your own
text for Yes/No fields in the web publisher and document templates. The default
if you don't supply a Lookup Items for a Yes/No field is 0=Yes|1=No 

For example, to add a new field to the animal screen to say whether the animal
has been tested for kennel cough, create a new additional field and enter the
following values::

    Name: KennelCough 
    Label: Kennel Cough Tested? 
    Tooltip: Tick this box if the animal has been tested for kennel cough 
    Type: Yes/No 
    Link: Animal - Additional
    DisplayIndex: 0 

The new field will appear under the Additional tab on the animal screen. 

You will be able to reference it in generated animal documentation with the
<<KennelCough>> key. 

Data for these fields is stored in the “additional” table in the database, the
LinkID field holds the animal or person ID (with LinkType being the location, 0
is animal additional tab, 1 is person additional tab).

You can access additional fields in reports by using a subquery. For example,
to output a list of all our animal names with the new KennelCough field we
defined::

    SELECT a.AnimalName, 
        (SELECT ad.VALUE FROM additional ad 
         INNER JOIN additionalfield af ON af.ID = ad.AdditionalFieldID 
         WHERE ad.LinkID = a.ID AND af.FieldName = 'KennelCough') AS KennelCough
    FROM animal a

Lookup Data
-----------

.. image:: images/lookup_data.png

The lookup data screen allows editing of lookups. These are small, standard
tables of information used throughout the system for values such as breeds,
species, colours, etc. 

Document templates
------------------

.. image:: images/document_templates.png

Here, you can edit the available document templates on the system. For a
comprehensive list of tokens for use in templates, see the appendix on
wordkeys.

Reports
-------

.. image:: images/reports_edit.png

Here, you can create and edit all the available reports on the system. The
“Browse sheltermanager.com” button allows you to browse reports from the online
repository and choose reports, graphs and mail merges to install. 

The “Edit Header/Footer” button allows you to modify the HTML header that is
prepended and footer that is appended to reports when they're run.

Extra Images
^^^^^^^^^^^^

The “Extra Images” button allows you to upload additional images for use in
reports and document templates. The screen will give you a URL for each image
so you can reference them in reports and document templates.

There are certain special names for images that the system will use to override
some of its standard pictures:

* nopic.jpg – this is the image the system will display when an animal does not
  have any image media. You cannot delete this image, however you can upload a
  new image called nopic.jpg to replace it.

* logo.jpg – this is the image the system will use for the home logo at the top
  left corner. By default, it's the ASM logo but it can be changed for your
  shelter. Ideally, your logo should not be more than 32 pixels high, but the
  system will scale down larger images.

* splash.jpg – this is the image the system will show on the login screen
  instead of the default ASM splash screens. Your splash image should be
  400x200 pixels.

System user accounts
--------------------

You may create, edit and delete system users from here. It is recommended that
every person who uses Animal Shelter Manager have their own login and user name
(when a user is finished, they should navigate to :menuselection:`User -->
Logout` to prepare the system for the next user) - simply to make sure that
people do not get other people's work attributed to them on the audit trails.

Whilst editing a user, you can choose absolutely everything that user may do
within the system by assigning one or more appropriate roles. If you set the
user type to "superuser", the user has full administrative privileges to the
system. If you choose "normal user", you will need to set permissions for
the user by assigning roles.

If you set an email address for the user and configure email, you can have the
system send diary notes and messages via email to users.

If you set a person record for the user, they will be forbidden from opening
that person record. The idea is to prevent them from viewing their own person
record. You can also set the role permission to forbid them opening any other
person record with the “Staff” flag if you wish to lock a user from opening any
staff person records.

Setting a location filter (a group of internal locations) for a user will
prevent them seeing animals who are not in those locations when:

* Viewing animal links on the home page.

* Viewing shelter view, search results or find animal results (basic or
  advanced). 

* When adding or editing animals, the internal location dropdown will only show
  those locations.

* When choosing report criteria, they will only be able to select one of those
  locations for any $ASK LOCATION$ tags.

Setting an IP restriction will only allow that user account to login from IP
addresses that match the set.

User roles
----------

.. image:: images/role_edit.png

Roles can be assigned to individual users and represent sets of permissions.
When you edit a role, ASM will show you a huge number of tickboxes to determine
what any user with that role is allowed to do within the system.

Import a CSV file
-----------------

ASM can import data from a CSV file. 

Microsoft Excel, OpenOffice Calc, Gnumeric, Google Docs and many other
spreadsheet products can all export individual sheets in CSV format.

.. image:: images/import_csv.png

The CSV file should have a header row that contains column names that ASM
recognises (see :ref:`csvimportfields`)

.. image:: images/sample_csv.png

Each row of data can contain animal, person, movement and donation information.
If movement data is present, then an adoption (or other movement if
MOVEMENTTYPE is set) record will be created to link the animal and person in
the row together. If donation data is present in the row, a donation will be
created and linked to the person (and movement if one was available).

If a column is not supplied, then ASM will use the default as set under the
default tab in Settings-Options. For example, not setting ANIMALTYPE will cause
ASM to use the default animal type.

ASM prefers the ANIMALDOB field to set the date of birth, but if you don't have
it, it will calculate the date of birth from the ANIMLAGE field (which it
assumes to be an integer number of years). If neither are set, it will use
today's date as a last resort.

If ANIMALBREED2 is not set, the animal is assumed to be a purebreed of
ANIMALBREED1. If ANIMALBREED2 is set and is different from ANIMALBREED1, then
the crossbreed flag will be set on the resulting animal.

If the “Create missing lookup values” option is on, and the file contains a
value that is not present in the database (for example, if you have “Goldfish”
in the ANIMALSPECIES column, but it isn't a species in your database), then it
will be created during the import and the animal linked to it.

If the “Clear tables before importing” option is on, ASM will remove all data
from the animal, person, movement and donation tables before doing the import.
This delete cannot be undone, so exercise caution when using this option as you
can wipe out your entire database!

Trigger Batch Processes
-----------------------

ASM runs various tasks overnight to keep animal records upto date and generate
cached versions of complex reports and figures. 

Ordinarily, users should have no need to trigger these batch processes
manually, however after importing CSV data or making bulk data changes with
queries, animal locations and historic figures data can get out of sync and
needs to be recalculated/regenerated.

Some of these processes can take many minutes to run and may block use of the
database for other users. They should be used sparingly.

Options
-------

The main :menuselection:`Settings --> Options` page allows configuring of the
general preferences within Animal Shelter Manager. 

Shelter Details
^^^^^^^^^^^^^^^

The shelter details tab allows you to enter contact information for your
shelter. This is used with reporting and internet publishing.

The “Visual Theme” option allows you to choose how the program looks. There are
a multitude of preset themes to choose from.

The “Server Adjustment” box allows you to set a time offset in hours from the
server clock. This is only necessary if your client is in a different timezone
from the server. For example, the main sheltermanager.com servers are in the
UK. East coast Americans will want to adjust the time by -5 hours to make sure
alerts appear at the correct time and reports are shown correctly.

Accounts
^^^^^^^^

ASM contains a full double entry accounting package. The options here are: 

* Enable Accounts Functionality: Unticking this box will cause ASM to remove
  all accounts related menu entries/buttons so that users do not see it, and
  you will not be using ASM to manage your accounts. 

* Creating donations and donation types creates matching accounts and
  transactions: When you create a new donation type, or log a new donation
  against an owner/animal, ASM will automatically create a matching account in
  the accounts system if one does not exist, and a matching transaction. It is
  suggested that you leave this option on, even if you have disabled accounts
  functionality in case you wish to use it in future. 

* When receiving donations, allow the deposit account to be overridden: When
  adding donations to the system, if you have the create matching transactions
  option on as well as this one, a destination account dropdown will be shown
  on donation screens allowing you to override the deposit account that the
  donation will be applied to (the withdrawal account is always the donation
  type's matching income account).

* Only show account totals for the current period, which starts on: If you wish
  to use accounting periods, put the start date in here. By enabling the show
  account totals for current period option, the totals shown on the account
  screen will only include transactions from this date or later. 

* Default transaction view: When viewing transactions for an account, ASM will
  show transactions matching this time period. The default is the current
  month.

* Default desination account for donations: When ASM creates a matching
  donation transaction, it will use the donation type to find the income
  account to use. The destination account here denotes where the money will be
  moved to. If you do not set one, ASM will use the first bank account on file. 

* Donations of type … are sent to ...: In addition to the default donation
  destination account, you can specify optional mappings, so that when ASM
  receives a donation of a particular type, it uses the specified destination
  account for it when creating the matching accounting transaction. 

Add Animal
^^^^^^^^^^

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

* Show the color field: Allow entry of a specific colour

* Show the internal location field: Allow entry of an internal location 

* Show the location unit field: Allow a cage/pen/kennel/hutch number to be set

* Allow a fosterer to be selected: Allow new animals to be fostered straight
  away

* Show the litter ID field: Allow a litter ID

* Show the size field: Allow entry of the size

* Show the weight field: Allow entry of the weight

* Show the altered fields: Allow an altered date to be set 

* Show the microchip fields: Allow a microchip date/number to be set 

* Show the entry category field: Allow an entry category to be set 

* Show the original owner field: Allow original owner to be set

* Show the brought in by field: Allow brought in by to be set

* Warn if the animal is similar to one entered recently: Pop up a warning
  dialog if the animal's name is the same as one entered recently to help
  prevent possible duplicates.

Age Groups
^^^^^^^^^^

It is possible to categorise your animals by their age in ASM. This is useful
when generating adoption paperwork and you don't have an exact date of birth
for the animal. Instead, ASM can specify one if its groups, using the AgeGroup
wordkey (or animal.AgeGroup field in custom reports).

This tab allows you to choose the threshold for each grouping, as well as the
grouping name. By default, anything under 6 months (0.5 years) is classed as a
Baby, anything under 2 years is Young Adult, under 7 years is Adult and over
that is Senior. 

Animal Codes
^^^^^^^^^^^^

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

Costs
^^^^^

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

Defaults
^^^^^^^^

This screen allows configuration of the system defaults. These defaults are
used to select starting values when finding and creating animals. 

* Mark new animals as not for adoption: Setting this option will cause ASM to
  automatically tick the “not for adoption” box when creating new animals. This
  is an extra precaution - by forcing users to untick the box when necessary,
  no animal can be accidentally published. 

* Prefill new media notes for animal images with animal comments if left blank:
  If no notes are given when adding images as media, ASM will default the
  animal's comments field.

* Prefill new media notes with the filename if left blank: If the media being
  added is not an image and the notes are blank, use the original filename as
  the notes.

* Include off-shelter animals in medical calendar and books: If ticked, animals
  with outstanding medical/vacc/tests that have left the shelter will be shown
  in medical books and the medical calendar.

* When I change the location of an animal, make a note of it in the log: If
  this option is on, a log record is created every time you change an animal's
  internal location with the new location so you can track the history of where
  the animal has moved within your shelter.

* When I change the weight of an animal, make a note of it in the log: If
  this option is on, a log record is created every time you change an animal's
  weight so you can track the history of an animal's wieght with reports and
  graphs.

Diary 
^^^^^

The diary tab allows you to set whether you would like to see the complete
diary on the home page, or just the diary notes for the current user. You can
also set whether you would like diary notes emailed to each user every day –
for this to work, you must have configured the system's email in the email
section of the screen and your users must have an email address set.

Display
^^^^^^^

* Enable Visual Effects: Enables visual sliding effects. Turn this off to speed
  up the UI.

* Use Fancy Tooltips: If your browser supports it (all but IE8), ASM can use
  modern callout style tooltips in the interface.

* Use HTML5 client side image scaling: If your browser supports it, media will
  be scaled on your PC before being uploaded to the server to save time.

* Show a minimap of the address on person screens: Show an embedded map to the
  person's address on the details screen.

* Show weight as lb rather than kg: Change the field label on the animal weight
  field to lb instead of the usual kg.

* Show animal thumbnails in movement and medical books: Show animal pictures in
  the rows of the movement and medical books (foster book, reservation book,
  vaccination book, etc.)

* Keep table headers visible when scrolling: If selected, when scrolling down
  long tables their headers will float at the top of the screen to remind you
  of the column headings.

* Open records in a new browser tab: Open all records in their own browser
  tabs.

* Open reports in a new browser tab: Open all reports in their own browser
  tabs.

* Show report menu items in collapsed categories: If you have a lot of reports
  installed, this option allows you to just show the categories in the reports
  menu. Clicking a category expands it.

* Auto log users out after this many minutes of activity: If a user leaves
  their browser open and idle for this many minutes, the system will
  automatically log them out.

* When displaying person names in lists, use the format: In movement books,
  donation books, the waiting list, etc. when showing person names, ASM can use
  different formats if you want surname first for sorting, etc.


Documents
^^^^^^^^^

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
  set, medical regimens will be included that are incomplete when accessing
  them via LastX and Recent wordkeys. 
  
* Include incomplete vaccination and test records when generating document
  templates: If set, vaccination and test records will be included that have
  not been given when accessing them via LastX and Recent wordkeys.

* When I generate a document, make a note of it in the log: If this option is
  on, a log record is created every time you generate a document.

Insurance
^^^^^^^^^

If you have an agreement with a pet insurer, Animal Shelter Manager can accept
a range of numbers under this tab and allow you to assign them to adoptions as
they are made. 

Simply fill in the start/end/next values and tick the box to ensure you are
using automatic numbers. When you next adopt an animal, a button will appear at
the side of the insurance number on the movement screen, allowing you to assign
an insurance number to that adoption. 

Find Animal/Person
^^^^^^^^^^^^^^^^^^

The find animal and person columns boxes allows you to specify which columns
are used on the find animal screens and in what order they appear. The waiting
list columns box operates similarly. 

A comma separated list of field names should be given here. You can also use
additional field names for your custom fields. 

* Default to advanced find animal screen: If ticked, the find animal screen
  will appear in advanced mode by default. 

* Advanced find animal screen defaults to on shelter: If ticked, the advanced
  find animal screen will automatically select “On Shelter” as the logical
  location when the screen is opened.

* Default to advanced find person screen: If ticked, the find person screen
  will appear in advanced mode by default. 

Home page
^^^^^^^^^

The home page tab allows configuration of the home page. If selected, some
shelter stats can be displayed for the current period on the home page as 
well as links to a chosen set of animals (eg: Recently changed or Up
for adoption).

* Show tips on the home page: Shows tips at the top of the home page.

* Show alerts on the home page: Shows alerts about outstanding vaccinations,
  medical treatments, donations, etc.

* Show timeline on the home page: Shows the last 10 things that happened at the
  shelter on the home page (intake, adoptions, euthanasia, etc)

Lost and Found
^^^^^^^^^^^^^^

The lost and found tab allows you to assign your own point weightings to the
different kinds of matches used when generating the lost and found match
report, as well as determine how many points are need for a match to be
included.

Movements
^^^^^^^^^

The movement tab allows a number of days to be set to automatically cancel
reservations. If an animal is reserved for this period of time and it does not
result in an adoption (or any kind of movement), ASM will automatically cancel
the reservation for you after this time.

* Treat foster animals as part of the shelter inventory: Setting this option
  will make ASM treat fostered animals as if they are on the shelter (with
  appropriate visual output to show they are fostered). Note that this option
  will not take effect until you restart ASM. 

* Automatically cancel any outstanding reservations on an animal when it is
  adopted: Self explanatory.

* Automatically return any outstanding foster movements on an animal when it is
  adopted: Applies to movement tabs/books. If an adoption record is created for
  an animal that still has an open foster movement, the foster movement will be
  returned with the adoption date so that the adoption can proceed.

* When creating payments from the Move menu screens, mark them due instead of
  received: Creating adoptions and reservations from :menuselection:`Move -->
  Adopt an animal` lets you receive a payment at the same time. If this option
  is ticked, the payment will be marked as due to be paid, but not actually
  received. 
  
* Allow creation of payments on the Move-Reserve screen: Allow payments to be
  taken on the :menuselection:`Move --> Reserve an animal` screen.

* Allow entry of two donations on the Move menu screens: When creating an
  adoption or reserve from :menuselection:`Move --> Adopt an animal`, allow
  space for two donations in case of adopters who would like to make a donation
  as well as paying the adoption fee.

* Allow overriding of the movement number on the Move menu screens: If turned
  on, the movement number field will be visible on all Move menu screens for
  the user to override.

* Our shelter does trial adoptions, allow us to mark these on movement screens:
  When creating an adoption from :menuselection:`Move --> Adopt an animal`, or
  in any of the movement tabs/screens, show a “trial” tickbox and trial end
  date. This allows for trial adoptions (some shelters call this “Foster to
  Adopt”), which can then be reported on by installing the “Active Trial
  Adoptions” and “Expired Trial Adoptions” reports.

* Treat Trial Adoptions as shelter inventory: As with the Foster as inventory
  option, trial adoptions are still shown in the Shelter View and on shelter
  searches/reports.

* Warn when adopting to a person who has not been homechecked: If the person
  record does not have them down as homechecked, the system can warn you if you
  try to adopt an animal to them. 
  
* Warn when adopting to a person who has been banned from adopting animals: The
  system can warn you if you try to adopt an animal to a person who has been
  marked as banned. 

* Warn when adopting to an owner in the same postcode as the original owner:
  Self explanatory. 

* Warn when creating multiple reservations on the same animal: If set, the
  system will warn you if you attempt to reserve the same animal to different
  people.  

* Warn when adopting to a person who has previously brought an animal to the
  shelter: The system can check and warn you if you attempt to adopt an animal
  to an owner who looks like an owner who brought an animal in. This is a loose
  check based on name and address. 

Quicklinks
^^^^^^^^^^

Quicklinks can be configured here and shown on the home page and optionally
all screens (at the cost of some vertical space). Quicklinks allow you to
quickly get to some of ASM's screens without having to open the menus.

Remove
^^^^^^

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

* Remove the rota functionality from menus: Setting this option removes
  the staff rota from the menu and person screens.

* Remove the stock control functionality from menus: Setting this option
  removes the stock control screens from the financial menu and
  medical/vaccination dialogs.

* Remove the transport functionality from menus: Setting this option removes
  the transport book from the menu and the tab from animal records.

* Remove the trap loan functionality from menus: Setting this option removes
  the trap loan link from the menu and the trap loan tab on the person screen.

* Remove the town/county (city and state) fields from the owner screen: Setting
  this option will prevent ASM from presenting the user with additional fields
  to store the city and state information. These are handy for group owner
  searches, but not all shelters want or need them and prefer to keep the
  complete address in the address box. 

* Remove the insurance number field from the movement screens: Setting this
  option hides the insurance number field and button from :menuselection:`Move
  --> Adopt an animal` and all movement tabs/books.

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

Waiting List
^^^^^^^^^^^^

The waiting list tab allows an update period to be configured here. Simply
specify in days the interval between updates (how often a waiting list entry is
bumped up the urgency ratings until it reaches “High”). Another option is
available to select the default waiting list urgency - this is the default
start value given to new waiting list entries. You can also choose hold
separate rankings for species on the waiting list. This makes sense if your
shelter takes dogs and cats for example and whether you can take a cat is
independent of how many dogs are on the shelter. 


