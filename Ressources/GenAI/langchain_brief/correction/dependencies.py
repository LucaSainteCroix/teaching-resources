from fastapi import Request

async def get_vector_store(request: Request):
    return request.app.state.vector_store
