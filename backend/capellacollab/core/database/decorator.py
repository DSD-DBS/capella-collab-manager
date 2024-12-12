# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pydantic
from sqlalchemy import types
from sqlalchemy.dialects import postgresql


class PydanticDecorator(types.TypeDecorator):
    """Maps a pydantic object to a JSONB column and vice versa.

    Use in Database models like this:
    ```py
    json_column: orm.Mapped[pydantic.BaseModel] = orm.mapped_column(PydanticDecorator(pydantic.BaseModel))
    ```

    Replace:
        - `json_column` with the name of the column in the database
        - `pydantic.BaseModel` with the pydantic model you want to use

    When auto-generating a migration, replace the unresolved PydaticDecorator with:
    ```py
    from sqlalchemy.dialects import postgresql

        sa.Column(
            "json_column",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        )
    ```
    """

    impl = postgresql.JSONB
    python_type = pydantic.BaseModel

    cache_ok = True

    def __init__(self, pydantic_model: type[pydantic.BaseModel]):
        super().__init__()
        self.pydantic_model = pydantic_model

    def process_bind_param(self, value, dialect):
        """Convert a pydantic object to JSONB."""
        if value is None:
            return None
        return value.model_dump()

    def process_literal_param(self, value, dialect):
        """Convert a literal pydantic object to JSONB."""
        if value is None:
            return None
        return value.model_dump()

    def process_result_value(self, value, dialect):
        """Convert JSONB to a pydantic object."""
        if value is None:
            return None
        return self.pydantic_model.model_validate(value)


class PydanticDatabaseModel(pydantic.BaseModel):
    """Base class for database models with an ID.

    Use it to extend pydantic models with the database ID field:
    ```py
    class PydanticModel(PydanticSuperModel, decorator.PydanticDatabaseModel):
        pass
    ```
    """

    id: int = pydantic.Field(
        description="Unique identifier of the resource.", ge=1
    )
