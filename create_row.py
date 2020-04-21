from decimal import Decimal
from typing import Dict, Union, List

from config import non_vat_counterparties, accept_counterparties_p


def collection(
    base: Dict[str, Union[str, int, Decimal]],
    line: List[str]
) -> Dict[str, Union[str, int, Decimal]]:
    """
    Creates complete inkas RS row on top of base with data from line.

    Parameters
    ----------
    base
        Dictionary with RS columns and their default values.
    line
        List of values from fincontrol report.

    Returns
    -------
    Dict[str, Union[str, int, Decimal]]
        Complete inkas RS row.

    """
    row = base.copy()

    be = row['be']
    last_year = row['last_year']
    last_month = row['last_month']
    tag = row['tag']
    fund = row['fund']

    counterparty = line[4]
    contract_code = line[12]
    raw_sum = float(line[10])
    creditor = line[14]

    sum_ = Decimal(raw_sum * 1.2)
    rs_header = \
        f'инкассация {last_year}.{last_month:02} {counterparty}'
    row_header = f'{rs_header} {tag} {fund}'
    VAT_code = 'Z0' if counterparty in non_vat_counterparties else 'Z5'

    row.update({
        'pfm': f'{be}04',
        'fp': '135703',
        'creditor': creditor,
        'VAT_code': VAT_code,
        'main_acc': '36200000',
        'sum_with_VAT': sum_,
        'text_pos': row_header,
        'contract_code': contract_code,
        'text_header': rs_header,
        'fund': fund,
    })
    return row


def recount(
    base: Dict[str, Union[str, int, Decimal]],
    line: List[str]
) -> Dict[str, Union[str, int, Decimal]]:
    """
    Creates complete recount RS row on top of base with data from line.

    Parameters
    ----------
    base
        Dictionary with RS columns and their default values.
    line
        List of values from fincontrol report.

    Returns
    -------
    Dict[str, Union[str, int, Decimal]]
        Complete recount RS row.

    """
    row = base.copy()

    be = row['be']
    last_year = row['last_year']
    last_month = row['last_month']
    tag = row['tag']
    fund = row['fund']

    counterparty = line[5]
    contract_code = line[13]
    raw_sum = line[11]
    creditor = line[15]

    sum_ = Decimal(raw_sum)
    doc_type = '02'
    if counterparty in accept_counterparties_p:
        contract_code = ''
        doc_type = '08'
        tag = ''
    rs_header = \
        f'пересчёт {last_year}.{last_month:02} {counterparty}'
    row_header = f'{rs_header} {tag} {fund}'

    row.update({
        'doc_type': doc_type,
        'pfm': f'{be}03',
        'fp': '136003',
        'creditor': creditor,
        'VAT_code': 'Z0',
        'main_acc': '37100120',
        'sum_with_VAT': sum_,
        'text_pos': row_header,
        'text_header': rs_header,
        'fund': fund,
        'contract_code': contract_code,
        'tag': tag
    })
    return row


def acquiring(
    base: Dict[str, Union[str, int, Decimal]],
    sum_: Decimal,
    fund: str
) -> Dict[str, Union[str, int, Decimal]]:
    """
    Creates complete acquiring RS row on top of base with given
    sum_with_VAT and fund.

    Parameters
    ----------
    base
        Dictionary with RS columns and their default values.
    sum_
        Total sum_with_VAT for the RS.
    fund
        Fund value for RS.

    Returns
    -------
    Dict[str, Union[str, int, Decimal]]
        Complete acquiring RS row.

    """
    row = base.copy()

    be = row['be']
    last_year = row['last_year']
    last_month = row['last_month']

    rs_header = \
        f'эквайринг {last_year}.{last_month:02} {be}'
    row_header = f'{rs_header} {fund}'

    row.update({
        'doc_type': '08',
        'be': '2020',
        'pfm': '200003',
        'fp': '136103',
        'mvz': '2020010300',
        'VAT_code': 'Z0',
        'main_acc': '37100320',
        'sum_with_VAT': sum_,
        'text_pos': row_header,
        'text_header': rs_header,
        'fund': fund,
    })
    return row


def cash_services(
    base: Dict[str, Union[str, int, Decimal]],
    sum_: Decimal
) -> Dict[str, Union[str, int, Decimal]]:
    """
    Creates complete RKO RS on top of base with given
    sum_with_VAT.

    Parameters
    ----------
    base
        Dictionary with RS columns and their default values.
    sum_
        Total sum_with_VAT for the RS.

    Returns
    -------
    Dict[str, Union[str, int, Decimal]]
        Complete RKO RS.

    """
    row = base.copy()

    be = row['be']
    last_year = row['last_year']
    last_month = row['last_month']
    fund = row['fund']

    rs_header = row_header = \
        f'РКО {last_year}.{last_month:02} {be}'

    row.update({
        'doc_type': '08',
        'pfm': f'{be}02',
        'fp': '135203',
        'VAT_code': 'Z0',
        'main_acc': '37100100',
        'sum_with_VAT': sum_,
        'text_pos': row_header,
        'text_header': rs_header,
        'fund': fund,
    })
    return row
