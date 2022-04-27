#!/bin/sh

flake8 . && pylint src
black .