# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from datetime import datetime

from sqlalchemy.orm import Session

from capellacollab.users.models import DatabaseUser, Role


def get_user_by_name(db: Session, username: str) -> DatabaseUser:
    return db.query(DatabaseUser).filter(DatabaseUser.name == username).first()


def get_user_by_id(db: Session, user_id: int) -> DatabaseUser:
    return db.query(DatabaseUser).filter(DatabaseUser.id == user_id).first()


def get_users(db: Session) -> list[DatabaseUser]:
    return db.query(DatabaseUser).all()


def create_user(
    db: Session,
    username: str,
    role: Role = Role.USER,
) -> DatabaseUser:
    user = DatabaseUser(
        name=username,
        role=role,
        created=datetime.now(),
        projects=[],
        events=[],
    )
    db.add(user)
    db.commit()

    return user


def update_role_of_user(
    db: Session, user: DatabaseUser, role: Role
) -> DatabaseUser:
    user.role = role
    db.commit()
    return user


def update_last_login(
    db: Session, user: DatabaseUser, last_login: datetime | None = None
) -> DatabaseUser:
    if not last_login:
        last_login = datetime.now()
    user.last_login = last_login
    db.commit()
    return user


def delete_user(db: Session, user: DatabaseUser):
    db.delete(user)
    db.commit()
