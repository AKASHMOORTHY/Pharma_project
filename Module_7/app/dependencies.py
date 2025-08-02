from fastapi import Header, HTTPException

def get_current_role(x_role: str = Header(...)):
    allowed_roles = ["Manager", "Supervisor", "QA", "Storekeeper", "Admin"]
    if x_role not in allowed_roles:
        raise HTTPException(status_code=403, detail="Invalid role")
    return x_role

def role_required(allowed: list):
    allowed = [role.lower() for role in allowed]
    def dependency(x_role: str = Header(...)):
        print(f"DEBUG: x_role header received: {x_role}")
        if x_role.lower() not in allowed:
            raise HTTPException(status_code=403, detail="Access denied for role")
        return x_role
    return dependency
