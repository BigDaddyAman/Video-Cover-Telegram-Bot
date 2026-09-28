import orjson


def dumps(data) -> bytes:
    return orjson.dumps(data)


def loads(data):
    return orjson.loads(data)