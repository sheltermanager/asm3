Online Forms
============

ASM allows you to setup online forms that you can use to take information from
members of the public through your website (if your ASM is publically
accessible, or you are using sheltermanager.com). 

This is very useful for handling adoption and waiting list application forms,
questionnaires, taking lost or found animal information from people,
complaints, behavioural assessments, etc. They can be used for any situation
where you'd like to take information from web site visitors.

Forms need a name and a description. The description will be shown to the user
while they are filling out the form. You can also specify a page you'd like to
redirect the user to after they've completed the form.

If you use certain key fields (which the system will autocomplete for you), the
system can create person, lost animal, found animal, animal control incident,
transport or waiting list records directly from the submitted form data. You
can also choose to attach form submissions to animal and people records.

If you set some person flags on your form, any person record created from the
form data will automatically have those flags. In addition to that, the
"checkbox" field type allows you to enter some additional person flags to set
if that checkbox is checked during submission.

If you set the "Send confirmation email to form submitter" checkbox for an
online form, the system will look for a field called "emailaddress" during
submission. If that field exists and is populated with an email address, a
confirmation email will be sent to that address. If the confirmation message
field is set, that will form the body of the email. HTML can be used, but
it must be a complete HTML document that contains an <html> tag. If the
confirmation message field is left blank, a copy of the form submission 
itself will be sent.

.. image:: images/onlineform_edit.png

As you can see in the screenshot, each form has a “Form URL”. This is the web
link you can use on your website to link people to the form. You can also click
it directly there in the UI to test your form. 

You may add extra parameters to the URL if you'd like to set default values
for some of your form fields, by using the format fieldname=value.

.. warning:: sheltermanager.com uses a short term 2 minute cache on forms, so if you make changes to a form you've recently viewed, you may have to wait 2 minutes for any changes you make to appear.

Clicking on the form's name will allow you to edit the individual fields of
information the report will take.

.. image:: images/onlineform_fields.png

The dialog will autocomplete the known fields that ASM can look for when
creating records from form submissions. For details, see :ref:`onlineformfields`

To create any record, you will need at least a lastname or surname field. Lost
animal records need an arealost and description, found animal records need an
areafound and description, waiting list records need a description.

The "lookup", "radio" or "multi-lookup" field types require a list of
values. You should separate these with the pipe character. Eg:
Option 1|Option 2|Option 3

The "signature" field type allows the person completing the form to sign
electronically with a touchscreen.

A "raw markup" field type allows you to insert your own HTML sections within
the form. This is useful for adding contract clauses, headings, or any sort
of extra formatting. 

The "GDPR contact" field type allows for a multiple lookup of GDPR
communication choices to be made for resulting person records.

When forms are submitted through the website they come through to the “View
Incoming Forms” screen, where the values can be inspected by clicking the name
of the form submission. The screen shows a preview of the incoming data and the
IP address that submitted it.

If a field called "emailaddress" is supplied as part of the form submission,
the complete submission will be emailed automatically to the person who
completed it for their records. 

Similarly, if a field called "emailsubmissionto" is supplied, containing one or
more comma separated email addresses, the submission will also be emailed to
these extra addresses. This can be useful to have form values trigger hidden
values to send submissions to other addresses.

.. image:: images/onlineform_incoming.png

Selecting a form allows you to intelligently create or attach records from the
data, or explicitly attach the form to existing records. 

* Attach Person: Prompts for a single person record and attaches a copy of the
  form to them as media.

* Attach Animal: Prompts for a single animal record and attaches a copy of the
  form to them as media.

* Attach Animal (via animalname): Attaches the form to a single animal
  record based on the animalname field in the form itself.

* Create Person: Searches for a person record matching either the email address
  if present, or the firstname, lastname and address fields on the form. If a
  match is found, the form is attached to that person. If no match is found, a
  new person record is created. If a “reserveanimalname” field was found on the
  form as well, a reservation to the matching animal is created to the person
  (these can be all viewed under :menuselection:`Move --> Reservation Book`).

* Create Lost Animal: Runs through the same steps as Person so needs enough
  information to create/find a person as well. “description” and “arealost”
  fields are the minimum required to create the lost animal record.

* Create Found Animal: Runs through the same steps as Person so needs enough
  information to create/find a person as well. “description” and “areafound”
  fields are the minimum required to create the found animal record.

* Create Incident: Runs through the same steps as Person so needs enough
  information to create/find a person as well. That person becomes the
  “caller”.  “callnotes” and “dispatchaddress” fields are the minimum required
  to create the incident record.

* Create Transport: Runs through the same steps as Animal, so needs
  an "animalname" field to figure out who to attach the transport to.

* Create Waiting List: Runs through the same steps as Person so needs enough
  information to create/find a person as well. A “description” field is the
  minimum required to create the waiting list record.

When you create a new record or attach the form, the whole form will be
included in the media tab of any created records (animal, incident, person AND
lost/found animal or waiting list). The screen will put a link in the Link
column to give you a clickable link to the newly created record as well so you
can view it. 

You can safely delete incoming forms once they have been attached to a record.
The system will also remove incoming forms older than 2 weeks by default.

Importing
---------

ASM also allows importing of online forms from files. 

Form files can be in a structured JSON format that ASM recognises, eg::

    {
        "name": "Adoption Application",
        "description": "",
        "header": "",
        "footer": ""
        "fields": [
            { "index": 1, "lookups": "", "mandatory": "true", "name": "reserveanimalname",
              "tooltip": "", "label": "Animal you are interested in", "type": "ADOPTABLEANIMAL" },
            { "index": 2, "lookups": "", "mandatory": true, "name": "firstname",
              "tooltip": "", "label": "Applicant's First Name", "type": "TEXT" },
            { "index": 3, "lookups": "", "mandatory": true, "name": "lastname",
              "tooltip": "", "label": "Applicant's Last Name", "type": "TEXT" }
        ]
    }

Files can also be HTML, where the import mechanism will extract all of the
input, select and textarea elements. It will use the name attribute to set the
field name and label. The HTML page title will be used as the form title.

HTML import is only basic, but can be used to grab the existing fields of a
form you already have ready for editing, eg::

    <!DOCTYPE html>
    <html>
    <head>
    <title>My Adoption Form</title>
    </head>
    <body>
    <form action="handler" method="post">
        <p><input type="text" name="firstname"> First Name</p>
        <p><input type="text" name="lastname"> Last Name</p>
    </form>
    </body>
    </html>


