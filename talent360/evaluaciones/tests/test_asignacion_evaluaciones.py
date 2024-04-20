from odoo.tests.common import TransactionCase

class TestAsignacionEvaluaciones(TransactionCase):

    def setUp(self):
        super(TestAsignacionEvaluaciones, self).setUp()
        # Preparación de datos comunes para usar en todos los tests
        self.evaluacion = self.env['evaluacion'].create({
            'nombre': 'Evaluación Base',
            'estado': 'borrador',
        })

    def tearDown(self):
        super(TestAsignacionEvaluaciones, self).tearDown()

    def crear_usuario(self, nombre, login):
        # Crear un usuario de prueba
        return self.env['res.users'].create({
            'name': nombre,
            'login': login,
        })

    def test_01_asignar_usuarios_a_evaluacion(self):
        usuario = self.crear_usuario('Usuario de prueba', 'usuario_prueba@gmail.com')
        self.evaluacion.write({'usuario_ids': [(4, usuario.id)]})
        self.assertIn(usuario, self.evaluacion.usuario_ids, "El usuario no se ha asignado a la evaluación correctamente")

    def test_02_mostrar_usuarios_asignados(self):
        colaborador1 = self.crear_usuario('Colaborador 1', 'colaborador1')
        colaborador2 = self.crear_usuario('Colaborador 2', 'colaborador2')
        self.evaluacion.write({'usuario_ids': [(4, colaborador1.id), (4, colaborador2.id)]})
        for colaborador in [colaborador1, colaborador2]:
            self.assertIn(colaborador, self.evaluacion.usuario_ids, f"El colaborador {colaborador.name} no se mostró correctamente en la evaluación.")

    def test_03_quitar_usuarios_asignados(self):
        colaborador = self.crear_usuario('Colaborador de prueba', 'colaborador_prueba')
        self.evaluacion.write({'usuario_ids': [(4, colaborador.id)]})
        self.assertIn(colaborador, self.evaluacion.usuario_ids, "El colaborador no está asignado a la evaluación antes de eliminarlo.")
        self.evaluacion.write({'usuario_ids': [(3, colaborador.id)]})
        self.assertNotIn(colaborador, self.evaluacion.usuario_ids, "El colaborador no se eliminó correctamente de la evaluación.")