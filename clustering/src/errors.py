from fastapi import HTTPException

emptyBody = HTTPException(status_code=400, detail="Empty Request Body - Cannot process request with empty body.")
requireTwoEmbeddings = HTTPException(status_code=400, detail="Need two or more embeddings - Most provide at least two embeddings.")
