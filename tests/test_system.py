"""Pruebas de aceptación y regresión ejecutables con pytest."""
from datetime import date
import sqlite3
import pytest
from santarosa.factory import CentroService,ServiceFactory,seed_demo
from santarosa.repository import SQLiteRepository
from santarosa.security import Vault
from santarosa.domain import ValidationError,Patient,day,quantity

TODAY=date(2026,10,3)
PASSWORD='Prueba-Academica-2026'

@pytest.fixture
def service():
    obj=CentroService(SQLiteRepository(),lambda:TODAY)
    yield obj
    obj.close()

def patient(s): s.patients.register('P001','Paciente ficticio de prueba')
def appointment(s,patient_code='P001',time='09:00'):
    return s.agenda.schedule(patient_code,'PROFESIONAL FICTICIO',f'{TODAY} {time}')

def test_patient_search_case_insensitive(service):
    patient(service)
    assert service.patients.search('FICTICIO')[0]['code']=='P001'
def test_duplicate_patient_rejected(service):
    patient(service)
    with pytest.raises(ValidationError): patient(service)
    assert len(service.patients.search())==1
def test_patient_immutable():
    from dataclasses import FrozenInstanceError
    p=Patient('p01','Ficticio')
    assert p.code=='P01'
    with pytest.raises(FrozenInstanceError): p._name='Cambio'
@pytest.mark.parametrize('value',['','2026-02-30','03-10-2026','2026-1-1'])
def test_invalid_dates(value):
    with pytest.raises(ValidationError): day(value)
@pytest.mark.parametrize('value',['0','-1','1.5','hola',True])
def test_invalid_quantities(value):
    with pytest.raises(ValidationError): quantity(value)
def test_unknown_patient(service):
    with pytest.raises(ValidationError): appointment(service)
def test_professional_conflict(service):
    patient(service);service.patients.register('P002','Ficticio dos');appointment(service)
    with pytest.raises(ValidationError): appointment(service,'P002')
def test_patient_conflict(service):
    patient(service);appointment(service)
    with pytest.raises(ValidationError): service.agenda.schedule('P001','OTRO',f'{TODAY} 09:00')
def test_cancel_releases_slot(service):
    patient(service);a=appointment(service);service.agenda.cancel(a);appointment(service)
    assert service.agenda.list()[0]['status']=='Cancelada'
def test_reschedule(service):
    patient(service);a=appointment(service);service.agenda.reschedule(a,f'{TODAY} 10:30')
    assert service.agenda.list()[0]['starts'].endswith('10:30')
def test_reschedule_conflict_rolls_back(service):
    patient(service);a=appointment(service);appointment(service,time='10:00')
    with pytest.raises(ValidationError): service.agenda.reschedule(a,f'{TODAY} 10:00')
    assert service.agenda.list()[0]['starts'].endswith('09:00')
def test_invalid_half_hour(service):
    patient(service)
    with pytest.raises(ValidationError): appointment(service,time='09:15')
def test_past_appointment(service):
    patient(service)
    with pytest.raises(ValidationError): service.agenda.schedule('P001','Ficticio','2025-01-01 09:00')
def test_future_attention_blocked(service):
    patient(service);a=service.agenda.schedule('P001','Ficticio','2027-01-01 09:00')
    with pytest.raises(ValidationError): service.agenda.attend(a,'General')
def test_attention_once(service):
    patient(service);a=appointment(service);service.agenda.attend(a,'General')
    with pytest.raises(ValidationError): service.agenda.attend(a,'General')
    assert len(service.agenda.attentions())==1
def test_cancelled_attention_blocked(service):
    patient(service);a=appointment(service);service.agenda.cancel(a)
    with pytest.raises(ValidationError): service.agenda.attend(a,'General')
def test_stock_and_movement(service):
    service.inventory.register('L1','Medicamento ficticio','2030-01-01',20)
    service.inventory.move('L1',2,'Salida')
    assert service.inventory.list()[0]['stock']==18
    assert len(service.inventory.movements())==2
def test_insufficient_stock(service):
    service.inventory.register('L1','Ficticio','2030-01-01',20)
    with pytest.raises(ValidationError): service.inventory.move('L1',99,'Salida')
    assert service.inventory.list()[0]['stock']==20
def test_expiry_today_blocks(service):
    service.inventory.register('L1','Ficticio',str(TODAY),20)
    with pytest.raises(ValidationError): service.inventory.move('L1',2,'Salida')
def test_movement_failure_rolls_back(service):
    service.inventory.register('L1','Ficticio','2030-01-01',20)
    service.repo.execute("CREATE TRIGGER fail BEFORE INSERT ON movements BEGIN SELECT RAISE(ABORT,'fallo provocado'); END")
    with pytest.raises(sqlite3.IntegrityError): service.inventory.move('L1',2,'Salida')
    assert service.inventory.list()[0]['stock']==20
def test_alerts_and_report(service):
    seed_demo(service,TODAY)
    assert len(service.inventory.alerts())==2
    assert service.reports.summarize(str(TODAY),str(TODAY))['total']==3
    assert service.reports.summarize('2025-01-01','2025-12-31')['total']==0
def test_report_invalid_range(service):
    with pytest.raises(ValidationError): service.reports.summarize('2026-12-31','2026-01-01')
def test_sql_text_is_data(service):
    service.patients.register('P1',"Ficticio'); DROP TABLE patients;--")
    assert len(service.patients.search())==1
def test_csv_has_no_patient_names(service,tmp_path):
    seed_demo(service,TODAY);f=tmp_path/'report.csv'
    service.reports.export(f,str(TODAY),str(TODAY))
    content=f.read_text(encoding='utf-8-sig')
    assert 'TOTAL,3' in content and 'Paciente' not in content and 'P001' not in content
def test_csv_formula_neutralized(service,tmp_path):
    patient(service);service.agenda.attend(appointment(service),'=1+1');f=tmp_path/'report.csv'
    service.reports.export(f,str(TODAY),str(TODAY))
    assert "'=1+1" in f.read_text(encoding='utf-8-sig')
def test_encryption_persistence_backup(tmp_path):
    path=tmp_path/'test.srdb';s=ServiceFactory.create(path,PASSWORD,lambda:TODAY)
    patient(s);backup=tmp_path/'copy.srdb';s.repo.backup(backup);s.close()
    raw=path.read_bytes()
    assert b'Paciente' not in raw and b'SQLite format' not in raw
    for file in [path,backup]:
        s=ServiceFactory.create(file,PASSWORD,lambda:TODAY)
        assert len(s.patients.search())==1;s.close()
def test_wrong_password(tmp_path):
    path=tmp_path/'test.srdb';s=ServiceFactory.create(path,PASSWORD);s.close()
    with pytest.raises(ValidationError): ServiceFactory.create(path,'Clave-incorrecta')
def test_tampering_detected(tmp_path):
    path=tmp_path/'test.srdb';s=ServiceFactory.create(path,PASSWORD);s.close()
    data=bytearray(path.read_bytes());data[-8]^=1;path.write_bytes(data)
    with pytest.raises(ValidationError): ServiceFactory.create(path,PASSWORD)
def test_disk_failure_rolls_back(tmp_path,monkeypatch):
    s=ServiceFactory.create(tmp_path/'test.srdb',PASSWORD)
    def fail(*args): raise OSError('disco no disponible')
    monkeypatch.setattr(s.repo.vault,'write',fail)
    with pytest.raises(OSError): patient(s)
    assert s.patients.search()==[];s.close()
def test_two_sessions_blocked(tmp_path):
    path=tmp_path/'test.srdb';s=ServiceFactory.create(path,PASSWORD)
    with pytest.raises(ValidationError): ServiceFactory.create(path,PASSWORD)
    s.close()
def test_repository_substitution():
    from santarosa.patients import PatientService
    class Catalog:
        def rows(self,*args): return [{'code':'P9','name':'Alternativo ficticio'}]
    assert PatientService(Catalog()).search('alternativo')[0]['code']=='P9'
