# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from sqlalchemy.orm import Session

from capellacollab.users.models import DatabaseUser, Role


def find_or_create_user(db: Session, username: str):
    user = get_user(db, username)
    if user:
        return user

    return create_user(db, username)


def get_user(db: Session, username: str) -> DatabaseUser | None:
    return db.query(DatabaseUser).filter(DatabaseUser.name == username).first()


def get_user_by_id(db: Session, user_id: int) -> DatabaseUser | None:
    return db.query(DatabaseUser).filter(DatabaseUser.id == user_id).first()


def get_all_users(db: Session) -> list[DatabaseUser]:
    return db.query(DatabaseUser).all()


def create_user(db: Session, username: str, role: Role = Role.USER):
    user = DatabaseUser(
        name=username,
        role=role,
        projects=[],
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_role_of_user(db: Session, user_id: int, role: Role):
    user = get_user_by_id(db, user_id)
    user.role = role
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int):
    db.query(DatabaseUser).filter(DatabaseUser.id == user_id).delete()
    db.commit()
