# Garage_Controller
Github link: https://github.com/dbcookcan/Garage_Controller.git

This python3/Raspberry Pi program provides an inteligent garage door controller and environmental monitor.
REQUIRES: RaspberryPi + Pimironi AutomationHat
Autostart with "python3 /mypath/garage_main.py &" in /etc/rc.local

garage_main.py
Main application file which should be run from /etc/rc.local.
 - Logs to /var/log/garage.log
 - Checks status of two (2) garage doors via door contacts on AutomationHat automationhat.input.one and automationhat.input.two
 - Provides garage door status lights via AutomationHat automationhat.output.one and automationhat.output.two
 - Checks status of security PIR sensor via AutomationHat automationhat.input.three
 - Triggers external security panel on PIR activation vi AutomationHat automationhat.output.three

garage_api.py
Flask framework API for controller
- Allows remote polling of garage door and PIR status
- Default operation on port 5000

