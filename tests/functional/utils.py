from typing import Dict


def is_paginated(json_data: Dict):
    return type(json_data) is dict and \
    '_items' in json_data and \
    '_count' in json_data and \
    '_page' in json_data and \
    '_total_pages' in json_data
