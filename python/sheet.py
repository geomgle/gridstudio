def from_sql(
    cell_range,
    query,
    columns=None,
    headers=True,
    sheet_index=0,
):
    df = None
    if columns is None:
        df = pd.read_sql(query, session.bind)
    else:
        df = pd.read_sql(query, session.bind, columns=columns)
    df = df.where(pd.notnull(df), None)
    df = df.map(lambda x: x[:190] if isinstance(x, str) else x)
    row_count = len(df.index)

    sheet(cell_range, df, headers, sheet_index)

    return row_count


def to_sql(
    cell_range,
    declared_object,
    on_conflict_do_update=True,
    update_columns=None,
    headers=True,
    sheet_index=0,
):
    if ":" not in cell_range:
        cell_range = ":".join([cell_range, "00"])

    df = sheet(cell_range, headers=headers, sheet_index=sheet_index)
    df_records = df.to_dict("records")
    print(df_records)
    # print(declared_object.__table__)

    # stmt = insert(declared_object.__table__).values(df_records)
    # if on_conflict_do_update:
    #     stmt = stmt.on_conflict_do_update(
    #         constraint=f"PK-{declared_object.__table__.name}-uid",
    #         set_={
    #             k: getattr(stmt.excluded, k)
    #             for k in df_records[0].keys()
    #             if not update_columns or k in update_columns
    #         },
    #     )
    # else:
    #     stmt = stmt.on_conflict_do_nothing(constraint="PK-mail-uid")
    #
    # session.execute(stmt)
    # session.commit()


import warnings

warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")

import os
import sys
import re
import json
import base64
import traceback
from typing import List, Dict, Tuple, Any, Union, Optional, Callable, TypeVar

import pandas as pd
import numpy as np

from sqlalchemy.dialects.postgresql import insert
from db.session import session
from db.declarations import Email

from server_io import real_print, getAndExecuteInputOnce

sheet_data = {}
received_range = ""


class Sheet:
    sheet_index: int
    cell_range: str

    def __init__(self, cell_range=None, sheet_index: int = 0):
        self.cell_range = cell_range
        self.sheet_index = sheet_index
        self.headers = True
        self.db = session

    @property
    def sheet_index(self):
        return self._sheet_index

    @sheet_index.setter
    def sheet_index(self, value):
        self._sheet_index = value

    @classmethod
    def from_sql(
        cls,
        cell_range=None,
        query=None,
        columns=None,
        headers=True,
        sheet_index=0,
    ):
        sheet = Sheet(cell_range, sheet_index)
        sheet.headers = headers

        df = None
        if columns is None:
            df = pd.read_sql(query, sheet.db.bind)
        else:
            df = pd.read_sql(query, sheet.db.bind, columns=columns)
        df = df.where(pd.notnull(df), None)
        df = df.map(lambda x: x[:190] if isinstance(x, str) else x)

        sheet.__call__(
            cell_range, data=df, headers=headers, sheet_index=sheet.sheet_index
        )

        return sheet

    def to_sql(
        self,
        table_name: str,
        schema: str,
        if_exists: str = "append",
        index: bool = False,
        index_label: Optional[str] = None,
        chunksize: Optional[int] = None,
        dtype: Optional[Dict[str, Any]] = None,
        method: Optional[str] = None,
    ):
        df = self.__call__(self.cell_range, headers=self.headers)

        df.to_sql(
            table_name,
            self.db.bind,
            schema=schema,
            if_exists=if_exists,
            index=index,
            index_label=index_label,
            chunksize=chunksize,
            dtype=dtype,
            method=method,
        )

    def __str__(self):
        return "Sheet(" + str(self.sheet_index) + ")"

    def __call__(self, cell_range=None, data=None, headers=True, sheet_index=0):
        # input data into sheet
        if data is not None:
            # convert numpy to array
            data_type_string = str(type(data))
            if data_type_string == "<class 'numpy.ndarray'>":
                data = data.tolist()

            if data_type_string == "<class 'pandas.core.series.Series'>":
                data = data.to_frame()
                data_type_string = str(type(data))

            if data_type_string == "<class 'pandas.core.frame.DataFrame'>":
                df_tuple = self._df_to_list(data, headers)
                data = df_tuple[0]
                column_length = df_tuple[1]
                column_count = df_tuple[2]

                # create cell_range
                if not self._has_number(cell_range):
                    cellColumnLetter = cell_range
                    cellColumnEndLetter = self._index_to_letter(
                        self._letter_to_index(cellColumnLetter) + column_count - 1
                    )
                    cell_range = (
                        cellColumnLetter
                        + "1:"
                        + cellColumnEndLetter
                        + str(column_length)
                    )

                else:
                    cellColumnLetter = self._index_to_letter(
                        self._get_ref_col_index(cell_range)
                    )
                    startRow = self._get_ref_row_index(cell_range)
                    cellColumnEndLetter = self._index_to_letter(
                        self._letter_to_index(cellColumnLetter) + column_count - 1
                    )
                    cell_range = (
                        cellColumnLetter
                        + str(startRow)
                        + ":"
                        + cellColumnEndLetter
                        + str(column_length + startRow - 1)
                    )

            # always convert cell to range
            if ":" not in cell_range:
                if not self._has_number(cell_range):
                    if type(data) is list:
                        cell_range = cell_range + "1:" + cell_range + str(len(data))
                    else:
                        cell_range = cell_range + "1:" + cell_range + "1"
                else:
                    cell_range = cell_range + ":" + cell_range

            if type(data) is list:
                newList = list(map(self._convert_to_json_string, data))

                arguments = ["RANGE", "SETLIST", cell_range, str(sheet_index)]

                # append list
                arguments = arguments + newList

                json_object = {"arguments": arguments}
                json_string = "".join(
                    ["#PARSE#", json.dumps(json_object), "#ENDPARSE#"]
                )
                real_print(json_string, flush=True, end="")

            else:
                data = self._convert_to_json_string(data)

                data = {
                    "arguments": [
                        "RANGE",
                        "SETSINGLE",
                        cell_range,
                        str(sheet_index),
                        "".join(["=", str(data)]),
                    ]
                }
                data = "".join(["#PARSE#", json.dumps(data), "#ENDPARSE#"])
                real_print(data, flush=True, end="")

        # get data from sheet
        else:
            print(headers)
            if ":00" in cell_range:
                real_print(
                    "#DATA#" + str(sheet_index) + "!" + cell_range + "#ENDPARSE#",
                    end="",
                    flush=True,
                )
                getAndExecuteInputOnce()
                cell_range = received_range
            else:
                # convert non-range to range for get operation
                if ":" not in cell_range:
                    cell_range = ":".join([cell_range, cell_range])

                # in blocking fashion get latest data of range from Go
                real_print(
                    "#DATA#" + str(sheet_index) + "!" + cell_range + "#ENDPARSE#",
                    end="",
                    flush=True,
                )
                getAndExecuteInputOnce()

            # if everything works, the exec command has filled sheet_data with the appropriate data
            # return data range as arrays
            column_references = self._cell_range_to_indexes(cell_range)

            result = []
            colnames = []
            for column in column_references:
                if headers:
                    reference = column.pop(0)
                    colnames.append(sheet_data[str(sheet_index) + "!" + reference])

                column_data = []
                for reference in column:
                    column_data.append(sheet_data[str(sheet_index) + "!" + reference])
                result.append(column_data)

            df = pd.DataFrame(data=result).transpose()
            if headers:
                df.columns = colnames

            return df

    def _get_ref_row_index(self, reference):
        return int(re.findall(r"\d+", reference)[0])

    def _get_ref_col_index(self, reference):
        return self._letter_to_index("".join(re.findall(r"[a-zA-Z]", reference)))

    def _letter_to_index(self, letters):
        columns = len(letters) - 1
        total = 0
        base = 26

        for x in letters:
            number = ord(x) - 64
            total += number * int(base**columns)
            columns -= 1
        return total

    def _index_to_letter(self, index):
        base = 26

        # start at the base that is bigger and work your way down
        leftOver = index

        columns = []

        while leftOver > 0:
            remainder = leftOver % base

            if remainder == 0:
                remainder = base

            columns.insert(0, int(remainder))
            leftOver = (leftOver - remainder) / base

        buff = ""

        for x in columns:
            buff += chr(x + 64)

        return buff

    def _cell_range_to_indexes(self, cell_range):
        references = []

        cells = cell_range.split(":")

        cell1Row = self._get_ref_row_index(cells[0])
        cell2Row = self._get_ref_row_index(cells[1])

        cell1Column = self._get_ref_col_index(cells[0])
        cell2Column = self._get_ref_col_index(cells[1])

        for x in range(cell1Column, cell2Column + 1):
            column_ref = []
            for y in range(cell1Row, cell2Row + 1):
                column_ref.append(self._index_to_letter(x) + str(y))
            references.append(column_ref)

        return references

    def _has_number(self, s):
        return any(i.isdigit() for i in s)

    def _convert_to_json_string(self, element):
        # if element is None:
        #     return 0

        if isinstance(element, str):
            # string meant as string, escape
            element = element.replace("\n", "")

            # if data is string without starting with =, add escape quotes
            if len(element) > 0 and element[0] == "=":
                return element[1:]
            else:
                return '"' + element + '"'
        else:
            return format(element, ".12f")

    def _df_to_list(self, df, include_headers=True):
        columns = list(df.columns.values)
        data = []
        column_length = 0
        for column in columns:
            column_data = df[column].tolist()

            if include_headers:
                column_data = [column] + column_data

            column_length = len(column_data)
            data = data + column_data
        return (data, column_length, len(columns))
