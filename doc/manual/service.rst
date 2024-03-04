.. _serviceapi:

Service API
===========

ASM includes a service API that you can call from other software via HTTP. To
call the API you construct a URL to the service controller. The service
controller is /service, so if you are accessing a local ASM from your local
machine, the URL will start http://localhost:5000/service. If you are using
sheltermanager.com, the URL will start https://service.sheltermanager.com/asmservice.

If you are using sheltermanager.com, or have enabled the option
CACHE_SERVICE_RESPONSES in your sitedefs.py, please be aware that some service
call responses are cached for performance. The cache time is indicated with the
call below.

While the examples here show passing the parameters with HTTP GET requests, you
can POST the parameters too if you prefer.

The service requires the following parameters:

* account: If this is a sheltermanager.com service call, the user's account
  number. Can be omitted for other installations.

* username: A valid ASM user.

* password: A valid ASM password. From a security standpoint, it's better to
  create at least one ASM user dedicated to calling the service to assist with
  audit trails and to lock it down so an attacker with the URL cannot change
  your data or view anything you don't want them to.

* method: A service method to call

* animalid / title: An animal ID or title depending on the service method
  called.

Animal Datasets
---------------

Many of the json and xml service calls return a dataset of animals, a sample animal
JSON result looks like this::

   [
       {
           "ACCEPTANCENUMBER": "",
           "ACTIVEMOVEMENTADOPTIONNUMBER": null,
           "ACTIVEMOVEMENTCOMMENTS": null,
           "ACTIVEMOVEMENTCREATEDBY": null,
           "ACTIVEMOVEMENTCREATEDBYNAME": null,
           "ACTIVEMOVEMENTCREATEDDATE": null,
           "ACTIVEMOVEMENTDATE": null,
           "ACTIVEMOVEMENTDONATION": null,
           "ACTIVEMOVEMENTID": 0,
           "ACTIVEMOVEMENTINSURANCENUMBER": null,
           "ACTIVEMOVEMENTLASTCHANGEDBY": null,
           "ACTIVEMOVEMENTLASTCHANGEDDATE": null,
           "ACTIVEMOVEMENTREASONFORRETURN": null,
           "ACTIVEMOVEMENTRESERVATIONDATE": null,
           "ACTIVEMOVEMENTRETURN": null,
           "ACTIVEMOVEMENTRETURNDATE": null,
           "ACTIVEMOVEMENTTRIALENDDATE": null,
           "ACTIVEMOVEMENTTYPE": null,
           "ACTIVEMOVEMENTTYPENAME": null,
           "ACTIVERESERVATIONS": 3,
           "ADDITIONALFLAGS": "|",
           "ADOPTAPETCOLOUR": "Black",
           "ADOPTIONCOORDINATOREMAILADDRESS": null,
           "ADOPTIONCOORDINATORHOMETELEPHONE": null,
           "ADOPTIONCOORDINATORID": 0,
           "ADOPTIONCOORDINATORMOBILETELEPHONE": null,
           "ADOPTIONCOORDINATORNAME": null,
           "ADOPTIONCOORDINATORWORKTELEPHONE": null,
           "AGEGROUP": "Senior",
           "AGEGROUPACTIVEMOVEMENT": "Senior",
           "ANIMALAGE": "12 years 7 months.",
           "ANIMALCOMMENTS": "Cat that needs a longer bio than 20 chars.",
           "ANIMALCONTROLINCIDENTDATE": null,
           "ANIMALCONTROLINCIDENTID": null,
           "ANIMALCONTROLINCIDENTNAME": null,
           "ANIMALNAME": "Sarah",
           "ANIMALTYPEID": 2,
           "ANIMALTYPENAME": "U (Unwanted Cat)",
           "ARCHIVED": 0,
           "ASILOMARINTAKECATEGORY": 0,
           "ASILOMARISTRANSFEREXTERNAL": 0,
           "ASILOMAROWNERREQUESTEDEUTHANASIA": 0,
           "BASECOLOURID": 1,
           "BASECOLOURNAME": "Black",
           "BONDEDANIMAL1ARCHIVED": null,
           "BONDEDANIMAL1CODE": null,
           "BONDEDANIMAL1NAME": null,
           "BONDEDANIMAL2ARCHIVED": null,
           "BONDEDANIMAL2CODE": null,
           "BONDEDANIMAL2ID": 0,
           "BONDEDANIMAL2NAME": null,
           "BONDEDANIMALID": 0,
           "BREED2ID": 231,
           "BREEDID": 231,
           "BREEDNAME": "British Shorthair",
           "BREEDNAME1": "British Shorthair",
           "BREEDNAME2": "British Shorthair",
           "BROUGHTINBYEMAILADDRESS": "",
           "BROUGHTINBYHOMETELEPHONE": "",
           "BROUGHTINBYJURISDICTION": "",
           "BROUGHTINBYMOBILETELEPHONE": "",
           "BROUGHTINBYOWNERADDRESS": "",
           "BROUGHTINBYOWNERCOUNTY": "",
           "BROUGHTINBYOWNERID": "",
           "BROUGHTINBYOWNERNAME": "",
           "BROUGHTINBYOWNERPOSTCODE": "",
           "BROUGHTINBYOWNERTOWN": "",
           "BROUGHTINBYWORKTELEPHONE": "",
           "COATTYPE": 4,
           "COATTYPENAME": "Corded",
           "CODE": "1D",
           "COMBITESTDATE": null,
           "COMBITESTED": 0,
           "COMBITESTEDNAME": "No",
           "COMBITESTRESULT": 0,
           "COMBITESTRESULTNAME": "Unknown",
           "CREATEDBY": "robin",
           "CREATEDDATE": "2010-01-18T10:20:50",
           "CROSSBREED": 0,
           "CROSSBREEDNAME": "No",
           "CRUELTYCASE": 0,
           "CRUELTYCASENAME": "No",
           "CURRENTOWNERADDRESS": "",
           "CURRENTOWNERCOUNTRY": "",
           "CURRENTOWNERCOUNTY": "",
           "CURRENTOWNEREMAILADDRESS": "",
           "CURRENTOWNEREXCLUDEEMAIL": "",
           "CURRENTOWNERFORENAMES": "",
           "CURRENTOWNERHOMETELEPHONE": "",
           "CURRENTOWNERID": "",
           "CURRENTOWNERINITIALS": "",
           "CURRENTOWNERJURISDICTION": "",
           "CURRENTOWNERMOBILETELEPHONE": "",
           "CURRENTOWNERNAME": "",
           "CURRENTOWNERPOSTCODE": "",
           "CURRENTOWNERSURNAME": "",
           "CURRENTOWNERTITLE": "",
           "CURRENTOWNERTOWN": "",
           "CURRENTOWNERWORKTELEPHONE": "",
           "CURRENTVETADDRESS": null,
           "CURRENTVETCOUNTY": null,
           "CURRENTVETEMAILADDRESS": null,
           "CURRENTVETID": 0,
           "CURRENTVETLICENCENUMBER": null,
           "CURRENTVETNAME": null,
           "CURRENTVETPOSTCODE": null,
           "CURRENTVETTOWN": null,
           "CURRENTVETWORKTELEPHONE": null,
           "DAILYBOARDINGCOST": 0,
           "DATEBROUGHTIN": "2010-01-18T00:00:00",
           "DATEOFBIRTH": "2008-01-18T00:00:00",
           "DAYSONSHELTER": 3886,
           "DECEASEDDATE": null,
           "DECLAWED": 0,
           "DECLAWEDNAME": "No",
           "DIEDOFFSHELTER": 0,
           "DIEDOFFSHELTERNAME": "No",
           "DISPLAYLOCATION": "Dog Block::3",
           "DISPLAYLOCATIONNAME": "Dog Block",
           "DOCMEDIADATE": "2015-05-11T00:00:00",
           "DOCMEDIANAME": "198.jpg",
           "ENTRYREASONID": 7,
           "ENTRYREASONNAME": "Stray",
           "ESTIMATEDDOB": 0,
           "ESTIMATEDDOBNAME": "No",
           "EXTRAIDS": "",
           "FEE": 0,
           "FLVRESULT": 0,
           "FLVRESULTNAME": "Unknown",
           "HASACTIVERESERVE": 0,
           "HASACTIVERESERVENAME": "No",
           "HASFUTUREADOPTION": 0,
           "HASPERMANENTFOSTER": 0,
           "HASSPECIALNEEDS": 0,
           "HASSPECIALNEEDSNAME": "No",
           "HASTRIALADOPTION": 0,
           "HASTRIALADOPTIONNAME": "No",
           "HEALTHPROBLEMS": "",
           "HEARTWORMTESTDATE": null,
           "HEARTWORMTESTED": 0,
           "HEARTWORMTESTEDNAME": "No",
           "HEARTWORMTESTRESULT": 0,
           "HEARTWORMTESTRESULTNAME": "Unknown",
           "HIDDENANIMALDETAILS": "",
           "HOLDUNTILDATE": null,
           "ID": 174,
           "IDENTICHIP2DATE": null,
           "IDENTICHIP2NUMBER": "",
           "IDENTICHIPDATE": null,
           "IDENTICHIPNUMBER": "",
           "IDENTICHIPPED": 0,
           "IDENTICHIPPEDNAME": "No",
           "ISCOURTESY": 0,
           "ISDOA": 0,
           "ISDOANAME": "No",
           "ISGOODWITHCATS": 0,
           "ISGOODWITHCATSNAME": "Yes",
           "ISGOODWITHCHILDREN": 2,
           "ISGOODWITHCHILDRENNAME": "Unknown",
           "ISGOODWITHDOGS": 2,
           "ISGOODWITHDOGSNAME": "Unknown",
           "ISHOLD": 0,
           "ISHOUSETRAINED": 2,
           "ISHOUSETRAINEDNAME": "Unknown",
           "ISNOTAVAILABLEFORADOPTION": 0,
           "ISNOTAVAILABLEFORADOPTIONNAME": "No",
           "ISNOTFORREGISTRATION": 0,
           "ISNOTFORREGISTRATIONNAME": "No",
           "ISPICKUP": 0,
           "ISPICKUPNAME": "No",
           "ISQUARANTINE": 0,
           "ISTRANSFER": 0,
           "ISTRANSFERNAME": "No",
           "JURISDICTIONID": 0,
           "JURISDICTIONNAME": null,
           "LASTCHANGEDBY": "robin",
           "LASTCHANGEDDATE": "2018-08-27T10:25:07.534155",
           "LOOKUPDEFAULT": "Item 3",
           "MARKINGS": "",
           "MOSTRECENTENTRYDATE": "2010-01-18T00:00:00",
           "NEUTERED": 1,
           "NEUTEREDBYVETID": 0,
           "NEUTEREDDATE": "2009-01-18T00:00:00",
           "NEUTEREDNAME": "Yes",
           "NEUTERINGVETADDRESS": null,
           "NEUTERINGVETCOUNTY": null,
           "NEUTERINGVETEMAILADDRESS": null,
           "NEUTERINGVETLICENCENUMBER": null,
           "NEUTERINGVETNAME": null,
           "NEUTERINGVETPOSTCODE": null,
           "NEUTERINGVETTOWN": null,
           "NEUTERINGVETWORKTELEPHONE": null,
           "NONSHELTERANIMAL": 0,
           "NONSHELTERANIMALNAME": "No",
           "ORIGINALOWNERADDRESS": "",
           "ORIGINALOWNERCOUNTRY": "",
           "ORIGINALOWNERCOUNTY": "",
           "ORIGINALOWNEREMAILADDRESS": "",
           "ORIGINALOWNERFORENAMES": "",
           "ORIGINALOWNERHOMETELEPHONE": "",
           "ORIGINALOWNERID": "",
           "ORIGINALOWNERINITIALS": "",
           "ORIGINALOWNERJURISDICTION": "",
           "ORIGINALOWNERMOBILETELEPHONE": "",
           "ORIGINALOWNERNAME": "",
           "ORIGINALOWNERPOSTCODE": "",
           "ORIGINALOWNERSURNAME": "",
           "ORIGINALOWNERTITLE": "",
           "ORIGINALOWNERTOWN": "",
           "ORIGINALOWNERWORKTELEPHONE": "",
           "OWNERID": 0,
           "OWNERNAME": null,
           "OWNERSVETADDRESS": null,
           "OWNERSVETCOUNTY": null,
           "OWNERSVETEMAILADDRESS": null,
           "OWNERSVETID": 0,
           "OWNERSVETLICENCENUMBER": null,
           "OWNERSVETNAME": null,
           "OWNERSVETPOSTCODE": null,
           "OWNERSVETTOWN": null,
           "OWNERSVETWORKTELEPHONE": null,
           "PETFINDERBREED": "British Shorthair",
           "PETFINDERBREED2": "British Shorthair",
           "PETFINDERSPECIES": "Cat",
           "PICKUPADDRESS": "",
           "PICKUPLOCATIONID": 0,
           "PICKUPLOCATIONNAME": null,
           "PTSREASON": "",
           "PTSREASONID": 8,
           "PTSREASONNAME": "Biting",
           "PUTTOSLEEP": 0,
           "PUTTOSLEEPNAME": "No",
           "RABIESTAG": "",
           "REASONFORENTRY": "",
           "REASONNO": "",
           "RECENTLYCHANGEDIMAGES": 0,
           "RECORDVERSION": 102507,
           "RESERVATIONDATE": null,
           "RESERVATIONSTATUSNAME": null,
           "RESERVEDOWNERADDRESS": "",
           "RESERVEDOWNERCOUNTY": "",
           "RESERVEDOWNEREMAILADDRESS": "",
           "RESERVEDOWNERHOMETELEPHONE": "",
           "RESERVEDOWNERID": "",
           "RESERVEDOWNERJURISDICTION": "",
           "RESERVEDOWNERMOBILETELEPHONE": "",
           "RESERVEDOWNERNAME": "",
           "RESERVEDOWNERPOSTCODE": "",
           "RESERVEDOWNERTOWN": "",
           "RESERVEDOWNERWORKTELEPHONE": "",
           "SEX": 0,
           "SEXNAME": "Female",
           "SHELTERCODE": "D2010001",
           "SHELTERLOCATION": 1,
           "SHELTERLOCATIONDESCRIPTION": "",
           "SHELTERLOCATIONNAME": "Dog Block",
           "SHELTERLOCATIONUNIT": "3",
           "SHORTCODE": "1D",
           "SITEID": 1,
           "SITENAME": "main",
           "SIZE": 1,
           "SIZENAME": "Large",
           "SMARTTAG": 0,
           "SMARTTAGDATE": null,
           "SMARTTAGNUMBER": "",
           "SMARTTAGSENTDATE": null,
           "SMARTTAGTYPE": 0,
           "SPECIESID": 2,
           "SPECIESNAME": "Cat",
           "TATTOO": 0,
           "TATTOODATE": null,
           "TATTOONAME": "No",
           "TATTOONUMBER": "",
           "TIMEONSHELTER": "10 years 7 months.",
           "TOTALDAYSONSHELTER": 3162,
           "TOTALTIMEONSHELTER": "8 years 7 months.",
           "UNIQUECODEID": 0,
           "UNITSPONSOR": "Mr and Mrs Smith",
           "VACCGIVENCOUNT": 0,
           "VACCOUTSTANDINGCOUNT": 0,
           "WEBSITEIMAGECOUNT": 2,
           "WEBSITEMEDIADATE": "2013-05-12T09:13:21",
           "WEBSITEMEDIAID": 118,
           "WEBSITEMEDIANAME": "118.jpg",
           "WEBSITEMEDIANOTES": "Cat that needs a longer bio than 20 chars.",
           "WEBSITEVIDEONOTES": "",
           "WEBSITEVIDEOURL": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
           "WEIGHT": 10.0,
           "YEARCODEID": 1
       }
   ]

animal_image
------------

.. rubric:: Cache time: 1 hour

Returns an animal's preferred image. Send the id of the animal::

    http://localhost:5000/service?method=animal_image&animalid=520&seq=1

An optional "seq" parameter can be included to return the animal's other
available images. seq=1 returns the preferred image (and will be assumed if
that parameter is omitted), seq=2 returns the second available image, etc. seq
is a 1-based count and can be used with the "WebsiteImageCount" property
included in animal records (which contains the number of images an animal has)
to programatically grab all the images for a particular animal.

animal_thumbnail
----------------

.. rubric:: Cache time: 1 day

Returns an animal's preferred image as a thumbnail. Send the id of the animal::
    
    http://localhost:5000/service?method=animal_thumbnail&animalid=520

The thumbnail will be sized to whatever the main application is using
(default is 150 pixels along the longest side). You can choose the thumbnail
size under :menuselection:`Publishing -> Set Publishing Options -> All Publishers`

animal_view
-----------

.. rubric:: Cache time: 10 minutes

Returns a webpage with information for one adoptable animal, constructed from the
animalview HTML publishing template (editable at :menuselection:`Publishing ->
Edit HTML publishing templates`). Pass the id of the animal::

    http://localhost:5000/service?method=animal_view&animalid=520

When you use :menuselection:`Share --> Link to this animal` on an animal's record, 
it is this service call that the system redirects you to.

If the animal is no longer adoptable, an error page will be displayed. If you prefer, you
can create an HTML publishing template called "animalviewnotadoptable" that will display
instead for animals that can no longer be adopted.

You can also optionally specify a style parameter to choose a template to use other
than animalview::

    http://localhost:5000/service?method=animal_view&animalid=520&style=animalviewcarousel


animal_view_adoptable_js
------------------------

.. rubric:: Cache time: 10 minutes

Returns a javascript file that when executed injects thumbnails of all
adoptable animals into the page with links to the animal_view service call. It
is most useful as the src attribute for a <script> tag.

The page must contain a div with an id attribute of "asm3-adoptables", where
the adoptable animal thumbnails are to appear. If div#asm3-adoptables cannot be
found, a popup error message will appear.

Here's an example page showing how to inject your adoptable animal list::

    <!DOCTYPE html>
    <html>
    <head>
    <title>Adoptable Animals</title>
    <style>
    .asm3-adoptable-thumbnail { border-radius: 8px; }
    </style>
    <body>
    
    <div id="asm3-adoptables" />
    <script src="http://localhost:5000/service?method=animal_view_adoptable_js"></script>

    </body>
    </html>

CSS and Styles
^^^^^^^^^^^^^^

The adoptable_js output is unstyled - just a thumbnail with a name/link below
and two lines of brief text containing some basic information about the animal.
You can style this information by adding CSS to your stylesheets for the
following classes:

* asm3-filters : The div surrounding the SELECT dropdown filters
* asm3-adoptable-list: The div surrounding all the animal thumbnails
* asm3-adoptable-item : The div surrounding each animal thumbnail
* asm3-adoptable-link : The a tag enclosing the thumbnail and animal name
* asm3-adoptable-thumbnail : The thumbnail img tag
* asm3-adoptable-name : The animal's name
* asm3-adoptable-reserved : The div surrounding the image if the animal is reserved
* asm3-adoptable-tagline : The brief animal information

and the following elements by their id attribute:

* asm3-adoptable-iframe-overlay: The div surrounding the popup iframe (if used)
* asm3-adoptable-iframe-close: The close link at the top right of the popup
* asm3-adoptable-iframe: The popup iframe itself

Eg: To add rounded corners to the thumbnails and show the animal's name in
bold, add this to your CSS::

    .asm3-adoptable-name { font-weight: bold; }
    .asm3-adoptable-thumbnail { border-radius: 8px; }

To increase the size of the close link, add this::

    #asm3-adoptable-iframe-close { font-size: 200%; }

Much more advanced and sophisticated styling can be done from these classes and
selectors. For example, to float a reserved banner over the top right corner of
animals with reservations, try this::

   .asm3-adoptable-reserved {
       position: relative;
       color: #fff;
       display: inline-block;
       padding: 5px;
       overflow: hidden;
       font-family: Arial, sans-serif;
       font-size: 8pt;
       font-weight: bold;
   }
   .asm3-adoptable-reserved span:before {
       content: "\00a0\00a0\00a0\00a0\00a0RESERVED";
   }
   .asm3-adoptable-reserved span {
       position: absolute; 
       display: inline-block;
       right: -25px;
       box-shadow: 0px 0px 10px rgba(0,0,0,0.2), inset 0px 5px 30px rgba(255,255,255,0.2);
       text-align: center;
       top: 6px;
       background: #ff0000;
       width: 100px;
       padding: 3px 10px;
       opacity: 0.9;
       transform: rotate(45deg);
   }

Thumbnail Size
^^^^^^^^^^^^^^

By default, animal thumbnails will be displayed at the default system size
(150px), which can be set up to a maximum of 300px in the options at 
:menuselection:`Publishing -> Set Publishing Options -> All Publishers`

If you would like to use larger images than 300px in the thumbnail list, you
can choose to use the full size images rather than thumbnails, then use CSS to
constrain them to the size you prefer::

    <script>
    asm3_adoptable_fullsize_images = true;
    </script>
    <style>
    .asm3-adoptable-thumbnail { max-width: 400px; } 
    </style>
    <div id="asm3-adoptables" />
    <script src="http://localhost:5000/service?method=animal_view_adoptable_js"></script>


Translations
^^^^^^^^^^^^

It's possible to translate any of the text output by the adoptable list on the
fly. By default, it only uses text from your database values so they will match
the language of your database. 

You can add on-the-fly translations by adding a script tag with a dictionary
called asm3_adoptable_translations above the script that makes the service
call. Eg to translate some English species to French and to change the default (any
species) to all as well as the no results and CLOSE link text::
   
    <script>
    asm3_adoptable_translations = {
        "No results": "We don't have any animals for adoption right now, check back soon!",
        "Dog": "Chien",
        "Cat": "Chat",
        "Pig": "Cochon",
        "(any species)": "all",
        "CLOSE": "Return to my webpage"
    }
    </script>
    <div id="asm3-adoptables" />
    <script src="http://localhost:5000/service?method=animal_view_adoptable_js"></script>


Filters
^^^^^^^

You can also add a filter callback, which allows you to implement your own
filter based on other elements in the page. The callback receives the complete
animal record and must return true if the record is to be included in the list
of thumbnails.

For example, to only output animals with a species of dog, you could use
this callback::

    <script>
    function asm3_adoptable_filter(a, index, arr) {
        return a.SPECIESNAME == "Dog";
    }
    </script>
    <div id="asm3-adoptables" />
    <script src="http://localhost:5000/service?method=animal_view_adoptable_js"></script>

Additional arguments are also passed to asm3_adoptable_filter containing the
index of the current element and complete list. 
Definition: asm3_adoptable_filter(item, index, arr)

Which dropdowns appear depends on the asm3_adoptable_filters string. To use
them all, include the following asm3_adoptable_filters line. The order in which
they appear in the filters line is also used to output that piece of
information below the animal's name in the list::

    <script>
    asm3_adoptable_filters = "sex breed agegroup size species goodwith where site";
    </script>
    <div id="asm3-adoptables" />
    <script src="http://localhost:5000/service?method=animal_view_adoptable_js"></script>

The "goodwith", "where" and "site" filters are special in that they do not
augment the description of the animal. The "goodwith" filter allows the user to
filter for animals who are good with dogs, cats or children. The where filter
allows them to filter for animals who are either in the shelter, fostered or
listed as a courtesy for someone else.

Sort
^^^^

You can choose the sort order by setting an asm3_adoptable_sort variable. The default is
ANIMALNAME, but another useful value is -DAYSONSHELTER to output animals based on how
long they've been on shelter with the longest first. Preceding the sort field with a 
minus symbol - will sort in descending order. You can also use precede the sort field with
an at symbol @ to do a numeric sort rather than a string/alphanumeric sort::

    <script>
    asm3_adoptable_sort = "-@DAYSONSHELTER";
    </script>
    <div id="asm3-adoptables" />
    <script src="http://localhost:5000/service?method=animal_view_adoptable_js"></script>

A special sort keyword of SHUFFLE can also be used, if instead of sorting you'd like the
adoptable animals to be output in a random order::
   
    <script>
    asm3_adoptable_sort = "SHUFFLE";
    </script>
    <div id="asm3-adoptables" />
    <script src="http://localhost:5000/service?method=animal_view_adoptable_js"></script>

Style
^^^^^

You can choose the template that will be passed to the animal_view call when an animal's
adoptable profile is viewed. By default, this value is "animalview" to use the template
with that name, but it can be overridden::

    <script>
    asm3_adoptable_style = "animalviewcarousel";
    </script>
    <div id="asm3-adoptables" />
    <script src="http://localhost:5000/service?method=animal_view_adoptable_js"></script>


Extra Content
^^^^^^^^^^^^^

It's also possible to add an extra content callback, which adoptable_js calls
for every animal it outputs. For example, to add the animal's bio below the
thumbnail and basic info::

    <script>
    asm3_adoptable_filters = "sex breed agegroup size species";
    asm3_adoptable_extra = function(a) {
        return a.WEBSITEMEDIANOTES;
    }
    </script>
    <div id="asm3-adoptables" />
    <script src="http://localhost:5000/service?method=animal_view_adoptable_js"></script>

You could set .asm3-adoptable-tagline to display: none and then use an extra
content callback to output and format any data from the animal's record in the
way you want and override the default behaviour.

Limit
^^^^^

You can limit the number of animals rendered by the adoptable_js output. This
is useful if you want to only show a limited number of animals - eg: If this
call is on the home page of your website and you'd like to show some featured
animals.

For example, this will limit output to the first 3 animals in the set. Combined
with the -DAYSONSHELTER sort, it will show the 3 animals who have been on
shelter the longest::

    <script>
    asm3_adoptable_sort = "-DAYSONSHELTER";
    asm3_adoptable_limit = 3;
    </script>
    <div id="asm3-adoptables" />
    <script src="http://localhost:5000/service?method=animal_view_adoptable_js"></script>

Popup iFrame
^^^^^^^^^^^^

By default, clicking on an animal thumbnail or link will load the target
animalview page in a new browser tab. However, the system can also load the
page in a floating iframe so that viewing adoptable animals does not leave your
site. You can enable this behaviour by setting asm3_adoptable_iframe = true in
your script. Eg::

    <script>
    asm3_adoptable_filters = "sex breed agegroup size species";
    asm3_adoptable_iframe = true;
    asm3_adoptable_iframe_fixed = true;
    </script>
    <div id="asm3-adoptables" />
    <script src="http://localhost:5000/service?method=animal_view_adoptable_js"></script>

Some positioning styles for the iframe have to be supplied programatically and
cannot be set by CSS (everything else can be), but there are a couple of
javascript variables you can set for them instead. 

Eg: To fix the iframe height at 2000 pixels and use a gray background instead
of the default of white::

    <script>
    asm3_adoptable_filters = "sex breed agegroup size species";
    asm3_adoptable_iframe = true;
    asm3_adoptable_iframe_height = "2000px";
    asm3_adoptable_iframe_bgcolor = "#888";
    </script>
    <div id="asm3-adoptables" />
    <script src="http://localhost:5000/service?method=animal_view_adoptable_js"></script>

By default, the iframe will use absolute positioning. If your page has multiple
screens of vertical height, this will cause it to scroll back to the top when
viewing an animal. Setting asm3_adoptable_iframe_fixed will use fixed
positioning instead, which keeps the position of the parent page when viewing
animals, but this has been found to be less compatible with some browsers and
iframes.

animal_view_adoptable_html
--------------------------

.. rubric:: Cache time: 10 minutes

Returns a complete HTML document that references animal_view_adoptable_js to
show a list of adoptable animals. It looks for an HTML template called
"animalviewadoptable" and falls back to a basic internal template if it does
not exist::

    http://localhost:5000/service?method=animal_view_adoptable_html

csv_import
----------

The CSV import endpoint can be used to send CSV data to the system. GET or POST
can be used and it accepts the following parameters:

* data: The base64 encoded CSV data.

* encoding: The text encoding used for the CSV data (defaults to utf-8 if not supplied)

As this is a synchronous method call, you should not use this method to import large
amounts of data - that should be done with the asynchronous screen at 
:menuselection:`Settings --> Import a CSV File`. This method call is intended for
small amounts of data and individual records being sent by other systems for integration 
purposes.

Unlike the Import a CSV File screen, you cannot set any of the CSV import options. When
importing via this method, "Merge Duplicates" will be on, but all other options will
be off.

The return value is a JSON document containing the success count, the number of rows in
the CSV data and details of errors from any rows that failed to be imported::

    { rows: 52,
      success: 51,
      errors: [
        [ 5, "Jeff,2,Dog,928310983219283", "This microchip number has already been used" ]
      ]
    }

csv_mail and csv_report
-----------------------

.. rubric:: Cache time: 10 minutes

Returns a CSV file containing a mail merge or report. Pass the name of the mail
merge/report in the title attribute and if the merge requires any parameters,
you can pass those too just like with html_report::

    http://localhost:5000/service?method=csv_report&username=user&password=letmein&title=Detailed+Shelter+Inventory

json_mail and json_report
-----------------------

.. rubric:: Cache time: 10 minutes

Returns a dataset containing a mail merge or report. Pass the name of the mail
merge/report in the title attribute and if the merge requires any parameters,
you can pass those too just like with html_report::

    http://localhost:5000/service?method=json_report&username=user&password=letmein&title=Detailed+Shelter+Inventory

extra_image
-----------

.. rubric:: Cache time: 1 day

Returns an extra image (see :menuselection:`Settings --> Reports --> Extra
Images`).  Pass the name of the image in the title parameter::

    http://localhost:5000/service?method=extra_image&title=splash.jpg

html_adoptable_animals
----------------------

.. rubric:: Cache time: 10 minutes

Returns a complete HTML document containing an HTML page of adoptable animals.

You can pass an HTML template name in an optional "template" parameter (leaving
it off will cause animalview to be used). It is also possible extra parameters:

* speciesid=X - only output animals of that species. In the default dataset, 
  speciesid=1 is Dogs and speciesid=2 is cats.

* animaltypeid=X - only output animals of that type. Run this query at
  the SQL interface to find out the ID numbers: SELECT * FROM animaltype

* locationid=X - only output animals in this location. Run this query at
  the SQL interface to find out the ID numbers: SELECT * FROM internallocation

* underweeks=X - only output animals aged under X weeks.

* overweeks=X - only output animals aged over X weeks

The rules governing which animals are adoptable are those set under
:menuselection:`Publishing --> Set Publishing Options --> Animal Selection`.
You can view the set at :menuselection:`Publishing --> View Animals Matching
Publishing Options`::
 
    http://localhost:5000/service?method=html_adoptable_animals&template=littlebox&speciesid=1
    http://localhost:5000/service?method=html_adoptable_animals

html_adopted_animals
----------------------

.. rubric:: Cache time: 30 minutes

Returns a complete HTML document containing an HTML page of recently adopted
animals.

You can pass an HTML template name in an optional "template" parameter (leaving
it off will cause animalview to be used). It is also possible to pass
speciesid=X or animaltypeid=X parameters to only output animals of that species
and type. In the default dataset, speciesid=1 is Dogs and speciesid=2 is cats.

An "order" parameter can be passed to indicate what order you would like the 
results to be in. The default is adoption date descending. Options are:

* adopted_asc / adopted_desc - adoption date in ascending or descending order

* code_asc / code_desc - shelter code of the animals

* created_asc / created_desc - creation date of the animal records

* dateofbirth_asc / dateofbirth_desc - the date of birth of the animals

* deceased_asc / deceased_desc - the date the animals died

* entered_asc / entered_desc - the most recent date the animals entered care

* holduntil_asc / holduntil_desc - the date the animal holds end

* lastchanged_asc / lastchanged_desc - the last changed date of the animal records

* litterid_asc / litterid_desc - animal litter ID

* name_asc / name_desc - animal name

You can also pass a "days" parameter to indicate how far you would like to
go back. If you do not set it, the default is animals adopted in the last 30
days::
 
    http://localhost:5000/service?method=html_adopted_animals&template=littlebox&speciesid=1&days=60
    http://localhost:5000/service?method=html_adopted_animals&order=adopted_asc

html_deceased_animals
----------------------

.. rubric:: Cache time: 30 minutes

Returns a complete HTML document containing an HTML page of recently deceased 
animals.

You can pass an HTML template name in an optional "template" parameter (leaving
it off will cause animalview to be used). It is also possible to pass
speciesid=X or animaltypeid=X parameters to only output animals of that species
and type. In the default dataset, speciesid=1 is Dogs and speciesid=2 is cats.

An "order" parameter can be passed to indicate the sort order (see
html_adopted_animals). The default is deceased date descending.

You can also pass a "days" parameter to indicate how far you would like to
go back. If you do not set it, the default is animals deceased in the last 30
days::
 
    http://localhost:5000/service?method=html_deceased_animals&template=littlebox&speciesid=1&days=60
    http://localhost:5000/service?method=html_deceased_animals&order=deceased_desc

html_events
-----------

.. rubric:: Cache time: 1 hour

Returns a complete HTML document of shelter fundraising/adoption events
from :menuselection:`ASM --> Events --> Edit Events`

Looks for an HTML template called "events" to use. A basic template will be 
used if the template does not exist. The template can include the following tokens:

$$NAME$$ 
    The name of the event.
$$DESCRIPTION$$
    The event description. Note that this value is editable HTML from the screen.
$$STARTDATE$$
    The start date/time. 
$$ENDDATE$$
    The end date/time.
$$ADDRESS$$
    The event address.
$$CITY$$ / $$TOWN$$
    The event city (town for non-US).
$$STATE$$ / $$COUNTY$$
    The event state (county/region for non-US).
$$ZIPCODE$$ / $$POSTCODE$$
    The event zip/postal code.
$$COUNTRY
    The event country.

A "count" parameter can be passed to return the most recent X events (default 10)
and a "template" parameter can set the name of the template to use.

This is useful for including a page of events on your website::

    http://localhost:5000/service?method=html_events&template=events&count=20

html_flagged_animals
----------------------

.. rubric:: Cache time: 30 minutes

Returns a complete HTML document containing an HTML page of shelter animals
that have a particular flag.

You can pass an HTML template name in an optional "template" parameter (leaving
it off will cause animalview to be used). It is also possible to pass
speciesid=X or animaltypeid=X parameters to only output animals of that species
and type. In the default dataset, speciesid=1 is Dogs and speciesid=2 is cats.

An "order" parameter can be passed to indicate the sort order (see
html_adopted_animals). The default is entered date descending.

A "flag" parameter must be passed to specify the flag you want the returned
animals to have. If no flag is set, an error is returned. An "all=1"
parameter can optionally be passed if you'd like all animals to be included,
not just shelter animals::

    http://localhost:5000/service?method=html_flagged_animals&template=littlebox&speciesid=1&all=1&flag=Needs+Foster
    http://localhost:5000/service?method=html_flagged_animals&flag=At+Risk&order=entered_asc

html_held_animals
----------------------

.. rubric:: Cache time: 30 minutes

Returns a complete HTML document containing an HTML page of current held animals.

An "order" parameter can be passed to indicate the sort order (see
html_adopted_animals). The default is entered date descending.

You can pass an HTML template name in an optional "template" parameter (leaving
it off will cause animalview to be used). It is also possible to pass
speciesid=X or animaltypeid=X parameters to only output animals of that species
and type. In the default dataset, speciesid=1 is Dogs and speciesid=2 is cats::

    http://localhost:5000/service?method=html_held_animals&template=littlebox&speciesid=1&order=holduntildate_desc
    http://localhost:5000/service?method=html_held_animals

html_report
-----------

.. rubric:: Cache time: 10 minutes

Returns an HTML document containing a report. Pass the name of the report in
the title attribute. If the report requires any parameters, you can pass those
too. VAR parameters are just their name, ASK parameters are ASKn where n is the
order within the SQL. If you run the report within the ASM frontend you will
see the parameters it requires in the address bar::

    http://localhost:5000/service?method=html_report&username=user&password=letmein&title=Detailed+Shelter+Inventory
   
json_adoptable_animal and xml_adoptable_animal
----------------------------------------------

.. rubric:: Cache time: 1 hour

Returns a dataset containing a single animal record from the list of animals
available for adoption. The method determines whether the format returned is
JSON or XML::

    http://localhost:5000/service?method=xml_adoptable_animal&animalid=123&username=user&password=letmein

.. note:: If the animal with animalid is not adoptable, an empty result set will be returned.

json_adoptable_animals and xml_adoptable_animals
------------------------------------------------

.. rubric:: Cache time: 10 minutes 

Returns a dataset containing all animals available for adoption. The method
determines whether the format returned is JSON or XML::

    http://localhost:5000/service?method=xml_adoptable_animals&username=user&password=letmein

json_lost_animals, xml_lost_animals, json_found_animals, xml_found_animals
--------------------------------------------------------------------------

.. rubric:: Cache time: 1 hour 

Returns a dataset containing all lost or found animals reported in the last 90
days that are still active.  The method determines whether the format returned
is JSON or XML::

    http://localhost:5000/service?method=xml_found_animals&username=user&password=letmein

json_held_animals and xml_held_animals
--------------------------------------

.. rubric:: Cache time: 1 hour 

Returns a dataset containing all animals currently held. The method
determines whether the format returned is JSON or XML::

    http://localhost:5000/service?method=xml_adoptable_animals&username=user&password=letmein

json_recent_adoptions and xml_recent_adoptions
----------------------------------------------

.. rubric:: Cache time: 1 hour 

Returns a dataset containing all recently adopted animals with their new owner
information. The method name determines whether the format returned is JSON or
XML::
    
    http://localhost:5000/service?method=xml_recent_adoptions&username=user&password=letmein

json_recent_changes and xml_recent_changes
--------------------------------------------

.. rubric:: Cache time: 1 hour 

Returns a dataset containing all animals who have been modified in the last
month. The method determines whether the format returned is JSON or XML::

    http://localhost:5000/service?method=xml_recent_changes&username=user&password=letmein


json_shelter_animals and xml_shelter_animals
--------------------------------------------

.. rubric:: Cache time: 1 hour 

Returns a dataset containing all animals currently in the care of the shelter.
The method determines whether the format returned is JSON or XML::

    http://localhost:5000/service?method=xml_shelter_animals&username=user&password=letmein

By default, any personal or sensitive data (such as names and contact
information of fosterers and surrenders) will be stripped from the results. If
you wish them to be included, pass an extra sensitive=1 parameter::

    http://localhost:5000/service?method=xml_shelter_animals&username=user&password=letmein&sensitive=1

media_file
----------

.. rubric:: Cache time: 1 day

Responds with media file data for the mediaid given. The content type is set to
the correct MIME type for the data::
    
    http://localhost:5000/service?method=media_file&username=user&password=letmein&mediaid=52

online_form_html and online_form_json
-------------------------------------

.. rubric:: Cache time: 30 minutes

Responds with the online form HTML or JSON for the id given.

    http://localhost:5000/service?method=online_form_html&id=1

rss_timeline
------------

.. rubric:: Cache time: 1 hour 

Returns an RSS feed of the timeline for use with feed aggregators::
    
    http://localhost:5000/service?method=rss_timeline&username=user&password=letmein


