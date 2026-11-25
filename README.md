# Software FJ

Proyecto de la Fase 4 (prácticas simuladas) de Programación, código 213023, UNAD.

La empresa ficticia Software FJ necesita gestionar clientes, reservas de salas, alquiler de equipos y asesorías. El programa utiliza listas y objetos, sin base de datos. El único archivo de datos generado es el registro de eventos y errores.

## Cómo ejecutar

Requiere Python 3.10 o posterior. No hay paquetes externos.

```bash
python main.py
python simulaciones.py
python -m unittest -v
```

El primer comando abre el menú. El segundo ejecuta 25 casos correctos e incorrectos y el tercero comprueba el comportamiento del programa con 30 pruebas unitarias. El resultado de las pruebas debe comprobarse ejecutándolas; los números indican los casos incluidos, no resultados certificados.

El log se crea en `logs/software_fj.log`. Los datos de ejemplo son ficticios y se pierden al cerrar el programa.

## Archivos

- `modelos.py`: entidades abstractas, cliente, servicios, reserva, validaciones y excepciones.
- `gestor.py`: listas, búsqueda, registro de objetos y control de errores.
- `main.py`: menú de consola.
- `simulaciones.py`: demostración de operaciones válidas e inválidas.
- `test_software_fj.py`: pruebas unitarias.

## Decisiones del ejercicio

La sala y la asesoría se cobran por horas; los equipos se cobran por días completos. Las tarifas son ficticias y se expresan en COP. Los porcentajes de impuesto y descuento se introducen como números entre 0 y 100. No se simula un calendario: un servicio queda ocupado al confirmar una reserva y se libera al cancelar o procesar esa reserva.

Se emplea la clase abstracta Entidad y la clase abstracta Servicio. Sala, Equipo y Asesoria sobrescriben los métodos de validación, costo base y descripción. Las variantes del cálculo se resuelven con parámetros opcionales, ya que Python no admite la sobrecarga tradicional por firma.

Los errores personalizados se capturan en el gestor y se registran junto con los eventos exitosos. Se utilizan try/except, else, finally y encadenamiento con raise ... from.

## Contexto académico

Propuesta individual de recuperación de la actividad después del cierre del foro. La guía exige trabajo en equipo; no se presentan aportes de compañeros inexistentes. Código preparado con apoyo de ChatGPT para revisión, ejecución y comprensión por parte del estudiante. La aceptación de la entrega individual queda a criterio del tutor.

Base del ejercicio: Anexo 3 – Problema a desarrollar Fase 4 y guía del componente práctico (UNAD). Como referencia de lenguaje, consultar el [tutorial de errores y excepciones de Python](https://docs.python.org/es/3.12/tutorial/errors.html).
