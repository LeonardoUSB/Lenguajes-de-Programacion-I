import unittest
from unittest.mock import patch
import math
from tipo import TipoAtomico, TipoCompuesto, ManejadorTipos, main


class TestManejadorTiposAltaCobertura(unittest.TestCase):
    def setUp(self):
        self.mt = ManejadorTipos()

    # -----------------------------
    # Tipos atómicos: creación y errores
    # -----------------------------
    def test_agregar_tipo_atomico_ok(self):
        self.mt.agregar_tipo_atomico("char", 1, 2)
        self.assertIn("char", self.mt.tipos)
        self.assertIsInstance(self.mt.tipos["char"], TipoAtomico)
        self.assertEqual(self.mt.tipos["char"].representacion, 1)
        self.assertEqual(self.mt.tipos["char"].alineacion, 2)

    @patch('builtins.print')
    def test_agregar_tipo_atomico_duplicado(self, mock_print):
        self.mt.agregar_tipo_atomico("char", 1, 2)
        self.mt.agregar_tipo_atomico("char", 1, 2)
        mock_print.assert_any_call("Error: el tipo 'char' ya existe.")

    # -----------------------------
    # Tipos compuestos: creación y validaciones
    # -----------------------------
    def test_agregar_tipo_compuesto_struct_ok(self):
        self.mt.agregar_tipo_atomico("char", 1, 2)
        self.mt.agregar_tipo_atomico("int", 4, 4)
        self.mt.agregar_tipo_compuesto("foo", ["char", "int"])
        self.assertIn("foo", self.mt.tipos)
        self.assertIsInstance(self.mt.tipos["foo"], TipoCompuesto)
        self.assertFalse(self.mt.tipos["foo"].es_union)

    def test_agregar_tipo_compuesto_union_ok(self):
        self.mt.agregar_tipo_atomico("char", 1, 2)
        self.mt.agregar_tipo_atomico("int", 4, 4)
        self.mt.agregar_tipo_compuesto("bar", ["char", "int"], es_union=True)
        self.assertIn("bar", self.mt.tipos)
        self.assertTrue(self.mt.tipos["bar"].es_union)

    @patch('builtins.print')
    def test_agregar_tipo_compuesto_campo_inexistente(self, mock_print):
        self.mt.agregar_tipo_atomico("char", 1, 2)
        self.mt.agregar_tipo_compuesto("foo", ["char", "int"])  # 'int' no definido
        mock_print.assert_any_call("Error: el tipo 'int' no está definido.")
        self.assertNotIn("foo", self.mt.tipos)

    @patch('builtins.print')
    def test_agregar_tipo_compuesto_duplicado(self, mock_print):
        self.mt.agregar_tipo_atomico("char", 1, 2)
        self.mt.agregar_tipo_atomico("int", 4, 4)
        self.mt.agregar_tipo_compuesto("foo", ["char", "int"])
        self.mt.agregar_tipo_compuesto("foo", ["char", "int"])
        mock_print.assert_any_call("Error: el tipo 'foo' ya existe.")

    # -----------------------------
    # size_alineacion: atómico, struct, union, anidados
    # -----------------------------
    def test_size_alineacion_struct_basico(self):
        self.mt.agregar_tipo_atomico("char", 1, 2)
        self.mt.agregar_tipo_atomico("int", 4, 4)
        self.mt.agregar_tipo_compuesto("foo", ["char", "int"])
        emp, no_emp, ali_emp, ali_no_emp, bits = self.mt.size_alineacion("foo", es_union=False)
        # Verificaciones razonables según tu lógica de padding
        self.assertEqual(emp, 5)
        self.assertGreaterEqual(no_emp, emp)
        self.assertEqual(ali_emp, ali_no_emp)
        self.assertIsInstance(bits, int)

    def test_size_alineacion_union_basico(self):
        self.mt.agregar_tipo_atomico("char", 1, 2)
        self.mt.agregar_tipo_atomico("int", 4, 4)
        self.mt.agregar_tipo_compuesto("u", ["char", "int"], es_union=True)
        emp, no_emp, ali_emp, ali_no_emp, bits = self.mt.size_alineacion("u", es_union=True)
        self.assertEqual(emp, 4)  # tamaño del mayor
        self.assertEqual(no_emp, 4)
        self.assertEqual(ali_emp, math.lcm(2, 4))
        self.assertEqual(ali_no_emp, ali_emp)
        self.assertEqual(bits, 0)  # tu código pone 0 si no hay compuestos

    def test_size_alineacion_anidado_struct_en_struct(self):
        self.mt.agregar_tipo_atomico("char", 1, 2)
        self.mt.agregar_tipo_atomico("int", 4, 4)
        self.mt.agregar_tipo_atomico("raro", 5, 3)
        self.mt.agregar_tipo_compuesto("foo", ["char", "int", "raro"])       # struct
        self.mt.agregar_tipo_compuesto("bar", ["char", "int", "raro"], es_union=True)  # union
        self.mt.agregar_tipo_compuesto("foobar", ["foo", "bar", "int"])      # struct anidado con union
        emp, no_emp, ali_emp, ali_no_emp, bits = self.mt.size_alineacion("foobar", es_union=False)
        self.assertIsInstance(emp, int)
        self.assertIsInstance(no_emp, int)
        self.assertIsInstance(bits, int)
        self.assertGreaterEqual(no_emp, emp)

    # -----------------------------
    # mejor_reordenamiento: óptimo de orden en campos
    # -----------------------------
    def test_mejor_reordenamiento_struct_simple(self):
        self.mt.agregar_tipo_atomico("a", 1, 2)
        self.mt.agregar_tipo_atomico("b", 4, 4)
        self.mt.agregar_tipo_atomico("c", 5, 3)
        self.mt.agregar_tipo_compuesto("s", ["a", "b", "c"], es_union=False)
        # Devuelve (mejor_size_no_empaquetado, mejor_alineacion_no_empaquetado, bits)
        mejor_size, mejor_ali, bits = self.mt.mejor_reordenamiento("s", self.mt.size_alineacion)
        self.assertIsInstance(mejor_size, int)
        self.assertIsInstance(mejor_ali, int)
        self.assertIsInstance(bits, int)

    def test_mejor_reordenamiento_no_altera_tipo_original(self):
        self.mt.agregar_tipo_atomico("x", 1, 2)
        self.mt.agregar_tipo_atomico("y", 2, 2)
        self.mt.agregar_tipo_atomico("z", 4, 4)
        campos = ["x", "y", "z"]
        self.mt.agregar_tipo_compuesto("t", campos, es_union=False)
        original = self.mt.tipos["t"].campos[:]
        _ = self.mt.mejor_reordenamiento("t", self.mt.size_alineacion)
        restaurado = self.mt.tipos["t"].campos
        self.assertEqual(original, restaurado)

    # -----------------------------
    # describir_tipo y describir_registro: impresión
    # -----------------------------
    @patch('builtins.print')
    def test_describir_tipo_atomico(self, mock_print):
        self.mt.agregar_tipo_atomico("char", 1, 2)
        self.mt.describir_tipo("char")
        mock_print.assert_any_call("Tipo Atómico: char")
        # Contiene alineación y representación
        self.assertTrue(any("Alineación:" in c for c in (call.args[0] for call in mock_print.call_args_list)))
        self.assertTrue(any("Representación" in c for c in (call.args[0] for call in mock_print.call_args_list)))

    @patch('builtins.print')
    def test_describir_tipo_compuesto_struct(self, mock_print):
        self.mt.agregar_tipo_atomico("char", 1, 2)
        self.mt.agregar_tipo_atomico("int", 4, 4)
        self.mt.agregar_tipo_compuesto("foo", ["char", "int"], es_union=False)
        self.mt.describir_tipo("foo")
        mock_print.assert_any_call("Tipo Struct: foo")
        # Debe imprimir tamaños y bytes desperdiciados
        printed = [c.args[0] for c in mock_print.call_args_list]
        self.assertTrue(any("Tamaño empaquetado" in s for s in printed))
        self.assertTrue(any("Tamaño no empaquetado" in s for s in printed))
        self.assertTrue(any("Tamaño óptimo" in s for s in printed))
        self.assertTrue(any("Bytes desperdiciados" in s for s in printed))

    @patch('builtins.print')
    def test_describir_tipo_inexistente(self, mock_print):
        self.mt.describir_tipo("noexiste")
        mock_print.assert_any_call("Error: el tipo 'noexiste' no está definido.")

    # -----------------------------
    # es_union: verificación
    # -----------------------------
    def test_es_union_flag(self):
        self.mt.agregar_tipo_atomico("char", 1, 2)
        self.mt.agregar_tipo_atomico("int", 4, 4)
        self.mt.agregar_tipo_compuesto("u", ["char", "int"], es_union=True)
        self.assertTrue(self.mt.es_union("u"))

    # -----------------------------
    # main: flujo interactivo y errores
    # -----------------------------
    @patch('builtins.input', side_effect=[
        'ATOMICO char 1 2',
        'ATOMICO char 1 5',                   # duplicado
        'ATOMICO int 4 4',
        'DESCRIBIR wenas',                    # tipo no definido
        'STRUCT wenas char int',              # correcto
        'ATOMICO atomico',                    # error de argumentos
        'DESCRIBIR wenas hellou',             # error de argumentos
        'DESCRIBIR wenas',                    # describe struct
        'SALIR'
    ])
    @patch('builtins.print')
    def test_main_interactivo(self, mock_print, mock_input):
        main()
        output = [call.args[0] for call in mock_print.call_args_list]
        # Errores esperados
        self.assertIn("Error: el tipo 'char' ya existe.", output)
        self.assertIn("Error: el tipo 'wenas' no está definido.", output)
        self.assertIn("Error: faltan argumentos o hay argumentos de mas", output)
        # Describe
        self.assertTrue(any("Tipo Struct: wenas" in s for s in output))
        self.assertTrue(any("Tamaño empaquetado:" in s for s in output))
        self.assertTrue(any("Tamaño no empaquetado:" in s for s in output))
        self.assertTrue(any("Tamaño óptimo:" in s for s in output))
        self.assertIn("Saliendo", output)

    # -----------------------------
    # Rama de error en size_alineacion: tipo desconocido en campos
    # -----------------------------
    def test_size_alineacion_tipo_desconocido_en_campos(self):
        self.mt.agregar_tipo_atomico("char", 1, 2)
        # Definimos un struct con un campo que luego alteramos a nombre inexistente
        self.mt.agregar_tipo_compuesto("foo", ["char"], es_union=False)
        # Forzamos un nombre inexistente en campos para disparar TypeError
        self.mt.tipos["foo"].campos = ["no_definido"]
        with self.assertRaises(KeyError):
            _ = self.mt.size_alineacion("foo", es_union=False)

    # -----------------------------
    # Compuestos recursivos: struct dentro de struct y union
    # -----------------------------
    def test_anidamiento_profundo_struct_union(self):
        self.mt.agregar_tipo_atomico("a", 1, 2)
        self.mt.agregar_tipo_atomico("b", 2, 2)
        self.mt.agregar_tipo_atomico("c", 4, 4)
        self.mt.agregar_tipo_compuesto("s1", ["a", "b"], es_union=False)
        self.mt.agregar_tipo_compuesto("u1", ["b", "c"], es_union=True)
        self.mt.agregar_tipo_compuesto("s2", ["s1", "u1", "c"], es_union=False)
        emp, no_emp, ali_emp, ali_no_emp, bits = self.mt.size_alineacion("s2", es_union=False)
        self.assertIsInstance(emp, int)
        self.assertGreaterEqual(no_emp, emp)
        self.assertIsInstance(bits, int)


if __name__ == '__main__':
    unittest.main()
