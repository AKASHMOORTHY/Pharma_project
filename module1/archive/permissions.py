from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from typing import List

SECRET_KEY = "your-secret-key"  #Make sure this matches your JWT setup


#Factory function: returns a dependency that checks role.

def role_required(allowed_roles: List[str]):
    def verify_role(request: Request):
        auth = HTTPBearer()
        credentials: HTTPAuthorizationCredentials = auth(request)
        token = credentials.credentials

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_role = payload.get("role")
            if user_role not in allowed_roles:
                raise HTTPException(status_code=403, detail="Access denied: Role not allowed")
        except Exception:
            raise HTTPException(status_code=403, detail="Invalid or expired token")

    return verify_role