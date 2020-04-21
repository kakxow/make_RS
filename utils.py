import itertools
import os
from typing import Dict, Iterator, List

import xlrd

from config import OBJECT_CODE_NAME_MAPPING


def find_nsi_file(directory: str) -> str:
    """
    Finds the latest file with NSI data.

    Parameters
    ----------
    directory
        Path to directory with NSI files.

    Returns
    -------
    str
        Path to the latest file with NSI data.

    """
    def is_nsi_file(entry) -> bool:
        return entry.name.startswith('НСИ') and 'общий' in entry.name.lower()

    all_nsi_files = [entry for entry in os.scandir(directory)
                     if is_nsi_file(entry)]
    file = max(all_nsi_files, key=lambda x: x.stat().st_ctime)
    return file.path


def get_object_code_name_mapping(directory: str = 'C:\\Max') -> Dict[str, str]:
    """
    Maps SAP object codes to object names, data is from the latest NSI file,
    located in directory.

    Parameters
    ----------
    directory
        Path to directory with NSI files.

    Returns
    -------
    Dict[str, str]
        SAP object code to object name mapping.

    """
    nsi_file = find_nsi_file(directory)
    with xlrd.open_workbook(nsi_file, on_demand=True) as wb:
        sh = wb.sheet_by_name('TDSheet')
        object_codes = sh.col_values(1, start_rowx=1)
        object_names = sh.col_values(3, start_rowx=1)
    result = {k: v for k, v in zip(object_codes, object_names)}
    return result


def line_generator(filename: str, sheet_name: str) -> Iterator[List[str]]:
    """
    Yields lines from the given sheet of the given files.

    Parameters
    ----------
    filename
        Path to the file.
    sheet_name
        Name of the target sheet.

    Yields
    -------
    List[str]
        Yields lists of str, each being a row from the sheet with leading
        empty values skipped.

    """
    with xlrd.open_workbook(filename, on_demand=True) as wb:
        sh = wb.sheet_by_name(sheet_name)
        for i in range(sh.nrows):
            row = sh.row_values(i)
            line = list(itertools.dropwhile(lambda x: not x, row))
            yield line
        wb.unload_sheet(sheet_name)


def get_shared(line: List[str]) -> Dict[str, str]:
    """
    Creates mapping with RS columns and values shared between inkass RS
    and recount RS for the given line.

    Parameters
    ----------
    line
        List of values from fincontrol report.

    Returns
    -------
    Dict[str, str]
        Returns dictionary with RS columns and values for the given line,
        shared between recount and inkass RS's.

    """
    object_code = line[0]
    object_name = OBJECT_CODE_NAME_MAPPING[object_code]
    if '000' in object_name:
        fund = 'E_COMMERCE'
    elif 'APPLE' in object_name:
        fund = 'CSTORE'
    else:
        fund = ''
    try:
        tag = line[16]
    except IndexError:
        tag = ''
    return {
        'object_name': object_name,
        'tag': tag,
        'fund': fund
    }
