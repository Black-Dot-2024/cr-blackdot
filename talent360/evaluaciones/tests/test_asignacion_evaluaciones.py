from odoo.tests.common import TransactionCase

class TestAsignacionEvaluaciones(TransactionCase):
    """
    Caso de prueba para evaluar la funcionalidades relacionada con evaluaciones en Odoo.
    """
    def setUp(self):
        """
        Método para inicializar las variables de la clase antes de cada prueba.
        """
        super(TestAsignacionEvaluaciones, self).setUp()
        self.evaluacion = self.env["evaluacion"].create({
            "nombre": "Evaluación Base",
            "estado": "borrador",
        })

    def tearDown(self):
        """
        Método para finalizar las pruebas.
        """
        super(TestAsignacionEvaluaciones, self).tearDown()

    def crear_usuario(self, nombre, login):
        """
        Método para crear un usuario en Odoo.

        :param nombre (str): Nombre del usuario.
        :param login (str): Correo electrónico del usuario.
        :return res.users: Usuario creado en Odoo.
        """
        return self.env["res.users"].create({
            "name": nombre,
            "login": login,
        })

    def test_asignar_usuarios_a_evaluacion(self):
        """
        Prueba para asignar un usuario a una evaluación.

        Esta prueba asigna usuarios a una evaluaciones y verifica que el usuario se haya asignado correctamente.
        """
        usuario = self.crear_usuario("Usuario de prueba", "usuario_prueba@gmail.com")
        self.evaluacion.write({"usuario_ids": [(4, usuario.id)]})
        self.assertIn(usuario, self.evaluacion.usuario_ids, "El usuario no se ha asignado a la evaluación correctamente")

    def test_mostrar_usuarios_asignados(self):
        """
        Prueba para mostrar los usuarios asignados a una evaluación.

        Esta prueba asigna varios usuarios a una evaluación y verifica que los usuarios asignados se muestren correctamente en la evaluación.
        """
        colaborador1 = self.crear_usuario("Colaborador 1", "colaborador1")
        colaborador2 = self.crear_usuario("Colaborador 2", "colaborador2")
        self.evaluacion.write({"usuario_ids": [(4, colaborador1.id), (4, colaborador2.id)]})
        for colaborador in [colaborador1, colaborador2]:
            self.assertIn(colaborador, self.evaluacion.usuario_ids, f"El colaborador {colaborador.name} no se mostró correctamente en la evaluación.")

    def test_quitar_usuarios_asignados(self):
        """
        Prueba para quitar un usuario asignado a una evaluación.

        Esta prueba asigna un usuario a una evaluación y luego lo elimina de la evaluación. Verifica que el usuario se haya eliminado correctamente.
        """
        colaborador = self.crear_usuario("Colaborador de prueba", "colaborador_prueba")
        self.evaluacion.write({"usuario_ids": [(4, colaborador.id)]})
        self.assertIn(colaborador, self.evaluacion.usuario_ids, "El colaborador no está asignado a la evaluación antes de eliminarlo.")
        self.evaluacion.write({"usuario_ids": [(3, colaborador.id)]})
        self.assertNotIn(colaborador, self.evaluacion.usuario_ids, "El colaborador no se eliminó correctamente de la evaluación.")