1. Developement
===============

.. |br| raw:: html

   <br />

This section will depict how *you* can develop for classroom-connect. |br|\
It will be using the `classroomconnect-devtools <https://github.com/sudo-nova/classroomconnect-devtools>`_ .

1.1 Installation
----------------

Running the following **bash** commands will setup the enviroment for you.|br|\
At the moment, there is no support for windows, and you must do everything manually.|br|\
Additionally, this setup proccess assumes you have all the correct `secret files <#secret-files>`_

1.1.1 Secret Files
~~~~~~~~~~~~~~~~~~

As this service uses many *other* services, it requires a couple tokens, ids and secret keys. We call these
secret files. The chosen format to store all of this sensitive information is `json <https://www.json.org>`_.

At the moment, there are 3 required secret files [``client_secret.json``, ``firebase_secret.json``, ``django_secret.json``], and we'll go over each one individually.

client_secret
+++++++++++++

This file contains the credentials for google apis. This shouldn't be an issue, since the google developer (api) console
will automatically generate this file for you. Remember to name it ``client_secret.json``! More information on the format of this file can be found in
`google's documentation <https://developers.google.com/api-client-library/python/guide/aaa_client_secrets>`_

**EXAMPLE ONLY**

.. code-block:: json

    {
      "web": {
        "client_id": "asdfjasdljfasdkjf",
        "client_secret": "1912308409123890",
        "redirect_uris": ["https://www.example.com/oauth2callback"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://accounts.google.com/o/oauth2/token"
      }
    }

firebase_secret
+++++++++++++++

This file is our own format, so pay attention! It consists of 2 properties. The first, ``config``, this object is actually formatted to the needs of
a python api wrapper called `pyrebase <https://github.com/thisbejim/Pyrebase>`_ and the "documentation" (readme) for config can be found `here <https://github.com/thisbejim/Pyrebase#add-pyrebase-to-your-application>`_
The other property, secret, is the secret key of the firebase project. Though its use is deprecated, the api still supports it, and we still use it.
Instructions on retriving it can be found `here <http://stackoverflow.com/questions/37418372/firebase-where-is-my-account-secret-in-the-new-console#answer-37418932>`_.

.. code-block:: json

    {
      "config" : {
        "apiKey": "<<YOUR KEY>>",
        "authDomain": "<<PROJECT ID>>.firebaseapp.com",
        "databaseURL": "https://<<PROJECT ID>>.firebaseio.com",
        "storageBucket": "<<PROJECT ID>>.appspot.com"
      },
      "secret" : "<<PROJECT SECRET>>"
    }

django_secret
+++++++++++++

Simply insert the django secret key into this json file under the property ``"secret"``.

.. code-block:: json
    
    {
        "secret" : "<<DJANGO SECRET KEY>>"
    }

1.1.2 Setup
~~~~~~~~~~~

.. raw:: html

    <strong><a href="#hereshow">TL;DR</a></strong>

For linux users, this will be a breeze! Our developer `Calder White <https://github.com/CalderWhite>`_ took the time to write an entire sdk-like shell script.
It can be used for installing, and pushing to heroku. The purpose of the following setup is so you may push to our heroku app with the required sensitive data,
but not push to the public Github repository with said sensitive data.

First, let's explain the filesystem. Here's the full diagram:
::

    ./
     |---classroom-connect
             |
             |---deployment
             |       |
             |       |--classroom-connect (master)
             |
             |---developement
                     |
                     |--classroom-connect (master)

When used correctly, you only have to work from the ``developement`` directory. |br|
The bash script can delete the deployment directory, re-clone it, remove the .gitignore, copy all the sensitive files over and finally, deploy to heroku. |br|
For you.

.. raw:: html

    <strong id="hereshow">Here's how!</strong>

In short, run this.

.. code-block:: bash

    wget https://raw.githubusercontent.com/sudo-nova/classroomconnect-devtools/master/cc-tools.sh
    # only rw, since we don't want any 3rd party sources changing this script.
    chmod ug=rx cc-tools.sh
    ./cc-tools.sh install
    cd classroom-connect/developement
    sudo pip3 install -r requirements.txt
    
1.2 Contributing
----------------

At the moment, we have no guidlines for contributing, just fork and open a pull request! However, we do ask that
you be mindful when commiting, since we use 3 different secret files. Also remember that github keeps your commit history, so deleting an
accidental file isn't enough. Github has a help section for `removing sensitive information <https://help.github.com/articles/removing-sensitive-data-from-a-repository/#using-filter-branch>`_.

1.3 Find Us
-----------

.. image:: https://brandfolder.com/slack/attachments/oaxty0-egsr8w-17ksp7?dl=true&resource_key=op6f9hfynpza&resource_type=Brandfolder
    :target: https://sudo-nova.slack.com
    :height: 100
    :width: 100
    
.. raw:: html
    
    <a href="https://github.com/sudo-nova">
    <svg style="margin-bottom:-32px;margin-left:3px;margin-right:3px;"aria-hidden="true"  viewBox="0 0 16 16" width="100" height="100"><path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path></svg>
    </a>
    