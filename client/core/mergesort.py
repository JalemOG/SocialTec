from typing import List, Callable, TypeVar

T = TypeVar("T")

def merge_sort(items: List[T], key: Callable[[T], str]) -> List[T]:
    if len(items) <= 1:
        return items

    mid = len(items) // 2
    left = merge_sort(items[:mid], key)
    right = merge_sort(items[mid:], key)

    return _merge(left, right, key)

def _merge(left: List[T], right: List[T], key: Callable[[T], str]) -> List[T]:
    i = j = 0
    out: List[T] = []
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out
