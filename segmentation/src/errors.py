from fastapi import HTTPException

invalidJson = HTTPException(status_code=400, detail="Invalid JSON - No valid json provided.")
tooFewSubmissions = HTTPException(status_code=400,detail="Too few submissions -"
                                                         "To calculate new keywords at least 10 submissions are expected")
noSubmissions = HTTPException(status_code=400,detail="No Submissions and no feedback found -"
                                                     "Provide an array \"submissions\" or  \"feedback\" with {id.., text: ..}")
typeError = HTTPException(status_code=400,detail="TypeError: Could not deserialize to_segment -"
                                                 " Provide array to_segment with {\"id\": ..., \"text\": ...}")
keyError = HTTPException(status_code=400,detail="KeyError: Could not deserialize to_segment -"
                                                "Provide array to_segment with {\"id\": ..., \"text\": ...}")
