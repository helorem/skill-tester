#!/bin/sh

if[ "x${SKILL_TESTER_HOME}y" = "xy" ]
then
    SKILL_TESTER_HOME="/home/web/net.emaxilde.capfi/htdocs/skill-tester"
fi

if [ ! -d "${SKILL_TESTER_HOME}/api" ]
then
    echo "*** skill-tester/api directory was not found ***"
else
    cd "${SKILL_TESTER_HOME}/api" || exit 1
fi

exec python skill_tester.py > skill_tester.log 2>&1
