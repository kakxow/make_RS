from decimal import Decimal
import itertools
from typing import Dict, Union, List, Tuple, Iterator

from config import OBJECT_CODE_NAME_MAPPING
import create_row
from utils import line_generator, get_shared


def _collection_recount_pairs(
    base: Dict[str, Union[str, int, Decimal]],
    line: List[str]
) -> Tuple[Dict[str, Union[str, int, Decimal]], Dict[str, Union[str, int, Decimal]]]:
    """
    Process given line and build inkas and recount RS's on top of base.

    Parameters
    ----------
    base
        Dictionary with RS columns and their default values.
    line
        List of values from fincontrol report.

    Returns
    -------
    Tuple[Dict[str, Union[str, int, Decimal]], Dict[str, Union[str, int, Decimal]]]
        Returns twor RS's - inkas and recount.

    """
    shared = get_shared(line)
    base = {**base, **shared}
    row_inkas = create_row.collection(base, line)
    row_recount = create_row.recount(base, line)
    return row_inkas, row_recount


def collection_recount(
    report_path: str,
    base: Dict[str, Union[str, int, Decimal]]
) -> List[Dict[str, Union[str, int, Decimal]]]:
    report_lines = line_generator(report_path, 'расчет комиссии')
    collection_recount_pairs = (_collection_recount_pairs(base, line) for line in report_lines if is_valid(line))
    rows = itertools.chain.from_iterable(collection_recount_pairs)
    summed_rows = sum_by_key(rows)
    return summed_rows


def acquiring(
    report_path: str,
    base: Dict[str, Union[str, int, Decimal]]
) -> List[Dict[str, Union[str, int, Decimal]]]:
    """
    Creates trio of acquiring RS's.

    Parameters
    ----------
    report_path
        Path to the fincontrol report file.
    base
        Dictionary with RS columns and their default values.

    Returns
    -------
    List[Dict[str, Union[str, int, Decimal]]]
        List of formed acquiring RS'S.

    """
    reader = line_generator(report_path, 'эквайринг')
    sum_ = sum_cstore = sum_ecomm = Decimal()
    for line in reader:
        if len(line) < 6 or len(line[1]) > 4:
            continue
        object_code = line[1]
        object_name = OBJECT_CODE_NAME_MAPPING[object_code]
        sum_line = line[5]
        if not isinstance(sum_line, float):
            continue
        sum_line = Decimal(sum_line)
        if '000' in object_name:
            sum_ecomm += sum_line
        elif 'apple' in object_name.lower():
            sum_cstore += sum_line
        else:
            sum_ += sum_line
    return [
        create_row.acquiring(base, sum_, ''),
        create_row.acquiring(base, sum_ecomm, 'E_COMMERCE'),
        create_row.acquiring(base, sum_cstore, 'CSTORE'),
    ]


def cash_services(
    report_path: str,
    base: Dict[str, Union[str, int, Decimal]]
) -> List[Dict[str, Union[str, int, Decimal]]]:
    """
    Creates a list of one RKO RS.

    Parameters
    ----------
    report_path
        Path to the fincontrol report file.
    base
        Dictionary with RS columns and their default values.

    Returns
    -------
    List[Dict[str, Union[str, int, Decimal]]]
        List of one RKO RS.

    """
    total_sum = Decimal()
    reader = line_generator(report_path, 'РКО')
    for line in reader:
        if len(line) < 8:
            continue
        sum_ = line[6]
        if not isinstance(sum_, float):
            continue
        total_sum += Decimal(sum_)
    rko_row = create_row.cash_services(base, total_sum)
    return [rko_row]


def sum_by_key(
    rs_iter: Iterator[Dict[str, Union[str, int, Decimal]]]
) -> List[Dict[str, Union[str, int, Decimal]]]:
    """
    Summes RS's sum_with_VAT based on identical rows.

    Parameters
    ----------
    rs_iter
        Iterator that yields RS's.

    Returns
    List[Dict[str, Union[str, int, Decimal]]]
        Returns list of complete and summed RS's.

    """
    summed_rows: Dict[str, Dict[str, Union[str, int, Decimal]]] = {}
    for rs in rs_iter:
        temp = rs.copy()
        sum_: Decimal = temp.pop('sum_with_VAT')
        temp.pop('object_name')
        row_header = ' '.join(map(str, temp.values()))
        try:
            summed_rows[row_header]['sum_with_VAT'] += sum_
        except KeyError:
            summed_rows[row_header] = rs
    return list(summed_rows.values())


def is_valid(line: List[str]) -> bool:
    return len(line) < 12 or len(line[1]) > 4
