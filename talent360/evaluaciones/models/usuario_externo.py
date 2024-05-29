from odoo import models, fields, _
from odoo.exceptions import ValidationError


class UsuarioExterno(models.Model):
    """
    Modelo para representar a un usuario externo en Odoo.

    :param _name (str): Nombre del modelo en Odoo.
    :param _description (str): Descripción del modelo en Odoo.
    :param nombre (fields.Char): Nombre completo del usuario externo. Es un campo obligatorio.
    :param email (fields.Char): Correo electrónico del usuario externo. Es un campo obligatorio.
    :param puesto (fields.Char): Puesto del usuario externo.
    :param nivel_jerarquico (fields.Char): Nivel jerárquico del usuario externo.
    :param direccion (fields.Char): Dirección del usuario externo.
    :param gerencia (fields.Char): Gerencia del usuario externo.
    :param jefatura (fields.Char): Jefatura del usuario externo.
    :param genero (fields.Char): Género del usuario externo.
    :param fecha_ingreso (fields.Date): Fecha de ingreso del usuario externo.
    :param fecha_nacimiento (fields.Date): Fecha de nacimiento del usuario externo.
    :param region (fields.Char): Ubicación o región del usuario externo.
    :param evaluacion_ids (fields.Many2many): Relación de muchos a muchos con el modelo 'evaluacion' para asignar evaluaciones al usuario externo.
    """

    _name = "usuario.externo"
    _description = "Usuarios externos a la plataforma. Se utiliza para que puedan responer encuestas sin tener un usuario"
    _rec_name = "nombre"

    nombre = fields.Char(required=True)
    email = fields.Char(string="Correo electrónico", required=True)
    puesto = fields.Char()
    nivel_jerarquico = fields.Char(string="Nivel jerárquico")
    direccion = fields.Char(string="Dirección")
    gerencia = fields.Char()
    jefatura = fields.Char()
    genero = fields.Char(string="Género")
    fecha_ingreso = fields.Date(string="Fecha de ingreso")
    fecha_nacimiento = fields.Date(string="Fecha de nacimiento")
    region = fields.Char(string="Ubicación/Región")

    evaluacion_ids = fields.Many2many(
        "evaluacion",
        "usuario_evaluacion_rel",
        "usuario_externo_id",
        "evaluacion_id",
        string="Evaluaciones",
    )

    def ver_respuestas_usuario_externo(self):
        """
        Esta función busca las respuestas de un usuario externo para una evaluación específica. Si encuentra respuestas, muestra una ventana con las respuestas del usuario. Si no encuentra respuestas o si el usuario está asignado a la evaluación varias veces, lanza un error.
        """

        evaluacion_id = self._context.get("actual_evaluacion_id")

        usuario_evaluacion_rel = self.env["usuario.evaluacion.rel"].search(
            [
                ("evaluacion_id.id", "=", evaluacion_id),
                ("usuario_externo_id.id", "=", self.id),
            ]
        )

        if not usuario_evaluacion_rel:
            raise ValidationError(
                _("No se encontraron respuestas para el usuario seleccionado. test")
            )

        if len(usuario_evaluacion_rel) > 1:
            raise ValidationError(
                _(
                    "El usuario seleccionado está asognado a la evaluación multiples veces. Por favor contactar a un administrador."
                )
            )

        token = usuario_evaluacion_rel.token

        respuesta_ids = self.env["respuesta"].search(
            [
                ("evaluacion_id.id", "=", evaluacion_id),
                ("token", "=", token),
            ]
        )

        if respuesta_ids:
            return {
                "type": "ir.actions.act_window",
                "name": "Respuestas del usuario",
                "res_model": "respuesta",
                "view_mode": "tree",
                "domain": [
                    ("evaluacion_id", "=", evaluacion_id),
                    ("token", "=", token),
                ],
            }
        else:
            raise ValidationError(
                _("No se encontraron respuestas para el usuario seleccionado.")
            )


    def obtener_datos_demograficos(self):
        """
        Obtiene los datos demográficos de un usuario externo.

        :return: Un diccionario con los datos demográficos del usuario externo. Incluye nombre, género, puesto, año de nacimiento, generación y departamento.
        """


        datos = {}
        datos["nombre"] = self.nombre if self.nombre else "N/A"
        datos["genero"] = self.genero.capitalize() if self.genero else "N/A"
        datos["puesto"] = self.puesto if self.puesto else "N/A"
        datos["anio_nacimiento"] = (
            self.fecha_nacimiento.year if self.fecha_nacimiento else "N/A"
        )
        datos["generacion"] = (
            self.obtener_generacion(datos["anio_nacimiento"])
            if datos["anio_nacimiento"] != "N/A"
            else "N/A"
        )
        datos["departamento"] = self.direccion if self.direccion else "N/A"

        return datos

    def obtener_generacion(self, anio_nacimiento):
        """
        Obtiene la generación a la que pertenece una persona de acuerdo al año de nacimiento.
        :param anio_nacimiento: El año de nacimiento de la persona.

        :return: La generación a la que pertenece la persona.
        """

        if 1946 <= anio_nacimiento <= 1964:
            return "Baby Boomers"
        elif 1965 <= anio_nacimiento <= 1980:
            return "Generación X"
        elif 1981 <= anio_nacimiento <= 1999:
            return "Millenials"
        elif 2000 <= anio_nacimiento <= 2015:
            return "Generacion Z"
        else:
            return "N/A"