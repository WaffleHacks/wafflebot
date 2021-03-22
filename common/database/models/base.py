from abc import ABC
from pydantic import BaseModel
import sqlalchemy
from typing import ClassVar

from ..db import db

ESCAPE_CHARACTERS = ["%", "_"]
FIELD_OPERATORS = {
    "exact": "__eq__",
    "iexact": "ilike",
    "contains": "like",
    "icontains": "ilike",
    "in": "in_",
    "gt": "__gt__",
    "gte": "__ge__",
    "lt": "__lt__",
    "lte": "__le__",
}


def find_primary_key(table: sqlalchemy.Table) -> sqlalchemy.Column:
    """
    Determine the primary key of a SQLAlchemy table
    :param table: the table
    :return: the primary key
    """
    return list(table.primary_key)[0]


class Queryable(object):
    ESCAPE_CHARACTERS = ["%", "_"]

    def __init__(
        self,
        model_cls: "Model" = None,
        filter_clauses=None,
        select_related=None,
        limit_count=None,
        offset=None,
    ):
        self.model_cls = model_cls
        self.filter_clauses = [] if filter_clauses is None else filter_clauses
        self._select_related = [] if select_related is None else select_related
        self.limit_count = limit_count
        self.query_offset = offset

    def __get__(self, instance, owner):
        return self.__class__(model_cls=owner)

    @property
    def database(self):
        return self.model_cls.__database__

    @property
    def table(self):
        return self.model_cls.__table__

    def filter(self, **kwargs):
        """
        Restrict what is returned in a query
        :param kwargs: the query filters
        """
        filter_clauses = self.filter_clauses
        select_related = list(self._select_related)

        if kwargs.get("pk"):
            pk_name = self.model_cls.__primary_key__.name
            kwargs[pk_name] = kwargs.pop("pk")

        for key, value in kwargs.items():
            if "__" in key:
                parts = key.split("__")

                # Check if the final part should be a filter operator or field
                if parts[-1] in FIELD_OPERATORS:
                    op = parts[-1]
                    field_name = parts[-2]
                    related_parts = parts[:-1]
                else:
                    op = "exact"
                    field_name = parts[-1]
                    related_parts = parts[:-1]

                model_cls = self.model_cls
                if related_parts:
                    # Add any implied select_related
                    related_str = "__".join(related_parts)
                    if related_str not in select_related:
                        select_related.append(related_str)

                    # Get the comparison class
                    for part in related_parts:
                        # TODO: fix related to
                        pass

                column = model_cls.__table__.columns[field_name]

            else:
                op = "exact"
                column = self.table.columns[key]

            op_attr = FIELD_OPERATORS[op]
            has_escaped_character = False

            if op in ["contains", "icontains"]:
                has_escaped_character = any(c for c in ESCAPE_CHARACTERS if c in value)
                if has_escaped_character:
                    for char in ESCAPE_CHARACTERS:
                        value = value.replace(char, f"\\{char}")
                value = f"%{value}%"

            if isinstance(value, Model):
                value = getattr(value, value.__primary_key__.name)

            clause = getattr(column, op_attr)(value)
            clause.modifiers["escape"] = "\\" if has_escaped_character else None
            filter_clauses.append(clause)

        return self.__class__(
            model_cls=self.model_cls,
            filter_clauses=filter_clauses,
            select_related=select_related,
            limit_count=self.limit_count,
            offset=self.query_offset,
        )

    def select_related(self, related):
        if not isinstance(related, (list, tuple)):
            related = [related]

        related = list(self._select_related) + related
        return self.__class__(
            model_cls=self.model_cls,
            filter_clauses=self.filter_clauses,
            select_related=related,
            limit_count=self.limit_count,
            offset=self.query_offset,
        )

    def limit(self, limit_count: int):
        """
        Limit how many rows are returned
        :param limit_count: maximum number of rows
        """
        return self.__class__(
            model_cls=self.model_cls,
            filter_clauses=self.filter_clauses,
            select_related=self._select_related,
            limit_count=limit_count,
            offset=self.query_offset,
        )

    def offset(self, offset: int):
        """
        Skip some number of rows
        :param offset: number of rows to skip
        """
        return self.__class__(
            model_cls=self.model_cls,
            filter_clauses=self.filter_clauses,
            select_related=self._select_related,
            limit_count=self.limit_count,
            offset=offset,
        )

    def _build_select_expression(self):
        tables = [self.table]
        select_from = self.table

        for item in self._select_related:
            model_cls = self.model_cls
            select_from = self.table
            for part in item.split("__"):
                # TODO: fix select related
                pass

        expr = sqlalchemy.sql.select(tables)
        expr = expr.select_from(select_from)

        if self.filter_clauses:
            if len(self.filter_clauses) == 1:
                clause = self.filter_clauses[0]
            else:
                clause = sqlalchemy.sql.and_(*self.filter_clauses)
            expr = expr.where(clause)

        if self.limit_count:
            expr = expr.limit(self.limit_count)

        if self.query_offset:
            expr = expr.offset(self.query_offset)

        return expr

    async def count(self) -> int:
        """
        Count the number of rows matching a query
        :return: the number of rows
        """
        expr = self._build_select_expression().alias("subquery_for_count")
        expr = sqlalchemy.func.count().select().select_from(expr)
        return await self.database.fetch_val(expr)

    async def all(self, **kwargs):
        """
        Get all instances of a row
        :param kwargs: query filters
        :return: all matching rows
        """
        if kwargs:
            return await self.filter(**kwargs).all()

        expr = self._build_select_expression()
        rows = await self.database.fetch_all(expr)
        return [self.model_cls.parse_obj(row) for row in rows]

    async def get(self, **kwargs):
        """
        Query for an row
        :param kwargs: the query
        :return: the matching row
        :raises:
            ValueError: when multiple rows match the query
        """
        if kwargs:
            return await self.filter(**kwargs).get()

        expr = self._build_select_expression().limit(2)
        rows = await self.database.fetch_all(expr)

        if not rows:
            return None
        if len(rows) > 1:
            raise ValueError("multiple matches for get query")
        return self.model_cls.parse_obj(rows[0])

    async def first(self, **kwargs):
        """
        Get the first instance of a row
        :param kwargs: query filters
        :return: the first row matching the filters
        """
        if kwargs:
            return await self.filter(**kwargs).first()

        rows = await self.limit(1).all()
        if rows:
            return rows[0]
        return None

    async def create(self, **kwargs):
        """
        Create a new instance of the row
        :param kwargs: the row's fields
        :return: the created row
        """
        # Validate the arguments
        instance = self.model_cls.validate(kwargs)

        # Remove the primary key when none
        primary_key = self.model_cls.__primary_key__
        if kwargs.get(primary_key.name) is None and primary_key.nullable:
            del kwargs[primary_key.name]

        # Build the insert expression
        expression = self.table.insert().values(**kwargs)

        # Execute the insert and set the primary key value (if not provided)
        pk = await self.database.execute(expression)
        if pk is not None:
            instance.set_pk(pk)

        return instance


class Model(BaseModel, ABC):
    __database__ = db
    __table__: sqlalchemy.Table
    __primary_key__: sqlalchemy.Column

    objects: ClassVar[Queryable] = Queryable()

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, *args, **kwargs):
        # Prevent overwriting the primary key
        if "pk" in kwargs:
            kwargs[self.__primary_key__.name] = kwargs.pop("pk")

        super().__init__(*args, **kwargs)

    @property
    def pk(self):
        return getattr(self, self.__primary_key__.name)

    # @pk.setter will not work. See github.com/samuelcolvin/pydantic/issues/1577
    def set_pk(self, value):
        setattr(self, self.__primary_key__.name, value)

    async def update(self, **kwargs):
        """
        Update this rows values
        :param kwargs: the values to update
        """
        # Validate inputs
        kwargs = {key: value for key, value in kwargs.items() if key in self.__fields__}
        validators = self.__validators__
        for key in self.__fields__.keys():
            if key not in kwargs:
                continue

            if key not in validators:
                continue

            for validator in validators[key]:
                validator.func(self.__class__, kwargs[key])

        # Build the update expression
        pk_column = getattr(self.__table__.c, self.__primary_key__.name)
        expr = self.__table__.update()
        expr = expr.values(**kwargs).where(pk_column == self.pk)

        # Perform the update
        await self.__database__.execute(expr)

        # Update the instance
        for key, value in kwargs.items():
            setattr(self, key, value)

    async def delete(self):
        """
        Delete this row from the database
        """
        # Build the delete expression
        pk_column = getattr(self.__table__.c, self.__primary_key__.name)
        expr = self.__table__.delete().where(pk_column == self.pk)

        # Preform the delete
        await self.__database__.execute(expr)

    async def load(self):
        # Build the select expression
        pk_column = getattr(self.__table__.c, self.__primary_key__.name)
        expr = self.__table__.select().where(pk_column == self.pk)

        # Perform the fetch
        row = await self.__database__.fetch_one(expr)
        if row is None:
            raise ValueError(f"row with primary key '{self.pk}' does not exist")

        # Update the instance
        for key, value in dict(row).items():
            setattr(self, key, value)


# TODO: (maybe) implement foreign key one-to-one and one-to-many fields
