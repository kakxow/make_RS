import calendar
import csv
import datetime as dt
from decimal import Decimal
from typing import Dict, List, Tuple, Union

from config import FIELDNAMES
import make_rows


def get_base(be: str, peronnel_number: str) -> Dict[str, Union[str, int, Decimal]]:
    """
    Creates base for all RS rows from BE, personnel number and current date.

    Parameters
    ----------
    be
        SAP business unit, '4950', '2020' or smth.
    personnel_number
        SAP personnel number of the person in charge.

    Returns
    -------
    Dict[str, Union[str, int]]
        Returns dictionary with RS columns and their default values.

    """
    today = dt.datetime.now().date()
    last_year, last_month = calendar.prevmonth(today.year, today.month)
    last_day = calendar.monthlen(last_year, last_month)
    date_pay = today.strftime('%d.%m.%Y')
    date_period = dt.datetime(last_year, last_month, 1).strftime('%d.%m.%Y')
    date_doc = dt.datetime(last_year, last_month, last_day).strftime('%d.%m.%Y')

    return {
        'group_code': 1,
        'doc_type': '02',
        'date_period': date_period,
        'date_doc': date_doc,
        'be': be,
        'currency': 'RUB',
        'pfm': '',
        'fp': '',
        'mvz': f'{be}010300',
        'creditor': '',
        'date_pay': date_pay,
        'calc_type': '1',
        'VAT_code': '',
        'main_acc': '',
        'sum_with_VAT': Decimal(),
        'peronnel_number': peronnel_number,
        'block_code': '1',
        'text_pos': '',
        'contract_code': '',
        'text_header': '',
        'fund': '',
        'last_year': last_year,
        'last_month': last_month,
    }


def process(
    list_of_rs: List[Dict[str, Union[str, int, Decimal]]]
) -> List[Dict[str, str]]:
    """
    Properly form list of RS's: delete extra keys, format sum_with_VAT
    and creditor to proper strings and enumerate groups.

    Parameters
    ----------
    list_of_rs
        List of freshly formed RS's.

    Returns
    -------
    List[Dict[str, Union[str, int]]]
        List of serialize-friendly RS's.

    """
    formatted_list_of_rs = sorted(list_of_rs, key=lambda x: x['text_header'])

    group_code = 1
    prev = None
    for rs in formatted_list_of_rs:
        rs = delete_extra(rs)
        rs = format_sum(rs)
        rs['creditor'] = str(rs['creditor']).split('.')[0]

        if not prev:
            prev = rs
            continue
        rs, prev, group_code = set_groups(rs, prev, group_code)

    return formatted_list_of_rs


def format_sum(
    rs: Dict[str, Union[str, int, Decimal]]
) -> Dict[str, Union[str, int]]:
    """
    Converts sum_with_VAT from Decimal to str.

    Parameters
    ----------
    rs
        Non formatted RS.

    Returns
    -------
    Dict[str, Union[str, int]]
        RS with formatted sum_with_VAT.

    """

    sum_ = rs['sum_with_VAT']
    rs['sum_with_VAT'] = f'{sum_:.2f}'.replace('.', ',')
    return rs


def delete_extra(
    rs: Dict[str, Union[str, int, Decimal]]
) -> Dict[str, Union[str, int, Decimal]]:
    """
    Deletes extra fields from RS.

    Parameters
    ----------
    rs
        Non formatted RS.

    Returns
    -------
    Dict[str, Union[str, int, Decimal]]
        Returns RS without extra fields.

    """
    exclude = ['last_year', 'last_month', 'object_name', 'tag']
    for key in exclude:
        rs.pop(key, None)
    return rs


def set_groups(
    rs: Dict[str, Union[str, int]],
    previous_rs: Dict[str, Union[str, int]],
    group_code: int
) -> Tuple[Dict[str, Union[str, int]], Dict[str, Union[str, int]], int]:
    """
    Takes two RS's and a current group number and assigns correct group numbers
    to RS's

    Parameters
    ----------
    rs
        Current RS.
    previous_rs
        Previous RS.
    group_code
        Current group number.

    Returns
    -------
    Tuple[Dict[str, Union[str, int]], Dict[str, Union[str, int]], int]
        Returns same and previous RS's and increased group number.

    """
    if rs['text_header'] != previous_rs['text_header']:
        group_code += 1
    rs['group_code'] = group_code
    previous_rs = rs
    return rs, previous_rs, group_code


def to_csv(rs_list: List[Dict[str, Union[str, int]]], filename: str = None):
    """
    Output list of RS's to csv file.

    Parameters
    ----------
    rs_list
        List of serialization ready RS's.
    filename
        Path to file where to save file.

    Returns
    -------
    None
        Only writes to file.

    """
    filename = filename or 'test_file4.csv'
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rs_list[0], delimiter=';')
        f.write(';'.join(FIELDNAMES) + '\n')
        writer.writerows(rs_list)


def parse_report(report_path: str, be: str, peronnel_number: str):
    base = get_base(be, peronnel_number)

    collection_recount_rows = make_rows.collection_recount(report_path, base)
    acquiring_rows = make_rows.acquiring(report_path, base)
    rko_rows = make_rows.cash_services(report_path, base)

    formatted_rows = process(collection_recount_rows + acquiring_rows + rko_rows)

    return formatted_rows


if __name__ == '__main__':
    result = \
        parse_report('C:\\Max\\Отчёт ФК 3-2020 ЦР 4950.xlsx', '4950', '357690')
    to_csv(result, 'excel_march2020.csv')
