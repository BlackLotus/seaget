seaget
======

Wget like tool to dump seagate memory and buffer
This are all the scripts I hacked together.This is neither refined nor cleaned.

Usage is simple:
python2 see.py device dumpfile baud

Default baud should be 38400 maximum is 115200

If you have problems dumping anything you can set the timeout in see.py to something higher.
timeout=1 should work with every hardware.
