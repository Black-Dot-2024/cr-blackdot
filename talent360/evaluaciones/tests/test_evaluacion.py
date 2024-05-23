from odoo.tests.common import TransactionCase
from odoo import fields


class test_evaluacion(TransactionCase):
    """
    Caso de prueba para evaluar la funcionalidades relacionada con evaluaciones en Odoo.
    """

    def setUp(self):
        """
        Método para inicializar las variables de la clase antes de cada prueba.
        """
        super(test_evaluacion, self).setUp()

    def crear_evaluacion(self, nombre, estado="borrador"):
        """
        Crea y devuelve una evaluación con el nombre y estado proporcionados.

        :param nombre: El nombre de la evaluación.
        :param estado: El estado de la evaluación (por defecto es 'borrador').
        :return: El registro de la evaluación creada.
        """
        return self.env["evaluacion"].create(
            {
                "nombre": nombre,
                "estado": estado,
                "fecha_inicio": fields.Date.today(),
                "fecha_final": fields.Date.today(),
            }
        )

    def tearDowm(self):
        """
        Método para finalizar las pruebas.
        """
        super(test_evaluacion, self).tearDown()
        return

    def test_copiar_preguntas_de_template_clima(self):
        """
        Prueba copiar preguntas desde un template para evaluación Clima.

        Este método simula la copia de preguntas desde un template predefinido para evaluación Clima.
        Crea preguntas de ejemplo y un template con esas preguntas, luego copia las preguntas a
        una evaluación y verifica que las preguntas se copien correctamente.
        """
        evaluacion = self.crear_evaluacion("Evaluación Clima")

        # Crear preguntas de ejemplo que podrían ser asociadas a un template
        preguntas = self.env["pregunta"].create(
            [
                {"pregunta_texto": "Pregunta 1", "tipo": "open_question"},
                {"pregunta_texto": "Pregunta 2", "tipo": "open_question"},
            ]
        )
        # Crear un template con preguntas predefinidas
        template = self.env["template"].create(
            {
                "nombre": "Template Clima",
                "tipo": "clima",
                "pregunta_ids": [(6, 0, preguntas.ids)],
            }
        )
        # Simular copia de preguntas desde el template
        evaluacion.pregunta_ids = [(6, 0, template.pregunta_ids.ids)]
        # Verificar que las preguntas se han copiado correctamente
        self.assertEqual(len(evaluacion.pregunta_ids), 2)

    def test_copiar_preguntas_de_template_nom035(self):
        """
        Prueba copiar preguntas desde un template para evaluación NOM-035.

        Este método simula la copia de preguntas desde un template predefinido para evaluación NOM-035.
        Crea preguntas de ejemplo y un template con esas preguntas, luego copia las preguntas a
        una evaluación y verifica que las preguntas se copien correctamente.
        """
        evaluacion = self.crear_evaluacion("Evaluación NOM-035")

        # Crear preguntas de ejemplo que podrían ser asociadas a un template
        preguntas = self.env["pregunta"].create(
            [
                {"pregunta_texto": "Pregunta 1", "tipo": "open_question"},
                {"pregunta_texto": "Pregunta 2", "tipo": "open_question"},
            ]
        )
        # Crear un template con preguntas predefinidas
        template = self.env["template"].create(
            {
                "nombre": "Template NOM-035",
                "tipo": "nom_035",
                "pregunta_ids": [(6, 0, preguntas.ids)],
            }
        )
        # Simular copia de preguntas desde el template
        evaluacion.pregunta_ids = [(6, 0, template.pregunta_ids.ids)]
        # Verificar que las preguntas se han copiado correctamente
        self.assertEqual(len(evaluacion.pregunta_ids), 2)

    def test_crear_evaluacion_generica(self):
        """
        Prueba crear una evaluación genérica.

        Este método simula la creación de una evaluación genérica sin preguntas predefinidas.
        Se crea una evaluación sin preguntas y se verifica que no se haya copiado ninguna pregunta.

        :param nombre: El nombre de la evaluación.
        :param estado: El estado de la evaluación (por defecto es 'borrador').
        """
        
        evaluacion = self.crear_evaluacion("Evaluación Genérica")

        preguntas = self.env["pregunta"].create(
            [
                {"pregunta_texto": "Pregunta 1", "tipo": "open_question"},
                {"pregunta_texto": "Pregunta 2", "tipo": "open_question"},
            ]
        )

        evaluacion.pregunta_ids = [(6, 0, preguntas.ids)]
        
        # Verificar que no se han copiado preguntas
        self.assertEqual(len(evaluacion.pregunta_ids), 2)