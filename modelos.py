"""Clases del ejercicio Software FJ (Programación, fase 4)."""
from abc import ABC, abstractmethod
import math
import re


class ErrorFJ(Exception):
    """Error general de la aplicación."""


class DatoInvalido(ErrorFJ):
    pass


class NoDisponible(ErrorFJ):
    pass


class EstadoIncorrecto(ErrorFJ):
    pass


class NoEncontrado(ErrorFJ):
    pass


class Duplicado(ErrorFJ):
    pass


def texto(valor, campo):
    # Evita valores vacíos y datos de tipo incorrecto.
    if not isinstance(valor, str) or not valor.strip():
        raise DatoInvalido(f"{campo} es obligatorio")
    return valor.strip()


def numero(valor, campo, minimo=0, maximo=None):
    try:
        if isinstance(valor, bool):
            raise TypeError("No se admite un booleano")
        valor = float(valor)
    except (ValueError, TypeError, OverflowError) as error:
        raise DatoInvalido(f"{campo} debe ser numérico") from error
    if not math.isfinite(valor) or valor < minimo:
        raise DatoInvalido(f"{campo} fuera del rango permitido")
    if maximo is not None and valor > maximo:
        raise DatoInvalido(f"{campo} supera el máximo")
    return valor


def positivo(valor, campo):
    valor = numero(valor, campo)
    if valor <= 0:
        raise DatoInvalido(f"{campo} debe ser mayor que cero")
    return valor


class Entidad(ABC):
    def __init__(self, codigo):
        self.__codigo = texto(codigo, "Código")

    @property
    def codigo(self):
        return self.__codigo

    @abstractmethod
    def describir(self):
        pass


class Cliente(Entidad):
    def __init__(self, documento, nombre, correo, telefono):
        super().__init__(documento)
        if not re.fullmatch(r"[A-Za-z0-9]{5,20}", self.codigo):
            raise DatoInvalido("Documento inválido")
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        valor = texto(valor, "Nombre")
        if len(valor) < 3 or not any(c.isalpha() for c in valor):
            raise DatoInvalido("Nombre inválido")
        self.__nombre = valor

    @property
    def correo(self):
        return self.__correo

    @correo.setter
    def correo(self, valor):
        valor = texto(valor, "Correo")
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", valor):
            raise DatoInvalido("Correo inválido")
        self.__correo = valor

    @property
    def telefono(self):
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        valor = texto(valor, "Teléfono")
        if not re.fullmatch(r"\+?\d{7,15}", valor):
            raise DatoInvalido("Teléfono inválido")
        self.__telefono = valor

    def describir(self):
        return f"{self.codigo} - {self.nombre}"


class Servicio(Entidad, ABC):
    def __init__(self, codigo, nombre, tarifa):
        super().__init__(codigo)
        self.__nombre = texto(nombre, "Servicio")
        self.__tarifa = positivo(tarifa, "Tarifa")
        self.__disponible = True

    @property
    def nombre(self):
        return self.__nombre

    @property
    def tarifa(self):
        return self.__tarifa

    @property
    def disponible(self):
        return self.__disponible

    def ocupar(self):
        if not self.disponible:
            raise NoDisponible(f"{self.codigo} no está disponible")
        self.__disponible = False

    def liberar(self):
        self.__disponible = True

    @abstractmethod
    def validar_parametros(self, duracion):
        pass

    @abstractmethod
    def costo_base(self, duracion):
        pass

    # En Python se simulan variantes de un método con parámetros opcionales.
    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        duracion = self.validar_parametros(duracion)
        impuesto = numero(impuesto, "Impuesto", 0, 100)
        descuento = numero(descuento, "Descuento", 0, 100)
        subtotal = self.costo_base(duracion)
        total = subtotal * (1 - descuento / 100) * (1 + impuesto / 100)
        if not math.isfinite(total):
            raise DatoInvalido("El cálculo del costo no es válido")
        return round(total, 2)


class Sala(Servicio):
    def __init__(self, codigo, nombre, tarifa, capacidad):
        super().__init__(codigo, nombre, tarifa)
        capacidad = positivo(capacidad, "Capacidad")
        if not capacidad.is_integer():
            raise DatoInvalido("La capacidad debe ser entera")
        self.capacidad = int(capacidad)

    def validar_parametros(self, duracion):
        return positivo(duracion, "Horas de sala")

    def costo_base(self, duracion):
        return self.tarifa * duracion

    def describir(self):
        return f"{self.codigo} - Sala {self.nombre} ({self.capacidad} personas)"


class Equipo(Servicio):
    def __init__(self, codigo, nombre, tarifa, tipo):
        super().__init__(codigo, nombre, tarifa)
        self.tipo = texto(tipo, "Tipo de equipo")

    def validar_parametros(self, duracion):
        dias = positivo(duracion, "Días de alquiler")
        if not dias.is_integer():
            raise DatoInvalido("El alquiler se calcula por días completos")
        return dias

    def costo_base(self, duracion):
        return self.tarifa * duracion

    def describir(self):
        return f"{self.codigo} - Equipo {self.nombre} ({self.tipo})"


class Asesoria(Servicio):
    def __init__(self, codigo, nombre, tarifa, especialidad):
        super().__init__(codigo, nombre, tarifa)
        self.especialidad = texto(especialidad, "Especialidad")

    def validar_parametros(self, duracion):
        horas = positivo(duracion, "Horas de asesoría")
        if horas < 1:
            raise DatoInvalido("La asesoría requiere al menos una hora")
        return horas

    def costo_base(self, duracion):
        return self.tarifa * duracion

    def describir(self):
        return f"{self.codigo} - Asesoría {self.nombre} ({self.especialidad})"


class Reserva(Entidad):
    def __init__(self, codigo, cliente, servicio, duracion):
        super().__init__(codigo)
        if not isinstance(cliente, Cliente) or not isinstance(servicio, Servicio):
            raise DatoInvalido("La reserva necesita un cliente y un servicio")
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = servicio.validar_parametros(duracion)
        self.__estado = "Pendiente"
        self.__total = None

    @property
    def estado(self):
        return self.__estado

    @property
    def total(self):
        return self.__total

    def confirmar(self):
        if self.estado != "Pendiente":
            raise EstadoIncorrecto("Solo se confirman reservas pendientes")
        self.servicio.ocupar()
        self.__estado = "Confirmada"

    def cancelar(self):
        if self.estado not in ("Pendiente", "Confirmada"):
            raise EstadoIncorrecto("La reserva no puede cancelarse")
        if self.estado == "Confirmada":
            self.servicio.liberar()
        self.__estado = "Cancelada"

    def procesar(self, impuesto=0, descuento=0):
        if self.estado != "Confirmada":
            raise EstadoIncorrecto("Primero se debe confirmar la reserva")
        # Si falla el cálculo, la reserva sigue confirmada.
        try:
            total = self.servicio.calcular_costo(self.duracion, impuesto, descuento)
        except DatoInvalido as error:
            raise DatoInvalido("No se pudo calcular el total de la reserva") from error
        else:
            self.__total = total
            self.__estado = "Procesada"
            self.servicio.liberar()
            return total

    def describir(self):
        return f"{self.codigo} - {self.cliente.nombre} / {self.servicio.nombre} / {self.estado}"
