# General Imports
from __future__ import annotations # For self-referential type-hints
from pathlib import Path
import os
from abc import abstractmethod, ABC
from typing import Union, Any
import json
import sqlite3

# Package Imports
from .path_handling import CONFIG_PATH

class DatabaseEntity(ABC):
    
    def __init__(self, id : Union[int, None] = None, **kwargs) -> None:
        super().__init__()
        self.id = id    # None if not presently in the database, else the internal db id.
    
    @abstractmethod
    def save(self) -> int:
        pass

    @classmethod
    @abstractmethod
    def find(cls, *args, **kwargs) -> list[DatabaseEntity]:
        pass

    @classmethod
    @abstractmethod
    def get(cls, id : int) -> DatabaseEntity:
        pass

    @classmethod
    @abstractmethod
    def delete(cls, id : int) -> None:
        pass

    @classmethod
    @abstractmethod
    def _instantiate_table(cls) -> None:
        pass

    def __eq__(self, other : DatabaseEntity) -> bool:
        return self.id == other.id

class DatabaseHandler():

    def __init__(self) -> None:
        pass

    @classmethod
    @abstractmethod
    def find_one(cls, name : str, **fields) -> tuple(Any):
        pass

    @classmethod
    @abstractmethod
    def find_many(cls, name : str, **fields) -> list(tuple(Any)):
        pass

    @classmethod
    @abstractmethod
    def delete(cls, name : str, id : int) -> bool:
        pass

    @classmethod
    @abstractmethod
    def update(cls, name : str, setfields, **condfields) -> bool:
        pass

    @classmethod
    @abstractmethod
    def insert(cls, name : str, **fields) -> int:
        pass

class SQLiteDatabaseHandler(DatabaseHandler):

    DB_CONNECTION : sqlite3.Connection = None

    def __init__(self) -> None:
        raise RuntimeError("Class cannot be used outside of a static context.")
    
    @classmethod
    def _get_db(cls) -> sqlite3.Connection:
        if not SQLiteDatabaseHandler.DB_CONNECTION:
            with open(CONFIG_PATH, "r") as f:
                cfg = json.load(f)
                DB_PATH = Path(os.path.expanduser(cfg["DB_PATH"]))
                cls.DB_CONNECTION = sqlite3.connect(DB_PATH)
        return cls.DB_CONNECTION
    
    @classmethod
    def _sql_fields_str_builder(cls, fields : dict[str, Any]) -> tuple(str, list(Any)):
        keys = list(fields.keys())
        values = [fields[key] for key in keys]
        sql = ""
        if len(values) > 0:
            sql += f" {keys[0]} = ? "
            for i in range(1, len(values)):
                sql += f"AND {keys[i]} = ? "
        return sql, values

    @classmethod
    def find_one(cls, name, **fields) -> tuple(Any):
        sql, values = cls._sql_fields_str_builder(fields)
        sql = f"SELECT * from {name} WHERE" + sql
        result = cls._get_db().cursor().execute(sql, values).fetchone()
        return result

    @classmethod
    def find_many(cls, name, **fields) -> list(tuple(Any)):
        sql, values = cls._sql_fields_str_builder(fields)
        sql = f"SELECT * from {name} WHERE" + sql
        results = cls._get_db().cursor().execute(sql, values).fetchall()
        return results

    @classmethod
    def delete(cls, name, **fields) -> bool:
        db = cls._get_db()
        cursor = db.cursor()
        sql, values = cls._sql_fields_str_builder(fields)
        sql = f"DELETE FROM {name} WHERE" + sql
        cursor.execute(sql, values)
        db.commit()
        return cursor.rowcount > 0

    @classmethod
    def update(cls, name : str, setfields, **condfields) -> bool:
        db = cls._get_db()
        cursor = db.cursor()
        setsql, setvalues = cls._sql_fields_str_builder(setfields)
        wheresql, wherevalues = cls._sql_fields_str_builder(condfields)
        sql = f"UPDATE {name} SET" + setsql + "WHERE" + wheresql
        values = setvalues + wherevalues
        cursor.execute(sql, values)
        db.commit()
        return cursor.rowcount > 0

    @classmethod
    def insert(cls, name : str, **fields) -> int:
        db = cls._get_db()
        cursor = db.cursor()
        keys = list(fields.keys())
        values = [fields[key] for key in keys]
        # Insert string builder
        sql = f"INSERT INTO {name}("
        values_str = " VALUES("
        for key in keys:
            sql += f"{key},"
            values_str += "?,"
        values_str = values_str[:-1] + ")"
        sql = sql[:-1] + ")" + values_str
        # Insertion
        cursor.execute(sql, values)
        db.commit()
        return cursor.lastrowid