#!/bin/bash

rm -rf App
rm -f Bindery.exe

mkdir -p App

pyinstaller \
    --windowed \
    --name Bindery \
    --icon=../Bindery.ico \
    --workpath App/build \
    --distpath App \
    --specpath App \
    --add-data "../Book;Book" \
    --add-data "../Bindery.ico;." \
    bindery.py