from falcon import HTTPBadRequest

emptyBody = HTTPBadRequest("Empty Request Body", "Cannot process request with empty body.")
requireTwoBlocks = HTTPBadRequest("Need two or more blocks", "Must provide at least two text blocks.")
requireCourseId = HTTPBadRequest("CourseId not provided", "Must provide a course identifier to upload material")
requireFileData = HTTPBadRequest("File data is not provided", "Must provide file data to upload material")
requireFileName = HTTPBadRequest("File name is not provided", "Must provide file name to upload material")
requireFeedbackWithTextBlock = HTTPBadRequest("Need feedback with text blocks", "Must provide feedbackWithTextBlock")
requireExerciseId = HTTPBadRequest("Need exercise id", "Must provide exercise id")
