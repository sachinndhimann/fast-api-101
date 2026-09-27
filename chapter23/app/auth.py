from fastapi import Header, HTTPException, status

def get_current_user(x_user_email: str = Header(...)):
    """Simplified stand-in for chapter 6's real JWT auth, to keep this chapter's focus on testing."""
    if not x_user_email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return {"email": x_user_email}
