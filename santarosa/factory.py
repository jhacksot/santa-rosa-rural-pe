"""Factory centraliza la construcción y la inyección de dependencias."""
from datetime import date,timedelta
from .security import Vault,SessionLock
from .repository import SQLiteRepository
from .patients import PatientService
from .agenda import AgendaService
from .inventory import InventoryService
from .reports import ReportService

class CentroService:
    def __init__(self,repo,clock=date.today,lock=None):
        self.repo,self.lock=repo,lock
        self.patients=PatientService(repo)
        self.agenda=AgendaService(repo,clock)
        self.inventory=InventoryService(repo,clock)
        self.reports=ReportService(repo)
    def close(self):
        self.repo.close()
        if self.lock: self.lock.close()

class ServiceFactory:
    @staticmethod
    def create(path,password,clock=date.today):
        from pathlib import Path
        Path(path).parent.mkdir(parents=True,exist_ok=True)
        lock=SessionLock(path)
        try: return CentroService(SQLiteRepository(Vault(path,password)),clock,lock)
        except Exception:
            lock.close();raise

def seed_demo(service,today=None):
    today=today or date.today()
    if service.patients.search(): return
    for i in range(1,5): service.patients.register(f'P{i:03}',f'Paciente ficticio {i:02}')
    for i in range(1,4):
        identifier=service.agenda.schedule(f'P{i:03}','Profesional de demostración',f'{today} {8+i:02}:00')
        service.agenda.attend(identifier,'Medicina general' if i<3 else 'Enfermería')
    service.agenda.schedule('P004','Profesional de demostración',f'{today} 14:00')
    service.inventory.register('L001','Medicamento ficticio A',(today+timedelta(days=365)).isoformat(),20)
    service.inventory.register('L002','Medicamento ficticio B',(today+timedelta(days=15)).isoformat(),4)
    service.inventory.register('L003','Medicamento ficticio C',(today-timedelta(days=1)).isoformat(),3)
