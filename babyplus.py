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
import ontology as ont

FILE_JSON = "babyplus_data_export.json"
FILE_XLSX = "babyplus_data_export.xlsx"

COL_TIMESTAMP = "Timestamp"
COL_DATE = "Date"
COL_TIME = "Time"
COL_TIMEZONE = "Timezone"
COL_DATETIME = "DateTime"
COL_AMOUNT = "Amount"
COL_CONSISTENCY = "Consistency"
COL_BOTTLE = "Bottle"
COL_FOOD = "Food"
COL_SHIT = "Shit"


def gen_feed(data, notes={}):
    """Yields feed amounts with timestamps.
    """
    for dct in data:
        timestamp = dct.get("date")
        # Delete timezone info
        # TODO: keep it in a separate column
        # TODO: use proper date parser
        datetime, timezone = timestamp.split("+")
        date, time = datetime.split("T")
        # TODO: cleanup
        bottle = None
        food = None
        lst = notes.get(dct.get("pk"), set())
        for item in lst:
            if isinstance(item, ont.F):
                food = item.__str__()
            elif isinstance(item, ont.B):
                bottle = item.__str__()
            else:
                print(f"ERROR: feed: {item}")
        yield timestamp, date, time, timezone, dct.get("amountML"), bottle, food


def gen_nappy(data, notes={}):
    """Yields nappy details with timestamps.
    """
    for dct in data:
        timestamp = dct.get("date")
        # Delete timezone info
        # TODO: keep it in a separate column
        # TODO: use proper date parser
        datetime, timezone = timestamp.split("+")
        date, time = datetime.split("T")
        # TODO: clean up
        shit = None
        lst = notes.get(dct.get("pk"), set())
        for item in lst:
            if isinstance(item, ont.S):
                shit = item.__str__()
            else:
                print(f"ERROR: nappy: {item}")
        yield timestamp, date, time, timezone, dct.get("details"), shit


def main() -> int:
    """Main"""
    with open(FILE_JSON) as stream:
        data = json.load(stream)

        notes = {}
        for dct in data["tracker_detail"]:
            key = dct.get("a")
            val = dct.get("b")
            notes[key] = ont.gen_tag(val)

        df_feed = pd.DataFrame(
            gen_feed(data["baby_bottlefeed"], notes),
            columns=[
                COL_TIMESTAMP,
                COL_DATE,
                COL_TIME,
                COL_TIMEZONE,
                COL_AMOUNT,
                COL_BOTTLE,
                COL_FOOD,
            ],
        )
        df_nappy = pd.DataFrame(
            gen_nappy(data["baby_nappy"], notes),
            columns=[
                COL_TIMESTAMP,
                COL_DATE,
                COL_TIME,
                COL_TIMEZONE,
                COL_CONSISTENCY,
                COL_SHIT,
            ],
        )
        df_nappy.style.set_properties(**{'background-color': 'red'}, subset=[COL_SHIT])

        df_pivot_amount = pd.pivot_table(
            df_feed,
            values=COL_AMOUNT,
            index=[COL_DATE],
            aggfunc={COL_AMOUNT: [np.sum, np.count_nonzero]},
            #margins=True,
        )
        df_pivot_amount_notes = pd.pivot_table(
            df_feed,
            values=COL_AMOUNT,
            index=[COL_DATE],
            columns=[COL_FOOD, COL_BOTTLE],
            aggfunc=np.sum,
            margins=True,
        )
        df_pivot_consistency = pd.pivot_table(
            df_nappy, values=COL_CONSISTENCY, index=[COL_DATE], aggfunc=np.count_nonzero,
            margins=True,
        )

        if True:
            # df[COL_DATE] = pd.to_datetime(df[COL_DATE])
            with pd.ExcelWriter(FILE_XLSX) as writer:
                df_feed.to_excel(writer, sheet_name="Bottlefeed")
                df_nappy.to_excel(writer, sheet_name="Nappy")
                df_pivot_amount.to_excel(writer, sheet_name="Pivot Amount")
                df_pivot_amount_notes.to_excel(writer, sheet_name="Pivot Amount Notes")
                df_pivot_consistency.to_excel(writer, sheet_name="Pivot Consistency")

        if True:
            print(df_nappy)
            print(df_pivot_amount)
            print(df_pivot_amount_notes)
            print(df_pivot_consistency)
    return 0


if __name__ == "__main__":
    sys.exit(main())
