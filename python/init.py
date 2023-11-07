import os
import re
import sys
import traceback

import pandas as pd
import numpy as np
from sqlalchemy.dialects.postgresql import insert

if os.path.isdir("/home/dev/gridstudio/python"):
    sys.path.append("/home/dev/gridstudio/python")
    os.chdir("/home/dev/gridstudio/python")

from db.session import session
from db.declarations import Email, Base
from utils.table_io import get_whole_table
from sheet import sheet, add_sheet, rename_sheet, real_print
from utils.table import T

data_layout = {}


def excel_date_to_datetime(xl_date):
    date = pd.to_datetime(xl_date, format="%Y-%m-%d", errors="coerce")
    print(date)

    return date.strftime("%Y-%m-%d")


def read_table_exec(source, *args, **kwargs):
    if "date_columns" in kwargs:
        converters = {col: excel_date_to_datetime for col in kwargs.pop("date_columns")}
        kwargs["converters"] = converters

    return get_whole_table(
        source,
        sheet_name=0,
        header=0,
        na_filter=False,
        *args,
        **kwargs,
    )


def read_db_exec(source, *args, **kwargs):
    return pd.read_sql(source, session.bind, *args, **kwargs)


def get(cell_range, source, columns=None, headers=True, sheet_index=0, *args, **kwargs):
    exec = None
    if "/" in source:
        exec = read_table_exec
    else:
        exec = read_db_exec

    df = None
    # if source is file or directory, exec is get_whole_table, else exec is pd.read_sql
    if columns is None:
        df = exec(source, *args, **kwargs)
    else:
        df = exec(source, columns=columns, *args, **kwargs)

    # df = df.where(pd.notnull(df), None)
    df = df.map(lambda x: x[:190] if isinstance(x, str) else x)

    sheet(cell_range, df, headers, sheet_index)

    return df


def put(
    cell_range,
    declared_object,
    columns=None,
    on_conflict_do_update=True,
    headers=True,
    sheet_index=0,
):
    if ":" not in cell_range:
        cell_range = ":".join([cell_range, "00"])

    df = sheet(cell_range, headers=headers, sheet_index=sheet_index)
    df_records = df.to_dict("records")

    table = declared_object.__table__
    stmt = insert(table).values(df_records)
    stmt = stmt.on_conflict_do_update(
        constraint=f"PK-{table}-uid",
        set_={
            col: getattr(stmt.excluded, col)
            for col in df_records[0].keys()
            if not columns or col in columns
        },
    )
    try:
        result = session.execute(stmt)
        session.commit()

        affected_rows = result.rowcount
        print("Affected rows: " + str(affected_rows))

        return affected_rows
    except Exception as e:
        session.rollback()
        traceback.print_exc()


def print(text):
    if not isinstance(text, str):
        text = str(text)

    real_print("#INTERPRETER#" + text + "#ENDPARSE#", end="", flush=True)


def getAndExecuteInput():
    command_buffer = ""

    while True:
        code_input = input("")
        # when empty line is found, execute code
        if code_input == "":
            try:
                exec(command_buffer, globals(), globals())

                # onlyprint COMANDCOMPLETE when the input doesn't start with parseCall,
                # since it's a special internal Python call
                # which requires a single print between exec and return
                if not command_buffer.startswith("parseCall"):
                    real_print("#COMMANDCOMPLETE##ENDPARSE#", end="", flush=True)
            except:
                traceback.print_exc()
            command_buffer = ""
        else:
            command_buffer += code_input + "\n"


# testing
# sheet("A1:A2", [1,2])
# df = pd.DataFrame({'a':[1,2,3], 'b':[4,5,6]})
# sheet("A1:B2")
# from("A1", "/home/Dropbox/seolos/labor.xlsx", date_columns=["입사일", "퇴사일", "생년월일"])
# get("A1", "mail", columns=["uid", "spam", "origin", "msg"])
a = T("/home/Dropbox/seolos/l.xlsx")
a.to("A1")

# b = T(Email, columns=["uid", "spam", "origin", "msg"])
# b.to("A25")
# print(type(Email))
# sheet("A1", type("Email", (Base,), {}), columns=["uid", "spam", "origin", "msg"])
# df = sheet("A1:00")

getAndExecuteInput()
