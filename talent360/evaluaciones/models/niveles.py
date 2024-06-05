from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Niveles(models.Model):
    """
    Modelo para representar los niveles de semaforización de las evaluaciones.

    :param _name (str): Nombre del modelo en Odoo.
    :param _description (str): Descripción del modelo en Odoo.
    :param evaluacion_id (Many2one): Relación con el modelo de evaluación.
    :param descripcion_nivel (Char): Descripción del nivel.
    :param techo (Integer): Ponderación del nivel.
    :param color (Char): Color del nivel.
    """

    _name = "niveles"
    _description = "Niveles de semaforización"

    evaluacion_id = fields.Many2one("evaluacion", string="Evaluación")
    descripcion_nivel = fields.Char(string="Descripción", default="Cambiar descripción", size=20)
    techo = fields.Float(string="Ponderación", default=100)
    color = fields.Char(string="Color", default="white")