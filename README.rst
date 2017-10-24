Resize Photos Challenge Solution
================================

.. image:: https://travis-ci.org/felipeanchieta/resize-photos.svg?branch=master
    :target: https://travis-ci.org/felipeanchieta/resize-photos

The Problem
-----------

The challenge proposed to consume a given online webservice that servers JPG images, resize them as 320x240, 384x288,
and 640x480 persist them as MongoDB documents and then build a webserver that servers these resized images using a JSON
response as the pointer list for all these images, with their respective available sizes.


Proposed Solution
-----------------

The proposed solution was to build a webserver using Python Flask, for its simplicity, and then use PIL to resize
the images and a MongoDB adapter in order to persist the new files.

It has been develop a module in which we do all this logic, so that we can only need to have a MongoDB running and run the Flask application by executing

>>> python resizephotos/core.py

It is assumed you have Python 3 available, since it is the requirement.

Automated Tests
-----------------

You can run the automated tests by executing:

>>> python -m unittest tests/test_automated_tests

It is going to check the state of B2W webservice and what we are doing here (downloading, resizing, saving, and so on).
