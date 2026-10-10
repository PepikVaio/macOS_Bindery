#!/bin/bash

rm -rf App
rm -f Bindery

mkdir -p App

pyinstaller \
    --windowed \
    --name Bindery \
    --icon=../Bindery.icns \
    --workpath App/build \
    --distpath App \
    --specpath App \
    --add-data "../Book:Book" \
    --add-data "../Bindery.icns:." \
    bindery.py