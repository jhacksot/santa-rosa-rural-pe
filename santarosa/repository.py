"""Contrato de persistencia y adaptador SQLite en memoria con disco cifrado."""
from abc import ABC, abstractmethod
from contextlib import contextmanager
import sqlite3
from .domain import ValidationError

SCHEMA='''
CREATE TABLE IF NOT EXISTS patients(code TEXT PRIMARY KEY,name TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS appointments(
 id INTEGER PRIMARY KEY,patient TEXT NOT NULL REFERENCES patients(code),
 professional TEXT NOT NULL,starts TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'Programada'
 CHECK(status IN ('Programada','Cancelada','Atendida')));
CREATE UNIQUE INDEX IF NOT EXISTS professional_slot ON appointments(professional,starts) WHERE status!='Cancelada';
CREATE UNIQUE INDEX IF NOT EXISTS patient_slot ON appointments(patient,starts) WHERE status!='Cancelada';
CREATE TABLE IF NOT EXISTS attentions(
 id INTEGER PRIMARY KEY,appointment INTEGER UNIQUE NOT NULL REFERENCES appointments(id),
 attended TEXT NOT NULL,area TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS lots(
 code TEXT PRIMARY KEY,product TEXT NOT NULL,expires TEXT NOT NULL,stock INTEGER NOT NULL CHECK(stock>=0));
CREATE TABLE IF NOT EXISTS movements(
 id INTEGER PRIMARY KEY,lot TEXT NOT NULL REFERENCES lots(code),kind TEXT NOT NULL,
 amount INTEGER NOT NULL CHECK(amount>0),created TEXT NOT NULL);
'''

class Repository(ABC):
    @abstractmethod
    def rows(self,sql,params=()): pass
    @abstractmethod
    def execute(self,sql,params=()): pass
    @abstractmethod
    def transaction(self): pass

class SQLiteRepository(Repository):
    def __init__(self,vault=None):
        self.vault=vault
        self._db=sqlite3.connect(':memory:',isolation_level=None)
        self._db.row_factory=sqlite3.Row
        if vault and vault.initial:
            self._db.deserialize(vault.initial)
        self._db.execute('PRAGMA foreign_keys=ON')
        self._db.executescript(SCHEMA)
        if self._db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':
            raise ValidationError('La base no supera la comprobación de integridad.')
        if vault and not vault.initial: vault.write(self._db.serialize())
    def rows(self,sql,params=()):
        return [dict(row) for row in self._db.execute(sql,params).fetchall()]
    def execute(self,sql,params=()):
        return self._db.execute(sql,params)
    @contextmanager
    def transaction(self):
        before=self._db.serialize()
        self._db.execute('BEGIN IMMEDIATE')
        try:
            yield
            self._db.execute('COMMIT')
            if self.vault: self.vault.write(self._db.serialize())
        except Exception:
            if self._db.in_transaction: self._db.execute('ROLLBACK')
            self._db.deserialize(before)
            self._db.execute('PRAGMA foreign_keys=ON')
            raise
    def backup(self,path):
        if not self.vault: raise ValidationError('Esta sesión no tiene archivo cifrado.')
        if str(self.vault.path.resolve())==str(__import__('pathlib').Path(path).resolve()):
            raise ValidationError('Guarde el respaldo con otro nombre.')
        self.vault.write(self._db.serialize(),path)
    def close(self): self._db.close()
