Publishing
==========

ASM can update many third party adoption sites and microchip registries as well
as generating websites of your adoptable and recently adopted animals. The
sites produced are based on simple editable templates and can be completely
customised and branded to suit you. 

All of this functionality is accessed via the top level Publishing menu.

There are many options you can set to choose what appears on the output, and
how the output is generated. Set these options under :menuselection:`Publishing
--> Set Publishing Options`

Animal Selection
----------------

.. image:: images/animal_selection.png

The Animal Selection tab allows you to control which animals are considered
adoptable by ASM's internet publishers. 

* Include [category] animals: Select “yes” to include animals fitting the
  category.

* Merge bonded animals into a single record: When outputting bonded animals,
  merge them into a single entry. The names will be joined together with
  commas, but other than that all the details will be of the first animal in
  the sort so make sure the bio/notes include information on the bonded animals
  for all of them.

* Exclude animals aged under: This box is to prevent puppies and kittens who
  are too young being included in the list of available adoptions. You may
  choose an age limit on animals that appear. By default, the system excludes
  animals less than 1 year old (52 weeks). 

* Include animals in the following locations: Select the locations to include
  adoptable animals from. If none are selected, all locations will be used.

.. note:: In addition to items you select here, any animal which has the "Courtesy Listing" flag will be automatically included.

All Publishers
--------------

.. image:: images/all_publishers.png

The All Publishers tab allows you to set options common to all internet publishers.

* Register microchips after: If you are registering microchips, ASM will update
  the owner information with the registry after these types of movements.
  Non-shelter animals will always be registered with their original owner
  information if present, using the microchip date as a trigger.
  A special "Intake" option allows registering of microchips to the shelter's
  contact info for animals currently in the care of the shelter. This includes
  animals brought to the shelter as well as those returned from a previous movement.
  Animals who are marked as held awaiting reclaim will *not* be registered until
  after the hold is removed.

* Register microchips from: When registering microchips, only consider animals
  where the event triggering registration (intake, adoption, reclaim, etc)
  occurred after this date. This is useful when enabling registration for the
  first time on a database full of a historic data where you do not want to
  re-register old chips to potentially out of date adopters.

* Update adoption websites every: Some adoption websites will accept updates
  more frequently than the 24 hour default. Setting this option to a value
  smaller than 24 will update those services at the chosen interval. Services
  affected by this value are PetFinder, AdoptAPet, PetRescue, SavourLife and
  Maddie's Pet Assistant

* Reupload animal images every time: Ticking this box will tell the publisher
  to reupload images for all the animals published. Normally, ASM will not
  upload an image it has previously uploaded to save bandwidth. ASM will detect
  the preferred image changing and force a reupload for that animal without
  the need for this option. This option will be ignored by some publishers
  (notably RescueGroups.org and AdoptAPet.com) as reuploading all images constantly
  is considered abusive behaviour.

* Upload all available images for animals: Ticking this box will have the
  publisher upload all the images for each animal where available. They will be
  named sheltercode-X.jpg (X increments for each image). The first image will
  be the image flagged as web preferred. 

* Order published animals by: Sorts the list of animals before they are
  published.

* Thumbnail size: Controls the size of thumbnails the system generates for adoptable 
  animal publishers (in particular the ones used by the javascript include 
  method of website integration). The size is for the thumbnail's longest side.

* Animal descriptions: This determines the source of the main description for
  animals when being published. For the HTML/FTP publisher, this is the source
  of the $$WebMediaNotes$$ token. Set to “Use animal comments” to use the
  comments field from the notes section of the animal's record. “Use notes from
  preferred photo” will use the notes field on the animal's web preferred
  photo.

* Add this text to all animal descriptions: Allows you to set a footer on every
  animal description before it is published. Note that this does not apply
  to courtesy listings, allowing you to add additional contact info.

.. _htmlftppublisher:

HTML/FTP Publishing
-------------------

ASM can create websites for you using a simple templating system and optionally
upload them to an FTP server. The pages themselves can be split down by species
and age, or arranged numerically with a fixed number of animals per page. In
addition, a recently adopted page can be generated along with an rss.xml for
feed readers.

.. warning:: Static HTML publishing is deprecated for sheltermanager.com and is no longer available.

* Generate javascript database: The site search facilities require a Javascript
  database, indexing the available animal records. If you wish to include
  search facilities, make sure this box is ticked. 

* Generate thumbnail images: The publisher will create thumbnails of all the
  animal images. Thumbnail images have the same name as the animal image, but
  are prefixed with tn and an underscore. You can use tn_$$WebMediaFilename$$
  in a template to get the thumbnail image for the current animal. 

* Thumbnail size: The desired length in pixels of the longest side of the
  generated thumbnail.

* Output a separate page for each animal type: Output extra pages of the form
  ANIMALTYPE.EXTENSION, eg: Miscellaneous.html. This means you can reference
  the page of miscellaneous animals only from your website. If you have used
  any punctuation or spaces in the animal type, then they will be turned into
  to underscores. For example, a type of "D (Dog)" will create a page called
  D__Dog_.html

* Output a separate page for each species: Output extra pages of the form
  SPECIES.EXTENSION, eg: Dog.html. This means you can reference the page of
  adoptable dogs only from your website.

* Split species pages with a baby/adult prefix: If this option is selected, ASM
  will output species pages in the form baby/adultSPECIES.EXTENSION. Eg:
  babyCat.html and adultCat.html for cats/kittens. This option only works in
  conjunction with the "Output a separate page for each species" option.

* Split baby/adult age at: The split point to determine juvenile animals.

* Output an adopted animals page: If set to yes, a file named adopted.EXTENSION
  will be output that you can use to reference recently adopted animals.

* Output a deceased animals page: If set to yes, a file named deceased.EXTENSION
  will be output that you can use to reference recently deceased animals
  as a tribute page.

* Output a page with links to available online forms: If set to yes, a file
  named forms.EXTENSION will be output that contains a link to all the online
  forms in the database.

* Output an rss.xml page: If set to yes, a file named rss.xml will be output
  for feed readers. It will use the rss template if it is available in your
  database, if it's not then it will be constructed from a default template
  built into the program.

* Show animals adopted: If outputting an adopted animals page is on, how far
  back the adoptions should be included.

* Page extension: The file EXTENSION to give a page. Eg: html 

* Publishing template: The template ASM should use to construct the
  header/footer/body elements of the pages. ASM comes with a set of included
  templates, outlined in the next section.

* Animals per page: ASM will always output numbered pages of the form
  1.EXTENSION, 2.EXTENSION, etc. Specify here how many animals you'd like
  before moving on to the next page. By default, the system shows 10 animals
  per page, however the more animals you put on a page, the longer the page
  will take to load.

* Scale published images to: This box allows you to reduce the size of your
  animal images to a particular resolution.  ASM scales down pictures when you
  attach them under the media tab, so unless you want to make them smaller
  still, it's best to leave this at No Scaling.  
  
* Publish to folder: Choose the folder where output is to be generated. 
  
.. warning:: This folder is on the machine that ASM is installed on, not your local client PC. If this is left blank, a temporary folder will be used.

Included templates
^^^^^^^^^^^^^^^^^^

ASM comes with a number of site templates – plain, rss, littlebox and sm.com. 

* plain produces very simple HTML output - just the animal's picture and a few
  details in a list.

* rss produces XML output for interpreting by an RSS feed reader.

* sm.com uses CSS hover elements and javascript to do image substitution for
  icons and other tricks.

* littlebox is also more advanced, using CSS overlays and popups.

* responsive uses relative sizings to work equally well on mobile devices. It
  is not dissimilar to plain, but also features the ability to click an
  animal's photo for more information.

You can edit these templates under :menuselection:`Publishing --> Edit HTML
Publishing Templates` and add your own new ones if desired. Templates are made
up of three sections.
 
* The header block - this is output for each page before any animal records. 

* The footer block - this is output for each page after all the animal records.

* The body block - this is output for each animal record and has keys to pull
  data from the database and the animal's image(s). The keys available are
  those available for animal documents (see wordkeys in the appendix at the end
  of this document) and are enclosed in $$ - eg: $$ShelterCode$$ will output
  the animal's shelter code. 

A number of special keys are allowed in the header and footer blocks that pull
information from other areas of the system. These are: 

* $$ORGNAME$$ - Becomes your organisation's name 

* $$ORGADDRESS$$ - Your organisation's address 

* $$ORGTEL$$ - Your organisation's telephone number (all of these org fields
  can be found under :menuselection:`System --> Options`) 

* $$ORGEMAIL$$ - Your email address (this is taken from
  :menuselection:`Settings --> Options --> Email`) 

* $$USER$$ - Substitutes the current system user, including their real name 

* $$DATE$$ - The current date 

* $$TIME$$ - The current time 

* $$DATETIME$$ - The current date and time 

* $$VERSION$$ - The ASM version 

* $$NAV$$ - If you are using numbered pages, outputs navigation with the
  current page disabled and links to the other available pages. Returns
  a blank for recently adopted animal pages.

* $$TITLE$$ - An appropriate title based on the page being published. If
  it is a recently adopted page, the title will be "Recently adopted" in
  your language. Otherwise, it will be "Available for adoption".

* $$TOTAL$$ - The number of animals output by the publisher 

adoptapet.com
-------------

ASM can send data to 1-800-Save-A-Pet.com (now known as AdoptAPet.com) and
upload your animals for adoption directly to your account with them.

You will need to go to the publishing options first and enter the user name
given to you by AdoptAPet.com and your password. All you need to do then is
choose Publish to AdoptAPet.com. The options for filtering animals are the same
(see previous section for reference). 

If you have mapped the colours and wish to include them, you will need to tick
the “Include colors in column 9” checkbox on the AdoptAPet panel of the
publishing options.

You can also have ASM stop sending the import.cfg file after the first export.
This means you can then grab it from their FTP server and edit it yourself if
you wish to change any mappings, then put it back again. This is generally only
necessary for users who want to send colour information.

helpinglostpets.com
-------------------

ASM can send data to www.helpinglostpets.com, a map-based website that
publishes adoptable and found animals. Your ASM found data will also be
published as well as adoptable animals. You will need an organisation ID, FTP
username and password and to enter the postal/zipcode of your shelter.

Helpinglostpets.com is global and can accept data from shelters in any country.

maddiesfund.org / Maddie's Pet Assistant
----------------------------------------

ASM can send data to Maddie's Fund/MPA - an application to provide information
and interactive help to fosterers, adopters and other caregivers. Basic data on
the animal and contact information for the adopter/fosterer is sent.

petfinder.com
-------------

In addition to creating standalone websites with animals up for adoption, ASM
can also integrate with PetFinder.com and upload your animals for adoption
directly to your account with them.  You will need to go to
:menuselection:`Publishing --> Set Publishing Options` first and view the
PetFinder panel. Here, you should enter the shelter Id given to you by
PetFinder.com and the FTP password they have assigned to you.

You can also opt to have your shelter animals with the "Hold" flag sent with
the PetFinder H status, and shelter animals who have the word "Stray" in
their entry category sent with an F status. This will put those animals into
PetFinder's lost and found database to help with reuniting stray pets with
their owners.

Finally, you can choose to send previously adopted animals with
status X. This helps PetFinder keep track of your adopted animals and can be
useful for grants. If you have many thousands of previously adopted animals,
this can have an effect on performance.

.. note:: If you have created new Species or Breeds within ASM, you will need to map them to the available publisher options under the Breed and Species sections of :menuselection:`Settings --> Lookup Data`

If you have some that are not mapped, the publisher will fail with an error
message.

PetFinder has some quirks in that they indicate an unknown crossbreed by having
a blank secondary breed with the crossbreed flag set. Since ASM doesn't allow
you to set an empty second breed field, there's a workaround - If you make the
second breed the same as the first breed with the crossbreed flag set, ASM will
send that second breed as a blank to PetFinder. This behaviour can also be
triggered by setting your second breed to "Crossbreed", "Unknown" or "Mix".

.. warning:: You have to let PetFinder know that you are using ASM to upload your data. Do this by logging into the PetFinder members area, go to the Admin System Help Center, then Contact Us and send PetFinder Tech Support a message that you are using ASM to publish animal data via their FTP server. They should give you the FTP login information and make sure permissions and quotas are correct.

Extra fields
^^^^^^^^^^^^

PetFinder have a number of extra fields that you can set by creating additional
animal fields with certain names in your database. The system responds to the
field names, you can label them anything you want, they must be linked to
animal records.

* pfprimarycolor, pfsecondarycolor, pftertiarycolor (Text): ASM only uses a
  single value for animal color, so our color field cannot be mapped to PetFinder. 
  Instead, you can add the three color fields that PetFinder used and supply 
  appropriate values. The values they will accept for color depend on the species
  of your animal and can be found here: https://github.com/bobintetley/asm3/files/3487421/import.breeds.coats.colors.updated.Aug.2019.xlsx

* pfcoatlength (Text): PetFinder can accept a coat length value, which is one of
  Short, Long, Medium, Wire, Hairless, Curly

* pfadoptionfeewaived (Bool): a 1 or 0 to indicate that there is no adoption fee 
  for this animal.

* pfspecialneedsnotes (Text): If the animal has special needs, you can add a
  note about those needs to be output on their PetFinder listing.

petrescue.com.au
----------------

In addition to creating standalone websites with animals up for adoption, ASM
can also integrate with Petrescue.com.au and upload your animals for adoption
directly to your account with them. 

You will need to go to :menuselection:`Publishing --> Set Publishing Options`
first and view the PetRescue panel. Here, you should enter the access token given
to you by PetRescue.com.au. All you need to do then is choose
Publish to PetRescue.com.au in place of the normal internet publisher. The
options for filtering animals are the same (see previous section for
reference).

Determing whether an animal is vaccinated
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ASM will determine if your animals are vaccinated, wormed or heartworm treated
and indicate this to PetRescue via the following rules:

* If the animal has at least 1 previously given vaccination on file and there
  are no vaccinations outstanding, the vaccination flag is set.

* If the animal has a medical treatment containing the word "worm" and not
  the word "heart" in the last 6 months, the wormed flag is set.

* If the animal has a medical treatment containing the words "heart" and
  "worm" in the last 6 months, the heartworm treated flag is set.

Extra fields
^^^^^^^^^^^^

PetRescue have a number of extra fields that you can set by creating additional
animal fields with certain names in your database. The system responds to the
field names, you can label them anything you want, they must be linked to
animal records.

* bestfeature (Text): PetRescue show a tagline at the top of listings.  By default,
  this value is set to "Looking for love" on all listings. You are allowed 25
  letters and can override the tagline on a per-animal basis.

* needsconstantcare (Yes/No): This can be used to indicate that an adoptable
  cannot be left by itself.

* bredincareofgroup (Yes/No): Indicates the animal was bred whilst in the care
  of the group. Setting this to true makes breederid mandatory for all listings
  in South Australia after July 2018.

* needsfoster (Yes/No): Indicates that foster care is required for the animal.

.. note:: PetRescue integration relies on you naming your breeds and species with the same values that they do. If a breed does not match one of the PetRescue breeds, ASM will send it as "Mixed Breed" instead. 

rescuegroups.org
----------------

ASM can integrate with RescueGroups.org. They run a pet adoption portal service
that allows updating of multiple online services (including Facebook and
Petsmart). See their website for information on which services they update. For
more information on setting up RescueGroups to receive data from ASM, see their
userguide at https://userguide.rescuegroups.org/ and search for ASM.

To configure ASM, you will need to go to :menuselection:`Publish --> Set
Publishing Options` and enter the FTP username and password given to you by
RescueGroups (you can find this by going to :menuselection:`Services --> FTP
account` in the RescueGroups management interface).

Once you've done that, you can choose the Publish to RescueGroups.org menu
item. The options for filtering animals are the same as for the other
publishers.

.. warning:: If you are using the “Upload all images” option, ASM will only send the first 4 images (the first is always the preferred) as RescueGroups.org do not support more than 4 images per animal.

.. warning:: The RescueGroups.org publisher uses the publisher breeds and species mappings, so you should make sure that you have mappings for all your breeds and species before using the publisher (the publisher will give an error message if any species or breeds do not have mappings).

savour-life.com.au
----------------

ASM can integrate with savour-life.com.au and upload your animals for adoption
directly to your account with them. 

You will need to go to :menuselection:`Publishing --> Set Publishing Options`
first and view the SavourLife panel. Here, you should enter the username and
password given to you by SavourLife. The options for filtering animals are the
same as for other publishers, although ASM will only send dogs (Species 1) as
SavourLife will not accept listings for other species of animals.

Note that regardless of whether you have set the publishing option to
"Include animals who don't have a picture", SavourLife will not accept listings
without a photo, so we will not send animals who do not have a photo.

Determing whether an animal is vaccinated
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ASM will determined if your dogs are vaccinated, wormed or heartworm treated
and indicate this to SavourLife via the following rules:

* If the animal has at least 1 previously given vaccination on file and there
  are no vaccinations outstanding, the vaccination flag is set.

* If the animal has a medical treatment containing the word "worm" and not
  the word "heart" in the last 6 months, the wormed flag is set.

* If the animal has a medical treatment containing the words "heart" and
  "worm" in the last 6 months, the heartworm treated flag is set.

Extra fields
^^^^^^^^^^^^

SavourLife have extra fields that you can set by creating additional 
fields with certain names in your database. The system responds to the field
names, you can label them anything you want, they must be linked to animal
records.

* enquirynumber (Text): SavourLife will give potential adopters an enquiry 
  number that can be given to the shelter. This enquiry number is used to link
  adopters with the adopted animal and qualify them for free food from
  SavourLife.

* needsfoster (Yes/No): Indicates that foster care is required for the animal.

* interstateadoptable (Yes/No): Overrides the global interstate adoptable value on
  the config screen and allows you to apply it on a per-animal basis instead.

.. note:: SavourLife integration relies on you naming your breeds and species with the same values that they do. If a breed does not match one of the SavourLife breeds, ASM will send it as "Mixed Breed" instead. 

shelteranimalscount.org
-----------------------

ASM can automatically update your statistics with shelteranimalscount.org, 
the US service for aggregating statistics on animal intakes and
outcomes (this publisher is sheltermanager.com only).

First, you will need to contact shelteranimalscount and let them know your
sheltermanager.com account number. This is so they can tie your organisation
to the incoming data.

Next, go to :menuselection:`Publish --> Set Publishing Options -->
ShelterAnimalsCount` and configure the entry categories in your database that
represent Stray, Surrender and TNR. It is likely you will only have one for
Stray and TNR, but may have many entry categories that correspond to a
surrender. There is no config for transfers as we use the "Transfer In" tickbox
on the animal's record to determine that. 

Like the other publishers, shelteranimalscount will run automatically overnight
to send updates and does not require any interaction.

When the publisher runs, the first phase is to determine which months of data
it will send. 

* If today is the 1st of the month, last month's data will be sent.

* If an animal or movement record with an event date in a previous month has
  been added or changed in the last 24 hours, that month's data will be sent.
  An event date is one of intake, return, death or movement.

.. warn:: Like the SAC reports, this publisher relies on the default species from the default database. If you have deleted the original species and recreated them, you will need to contact sheltermanager.com support for assistance.

petslocated.com
---------------

ASM can integrate with petslocated.com, a lost/found matching database for
shelters in the UK.

To configure ASM, you will need to go to :menuselection:`Publish --> Set
Publishing Options` and enter your petslocated.com customer number. Once the
petslocated.com publisher is enabled, ASM will automatically send all active
found animal records to them with the overnight batch.

The petslocated.com publisher also has a pair of additional options you can set
for "Include shelter animals" and "Only shelter animals with this flag". 

If you set "Include shelter animals" to "Yes", you will need to specify a flag.
You should create an animal flag (:menuselection:`Settings --> Lookup Data`) to
tag shelter animals that you would like to be sent to petslocated - typically
strays and animals that have come via dog wardens, etc.

AVID/PETtrac UK
---------------

ASM can register animals with the AVID PETtrac database for shelters in the
United Kingdom.

When you publish to PETtrac, ASM finds all animals with a PETtrac microchip
(they are 15 digits and start with 977) that have been adopted and sends their
information and new owner info to PETtrac to update their records. ASM tracks
the date PETtrac was last updated, so if the animal is returned and adopted
again, another update will be done automatically.

In order to handle re-registrations, you will need to nominate one of your
system users as the "authorised user". This user account needs to have a real
name and an electronic signature on file. When re-registrations are generated,
ASM will create a signed PDF disclaimer document to transmit to AVID,
explaining that the shelter has done all it can to find the previous owner of
the animal.

.. warning:: If you have the "Intake" option set of "Register microchips after", the AVID publisher will ignore it. Instead, AVID have a "selfreg" parameter, which ASM will always set so the shelter is always logged as the secondary contact on a chip.

idENTICHIP/Anibase UK
---------------------

ASM can register animals with the Anibase database for shelters in the United
Kingdom.

When you publish to Anibase, ASM finds all animals with an idENTICHIP microchip
(they are 15 digits and start with 9851 or 9861) that have been adopted and
sends their information and new owner info to Anibase to update their records.
ASM tracks the date Anibase was last updated, so if the animal is returned and
adopted again, another update will be done automatically.

AKC Reunite
-----------

ASM can register microchips with AKC Reunite, part of the American Kennel Club,
who supply microchips to US organisations and pet owners. AKC microchips are 
either 15-digits, starting with 956 or 10-digits, starting with 0006 or 0007.

They will optionally accept registration of any microchip, although this has
to be agreed with them first. 

BuddyID
-------

ASM can register microchips with BuddyID, who supply microchips to US 
organisations and pet owners. Their registry is free to use and will accept
registration of microchips from any manufacturer. To signup, you will need
to get in touch with them and have them issue you with a "provider code"
to configure in ASM.

ASM will attempt to register all microchips with BuddyID and as with
the other chip registration publishers, will track when it last updated a
chip with them in case of subsequent adoption or reclaim.

FoundAnimals/24Pet
------------------

ASM can register microchips with foundanimals.org (now named FoundAnimals/24Pet
after being acquired by PetHealth), a non-profit organisation that supplies
microchips to US shelters.

Their microchip registry is completely free and accepts microchips from any
provider. To signup, just get in touch and request a folder name from them
to configure in ASM.

ASM will attempt to register all microchips with foundanimals.org and as with
the other chip registration publishers, will track when it last updated a
chip with them in case of subsequent adoption or reclaim.

HomeAgain
----------

ASM can register microchips with HomeAgain, a company that supplies microchips
to US shelters and pet owners. HomeAgain microchips are 15-digits, starting with 985.

PetLink
-------

ASM can register microchips with PetLink, a company that supply microchips to
US shelters.

When you register animals with PetLink, ASM finds all animals with a PetLink
microchip (their microchips are 15 digits and start with 98102) that have been
adopted and sends their information and new owner info to PetLink to update
their records. If an animal is returned and adopted out again later, ASM will
automatically update PetLink again.

SmartTag
--------

ASM can register animals with SmartTag PETID, a company that supply collar tags
to shelters for free in the US. Each tag has a unique number on it and if your
locale is set to US and you have SmartTag PETID Settings in your database, you
can enter the tag information in fields on the animal health and identification
section.

When you register animals with SmartTag, ASM finds all animals with a SmartTag
that have been adopted and sends their information (along with owner info and a
picture) to SmartTag so they can be identified in the event they are lost.  If
an animal is returned and adopted out again later, ASM will register the tag
again to the new owner.

SmartTag also supply ISO microchips. ASM will also register SmartTag microchips
(15 digits starting with 90007400) in a similar manner to ASM's other chip
registration publishers.

Exclude animals from specific publishers
----------------------------------------

It is possible to exclude an animal from a specific publisher. To do this,
create a new animal flag called "Exclude from PUBLISHER", where PUBLISHER is
the name of the service you wish to exclude. Eg: "Exclude from PetFinder".

Assigning this animal flag to your animal will then prevent it being sent by
that publisher. You can create flags for all the 3rd party publishers you use
and assign them in combination where necessary.

The flag names are not case sensitive. The names should not include any domains,
eg: petfinder, adoptapet, rescuegroups, maddiesfund, petrescue, savourlife

This is useful in situations where you get inundanted with applications for
very popular animals and only want to put them on your own website.
