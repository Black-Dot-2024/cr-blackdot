from odoo.tests.common import TransactionCase

class TestRF02(TransactionCase):
    def setUp(self):
        super(TestRF02, self).setUp()
        
    def tearDowm(self):
        super(TestRF02, self).tearDown()

    # def test_01_crear_evaluacion(self):
    #     evaluacion = self.env['evaluacion'].create({
    #         'nombre': 'Evaluación de ejemplo',
    #         'estado': 'borrador',
    #     })
    #     self.assertTrue(evaluacion, "La evaluación no se ha creado correctamente")

    # def test_02_crear_evaluacion_sin_nombre(self):
    #     evaluacion = self.env['evaluacion'].create({
    #         'estado': 'borrador',
    #     })
    #     self.assertTrue(evaluacion, "La evaluación no se ha creado correctamente")

    # def test_03_crear_evaluacion_sin_estado(self):
    #     evaluacion = self.env['evaluacion'].create({
    #         'nombre': 'Evaluación de ejemplo',
    #     })
    #     self.assertTrue(evaluacion, "La evaluación no se ha creado correctamente")

    # def test_04_actualizar_estado_evaluación(self):
    #     evaluacion = self.env['evaluacion'].create({
    #         'nombre': 'Evaluación para actualizar estado',
    #         'estado': 'borrador',
    #     })
    #     evaluacion.write({'estado': 'publicado'})
    #     evaluacion_actualizada = self.env['evaluacion'].browse(evaluacion.id)
    #     self.assertEqual(evaluacion_actualizada.estado, 'publicado', "El estado de la evaluación no se ha actualizado correctamente")
    
    def test_01_asignar_usuarios_a_evaluacion(self):
    # Crear una evaluación
        evaluacion = self.env['evaluacion'].create({
            'nombre': 'Evaluación para asignar usuarios',
            'estado': 'borrador',
        })
        
        # Crear un usuario de prueba
        usuario = self.env['res.users'].create({
            'name': 'Usuario de prueba',
            'login': 'usuario_prueba',
        })

        # Asignar el usuario a la evaluación utilizando el método `write`
        evaluacion.write({'usuario_ids': [(4, usuario.id)]})

        # Obtener los usuarios asignados a la evaluación después de la asignación
        usuarios_asignados = evaluacion.usuario_ids

        # Verificar si el usuario está en la lista de usuarios asignados
        self.assertTrue(usuario in usuarios_asignados, "El usuario no se ha asignado a la evaluación correctamente")
