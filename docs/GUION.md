# Guion de sustentación

Duración objetivo: 15 minutos y 5 minutos de preguntas. Reparto propuesto, por confirmar por el grupo. Todos deben conocer el proyecto completo.

## Reparto y tiempos

| Tiempo | Contenido | Responsable propuesto |
|---|---|---|
| 0:00-3:00 | Caso, requisitos y comparación de paradigmas | Jhack |
| 3:00-5:30 | UML, Repository, Factory y protección | Josué |
| 5:30-9:30 | Demostración de pacientes, agenda e inventario | José |
| 9:30-13:00 | Pruebas, calidad y riesgos | Wilder |
| 13:00-15:00 | Conclusiones y pendientes reales | Jhack y cierre del equipo |

## Apertura

“Nuestro caso es Santa Rosa, Chugur, tal como aparece en el desafío. Construimos un prototipo académico para organizar pacientes ficticios, citas, atenciones e inventario. La versión funciona de forma local y la probamos técnicamente. No afirmamos haber realizado una validación de campo.”

## Demostración

Seguir el recorrido numerado del README. Abrir una demo nueva antes de ensayar. No usar datos reales. La fecha se genera a partir del día del equipo: revisar que el reloj de Windows sea correcto. Después de una salida, distinguir el saldo del número de movimientos. El total de atenciones solo cambia al registrar una atención, no al reservar una cita.

## Preguntas técnicas para practicar

1. **¿Por qué tres paradigmas?** POO organiza reglas en servicios y entidades; map/filter transforman y seleccionan colecciones; eventos conectan botones con operaciones. Relacionar con RF01, RF05 y RF02.
2. **¿Cómo evitan dos citas en el mismo horario?** Índices únicos por profesional y por paciente sobre citas no canceladas, además del manejo de IntegrityError. Todos los turnos duran 30 minutos.
3. **¿Qué pasa si falla una salida?** Stock y movimiento comparten transacción. Si falla la escritura cifrada, se restaura la instantánea anterior. Test con trigger de fallo comprueba que no quedan descuentos sin movimiento.
4. **¿Dónde está el encapsulamiento?** Patient almacena _code y _name, valida al construir y expone propiedades de solo lectura. frozen impide cambios posteriores; no necesita setters.
5. **¿Qué diferencia hay entre Repository y Factory?** Repository define operaciones de persistencia; Factory construye el conjunto de servicios, repositorio y cifrado. Es fábrica simple, no una jerarquía Factory Method.
6. **¿Dónde se usa SOLID?** Responsabilidad única en archivos y servicios; inversión de dependencias al recibir Repository y reloj. La sustitución se prueba en búsqueda con un catálogo alternativo; no se exagera esa cobertura.
7. **¿Por qué cifrar toda la base?** Para no escribir nombres de prueba ni relaciones en texto plano. SQLite opera en memoria y Vault cifra al guardar. La clave se deriva de contraseña y salt; un respaldo conserva esa contraseña.
8. **¿Es un sistema clínico listo para el centro?** No. Es una demostración con datos ficticios, sin validación de campo, roles diferenciados ni evaluación institucional. El cifrado no certifica cumplimiento legal integral.
9. **¿Cuál es la diferencia entre prueba y validación?** Las 38 pruebas y 15 comprobaciones revisan reglas y operación. Una sesión real con personal evalúa adecuación y facilidad de uso; sigue pendiente.
10. **¿Qué pasa si se pierde la contraseña?** No existe recuperación. Se requiere conservar la contraseña y respaldos de manera segura. La clave pública de demo solo protege registros sintéticos para ensayar.
11. **¿Por qué no hay ventas?** El contexto actual es administrativo de salud. Se controlan entradas y salidas por lote, sin importes ni lógica comercial.
12. **¿Qué mejorarían?** Validación con usuarios, roles y auditoría, cierre por inactividad, medición de volumen y pruebas en el equipo de destino.

## Antes de salir hacia la presentación

- Copiar el EXE y documentos a la laptop y a un USB.
- Abrir el EXE en el equipo que usarán, sin depender de internet.
- Probar demo y tamaño de ventana en el proyector.
- Llevar las diapositivas en PPTX y PDF.
- Revisar el repositorio público y la declaración de IA oficial.
- No prometer entrevistas ni conformidades que todavía no existen.
