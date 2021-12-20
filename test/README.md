# Regression test


Usage:

    unzip -p babyplus_data_export.zip babyplus_data_export.json | jq | ../babyplus.py - | tee out.txt

TODO: We use ``jq`` to convert (some) floats to ints?
