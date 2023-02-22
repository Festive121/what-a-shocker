from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

app = FastAPI()

# A dictionary to store the one-time tokens
tokens = {}

# The security scheme to use for the endpoint that requires a one-time token
bearer_scheme = HTTPBearer()

# A decorator function to enforce the use of a one-time token
def requires_token(token: str):
    if token not in tokens:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    # Remove the token from the dictionary to ensure it can only be used once
    tokens.pop(token)

# Endpoint that generates a one-time token
@app.get("/generate_token")
def generate_token():
    # Generate a unique token (e.g. using the secrets module)
    token = "unique_token_here"
    # Store the token in the dictionary with a value of True
    tokens[token] = True
    return {"token": token}

# Endpoint that requires a one-time token for access
@app.get("/protected_endpoint")
@requires_token
def protected_endpoint():
    return {"message": "Access granted!"}
