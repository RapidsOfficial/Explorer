from webargs import fields, validate

page_args = {
    "page": fields.Int(missing=1, validate=validate.Range(min=1))
}

broadcast_args = {
    "raw": fields.Str(required=True)
}
