"""Cifrado autenticado de la base completa y escritura atómica en disco."""
import base64
import os
import tempfile
from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from .domain import ValidationError

MAGIC=b'SANTAROSA1\n'

class Vault:
    def __init__(self, path, password):
        self.path=Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if len(password)<10:
            raise ValidationError('La contraseña debe tener al menos 10 caracteres.')
        raw=self.path.read_bytes() if self.path.exists() else None
        if raw and (not raw.startswith(MAGIC) or len(raw)<len(MAGIC)+17):
            raise ValidationError('El archivo no es una base Santa Rosa válida.')
        self.salt=raw[len(MAGIC):len(MAGIC)+16] if raw else os.urandom(16)
        key=PBKDF2HMAC(algorithm=hashes.SHA256(),length=32,salt=self.salt,iterations=600000).derive(password.encode('utf-8'))
        self._cipher=Fernet(base64.urlsafe_b64encode(key))
        self.initial=None
        if raw:
            try:
                self.initial=self._cipher.decrypt(raw[len(MAGIC)+16:])
            except InvalidToken:
                raise ValidationError('Contraseña incorrecta o archivo alterado.') from None

    def write(self, data, target=None):
        destination=Path(target) if target else self.path
        destination.parent.mkdir(parents=True,exist_ok=True)
        payload=MAGIC+self.salt+self._cipher.encrypt(data)
        handle,tmp=tempfile.mkstemp(prefix='santarosa-',suffix='.tmp',dir=destination.parent)
        try:
            with os.fdopen(handle,'wb') as f:
                f.write(payload);f.flush();os.fsync(f.fileno())
            os.replace(tmp,destination)
        finally:
            if os.path.exists(tmp): os.unlink(tmp)

class SessionLock:
    """Impide dos escritores del mismo archivo en Windows. El SO libera al salir."""
    def __init__(self,path):
        import msvcrt
        self._file=open(str(path)+'.lock','a+b')
        self._file.seek(0);self._file.write(b'0');self._file.flush();self._file.seek(0)
        try:
            msvcrt.locking(self._file.fileno(),msvcrt.LK_NBLCK,1)
        except OSError:
            self._file.close()
            raise ValidationError('Esta base ya está abierta. Cierre la otra ventana.') from None
    def close(self):
        if not self._file.closed:
            import msvcrt
            self._file.seek(0);msvcrt.locking(self._file.fileno(),msvcrt.LK_UNLCK,1);self._file.close()
