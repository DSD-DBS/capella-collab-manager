# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

def get_existing_session(
    session_id: str,
    db: orm.Session = fastapi.Depends(database.get_db),
    username: str = fastapi.Depends(auth_injectables.get_username),
) -> models.DatabaseSession:
    if not (session := crud.get_session_by_id(db, session_id)):
        raise fastapi.HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "reason": f"The session with id {session_id} was not found."
            },
        )
    if not (
        session.owner_name == username
        or auth_injectables.RoleVerification(
            required_role=users_models.Role.ADMIN, verify=False
        )(username, db)
    ):
        raise fastapi.HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "reason": f"The session with id {session.id} does not belong to your user. Only administrators can manage other sessions!"
            },
        )

    return session
