#!/bin/bash
PROJECTID=$(awk -F "=" '/PROJECTID/ {print $2}' config.ini)

