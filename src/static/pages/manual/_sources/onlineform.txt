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
system can create person, lost animal, found animal, animal control incident or
waiting list records directly from submitted form data. You can also attach
form submissions to animal records.

If you set some person flags on your form, any person record created from the
form data will automatically have those flags. In addition to that, the
"checkbox" field type allows you to enter some additional person flags to set
if that checkbox is checked during submission.

If you set the "Send confirmation email to form submitter" checkbox for an
online form, the system will look for a field called "emailaddress" during
submission. If that field exists and is populated with an email address, a copy
of the form submission will be sent to that address.

.. image:: images/onlineform_edit.png

As you can see in the screenshot, each form has a “Form URL”. This is the web
link you can use on your website to link people to the form. You can also click
it directly there in the UI to test your form. 

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

When forms are submitted through the website they come through to the “View
Incoming Forms” screen, where the values can be inspected by clicking the name
of the form submission. The screen shows a preview of the incoming data and the
IP address that submitted it.

If a field called "emailaddress" is supplied as part of the form submission,
the complete submission will be emailed automatically to the person who
completed it for their records.

.. image:: images/onlineform_incoming.png

Selecting a form allows you to create records from the data, or attach the
form to existing records. 

* Attach Person: Prompts for a single person record and attaches a copy of the
  form to them.

* Attach Animal: Prompts for a single animal record and attaches a copy of the
  form to them.

* Animal: Requires an “animalname” field in the form. Attaches selected forms
  to their matching shelter animal.

* Person: Searches for a person record matching the firstname, lastname and
  address fields on the form. If a match is found, the form is attached to that
  person. If not match is found, a new person record is created. If a
  “reserveanimalname” field was found on the form as well, a reservation to the
  matching animal is created to the person (these can be all viewed under
  :menuselection:`Move --> Reservation Book`).

* Lost Animal: Runs through the same steps as Person so needs enough
  information to create/find a person as well. “description” and “arealost”
  fields are the minimum required to create the lost animal record.

* Found Animal: Runs through the same steps as Person so needs enough
  information to create/find a person as well. “description” and “areafound”
  fields are the minimum required to create the found animal record.

* Incident: Runs through the same steps as Person so needs enough information
  to create/find a person as well. That person becomes the “caller”.
  “callnotes” and “dispatchaddress” fields are the minimum required to create
  the incident record.

* Waiting List: Runs through the same steps as Person so needs enough
  information to create/find a person as well. A “description” field is the
  minimum required to create the waiting list record.

When you create a new record or attach the form, the whole form will be
included in the media tab of any created records (animal, incident, person AND
lost/found animal or waiting list). The screen will put a link in the Link
column to give you a clickable link to the newly created record as well so you
can view it. 

You can safely delete incoming forms once they have been attached to a record.
The system will also remove incoming forms older than 2 weeks by default.


