"""Casos de prueba con datos ficticios."""
from modelos import Sala, Equipo, Asesoria
from gestor import Gestor, configurar_log, ejecutar


def simular(logger=None):
    logger = logger or configurar_log()
    g = Gestor()
    # Cada caso indica si debe funcionar (True) o rechazarse (False).
    casos = [
        ("Cliente válido", True, lambda: g.registrar_cliente("10001", "Ana Pérez", "ana@example.com", "3001234567")),
        ("Cliente con correo incorrecto", False, lambda: g.registrar_cliente("10002", "Luis Díaz", "correo", "3001112222")),
        ("Cliente duplicado", False, lambda: g.registrar_cliente("10001", "Ana Pérez", "ana@example.com", "3001234567")),
        ("Segundo cliente válido", True, lambda: g.registrar_cliente("10003", "Luis Díaz", "luis@example.com", "3001112222")),
        ("Registrar sala", True, lambda: g.registrar_servicio(Sala("S1", "Sala principal", 50000, 12))),
        ("Tarifa negativa", False, lambda: g.registrar_servicio(Sala("S2", "Sala auxiliar", -10, 8))),
        ("Registrar equipo", True, lambda: g.registrar_servicio(Equipo("E1", "Portátil", 80000, "Computación"))),
        ("Registrar asesoría", True, lambda: g.registrar_servicio(Asesoria("A1", "Consultoría", 100000, "Software"))),
        ("Servicio con parámetro faltante", False, lambda: g.registrar_servicio(Asesoria("A2", "Consultoría", 100000, ""))),
        ("Reserva de sala", True, lambda: g.crear_reserva("R1", "10001", "S1", 2)),
        ("Confirmar reserva", True, lambda: g.confirmar("R1")),
        ("Servicio ocupado", False, lambda: g.crear_reserva("R2", "10003", "S1", 1)),
        ("Confirmar dos veces", False, lambda: g.confirmar("R1")),
        ("Descuento inválido", False, lambda: g.procesar("R1", 19, 120)),
        ("Procesar reserva con impuesto y descuento", True, lambda: g.procesar("R1", 19, 10)),
        ("Reserva de equipo", True, lambda: g.crear_reserva("R3", "10003", "E1", 3)),
        ("Procesar sin confirmar", False, lambda: g.procesar("R3")),
        ("Confirmar equipo", True, lambda: g.confirmar("R3")),
        ("Cancelar equipo", True, lambda: g.cancelar("R3")),
        ("Volver a reservar equipo", True, lambda: g.crear_reserva("R4", "10001", "E1", 1)),
        ("Asesoría con duración incorrecta", False, lambda: g.crear_reserva("R5", "10001", "A1", 0)),
        ("Cliente inexistente", False, lambda: g.crear_reserva("R6", "99999", "A1", 1)),
        ("Asesoría válida", True, lambda: g.crear_reserva("R7", "10001", "A1", 2)),
        ("Confirmar asesoría", True, lambda: g.confirmar("R7")),
        ("Procesar asesoría", True, lambda: g.procesar("R7")),
    ]
    correctos = 0
    print("\n--- Simulación Software FJ ---")
    for indice, (nombre, esperado, accion) in enumerate(casos, 1):
        exito, resultado = ejecutar(logger, nombre, accion)
        coincide = exito == esperado
        correctos += int(coincide)
        detalle = "Operación aceptada" if exito else str(resultado)
        print(f"{indice:02d}. {nombre}: {'OK' if coincide else 'REVISAR'} - {detalle}")
    print(f"Resultado: {correctos}/{len(casos)} casos coinciden con lo esperado.")
    return correctos, len(casos)


if __name__ == "__main__":
    correctos, total = simular()
    raise SystemExit(0 if correctos == total else 1)
