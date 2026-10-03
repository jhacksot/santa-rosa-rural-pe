"""Agenda de intervalos de 30 minutos y atenciones administrativas."""
import sqlite3
from datetime import date
from .domain import code, text, slot, day, ValidationError
from .repository import Repository

class AgendaService:
    def __init__(self,repo:Repository,clock=date.today): self.repo,self.clock=repo,clock
    def schedule(self,patient,professional,starts):
        patient,professional,starts=code(patient),text(professional,'Profesional',60).upper(),slot(starts)
        if day(starts[:10])<self.clock(): raise ValidationError('No programe citas en fechas pasadas.')
        if not self.repo.rows('SELECT code FROM patients WHERE code=?',(patient,)):
            raise ValidationError('El paciente no está registrado.')
        try:
            with self.repo.transaction():
                return self.repo.execute('INSERT INTO appointments(patient,professional,starts) VALUES (?,?,?)',(patient,professional,starts)).lastrowid
        except sqlite3.IntegrityError:
            raise ValidationError('Ese profesional o paciente ya tiene una cita en ese horario.') from None
    def list(self):
        return self.repo.rows('SELECT * FROM appointments ORDER BY starts,id')
    def _active(self,identifier):
        rows=self.repo.rows('SELECT * FROM appointments WHERE id=?',(identifier,))
        if not rows or rows[0]['status']!='Programada':
            raise ValidationError('Seleccione una cita programada.')
        return rows[0]
    def reschedule(self,identifier,starts):
        starts=slot(starts)
        if day(starts[:10])<self.clock(): raise ValidationError('No reprograme en fechas pasadas.')
        self._active(identifier)
        try:
            with self.repo.transaction(): self.repo.execute('UPDATE appointments SET starts=? WHERE id=?',(starts,identifier))
        except sqlite3.IntegrityError:
            raise ValidationError('El nuevo horario ya está ocupado.') from None
    def cancel(self,identifier):
        self._active(identifier)
        with self.repo.transaction(): self.repo.execute("UPDATE appointments SET status='Cancelada' WHERE id=?",(identifier,))
    def attend(self,identifier,area):
        area=text(area,'Área',60)
        appointment=self._active(identifier)
        if day(appointment['starts'][:10])>self.clock():
            raise ValidationError('No registre una atención de una cita futura.')
        with self.repo.transaction():
            self.repo.execute('INSERT INTO attentions(appointment,attended,area) VALUES (?,?,?)',(identifier,self.clock().isoformat(),area))
            self.repo.execute("UPDATE appointments SET status='Atendida' WHERE id=?",(identifier,))
    def attentions(self):
        return self.repo.rows('SELECT a.id,c.patient,c.professional,a.attended,a.area FROM attentions a JOIN appointments c ON c.id=a.appointment ORDER BY a.id DESC')
