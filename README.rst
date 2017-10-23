Resize Photos Challenge Solution
================================

The Problem
-----------

The challenge proposed to consume a given online webservice that servers JPG images, resize them as 320x240, 384x288,
and 640x480 persist them as MongoDB documents and then build a webserver that servers these resized images using a JSON
response as the pointer list for all these images, with their respective available sizes.


Proposed Solution
-----------------

The proposed solution was to build a webserver using Python Flask, for its simplicity, and then use scipy, PIL to resize
the images and a MongoDB adapter in order to persist the new files.

WIP: It has been develop a module in which we do all this logic.
