from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

app = FastAPI()

# A dictionary to store the one-time tokens
tokens = {}

# The security scheme to use for the endpoint that requires a one-time token
bearer_scheme = HTTPBearer()

# A decorator function to enforce the use of a one-time token
def requires_token(func):
    @wraps(func)
    async def decorated(*args, **kwargs):
        credentials: HTTPAuthorizationCredentials = HTTPBearer()
        try:
            token = await authenticate_token(credentials)
        except ValueError as e:
            raise HTTPException(status_code=401, detail=str(e))
        if token not in tokens:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        tokens.pop(token)
        return await func(*args, **kwargs)
    return decorated


# Endpoint that generates a one-time token
@app.get("/generate_token")
def generate_token():
    # Generate a unique token (e.g. using the secrets module)
    token = "unique_token_here"
    # Store the token in the dictionary with a value of True
    tokens[token] = True
    return {"token": token}

async def authenticate_token(credentials: HTTPAuthorizationCredentials):
    token = credentials.credentials
    if token != "secret-token":
        raise ValueError("Invalid token")
    return token
