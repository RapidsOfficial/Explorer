from webargs import fields, validate

page_args = {
    "page": fields.Int(missing=1, validate=validate.Range(min=1))
}

masternodes_args = {
    "page": fields.Int(missing=1, validate=validate.Range(min=1)),
    "filter": fields.Str(missing=None)
}

broadcast_args = {
    "raw": fields.Str(required=True)
}

bulwark_broadcast_args = {
    "rawtx": fields.Str(required=True)
}

filter_args = {
    "page": fields.Int(missing=1, validate=validate.Range(min=1)),
    "subcategory": fields.Str(missing=None),
    "category": fields.Str(missing=None),
    "search": fields.Str(missing=None),
    "issuer": fields.Str(missing=None),
    "nft": fields.Bool(missing=False)
}

search_args = {
    "query": fields.Str(missing=None)
}
