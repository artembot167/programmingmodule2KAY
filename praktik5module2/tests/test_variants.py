"""Відкриті тести практичної роботи 5: 10 задач × 3 набори даних (data/sites.json).

Запуск своєї задачі: pytest -k T05  (замініть 05 на номер вашої задачі).
Запуск для свого набору: pytest -k "T05-S2".
"""
import copy

import pytest
from conftest import load

from checks_open import FUNCS, OPEN, OPEN_ERRORS
from helpers import load_sites

SITES = load_sites()

CASES = []
for n in range(1, 11):
    for i, site in enumerate(SITES, 1):
        for fn in OPEN[n]:
            CASES.append(pytest.param(n, site, fn, id=f"T{n:02d}-S{i}-{fn.__name__.split('_', 1)[1]}"))

ERRORS = []
for n in range(1, 11):
    for k, (label, make, message) in enumerate(OPEN_ERRORS[n], 1):
        ERRORS.append(pytest.param(n, make, message, id=f"T{n:02d}-E{k}"))


@pytest.mark.parametrize("n,site,check", CASES)
def test_check(n, site, check):
    check(load(n), site)


@pytest.mark.parametrize("n,make,message", ERRORS)
def test_errors(n, make, message):
    broken = make(copy.deepcopy(SITES[0]))
    with pytest.raises(ValueError) as info:
        getattr(load(n), FUNCS[n])(broken)
    assert str(info.value) == message
