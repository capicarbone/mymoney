from typing import Dict

from flask_restful import fields
from collections import namedtuple

Page = namedtuple('Page', ['items', 'count', 'page', 'total_pages'])


def paged_entity_scheme(entity_fields: Dict) -> Dict:
    return {
        '_items': fields.List(fields.Nested(entity_fields), attribute='items'),
        '_count': fields.Integer(attribute='count'),
        '_page': fields.Integer(attribute='page'),
        '_total_pages': fields.Integer(attribute='total_pages')
    }


def create_page_response(query, page_index: int, page_size: int) -> Dict:
    pagination = query.paginate(page=page_index, per_page=page_size)
    return Page(
        items=pagination.items,
        count=query.count(),
        page=page_index,
        total_pages=pagination.pages
    )._asdict()

