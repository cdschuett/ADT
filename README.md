# ADT
ADT code

Operating the script
The directory in use is:
~/Documents/py_test/ADT
The application that starts the script and menu is:
/home/pi/Documents/py_test/ADT/mission_comp

This is started anytime the pi profile is loaded from .bashrc
because the .bashrc profile script executes mission_comp when it runs
It does this by executing mission_comp as the last line of the profile


Github Notes
To update the repo from this device, use the following commands:
cd ~/Documents/py_test/ADT
git add
git commit -a -m "some description of the commit"
git push

structure:
mission_comp drives execution
start.sh starts the EICAS execution
test.sh starts a test pattern execution
You shouldn't run both simultaneously

/home/pi/processes stores an eicas.pid file so it knows what process to stop if you need to terminate the EICAS


stop_eicas.sh stops EICAS execution. It needs that PID file described above to do so
stop_test.sh kills the test pattern program

eicas.py is the core of the EICAS program
constants.py provides needed constant values
Graphics.py provides all the gfxdraw sections for updating the display
ARINC_Engine.ino is the arduino sketch file for the transmitter. This is probably out of date

test_pattern.py is a simple test pattern script.

Everything is built around pygame