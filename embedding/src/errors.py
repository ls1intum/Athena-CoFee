from falcon import HTTPBadRequest

emptyBody = HTTPBadRequest("Empty Request Body", "Cannot process request with empty body.")
requireTwoBlocks = HTTPBadRequest("Need two or more blocks", "Must provide at least two text blocks.")
requireTextBlocks = HTTPBadRequest("Need text blocks", "Must provide text blocks.")
requireFeedback = HTTPBadRequest("Need feedback", "Must provide feedback.")
requireCourseId = HTTPBadRequest("CourseId not provided", "Must provide a course identifier to upload material")
requireFileData = HTTPBadRequest("File data is not provided", "Must provide file data to upload material")
requireFileName = HTTPBadRequest("File name is not provided", "Must provide file name to upload material")
