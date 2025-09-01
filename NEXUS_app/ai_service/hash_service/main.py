from .hashing import create_hash, verify_hash

app = FastAPI()


class HashRequest(BaseModel):

    data: str


class HashResponse(BaseModel):
    hash: str


class VerifyRequest(BaseModel):
    data: str
    hash: str


class VerifyResponse(BaseModel):
    is_valid: bool


@app.post("/hash", response_model=HashResponse)
async def hash_data(request: HashRequest):
    hash_string = create_hash(request.data)
    return HashResponse(hash=hash_string)


@app.post("/verify", response_model=VerifyResponse)
async def verify_data(request: VerifyRequest):
    is_valid = verify_hash(request.data, request.hash)
    return VerifyResponse(is_valid=is_valid)
