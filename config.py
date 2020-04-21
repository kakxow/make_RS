from typing import Tuple

from utils import get_object_code_name_mapping


OBJECT_CODE_NAME_MAPPING = get_object_code_name_mapping()

accept_counterparties_i = ('ПАО "Сбербанк России"',)
non_vat_counterparties: Tuple[str, ...] = tuple()
accept_counterparties_p = \
    ('ПАО "Сбербанк России"', 'Альфа-Банк АО', 'Банк ВТБ (ПАО) г.Москва')

FIELDNAMES = (
    'Код группировки',
    'Вид документа',
    'Дата проводки',
    'Дата документа',
    'БЕ',
    'Валюта',
    'ПФМ',
    'ФП',
    'МВЗ',
    'Кредитор',
    'К оплате',
    'Вид расчета',
    'Код НДС',
    'Основной счет',
    'Сумма с НДС',
    'Таб. Сотр.',
    'Код блокировки',
    'Текст позиции',
    'Внутренний номер договора для коммечреских закупок',
    'Текст заголовка документа',
    'Фонд',
)
