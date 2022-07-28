from webargs import fields, validate

trade_cancel_pair_args = {
    "tickerforsale": fields.Str(required=True),
    "tickerdesired": fields.Str(required=True),
}

trade_args = {
    "tickerforsale": fields.Str(required=True),
    "tickerdesired": fields.Str(required=True),
    "amountforsale": fields.Float(
        required=True, validate=validate.Range(min=0)
    ),
    "amountdesired": fields.Float(
        required=True, validate=validate.Range(min=0)
    ),
}

dex_sell_args = {
    "amountforsale": fields.Float(
        required=True, validate=validate.Range(min=0)
    ),
    "amountdesired": fields.Float(
        required=True, validate=validate.Range(min=0)
    ),
    "minacceptfee": fields.Float(
        required=True, validate=validate.Range(min=0)
    ),
    "paymentwindow": fields.Int(
        required=True, validate=validate.Range(min=0, max=100)
    ),
    "ticker": fields.Str(required=True),
    "action": fields.Str(required=True, validate=lambda f: f in [
        "new", "update", "cancel"
    ])
}

close_args = {
    "ticker": fields.Str(required=True)
}

send_args = {
    "amount": fields.Float(required=True, validate=validate.Range(min=0)),
    "ticker": fields.Str(required=True)
}

fixed_args = {
    "amount": fields.Float(required=True, validate=validate.Range(min=0)),
    "divisible": fields.Bool(required=True),
    "subcategory": fields.Str(missing=""),
    "category": fields.Str(missing=""),
    "ticker": fields.Str(required=True),
    "name": fields.Str(required=True),
    "url": fields.Str(missing=""),
    "data": fields.Str(missing="")
}

managed_args = {
    "divisible": fields.Bool(required=True),
    "subcategory": fields.Str(missing=""),
    "category": fields.Str(missing=""),
    "ticker": fields.Str(required=True),
    "name": fields.Str(required=True),
    "url": fields.Str(missing=""),
    "data": fields.Str(missing="")
}

crowdsale_args = {
    "tokensperunit": fields.Float(required=True, validate=validate.Range(min=0)),
    "earlybonus": fields.Int(required=True, validate=validate.Range(min=0)),
    "issuerpercentage": fields.Int(required=True),
    "divisible": fields.Bool(required=True),
    "deadline": fields.Int(required=True),
    "subcategory": fields.Str(missing=""),
    "category": fields.Str(missing=""),
    "ticker": fields.Str(required=True),
    "name": fields.Str(required=True),
    "url": fields.Str(missing=""),
    "data": fields.Str(missing="")
}

multisig_args = {
    "payload": fields.Str(required=True),
    "address": fields.Str(required=True),
    "pubkey": fields.Str(required=True)
}
