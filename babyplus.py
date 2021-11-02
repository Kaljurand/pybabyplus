#!/usr/bin/env python3

"""
Converts a Baby+ app's data export (babyplus_data_export.json) into a multi-sheet
Excel feile with various pivot tables and visualizations.

Work in progress: only does baby_bottlefeed for the time being.
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


def gen_feed(fname):
    """Yields feed amounts with timestamps.
    """
    with open(fname) as stream:
        data = json.load(stream)
        for dct in data.get("baby_bottlefeed", []):
            date = dct.get("date")
            # Delete timezone info
            # TODO: keep it in a separate column
            # TODO: use proper date parser
            datetime, timezone = date.split("+")
            date, time = datetime.split("T")
            yield date, time, timezone, dct.get("amountML")


def main() -> int:
    """Main"""
    df_feed = pd.DataFrame(
        gen_feed(FILE_JSON), columns=[COL_DATE, COL_TIME, COL_TIMEZONE, COL_AMOUNT]
    )
    # table = pd.pivot_table(df, values=COL_AMOUNT, index=[COL_DATE], columns=[COL_TIMEZONE], aggfunc=np.sum)
    df_pivot_amount = pd.pivot_table(
        df_feed, values=COL_AMOUNT, index=[COL_DATE], aggfunc=np.sum
    )
    # df[COL_DATE] = pd.to_datetime(df[COL_DATE])
    with pd.ExcelWriter(FILE_XLSX) as writer:
        df_feed.to_excel(writer, sheet_name="Data")
        df_pivot_amount.to_excel(writer, sheet_name="Pivot Amount")
    print(df_pivot_amount)
    return 0


if __name__ == "__main__":
    sys.exit(main())
