"""Pruebas unitarias. Ejecutar: python -m unittest -v"""
import tempfile
import unittest
from pathlib import Path
from modelos import (Entidad, Servicio, Cliente, Sala, Equipo, Asesoria,
                     DatoInvalido, Duplicado, NoDisponible, NoEncontrado, EstadoIncorrecto)
from gestor import Gestor, configurar_log, ejecutar
from simulaciones import simular


class PruebasSoftwareFJ(unittest.TestCase):
    def setUp(self):
        self.g = Gestor()
        self.cliente = self.g.registrar_cliente("12345", "Ana Pérez", "ana@example.com", "3001234567")
        self.sala = self.g.registrar_servicio(Sala("S1", "Principal", 50000, 10))

    def reserva(self, codigo="R1"):
        return self.g.crear_reserva(codigo, "12345", "S1", 2)

    def test_entidad_abstracta(self):
        with self.assertRaises(TypeError):
            Entidad("X")

    def test_servicio_abstracto(self):
        with self.assertRaises(TypeError):
            Servicio("S", "Servicio", 10)

    def test_nombre_invalido(self):
        with self.assertRaises(DatoInvalido):
            self.cliente.nombre = ""

    def test_correo_invalido(self):
        with self.assertRaises(DatoInvalido):
            self.cliente.correo = "ana"
        self.assertEqual(self.cliente.correo, "ana@example.com")

    def test_telefono_invalido(self):
        with self.assertRaises(DatoInvalido):
            self.cliente.telefono = "abc"

    def test_documento_invalido(self):
        with self.assertRaises(DatoInvalido):
            Cliente("1", "Ana Pérez", "ana@example.com", "3001234567")

    def test_cliente_duplicado(self):
        with self.assertRaises(Duplicado):
            self.g.registrar_cliente("12345", "Ana Pérez", "ana@example.com", "3001234567")
        self.assertEqual(len(self.g.clientes), 1)

    def test_tarifa_negativa(self):
        with self.assertRaises(DatoInvalido):
            Sala("S2", "Otra sala", -1, 10)

    def test_tarifa_no_finita(self):
        with self.assertRaises(DatoInvalido):
            Sala("S2", "Otra sala", float("inf"), 10)

    def test_capacidad_decimal(self):
        with self.assertRaises(DatoInvalido):
            Sala("S2", "Otra sala", 100, 2.5)

    def test_costo_base(self):
        self.assertEqual(self.sala.calcular_costo(2), 100000)

    def test_costo_impuesto(self):
        self.assertEqual(self.sala.calcular_costo(2, 19), 119000)

    def test_costo_descuento(self):
        self.assertEqual(self.sala.calcular_costo(2, 19, 10), 107100)

    def test_impuesto_invalido(self):
        with self.assertRaises(DatoInvalido):
            self.sala.calcular_costo(2, -1)

    def test_alquiler_dias_enteros(self):
        equipo = Equipo("E1", "Portátil", 80000, "Informática")
        self.assertEqual(equipo.calcular_costo(3), 240000)
        with self.assertRaises(DatoInvalido):
            equipo.calcular_costo(1.5)

    def test_asesoria(self):
        asesoria = Asesoria("A1", "Consultoría", 100000, "Software")
        self.assertEqual(asesoria.calcular_costo(2), 200000)

    def test_asesoria_corta(self):
        with self.assertRaises(DatoInvalido):
            Asesoria("A1", "Consultoría", 100, "Software").calcular_costo(0.5)

    def test_servicio_duplicado(self):
        with self.assertRaises(Duplicado):
            self.g.registrar_servicio(self.sala)

    def test_cliente_inexistente(self):
        with self.assertRaises(NoEncontrado):
            self.g.crear_reserva("R1", "99999", "S1", 1)

    def test_duracion_invalida(self):
        with self.assertRaises(DatoInvalido):
            self.g.crear_reserva("R1", "12345", "S1", 0)
        self.assertEqual(len(self.g.reservas), 0)

    def test_confirmar(self):
        r = self.reserva()
        self.g.confirmar("R1")
        self.assertEqual(r.estado, "Confirmada")
        self.assertFalse(self.sala.disponible)

    def test_confirmacion_doble(self):
        r = self.reserva()
        r.confirmar()
        with self.assertRaises(EstadoIncorrecto):
            r.confirmar()

    def test_servicio_ocupado(self):
        self.reserva().confirmar()
        with self.assertRaises(NoDisponible):
            self.reserva("R2")

    def test_cancelar_pendiente(self):
        r = self.reserva()
        r.cancelar()
        self.assertEqual(r.estado, "Cancelada")
        self.assertTrue(self.sala.disponible)

    def test_cancelar_confirmada(self):
        r = self.reserva()
        r.confirmar()
        r.cancelar()
        self.assertTrue(self.sala.disponible)

    def test_procesar_pendiente(self):
        with self.assertRaises(EstadoIncorrecto):
            self.reserva().procesar()

    def test_procesar_confirmada(self):
        r = self.reserva()
        r.confirmar()
        self.assertEqual(r.procesar(19, 10), 107100)
        self.assertEqual(r.estado, "Procesada")
        self.assertTrue(self.sala.disponible)

    def test_error_encadenado(self):
        r = self.reserva()
        r.confirmar()
        with self.assertRaises(DatoInvalido) as error:
            r.procesar(descuento=101)
        self.assertIsInstance(error.exception.__cause__, DatoInvalido)
        self.assertEqual(r.estado, "Confirmada")

    def test_reserva_duplicada(self):
        self.reserva()
        with self.assertRaises(Duplicado):
            self.reserva()

    def test_simulaciones_y_log(self):
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "prueba.log"
            logger = configurar_log(ruta)
            try:
                correctos, total = simular(logger)
                self.assertEqual(correctos, total)
                self.assertGreaterEqual(total, 10)
                contenido = ruta.read_text(encoding="utf-8")
                self.assertIn("ERROR", contenido)
                self.assertIn("Correcto", contenido)
                self.assertIn("Fin de operación", contenido)
            finally:
                for handler in logger.handlers[:]:
                    handler.close()
                    logger.removeHandler(handler)


if __name__ == "__main__":
    unittest.main()
