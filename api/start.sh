#!/bin/sh
start-stop-daemon --start --background --exec skill_tester.sh --chdir $(pwd) --chuid www-data:www-data
