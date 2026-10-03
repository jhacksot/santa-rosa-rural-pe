"""Registro y búsqueda de pacientes ficticios."""
import sqlite3
from .domain import Patient, ValidationError
from .repository import Repository

class PatientService:
    def __init__(self,repo:Repository): self.repo=repo
    def register(self,identifier,name):
        patient=Patient(identifier,name)
        try:
            with self.repo.transaction():
                self.repo.execute('INSERT INTO patients VALUES (?,?)',(patient.code,patient.name))
        except sqlite3.IntegrityError:
            raise ValidationError('Ya existe un paciente con ese código.') from None
    def search(self,query=''):
        term=query.strip().casefold()
        return list(filter(lambda row: term in row['code'].casefold() or term in row['name'].casefold(),
                           self.repo.rows('SELECT * FROM patients ORDER BY code')))
