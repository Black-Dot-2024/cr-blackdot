from odoo.tests.common import TransactionCase

class TestRF02(TransactionCase):
    def setUp(self):
        super(TestRF02, self).setUp()
        
    def tearDowm(self):
        super(TestRF02, self).tearDown()

    def test_01_crear_evaluacion(self):
        evaluacion = self.env['evaluacion'].create({
            'nombre': 'Evaluación de ejemplo',
            'estado': 'borrador',
        })
        self.assertTrue(evaluacion, "La evaluación no se ha creado correctamente")

    def test_02_crear_evaluacion_sin_nombre(self):
        evaluacion = self.env['evaluacion'].create({
            'estado': 'borrador',
        })
        self.assertTrue(evaluacion, "La evaluación no se ha creado correctamente")

    def test_03_crear_evaluacion_sin_estado(self):
        evaluacion = self.env['evaluacion'].create({
            'nombre': 'Evaluación de ejemplo',
        })
        self.assertTrue(evaluacion, "La evaluación no se ha creado correctamente")

    def test_04_actualizar_estado_evaluación(self):
        evaluacion = self.env['evaluacion'].create({
            'nombre': 'Evaluación para actualizar estado',
            'estado': 'borrador',
        })
        evaluacion.write({'estado': 'publicado'})
        evaluacion_actualizada = self.env['evaluacion'].browse(evaluacion.id)
        self.assertEqual(evaluacion_actualizada.estado, 'publicado', "El estado de la evaluación no se ha actualizado correctamente")

    # def test_03_asignar_usuarios_a_evaluacion(self):
    #     evaluacion = self.env['evaluacion'].create({
    #         'nombre': 'Evaluación para asignar usuarios',
    #         'estado': 'borrador',
    #     })
    #     usuario = self.env['res.users'].create({
    #         'name': 'Usuario de prueba',
    #         'login': 'usuario_prueba',
    #         'language': 'English (US)',
    #         'latest_auth': '04/10/2024 00:00:00',
    #         'company': 'Talent360',
    #         'status': 'confirmed',
    #     })

    #     evaluacion.write({'usuario_ids': (4, usuario.id)})

    #     usuarios_asignados = evaluacion.usuario_ids
    #     self.assertTrue(usuario in usuarios_asignados, "El usuario no se ha asignado a la evaluación correctamente")

