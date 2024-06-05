from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Opcion(models.Model):
    """
    Modelo para representar una opción para una pregunta.

    :param _name (str): Nombre del modelo en Odoo
    :param _description (str): Descripción del modelo en Odoo
    :param pregunta_id (int): Identificador de la pregunta
    :param opcion_texto (str): Texto de la opción
    :param valor (int): Valor de la opción
    """

    _name = "opcion"
    _description = "Opcion para una pregunta"

    pregunta_id = fields.Many2one("pregunta", string="Pregunta")
    opcion_texto = fields.Char("Opción", required=True)
    valor = fields.Integer(required=True, default=0)

    @api.constrains("opcion_texto")
    def checar_texto(self):
        """
        Método para verificar que el texto de la opción no sea vacío.
        """
        for registro in self:
            if registro.opcion_texto:
                if "\"" in registro.opcion_texto or "\'" in registro.opcion_texto:
                    raise ValidationError(_("El texto de la opción no puede contener comillas simples o dobles."))