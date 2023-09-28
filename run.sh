#!/bin/bash

pip3.10 freeze;
python3.10 main.py;
sbt 'runMain org.clulab.reach.RunReachCLI';
python3.10 output.py;
