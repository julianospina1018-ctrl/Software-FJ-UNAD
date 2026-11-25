"""Administración de las listas y registro de operaciones."""
import logging
from pathlib import Path
from modelos import Cliente, Servicio, Reserva, ErrorFJ, Duplicado, NoEncontrado, NoDisponible, DatoInvalido


def configurar_log(ruta="logs/software_fj.log"):
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("software_fj." + str(ruta.resolve()))
    logger.setLevel(logging.INFO)
    logger.propagate = False
    if not logger.handlers:
        archivo = logging.FileHandler(ruta, encoding="utf-8")
        archivo.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
        logger.addHandler(archivo)
    return logger


class Gestor:
    def __init__(self):
        # Las listas existen solo durante la ejecución.
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def buscar(self, lista, codigo):
        for elemento in lista:
            if elemento.codigo == codigo:
                return elemento
        raise NoEncontrado(f"No existe el código {codigo}")

    def agregar(self, lista, elemento):
        if any(item.codigo == elemento.codigo for item in lista):
            raise Duplicado(f"El código {elemento.codigo} ya existe")
        lista.append(elemento)
        return elemento

    def registrar_cliente(self, documento, nombre, correo, telefono):
        return self.agregar(self.clientes, Cliente(documento, nombre, correo, telefono))

    def registrar_servicio(self, servicio):
        if not isinstance(servicio, Servicio):
            raise DatoInvalido("Se requiere un objeto de tipo Servicio")
        return self.agregar(self.servicios, servicio)

    def crear_reserva(self, codigo, documento, servicio, duracion):
        cliente = self.buscar(self.clientes, documento)
        servicio = self.buscar(self.servicios, servicio)
        if not servicio.disponible:
            raise NoDisponible("El servicio ya está ocupado")
        return self.agregar(self.reservas, Reserva(codigo, cliente, servicio, duracion))

    def confirmar(self, codigo):
        self.buscar(self.reservas, codigo).confirmar()

    def cancelar(self, codigo):
        self.buscar(self.reservas, codigo).cancelar()

    def procesar(self, codigo, impuesto=0, descuento=0):
        return self.buscar(self.reservas, codigo).procesar(impuesto, descuento)


def ejecutar(logger, descripcion, operacion):
    """Captura y registra el error sin detener las siguientes operaciones."""
    try:
        resultado = operacion()
    except ErrorFJ as error:
        logger.exception("%s: %s", descripcion, error)
        return False, error
    except Exception as error:
        # Última barrera para errores inesperados de una operación.
        logger.exception("Error inesperado en %s", descripcion)
        return False, error
    else:
        logger.info("Correcto: %s", descripcion)
        return True, resultado
    finally:
        logger.info("Fin de operación: %s", descripcion)
