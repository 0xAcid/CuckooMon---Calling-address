monitor
=======

The new Cuckoo Monitor. [Click here for documentation][docs].
If at first it doesn't compile, just try a second time!

[docs]: http://cuckoo-monitor.readthedocs.org/en/latest/


# Cuckoo Monitor - Address Caller Identification
This repository is a clone of the new [Cuckoo Sandbox Monitor DLL](https://github.com/cuckoosandbox/monitor)
It is based on [Mr Polino version from the first Monitoring DLL](https://github.com/JinBlack/cuckoomon/commits/mem_pointer)
## How it works

Basically by editing Jinja2 files (files that generate automatically code for API hooking) we add functions that helps us determining the calling address.
Using the python script provided by Cuckoo Monitor, we add a new parameter for all logged API that is used to store the calling address.
