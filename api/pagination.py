from typing import Dict

from flask_restful import fields, reqparse
from collections import namedtuple

Page = namedtuple('Page', ['items', 'count', 'page', 'total_pages'])


def paged_entity_scheme(entity_fields: Dict) -> Dict:
    return {
        '_items': fields.List(fields.Nested(entity_fields), attribute='items'),
        '_count': fields.Integer(attribute='count'),
        '_page': fields.Integer(attribute='page'),
        '_total_pages': fields.Integer(attribute='total_pages')
    }

def parse_pagination_arguments():
    parser = reqparse.RequestParser()
    parser.add_argument('page', type=int, default=1)
    parser.add_argument('items_per_page', type=int, default=12)
    return parser.parse_args()

def create_page_response(query) -> Dict:
    args = parse_pagination_arguments()
    pagination = query.paginate(page=args['page'], per_page=args['items_per_page'])
    return Page(
        items=pagination.items,
        count=query.count(),
        page=args['page'],
        total_pages=pagination.pages
    )._asdict()

