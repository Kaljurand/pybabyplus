#!/usr/bin/env python3

"""
Converts a Baby+ app's data export (babyplus_data_export.json) into a multi-sheet
Excel feile with various pivot tables and visualizations.

Work in progress: only does baby_bottlefeed and baby_nappy for the time being.

TODO:

- refactor date parsing
- support tracker_detail
- plot feed and nappy on the same figure as a sequence of events
"""

import json
import sys
import pandas as pd
import numpy as np

FILE_JSON = "babyplus_data_export.json"
FILE_XLSX = "babyplus_data_export.xlsx"

COL_DATE = "Date"
COL_TIME = "Time"
COL_TIMEZONE = "Timezone"
COL_DATETIME = "DateTime"
COL_AMOUNT = "Amount"
COL_CONSISTENCY = "Consistency"
COL_NOTES = "Notes"


def gen_feed(data, notes={}):
    """Yields feed amounts with timestamps.
    """
    for dct in data:
        date = dct.get("date")
        # Delete timezone info
        # TODO: keep it in a separate column
        # TODO: use proper date parser
        datetime, timezone = date.split("+")
        date, time = datetime.split("T")
        yield date, time, timezone, dct.get("amountML"), notes.get(dct.get("pk"))


def gen_nappy(data, notes={}):
    """Yields nappy details with timestamps.
    """
    for dct in data:
        date = dct.get("date")
        # Delete timezone info
        # TODO: keep it in a separate column
        # TODO: use proper date parser
        datetime, timezone = date.split("+")
        date, time = datetime.split("T")
        yield date, time, timezone, dct.get("details"), notes.get(dct.get("pk"))


def main() -> int:
    """Main"""
    with open(FILE_JSON) as stream:
        data = json.load(stream)

        notes = {}
        for dct in data["tracker_detail"]:
            key = dct.get("a")
            val = dct.get("b")
            notes[key] = val

        df_feed = pd.DataFrame(
            gen_feed(data["baby_bottlefeed"], notes),
            columns=[COL_DATE, COL_TIME, COL_TIMEZONE, COL_AMOUNT, COL_NOTES],
        )
        df_nappy = pd.DataFrame(
            gen_nappy(data["baby_nappy"], notes),
            columns=[COL_DATE, COL_TIME, COL_TIMEZONE, COL_CONSISTENCY, COL_NOTES],
        )
        df_pivot_amount = pd.pivot_table(
            df_feed, values=COL_AMOUNT, index=[COL_DATE], aggfunc=np.sum
        )
        df_pivot_amount_notes = pd.pivot_table(
            df_feed,
            values=COL_AMOUNT,
            index=[COL_DATE],
            columns=[COL_NOTES],
            aggfunc=np.sum,
        )
        df_pivot_consistency = pd.pivot_table(
            df_nappy, values=COL_CONSISTENCY, index=[COL_DATE], aggfunc=np.count_nonzero
        )

        # df[COL_DATE] = pd.to_datetime(df[COL_DATE])
        with pd.ExcelWriter(FILE_XLSX) as writer:
            df_feed.to_excel(writer, sheet_name="Bottlefeed")
            df_nappy.to_excel(writer, sheet_name="Nappy")
            df_pivot_amount.to_excel(writer, sheet_name="Pivot Amount")
            df_pivot_amount_notes.to_excel(writer, sheet_name="Pivot Amount Notes")
            df_pivot_consistency.to_excel(writer, sheet_name="Pivot Consistency")

        print(df_pivot_amount)
        print(df_pivot_amount_notes)
        print(df_pivot_consistency)
    return 0


if __name__ == "__main__":
    sys.exit(main())
