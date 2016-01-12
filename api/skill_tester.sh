#!/bin/sh
SKILL_TESTER_HOME="/home/web/net.emaxilde.capfi/htdocs/skill-tester"

if [ ! -d "${SKILL_TESTER_HOME}/api" ]
then
    echo "*** skill-tester/api directory was not found ***"
else
    cd "${SKILL_TESTER_HOME}/api" || exit 1
fi
exec python skill_tester.py 2>&1 > skill_tester.log
