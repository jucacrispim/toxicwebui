#!/bin/bash

pylint toxicwebui/
if [ $? != "0" ]
then
    exit 1;
fi

flake8 toxicwebui/

if [ $? != "0" ]
then
    exit 1;
fi

flake8 tests
exit $?;
