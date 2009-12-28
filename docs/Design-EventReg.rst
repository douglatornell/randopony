===============================================
 RandoPony Event Registration App Design Notes
===============================================

:Author: Doug Latornell
:Created: 2009-12-05


These are design notes for a Django app to provide something like an
Oregon Randonneurs style registration site for BC Randonneurs
brevets. The conceptual design is Susan's.

For now, the scope of the app is limited to non-secure registration
for brevets. Implications:

* Collect a minimum of personal information from entrants
* Communication with entrants and brevet organizers via automated
  email
* Publication of entrant lists on non-secure pages
* No need for anyone other than app admin(s) to log in, and they will
  use the Django auto-generated admin pages, access to which can be
  secured using HTTPS via a self-signed or shared certificate
* Obviously, no payment transactions
* Fleche events are excluded because the information required from
  entrants is different to brevets, and more complicated in some ways
* Populaires are excluded because we generally want more info from
  entrants than we should collect without HTTPS and encrypted storage

User Stories
============

Brevet Entrant
--------------

The brevet entrant follows a link from the http://randonneurs.bc.ca/ schedule
page, or an email message to a brevet registration page such as
http://randopony.sadahome.ca/register/LM400/22May2010/. That
page presents information about the brevet:

* region
* distance
* date
* start location
* start time
* route name
* email address of organizer (plain, obfuscated, or
  captcha-protected?)
* link to privacy policy?

and an entry form to collect:

* entrant name
* entrant email address
* checkbox to declare whether or not they are a club member
* text box for them to describe their qualification for the brevet;
  e.g. date and location of their last 300; This box is included at
  the request of the brevet organizer
* a captcha to prevent form abuse by bots

Submission of the form triggers validation of the form data:

* entrant name is not empty
* email address has valid structure
* qualification info is not empty
* captcha answer is correct

If validation fails the form is re-presented with error message(s). If
the validation succeeds the entrant is redirected to a brevet
registration confirmation page such as
http://randopony.sadahome.ca/register/confirmation/. That page:

* Informs the entrant that a confirmation email has been sent to
  the address they provided.

* Provides a link to the event entry form on the club site
  with instructions that they can speed up their sign-on at the start
  by printing it, filling it in, and bringing it with them.

* If they have not declared that they are a club member, the page
  reiterates that they must be a member to ride the brevet, and
  provids a link to the membership form on the club site with similar
  instructions.

* Provides a link to a brevet rider list page such as
  http://randopony.sadahome.ca/register/LM400/22May2010/riderlist/.

The brevet rider list page provides a list of the people who have
pre-registered for the brevet, and a link to the register page for
those who may want to. This page can be linked to from the schedule
page, or elsewhere on the club site if Eric wishes to.

The root page at http://randopony.sadahome.ca/register/ provides links
to the registration pages for brevets in the future, and to the rider
list pages for brevets less than 8 days in the past. The latter is to
provide a small amount of information about some of the people who
rode the brevet in the interval between the end of the brevet and the
posting of the results on the club site.


Brevet Organizer
----------------

When a rider registers for a brevet the organizer is sent and email
message containing:

* entrant's name
* entrant's email address
* entrant's declaration of club membership
* entrant's brevet qualification info, if the organizer has chosen
  that field to be included in the entry form

The email reminds the organizer that none of the information has been
verified and that, in particular, they need to confirm the entrants
club membership status against a current membership list.

The message also contains a link to the brevet rider list page.


App Administrator
-----------------

A brevets registration administrator logs into the Django admin for
the app at http://randopony.sadahome.ca/admin/register/. On the admin
site they can:

* add, delete, or change brevet instances
* add, delete, or change entrant instances (though there should be no
  reason to, other than spam)
* trigger a re-send to the brevet organizer or the notification email
  generated for a particular entrant


URL Map
=======
::

   /admin/brevets/
   /register/
                  [rrkkk]/[ddmmmyyyy]/
                  [rrkkk]/[ddmmmyyyy]/riderlist/
                  confirmation/

Model Design
============

2 model classes:

* brevet
* entrant

There is a one to many relationship between brevets and entrants.

Brevet instances have the following attributes:

* region
* distance
* date
* start location
* start time
* route name
* email address of organizer
* boolean to enable collection of qualification info from entrants
* text of request for qualification info; may be empty

Entrant instances have the following attributes:

* name
* email address
* boolean for declaration of club membership
* brevet qualification info text; may be empty
* foreign key link to a brevet instance


Implementation Details
======================

After deciding to use the foxy_ page template by `spyka webmaster`_,
the URL map and flow of pages became clearer.

The http://randopony.sadahome.ca/register/ page will intially present
a welcome to the site and the sidebar links will be:

* Home - link to http://randopony.sadahome.ca/register/
* 1 link (tab) per brevet that is available for pre-registration, or
  completed less then 8 days previously - link to brevet page, for
  example, http://randopony.sadahome.ca/register/LM400/22May2010/
* randonneurs.bc.ca - link to the club site

If there is serious uptake of the system the
http://randopony.sadahome.ca/register/ sidebar will be replaced with
one that links to each of the regions brevet lists at, for example
http://randopony.sadahome.ca/register/LM/. The region page sidebars
will be as described above, limited to only the events in the
particular region.

The brevet pages will show the brevet information, and the list of
pre-registered riders. The sidebar links will be:

* Home - link to http://randopony.sadahome.ca/register/
* Pre-register - link to pre-registration form, either on a separate
  page, or as a JQuery-driven modal form
* Event Waiver - link to event waiver PDF on club site
* Club Membership - link to club membership form PDF on club site 
* randonneurs.bc.ca - link to the club site

When the pre-registration form is successfully submitted the brevet
page will be displayed again with the rider's name added to the list,
and a flash message that:

* confirms the pre-registration
* draws attention to the pre-registration confirmation emails sent to
  the rider and the event organizer
* draws attention to the event waiver form that can be printed, filled
  out, and brought to the start
* for non-members, draws attention to the club membership form that
  can be printed, filled out, and brought to the start
* directs any further enquiries to the event organizer


.. _foxy: http://justfreetemplates.com/preview/web-templates/206.html
.. _spyka webmaster: http://www.spyka.net/


.. 
   Local Variables:
   mode: rst
   mode: auto-fill
   End:
