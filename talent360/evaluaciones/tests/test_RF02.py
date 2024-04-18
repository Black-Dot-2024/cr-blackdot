from odoo.tests.common import TransactionCase

# Creamos una clase para realizar las pruebas de la RF02
class TestRF02(TransactionCase):

    # Método para inicializar las variables de la clase
    def setUp(self):
        super(TestRF02, self).setUp()
        
    # Método para finalizar las pruebas
    def tearDowm(self):
        super(TestRF02, self).tearDown()

    # Método para probar la asignación de usuarios a una evaluación
    def test_01_asignar_usuarios_a_evaluacion(self):
        # Creamos una evaluación
        evaluacion = self.env['evaluacion'].create({
            'nombre': 'Evaluación para asignar usuarios',
            'estado': 'borrador',
        })
        
        # Creamos un usuario
        usuario = self.env['res.users'].create({
            'name': 'Usuario de prueba',
            'login': 'usuario_prueba@gmail.com',
        })

        # Asignamos el usuario a la evaluación
        evaluacion.write({'usuario_ids': [(4, usuario.id)]})

        # Verificamos que el usuario se haya asignado correctamente
        usuarios_asignados = evaluacion.usuario_ids
        self.assertTrue(usuario in usuarios_asignados, "El usuario no se ha asignado a la evaluación correctamente")

    # Método para probar la eliminación de usuarios asignados a una evaluación
    def test_02_mostrar_usuarios_asignados(self):

        # Creamos una evaluación
        evaluacion = self.env['evaluacion'].create({
            'nombre': 'Evaluación con colaboradores',
            'estado': 'borrador',
        })
        
        # Creamos dos colaboradores
        colaborador1 = self.env['res.users'].create({
            'name': 'Colaborador 1',
            'login': 'colaborador1',
        })
        colaborador2 = self.env['res.users'].create({
            'name': 'Colaborador 2',
            'login': 'colaborador2',
        })

        # Asignamos los colaboradores a la evaluación
        evaluacion.write({'usuario_ids': [(4, colaborador1.id), (4, colaborador2.id)]})

        # Verificamos que los colaboradores se hayan asignado correctamente
        colaboradores_asignados = evaluacion.usuario_ids
        for colaborador in [colaborador1, colaborador2]:
            self.assertIn(colaborador, colaboradores_asignados, f"El colaborador {colaborador.name} no se mostró correctamente en la evaluación.")

    # Método para probar la eliminación de usuarios asignados a una evaluación
    def test_03_quitar_usuarios_asignados(self):
        # Creamos una evaluación
        evaluacion = self.env['evaluacion'].create({
            'nombre': 'Evaluación con colaboradores',
            'estado': 'borrador',
        })

        # Creamos un colaborador
        colaborador = self.env['res.users'].create({
            'name': 'Colaborador de prueba',
            'login': 'colaborador_prueba',
        })
        
        # Asignamos el colaborador a la evaluación
        evaluacion.write({'usuario_ids': [(4, colaborador.id)]})
        self.assertIn(colaborador, evaluacion.usuario_ids, "El colaborador no está asignado a la evaluación antes de eliminarlo.")
        
        # Eliminar el colaborador 
        evaluacion.write({'usuario_ids': [(3, colaborador.id)]})
        self.assertNotIn(colaborador, evaluacion.usuario_ids, "El colaborador no se eliminó correctamente de la evaluación.")
