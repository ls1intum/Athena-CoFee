from falcon import HTTPBadRequest

emptyBody = HTTPBadRequest("Empty Requerst Body", "Cannot process request with empty body.")
requireTwoBlocks = HTTPBadRequest("Need two or more blocks", "Must provide at least two text blocks.")