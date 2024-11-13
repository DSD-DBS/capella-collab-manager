# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add environment and session-config to tools

Revision ID: 7683b08b00ba
Revises: 6c4ff61acc8e
Create Date: 2024-02-20 09:24:05.465477

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "7683b08b00ba"
down_revision = "6c4ff61acc8e"
branch_labels = None
depends_on = None

t_tools_old = sa.Table(
    "tools",
    sa.MetaData(),
    sa.Column("id", sa.Integer()),
    sa.Column("integrations", postgresql.JSONB(astext_type=sa.Text())),
)

t_tools_new = sa.Table(
    "tools",
    sa.MetaData(),
    sa.Column("id", sa.Integer()),
    sa.Column("integrations", postgresql.JSONB(astext_type=sa.Text())),
    sa.Column("config", postgresql.JSONB(astext_type=sa.Text())),
)

t_sessions_old = sa.Table(
    "sessions",
    sa.MetaData(),
    sa.Column("id", sa.String()),
    sa.Column("rdp_password", sa.String()),
    sa.Column("guacamole_password", sa.String()),
    sa.Column("guacamole_username", sa.String()),
    sa.Column("guacamole_connection_id", sa.String()),
    sa.Column("tool_id", sa.Integer()),
)

t_sessions_new = sa.Table(
    "sessions",
    sa.MetaData(),
    sa.Column("id", sa.String()),
    sa.Column("connection_method_id", sa.String()),
    sa.Column("tool_id", sa.Integer()),
    sa.Column("environment", postgresql.JSONB(astext_type=sa.Text())),
    sa.Column("config", postgresql.JSONB(astext_type=sa.Text())),
)


def upgrade():
    connection = op.get_bind()
    tools = connection.execute(sa.select(t_tools_old)).mappings().all()
    sessions = connection.execute(sa.select(t_sessions_old)).mappings().all()

    update_tools_columns()
    add_sessions_columns()

    set_tool_session_configuration(tools, connection)
    migrate_old_sessions_columns(sessions, tools, connection)

    drop_session_project_reference()


def update_tools_columns():
    op.add_column(
        "tools",
        sa.Column(
            "config",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )
    op.drop_column("tools", "resources")


def add_sessions_columns():
    op.add_column(
        "sessions",
        sa.Column(
            "connection_method_id",
            sa.String(),
            nullable=False,
            server_default="default",
        ),
    )
    op.add_column(
        "sessions",
        sa.Column(
            "config", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
    )


def get_eclipse_configuration():
    return {
        "resources": {
            "cpu": {"requests": 0.4, "limits": 2},
            "memory": {"requests": "1.6Gi", "limits": "6Gi"},
        },
        "environment": {"RMT_PASSWORD": "{CAPELLACOLLAB_SESSION_TOKEN}"},
        "connection": {
            "methods": [
                {
                    "type": "guacamole",
                    "id": "guacamole",
                    "name": "Guacamole",
                    "description": (
                        "Guacamole doesn't support session sharing."
                    ),
                    "ports": {"metrics": 9118, "rdp": 3389},
                    "environment": {"CONNECTION_METHOD": "xrdp"},
                },
                {
                    "type": "http",
                    "id": "xpra",
                    "name": "Xpra",
                    "description": "Xpra supports session sharing.",
                    "ports": {"http": 10000, "metrics": 9118},
                    "environment": {
                        "CONNECTION_METHOD": "xpra",
                        "XPRA_SUBPATH": "{CAPELLACOLLAB_SESSIONS_BASE_PATH}",
                        "XPRA_CSP_ORIGIN_HOST": "{CAPELLACOLLAB_ORIGIN_BASE_URL}",
                    },
                    "redirect_url": (
                        "{CAPELLACOLLAB_SESSIONS_SCHEME}://{CAPELLACOLLAB_SESSIONS_HOST}:{CAPELLACOLLAB_SESSIONS_PORT}"
                        "{CAPELLACOLLAB_SESSIONS_BASE_PATH}/?floating_menu=0&path={CAPELLACOLLAB_SESSIONS_BASE_PATH}/"
                    ),
                    "cookies": {},
                },
            ]
        },
    }


def get_jupyter_configuration():
    return {
        "resources": {
            "cpu": {"requests": 1, "limits": 2},
            "memory": {"requests": "500Mi", "limits": "3Gi"},
        },
        "environment": {
            "JUPYTER_PORT": "8888",
            "JUPYTER_TOKEN": "{CAPELLACOLLAB_SESSION_TOKEN}",
            "CSP_ORIGIN_HOST": "{CAPELLACOLLAB_ORIGIN_BASE_URL}",
            "JUPYTER_BASE_URL": "{CAPELLACOLLAB_SESSIONS_BASE_PATH}",
        },
        "connection": {
            "methods": [
                {
                    "type": "http",
                    "id": "jupyter",
                    "name": "Direct Jupyter connection (Browser)",
                    "description": "The only available connection method for Jupyter.",
                    "ports": {"http": 8888, "metrics": 9118},
                    "redirect_url": "{CAPELLACOLLAB_SESSIONS_SCHEME}://{CAPELLACOLLAB_SESSIONS_HOST}:{CAPELLACOLLAB_SESSIONS_PORT}{CAPELLACOLLAB_SESSIONS_BASE_PATH}/lab?token={CAPELLACOLLAB_SESSION_TOKEN}",
                },
            ]
        },
    }


def set_tool_session_configuration(tools, connection):
    for tool in tools:
        if tool["integrations"]["jupyter"]:
            configuration = get_jupyter_configuration()
        else:
            configuration = get_eclipse_configuration()
        connection.execute(
            sa.update(t_tools_new)
            .where(t_tools_new.c.id == tool["id"])
            .values(config=configuration)
        )


def migrate_old_sessions_columns(sessions, tools, connection):
    op.drop_column("sessions", "rdp_password")
    op.drop_column("sessions", "guacamole_password")
    op.drop_column("sessions", "host")
    op.drop_column("sessions", "guacamole_username")
    op.drop_column("sessions", "guacamole_connection_id")
    op.drop_column("sessions", "ports")

    for session in sessions:
        tool = get_tool_by_id(tools, session["tool_id"])
        if tool["integrations"]["jupyter"]:
            connection.execute(
                sa.update(t_sessions_new)
                .where(t_sessions_new.c.id == session["id"])
                .values(
                    connection_method_id="jupyter",
                )
            )
        else:
            connection.execute(
                sa.update(t_sessions_new)
                .where(t_sessions_new.c.id == session["id"])
                .values(
                    environment=session.get("environment", {})
                    | {
                        "CAPELLACOLLAB_SESSION_TOKEN": session["rdp_password"],
                    },
                    config={
                        "guacamole_username": session["guacamole_username"],
                        "guacamole_password": session["guacamole_password"],
                        "guacamole_connection_id": session[
                            "guacamole_connection_id"
                        ],
                    },
                    connection_method_id="guacamole",
                )
            )


def get_tool_by_id(tools, tool_id):
    for tool in tools:
        if tool["id"] == tool_id:
            return tool
    return None


def drop_session_project_reference():
    op.drop_constraint(
        "sessions_project_id_fkey", "sessions", type_="foreignkey"
    )
    op.drop_column("sessions", "project_id")
