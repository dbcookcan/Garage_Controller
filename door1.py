#!/usr/bin/env python3

import time

import automationhat


if automationhat.is_automation_hat():
    automationhat.light.power.write(1)

automationhat.relay.one.on()
time.sleep(0.5)
automationhat.relay.one.off()

#
# EOF
#

