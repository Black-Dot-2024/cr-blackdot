from odoo.tests.common import TransactionCase

class TestRF02(TransactionCase):
    def setUp(self):
        super(TestRF02, self).setUp()
        
    def tearDowm(self):
        super(TestRF02, self).tearDown()

    def test_01_asignar_usuarios_a_evaluacion(self):
        evaluacion = self.env['evaluacion'].create({
            'nombre': 'Evaluación para asignar usuarios',
            'estado': 'borrador',
        })
        
        usuario = self.env['res.users'].create({
            'name': 'Usuario de prueba',
            'login': 'usuario_prueba@gmail.com',
        })

        evaluacion.write({'usuario_ids': [(4, usuario.id)]})

        usuarios_asignados = evaluacion.usuario_ids
        self.assertTrue(usuario in usuarios_asignados, "El usuario no se ha asignado a la evaluación correctamente")

    def test_02_mostrar_usuarios_asignados(self):
        evaluacion = self.env['evaluacion'].create({
            'nombre': 'Evaluación con colaboradores',
            'estado': 'borrador',
        })
        
        colaborador1 = self.env['res.users'].create({
            'name': 'Colaborador 1',
            'login': 'colaborador1',
        })
        colaborador2 = self.env['res.users'].create({
            'name': 'Colaborador 2',
            'login': 'colaborador2',
        })
    
        evaluacion.write({'usuario_ids': [(4, colaborador1.id), (4, colaborador2.id)]})

        colaboradores_asignados = evaluacion.usuario_ids
        for colaborador in [colaborador1, colaborador2]:
            self.assertIn(colaborador, colaboradores_asignados, f"El colaborador {colaborador.name} no se mostró correctamente en la evaluación.")

    def test_03_quitar_usuarios_asignados(self):
        evaluacion = self.env['evaluacion'].create({
            'nombre': 'Evaluación con colaboradores',
            'estado': 'borrador',
        })

        colaborador = self.env['res.users'].create({
            'name': 'Colaborador de prueba',
            'login': 'colaborador_prueba',
        })
        
        evaluacion.write({'usuario_ids': [(4, colaborador.id)]})
        self.assertIn(colaborador, evaluacion.usuario_ids, "El colaborador no está asignado a la evaluación antes de eliminarlo.")
        
        # Eliminar el colaborador 
        evaluacion.write({'usuario_ids': [(3, colaborador.id)]})
        self.assertNotIn(colaborador, evaluacion.usuario_ids, "El colaborador no se eliminó correctamente de la evaluación.")
