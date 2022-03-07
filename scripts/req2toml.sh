#!/bin/bash
# Loop over requirements.txt file and download with poetry
# IMPORTANT: it will download latest and not neccessary the
# implicite package specify under requirements.txt
# credit: https://github.com/danielmichaels/
# link: https://danielms.site/blog/requirements-txt-to-poetry-pyproject-toml/

cat requirements.txt | grep -E '^[^# ]' | cut -d= -f1 | xargs -n 1 poetry add
