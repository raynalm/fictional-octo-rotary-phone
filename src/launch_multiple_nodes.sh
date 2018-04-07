#!/bin/bash
for i in {1..$1} do
    gnome-terminal -e ./main.py
done
