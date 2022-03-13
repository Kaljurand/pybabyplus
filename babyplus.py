#!/usr/bin/env python3

"""
Converts a Baby+ app's data export (babyplus_data_export.json) into a multi-sheet
Excel file with various pivot tables and visualizations.

Work in progress: only does baby_bottlefeed and baby_nappy for the time being.
"""

import json
import sys

import click
import numpy as np
import pandas as pd

import ontology as ont

FILE_XLSX = "babyplus_data_export.xlsx"

COL_TIMESTAMP = "Timestamp"
COL_SKIP_MIN = "SkipMin"
COL_ML_PER_SKIP_MIN = "MlPerSkipMin"
COL_DATE = "Date"
COL_TIME = "Time"
COL_YEAR = "Year"
COL_WEEK = "Week"
COL_WEEKDAY = "Weekday"
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
        print(f"NAME: {self.id}")
        print(self.df.dtypes)
        print(self.df.head())
        print(self.df.tail())

    def plot(self):
        try:
            df_without_margins = self.df.drop(
                index="All", columns="All", errors="ignore"
            )
            fig = df_without_margins.plot(
                subplots=True, grid=True, sharex=True, kind="line"
            )
            fig[0].get_figure().savefig(f"{self.id}.png")
        except OverflowError as err:
            print(f"ERROR: {self.id}: {err}")

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
        yield timestamp, date, time, timestamp.year, timestamp.week, timestamp.weekday(), dct.get(
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
        yield timestamp, date, time, timestamp.year, timestamp.week, weekday, dct.get("details"), shit


@click.command()
@click.argument("stream", type=click.File("r"))
def main(stream) -> int:
    """Main"""
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
            COL_YEAR,
            COL_WEEK,
            COL_WEEKDAY,
            COL_AMOUNT,
            COL_BOTTLE,
            COL_FOOD,
        ],
    )

    # Minutes since the previous feeding
    df_feed[COL_SKIP_MIN] = (
        df_feed[COL_TIMESTAMP].shift() - df_feed[COL_TIMESTAMP]
    ).dt.seconds / 60.0
    # Amount consumed per minute
    df_feed[COL_ML_PER_SKIP_MIN] = df_feed[COL_AMOUNT].shift() / df_feed[COL_SKIP_MIN]

    feed = Table("Bottlefeed", df_feed)
    nappy = Table(
        "Nappy",
        pd.DataFrame(
            gen_nappy(data["baby_nappy"], notes),
            columns=[
                COL_TIMESTAMP,
                COL_DATE,
                COL_TIME,
                COL_YEAR,
                COL_WEEK,
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
            aggfunc={COL_AMOUNT: [np.sum, np.max, np.count_nonzero]},
            # margins=True,
        ),
    )

    pivot_amount_by_week = Table(
        "pivot_amount_sum_by_week",
        pd.pivot_table(
            feed.as_df(),
            values=COL_AMOUNT,
            index=[COL_YEAR, COL_WEEK],
            aggfunc={COL_AMOUNT: [np.sum, np.max]},
            # margins=True,
        ),
    )

    pivot_amount_max_by_week = Table(
        "pivot_amount_max_by_week",
        pd.pivot_table(
            feed.as_df(),
            values=COL_AMOUNT,
            index=[COL_YEAR, COL_WEEK],
            aggfunc={COL_AMOUNT: [np.max]},
            # margins=True,
        ),
    )

    pivot_skipmin = Table(
        "pivot_skipmin",
        pd.pivot_table(
            feed.as_df(),
            values=COL_SKIP_MIN,
            index=[COL_DATE],
            aggfunc={COL_SKIP_MIN: [np.mean, np.average, np.max]},
            # margins=True,
        ),
    )

    pivot_amount_by_weekday = Table(
        "pivot_amount_by_weekday",
        pd.pivot_table(
            feed.as_df(),
            values=COL_AMOUNT,
            index=[COL_WEEKDAY],
            aggfunc={COL_AMOUNT: [np.sum, np.max]},
            # margins=True,
        ),
    )

    # TODO: group by hour
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
            index=[COL_YEAR, COL_WEEK],
            aggfunc=np.count_nonzero,
            margins=True,
        ),
    )

    tables = [
        feed,
        nappy,
        pivot_amount,
        pivot_amount_by_week,
        pivot_skipmin,
        pivot_amount_max_by_week,
        pivot_amount_by_weekday,
        pivot_amount_by_time,
        pivot_amount_food,
        pivot_amount_bottle,
        pivot_amount_food_bottle,
        pivot_consistency,
    ]

    if is_excel:
        with pd.ExcelWriter(FILE_XLSX) as writer:
            for df in tables:
                df.to_excel(writer)

    if is_plain:
        for df in tables:
            df.show()

    if is_plots:
        for df in tables:
            df.plot()
            # nappy: No numeric data to plot

    return 0


if __name__ == "__main__":
    sys.exit(main())
