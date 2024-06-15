#!/bin/sh

export DISPLAY=:99
 Xvfb :99  -ac -screen 0, 1368x768x24 &
toxicjasmine ci tests/js-unit/SpecRunner.html --browser chrome --options=no-sandbox,disable-dev-shm-usage,headless,remote-debugging-port=9222,disable-gpu
status=$?
 killall Xvfb
 rm -f /tmp/.X99-lock
exit $status
