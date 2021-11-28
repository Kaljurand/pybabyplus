#!/usr/bin/env python3

"""
Converts a Baby+ app's data export (babyplus_data_export.json) into a multi-sheet
Excel feile with various pivot tables and visualizations.

Work in progress: only does baby_bottlefeed and baby_nappy for the time being.

TODO:

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
COL_WEEKDAY = "Weekday"
COL_DATETIME = "DateTime"
COL_AMOUNT = "Amount"
COL_CONSISTENCY = "Consistency"
COL_BOTTLE = "Bottle"
COL_FOOD = "Food"
COL_SHIT = "Shit"

is_excel = True
is_plain = True
is_plots = True


class Table:
    """Table"""

    def __init__(self, id: str, df: pd.DataFrame):
        self.id = id
        self.df = df

    def __str__(self):
        return self.id

    def as_df(self):
        return self.df

    def show(self):
        print(self.df.dtypes)
        print(self.df.head())
        print(self.df.tail())

    def plot(self):
        fig = self.df.plot().get_figure()
        fig.savefig(f"{self.id}.png")

    def to_excel(self, writer):
        self.df.to_excel(writer, sheet_name=self.id)


def gen_feed(data, notes={}):
    """Yields feed amounts with timestamps.
    """
    for dct in data:
        timestamp = pd.to_datetime(dct.get("date"))
        timestamp = timestamp.replace(tzinfo=None)
        date = timestamp.date()
        time = timestamp.time()
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
        yield timestamp, date, time, timestamp.weekday(), dct.get(
            "amountML"
        ), bottle, food


def gen_nappy(data, notes={}):
    """Yields nappy details with timestamps.
    """
    for dct in data:
        timestamp = pd.to_datetime(dct.get("date"))
        timestamp = timestamp.replace(tzinfo=None)
        date = timestamp.date()
        time = timestamp.time()
        weekday = timestamp.weekday()
        # TODO: clean up
        shit = None
        lst = notes.get(dct.get("pk"), set())
        for item in lst:
            if isinstance(item, ont.S):
                shit = item.__str__()
            else:
                print(f"ERROR: nappy: {item}")
        yield timestamp, date, time, weekday, dct.get("details"), shit


def main() -> int:
    """Main"""
    with open(FILE_JSON) as stream:
        data = json.load(stream)

        notes = {}
        for dct in data["tracker_detail"]:
            key = dct.get("a")
            val = dct.get("b")
            notes[key] = ont.gen_tag(val)

        feed = Table(
            "Bottlefeed",
            pd.DataFrame(
                gen_feed(data["baby_bottlefeed"], notes),
                columns=[
                    COL_TIMESTAMP,
                    COL_DATE,
                    COL_TIME,
                    COL_WEEKDAY,
                    COL_AMOUNT,
                    COL_BOTTLE,
                    COL_FOOD,
                ],
            ),
        )
        nappy = Table(
            "Nappy",
            pd.DataFrame(
                gen_nappy(data["baby_nappy"], notes),
                columns=[
                    COL_TIMESTAMP,
                    COL_DATE,
                    COL_TIME,
                    COL_WEEKDAY,
                    COL_CONSISTENCY,
                    COL_SHIT,
                ],
            ),
        )
        # nappy.style.set_properties(**{"background-color": "red"}, subset=[COL_SHIT])

        pivot_amount = Table(
            "pivot_amount",
            pd.pivot_table(
                feed.as_df(),
                values=COL_AMOUNT,
                index=[COL_DATE],
                aggfunc={COL_AMOUNT: [np.sum, np.count_nonzero]},
                # margins=True,
            ),
        )

        pivot_amount_by_time = Table(
            "pivot_amount_by_time",
            pd.pivot_table(
                feed.as_df(),
                values=COL_AMOUNT,
                index=[COL_TIME],
                aggfunc={COL_AMOUNT: [np.sum]},
                # margins=True,
            ),
        )

        pivot_amount_food = Table(
            "pivot_amount_food",
            pd.pivot_table(
                feed.as_df(),
                values=COL_AMOUNT,
                index=[COL_DATE],
                columns=[COL_FOOD],
                aggfunc=np.sum,
                margins=True,
            ),
        )
        pivot_amount_bottle = Table(
            "pivot_amount_bottle",
            pd.pivot_table(
                feed.as_df(),
                values=COL_AMOUNT,
                index=[COL_DATE],
                columns=[COL_BOTTLE],
                aggfunc=np.sum,
                margins=True,
            ),
        )
        pivot_amount_food_bottle = Table(
            "pivot_amount_food_bottle",
            pd.pivot_table(
                feed.as_df(),
                values=COL_AMOUNT,
                index=[COL_DATE],
                columns=[COL_FOOD, COL_BOTTLE],
                aggfunc=np.sum,
                margins=True,
            ),
        )
        pivot_consistency = Table(
            "pivot_consistency",
            pd.pivot_table(
                nappy.as_df(),
                values=COL_CONSISTENCY,
                index=[COL_DATE],
                aggfunc=np.count_nonzero,
                margins=True,
            ),
        )

        if is_excel:
            with pd.ExcelWriter(FILE_XLSX) as writer:
                feed.to_excel(writer)
                nappy.to_excel(writer)
                pivot_amount.to_excel(writer)
                pivot_amount_by_time.to_excel(writer)
                pivot_amount_food.to_excel(writer)
                pivot_amount_bottle.to_excel(writer)
                pivot_amount_food_bottle.to_excel(writer)
                pivot_consistency.to_excel(writer)

        if is_plain:
            feed.show()
            nappy.show()
            pivot_amount.show()
            pivot_amount_by_time.show()
            pivot_amount_food.show()
            pivot_amount_bottle.show()
            pivot_amount_food_bottle.show()
            pivot_consistency.show()

        if is_plots:
            feed.plot()
            # No numeric data to plot
            # nappy.plot()
            pivot_amount.plot()
            pivot_amount_by_time.plot()
            pivot_amount_food.plot()
            pivot_amount_bottle.plot()
            pivot_amount_food_bottle.plot()
            pivot_consistency.plot()

    return 0


if __name__ == "__main__":
    sys.exit(main())
