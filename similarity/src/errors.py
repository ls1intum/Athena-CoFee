from falcon import HTTPBadRequest

emptyBody = HTTPBadRequest("Empty Requerst Body", "Cannot process request with empty body.")
requireTwoBlocks = HTTPBadRequest("Need two or more blocks", "Must provide at least two text blocks.")
requireCourseId = HTTPBadRequest("CourseId not provided", "Must provide a course identifier to upload material")
requireFileData = HTTPBadRequest("File data is not provided", "Must provide file data to upload material")
requireFileName = HTTPBadRequest("File name is not provided", "Must provide file name to upload material")
requireTwoEmbeddings = HTTPBadRequest("Need two or more embeddings", "Most provide at least two embeddings.")
requireEmbeddingPairs = HTTPBadRequest("No embedding pairs provided.", "Must provide embedding pairs to train network.")
