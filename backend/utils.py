import requests
import config
import math
import json

def round_amount(amount):
    return round(amount, 8)

def location(address):
    try:
        r = requests.get(f"http://ip-api.com/json/{address}")
        data = r.json()

        if data["status"] != "success":
            return None

        return {
            "country": data["country"],
            "code": data["countryCode"],
            "lat": data["lat"],
            "lon": data["lon"],
            "city": data["city"]
        }

    except Exception:
        return None

def dead_response(message="Invalid Request", rid=config.rid):
    return {"error": {"code": 404, "message": message}, "id": rid}

def response(result, error=None, rid=config.rid):
    return {"error": error, "id": rid, "result": result}

def make_request(method, params=[]):
    headers = {"content-type": "text/plain;"}
    data = json.dumps({"id": config.rid, "method": method, "params": params})

    try:
        return requests.post(config.endpoint, headers=headers, data=data).json()
    except Exception:
        return dead_response()

def satoshis(value):
    return int(float(value) * math.pow(10, 8))

def amount(value, decimals=8):
    return round(float(value) / math.pow(10, decimals), decimals)

def pagination(url, page, items, total):
    pagination = range(page - 4, page + 5)
    pagination = [item for item in pagination if item >= 1 and item <= total]
    previous_page = page - 1 if page != 1 else None
    next_page = page + 1 if page != total else None

    return {
        "total": total,
        "current": page,
        "pages": pagination,
        "previous": previous_page,
        "next": next_page,
        "url": url
    }
