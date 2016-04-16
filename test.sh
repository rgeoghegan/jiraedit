#!/usr/bin/env bash
set -e
set -x

pyflakes jiraedit/issue.py tests/test_jiraedit.py jiraedit/cmd.py
python setup.py test

