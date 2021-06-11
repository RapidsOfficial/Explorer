from webargs import fields

search_args = {
    "query": fields.Str(required=True)
}

page_args = {
    "page": fields.Int(missing=1, validate=lambda val: val > 0)
}
