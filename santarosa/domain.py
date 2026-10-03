"""Entidades inmutables y validaciones compartidas del dominio."""
from dataclasses import dataclass
from datetime import date, datetime
import re

class ValidationError(ValueError):
    """Una regla de negocio impide completar la operación."""

def text(value, label, maximum=100):
    value = str(value).strip()
    if not value or len(value) > maximum:
        raise ValidationError(f'{label}: ingrese entre 1 y {maximum} caracteres.')
    return value

def code(value):
    value = str(value).strip().upper()
    if not re.fullmatch(r'[A-Z0-9-]{1,20}', value):
        raise ValidationError('Código: use de 1 a 20 letras, números o guiones.')
    return value

def day(value):
    try:
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', str(value)):
            raise ValueError()
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        raise ValidationError('Fecha inválida. Use AAAA-MM-DD.') from None

def slot(value):
    try:
        parsed = datetime.strptime(value, '%Y-%m-%d %H:%M')
        if parsed.strftime('%Y-%m-%d %H:%M') != value or parsed.minute not in (0,30):
            raise ValueError()
        return value
    except (ValueError, TypeError):
        raise ValidationError('Cita: use AAAA-MM-DD HH:MM, en intervalos de 30 minutos.') from None

def quantity(value, zero=False):
    if isinstance(value, bool) or not re.fullmatch(r'\d{1,8}', str(value)):
        raise ValidationError('Cantidad: ingrese un número entero positivo.')
    number=int(value)
    if number < (0 if zero else 1):
        raise ValidationError('La cantidad debe ser mayor que cero.')
    return number

@dataclass(frozen=True)
class Patient:
    """Encapsula un registro mínimo y evita cambios que omitan validación."""
    _code: str
    _name: str
    def __post_init__(self):
        object.__setattr__(self,'_code',code(self._code))
        object.__setattr__(self,'_name',text(self._name,'Nombre ficticio'))
    @property
    def code(self): return self._code
    @property
    def name(self): return self._name
