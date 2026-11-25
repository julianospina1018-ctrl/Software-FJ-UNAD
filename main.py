"""Menú de consola del ejercicio Software FJ."""
from modelos import Sala, Equipo, Asesoria
from gestor import Gestor, configurar_log, ejecutar
from simulaciones import simular


def alta_cliente(g):
    return g.registrar_cliente(input("Documento: "), input("Nombre: "),
                               input("Correo: "), input("Teléfono: "))


def alta_servicio(g):
    tipo = input("Tipo (1 sala, 2 equipo, 3 asesoría): ")
    clases = {"1": (Sala, "Capacidad"), "2": (Equipo, "Tipo de equipo"),
              "3": (Asesoria, "Especialidad")}
    if tipo not in clases:
        from modelos import DatoInvalido
        raise DatoInvalido("Tipo de servicio incorrecto")
    clase, campo = clases[tipo]
    codigo = input("Código: ")
    nombre = input("Nombre: ")
    tarifa = input("Tarifa por hora o día: ")
    return g.registrar_servicio(clase(codigo, nombre, tarifa, input(campo + ": ")))


def alta_reserva(g):
    return g.crear_reserva(input("Código de reserva: "), input("Documento del cliente: "),
                          input("Código de servicio: "), input("Duración (horas o días): "))


def listar(elementos):
    if not elementos:
        print("No hay registros.")
    for elemento in elementos:
        print(elemento.describir())


def main():
    logger = configurar_log()
    g = Gestor()
    opciones = {
        "1": ("Registrar cliente", lambda: alta_cliente(g)),
        "2": ("Listar clientes", lambda: listar(g.clientes)),
        "3": ("Registrar servicio", lambda: alta_servicio(g)),
        "4": ("Listar servicios", lambda: listar(g.servicios)),
        "5": ("Crear reserva", lambda: alta_reserva(g)),
        "6": ("Confirmar reserva", lambda: g.confirmar(input("Código: "))),
        "7": ("Cancelar reserva", lambda: g.cancelar(input("Código: "))),
        "8": ("Procesar reserva", lambda: g.procesar(input("Código: "), input("Impuesto (%): "), input("Descuento (%): "))),
        "9": ("Listar reservas", lambda: listar(g.reservas)),
        "10": ("Ejecutar simulaciones", lambda: simular(logger)),
    }
    while True:
        print("\n=== SOFTWARE FJ ===")
        for clave, (nombre, _) in opciones.items():
            print(f"{clave}. {nombre}")
        print("0. Salir")
        try:
            opcion = input("Seleccione: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nFin de la sesión.")
            break
        if opcion == "0":
            break
        if opcion not in opciones:
            logger.warning("Opción inválida del menú")
            print("Opción no válida.")
            continue
        nombre, accion = opciones[opcion]
        exito, resultado = ejecutar(logger, nombre, accion)
        if not exito:
            print("Error:", resultado)
        elif hasattr(resultado, "describir"):
            print(resultado.describir())
        elif isinstance(resultado, float):
            print(f"Total: {resultado:,.2f} COP")
        else:
            print("Operación terminada.")


if __name__ == "__main__":
    main()
