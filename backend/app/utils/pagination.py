"""Utilitarios para calculo de paginacao."""
import math


def total_pages(total_items: int, page_size: int) -> int:
    if page_size <= 0:
        return 0
    return max(1, math.ceil(total_items / page_size))
