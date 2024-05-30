from odoo import models, fields, api
from odoo.exceptions import ValidationError
from functools import reduce


class Users(models.Model):
    """
    Modelo para representar los usuarios de Odoo.

    :param _name (str): Nombre del modelo en Odoo
    :param evaluacion_ids (list): Lista de evaluaciones asociadas al usuario
    """

    _name = "res.users"
    _inherit = ["res.users"]

    evaluacion_ids = fields.Many2many(
        "evaluacion",
        "usuario_evaluacion_rel",
        "usuario_id",
        "evaluacion_id",
        string="Evaluaciones",
    )

    def ver_respuestas_usuario(self):
        """
        Redirecciona a la vista gráfica de las respuestas del usuario a cada pregunta de la evaluación.

        Returns:
            Parámetros necesarios para abrir la vista gráfica de las respuestas.
        """

        evaluacion_id = self._context.get("actual_evaluacion_id")
        respuesta_ids = self.env["respuesta"].search(
            [
                ("evaluacion_id.id", "=", evaluacion_id),
                ("usuario_id.id", "=", self.id),
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
                    ("usuario_id", "=", self.id),
                ],
            }
        else:
            raise ValidationError(
                _("No se encontraron respuestas para el usuario seleccionado.")
            )

    def obtener_datos_demograficos(self):
        """
        Obtiene los datos demográficos de un usuario.

        Este método obtiene los datos demográficos, como nombre, género, puesto, año de nacimiento, generación, departamento, nivel jerárquico, gerencia, jefatura, fecha de ingreso y ubicación/región.

        :return: Un diccionario con los datos demográficos del usuario.
        """

        datos = {}
        datos["nombre"] = self.name if self.name else "N/A"
        datos["genero"] = self.gender.capitalize() if self.gender else "N/A"
        datos["puesto"] = self.job_title if self.job_title else "N/A"
        datos["anio_nacimiento"] = self.birthday.year if self.birthday else "N/A"
        datos["generacion"] = (
            self.obtener_generacion(datos["anio_nacimiento"])
            if datos["anio_nacimiento"] != "N/A"
            else "N/A"
        )
        datos["departamento"] = self.department_id.name if self.department_id else "N/A"

        datos.update(self._obtener_atributos_extra())

        print("DATOS DEMO INTERNO", datos)

        return datos

    def _obtener_atributos_extra(self):
        atributos = self.employee_id._read_format(["employee_properties"])[0]["employee_properties"]
        atributos_extra = {}
        for attr in atributos:
            if attr["type"] in ["separator", "many2one", "many2many", "tags"]:
                continue
            atributos_extra[attr["string"]] = attr["value"] if attr["value"] else "N/A"

        return atributos_extra
    
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