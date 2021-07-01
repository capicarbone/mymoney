from typing import Dict

from flask_restful import fields
from collections import namedtuple

Page = namedtuple('Page', ['items', 'count', 'page'])


def paged_entity_scheme(entity_fields: Dict) -> Dict:
    return {
        '_items': fields.List(fields.Nested(entity_fields), attribute='items'),
        '_count': fields.Integer(attribute='count'),
        '_page': fields.Integer(attribute='page')
    }


def create_page_response(query, page_index: int) -> Dict:
    return Page(
        items=query.all(),
        count=query.count(),
        page=page_index
    )._asdict()

