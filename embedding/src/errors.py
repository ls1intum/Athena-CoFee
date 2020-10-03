from fastapi import HTTPException

invalidJson = HTTPException(status_code=400, detail="Invalid JSON - No valid json provided.")
requireTwoBlocks = HTTPException(status_code=400,
                                 detail="Need two or more blocks - Must provide at least two text blocks.")
requireCourseId = HTTPException(status_code=400,
                                detail="CourseId not provided - Must provide a course identifier to upload material")
requireFileData = HTTPException(status_code=400,
                                detail="File data is not provided - Must provide file data to upload material")
requireFileName = HTTPException(status_code=400,
                                detail="File name is not provided - Must provide file name to upload material")
requireFeedbackWithTextBlock = HTTPException(status_code=400,
                                             detail="Need feedback with text blocks - Must provide feedbackWithTextBlock")
requireExerciseId = HTTPException(status_code=400,
                                  detail="Need exercise id - Must provide exercise id")
