# Sistema Rural-PE: Santa Rosa

Prototipo académico para pacientes ficticios, citas, atenciones administrativas, inventario, alertas y reportes. Caso Santa Rosa, Chugur, tomado del enunciado UAIN1288P. No es un sistema clínico ni tiene validación de campo.

## Ejecutar para presentar

En Windows de 64 bits, abrir `SantaRosa.exe` con doble clic. No requiere instalar Python ni conectarse a internet. Seleccionar **Abrir demostración con datos de ejemplo**. Cada apertura de demostración crea una sesión independiente: 4 pacientes, 4 citas, 3 atenciones y 3 lotes.

Se probó en Windows 11 de 64 bits. La compatibilidad con otros equipos debe comprobarse antes de exponer. El ejecutable no tiene firma digital comercial. No se debe desactivar el antivirus. Si el equipo institucional impide ejecutables no firmados, solicitar autorización al responsable y usar las capturas incluidas como apoyo.

## Guardar práctica

Escribir una contraseña de al menos 10 caracteres y pulsar **Crear o abrir mi práctica**. Se guarda en `%LOCALAPPDATA%/SantaRosaAcademico/practica.srdb`. La misma contraseña abre esa práctica después. No existe recuperación de contraseña. Usar exclusivamente datos ficticios.

**Respaldo cifrado** crea una copia independiente. Para abrirla: cerrar sesión, introducir su contraseña y elegir **Abrir respaldo cifrado**. Una copia abierta se puede modificar; conservar otra copia intacta. Los respaldos de demostración usan la clave pública `SantaRosa-Demo-2026`, solo para datos sintéticos. Los de práctica usan la contraseña elegida por el usuario.

## Recorrido de exposición (5 minutos)

1. Abrir la demo. Pacientes: registrar `P005` y `Paciente ficticio cinco`. Buscar `cinco`. Intentar repetir el código para mostrar el rechazo.
2. Citas: programar `P005`, `Profesional de demostración`, fecha de hoy a las `15:00`. Repetir para mostrar conflicto. Seleccionar esa fila y reprogramar a `15:30`.
3. Atenciones: registrar cita `4`, área `Medicina general`. El total pasa de 3 a 4.
4. Medicamentos: seleccionar `L001`, escribir `2` en Unidades y pulsar Salida. El saldo pasa de 20 a 18. Intentar 99 y mostrar el bloqueo. No confundir Registrar lote con Entrada a seleccionado.
5. Alertas: mostrar L002 próximo a vencer y L003 vencido. Intentar salida de L003 para mostrar bloqueo.
6. Reportes: consultar hoy, mostrar 4 atenciones y exportar CSV. El CSV tiene totales por área, sin nombres ni códigos de pacientes.
7. Crear respaldo. Cerrar sesión y abrirlo con la clave de demo para demostrar persistencia.

## Desarrollo y pruebas

Python 3.12 de 64 bits con Tcl/Tk:

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements-dev.txt
.venv/Scripts/python main.py
.venv/Scripts/python -m pytest -v
.venv/Scripts/python main.py --self-check docs/ensayo_local --screenshots
.venv/Scripts/python -m PyInstaller --onefile --windowed --name SantaRosa main.py
```

`tests/test_system.py` contiene 38 casos ejecutados con pytest. `docs/ensayo_exe/resultado_ejecutable.json` registra 15 comprobaciones del EXE. Son pruebas automatizadas, no validación con usuarios. No se declara TDD: se desarrolló el módulo y después se añadieron pruebas de aceptación y regresión.

## Diseño y seguridad

- Repository: `Repository` define el contrato y `SQLiteRepository` realiza persistencia.
- Factory: `ServiceFactory` construye servicios y dependencias en un solo punto.
- POO: entidad `Patient` inmutable con propiedades; servicios separados por función.
- Funcional: `filter` para búsqueda y `map` más `filter` para alertas y reportes.
- Eventos: botones Tkinter llaman a servicios y actualizan tablas.
- La base SQLite vive en memoria. Se serializa y cifra completa con Fernet, con clave derivada de contraseña mediante PBKDF2-HMAC-SHA256 (600000 iteraciones, salt aleatorio de 16 bytes). La escritura usa reemplazo atómico. Los respaldos también se cifran.
- Hay bloqueo de una sesión por archivo. No se declara soporte multiusuario ni cifrado de la memoria. Una sesión abierta permite leer datos; se cierra manualmente. No hay roles diferenciados ni cierre por inactividad. El equipo podría paginar memoria: no usar datos reales.
- Reportes CSV neutralizan fórmulas y solo incluyen cantidades por área. No se recogen diagnósticos, DNI ni teléfonos.
- El programa no certifica cumplimiento integral de la Ley 29733. Un despliegue real requiere revisión institucional, base jurídica, controles operativos y evaluación de seguridad.

## Entrega y autoría

Grupo 1: Jhack Anderson Soto Chilon, Josué Alexander Gamboa Otero, José Bacón Hilario y Wilder Manuel Abanto Espinoza.

El desarrollo de esta versión utilizó Codex para código, pruebas, empaquetado y documentación. El historial local identifica a Codex; las cargas públicas se realizaron desde la cuenta del equipo con esta asistencia. Ambos conservan fechas reales. Los integrantes deben revisar, comprender y declarar el uso de IA con el formato oficial del aula. No se atribuyen entrevistas ni pruebas de campo inexistentes.

Repositorio público: https://github.com/jhacksot/santa-rosa-rural-pe. Su historial registra la publicación por módulos mediante commits descriptivos en español. El paquete de entrega incluye además `SantaRosa_desarrollo.bundle`, con el historial local de implementación; es un historial independiente, no una copia de la rama pública. Para recuperarlo: `git clone SantaRosa_desarrollo.bundle santa-rosa`. Los archivos y evidencias contienen exclusivamente datos sintéticos.

