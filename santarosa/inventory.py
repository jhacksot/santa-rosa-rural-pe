"""Movimientos de medicamentos por lote, sin ventas ni importes comerciales."""
from datetime import date
import sqlite3
from .domain import code,text,day,quantity,ValidationError
from .repository import Repository

class InventoryService:
    def __init__(self,repo:Repository,clock=date.today): self.repo,self.clock=repo,clock
    def register(self,identifier,product,expires,stock):
        identifier,product=code(identifier),text(product,'Medicamento')
        expires,stock=day(expires).isoformat(),quantity(stock)
        try:
            with self.repo.transaction():
                self.repo.execute('INSERT INTO lots VALUES (?,?,?,?)',(identifier,product,expires,stock))
                self.repo.execute('INSERT INTO movements(lot,kind,amount,created) VALUES (?,?,?,?)',(identifier,'Entrada',stock,self.clock().isoformat()))
        except sqlite3.IntegrityError:
            raise ValidationError('Ya existe ese lote. Use Entrada para agregar unidades.') from None
    def list(self): return self.repo.rows('SELECT * FROM lots ORDER BY expires,code')
    def move(self,identifier,amount,kind):
        identifier,amount=code(identifier),quantity(amount)
        if kind not in ('Entrada','Salida'): raise ValidationError('Movimiento desconocido.')
        with self.repo.transaction():
            rows=self.repo.rows('SELECT * FROM lots WHERE code=?',(identifier,))
            if not rows: raise ValidationError('Lote inexistente.')
            lot=rows[0]
            if kind=='Salida':
                if day(lot['expires'])<=self.clock(): raise ValidationError('Lote vencido: no se permite la salida.')
                if amount>lot['stock']: raise ValidationError('Stock insuficiente.')
            self.repo.execute('UPDATE lots SET stock=stock+? WHERE code=?',(amount if kind=='Entrada' else -amount,identifier))
            self.repo.execute('INSERT INTO movements(lot,kind,amount,created) VALUES (?,?,?,?)',(identifier,kind,amount,self.clock().isoformat()))
    def alerts(self,threshold=5,horizon=30):
        threshold,horizon=quantity(threshold,zero=True),quantity(horizon,zero=True)
        def decorate(row):
            days=(day(row['expires'])-self.clock()).days
            reasons=[]
            if row['stock']<=threshold: reasons.append('Stock bajo')
            if days<=0: reasons.append('Vencido')
            elif days<=horizon: reasons.append('Próximo a vencer')
            return {**row,'alert':', '.join(reasons)}
        return list(filter(lambda row: bool(row['alert']),map(decorate,self.list())))
    def movements(self): return self.repo.rows('SELECT * FROM movements ORDER BY id DESC')
