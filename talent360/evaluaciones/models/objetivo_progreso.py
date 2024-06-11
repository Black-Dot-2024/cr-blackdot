from odoo import fields, models, api, exceptions, _

class ObjetivoProgreso(models.Model):
    """
    Modelo para representar un progreso de un objetivo en Odoo

    :param _name(str): Nombre del modelo en Odoo
    :param _description (str): Descripción del modelo en Odoo
    :param objetivo_id (fields.Many2One): Relación con el objetivo
    :param fecha (fields.Date): Fecha del avance
    :param progreso (fields.Float): Progreso del objetivo
    :param comentarios (fields.Text): Comentarios del progreso
    """
    
    _name = "objetivo.progreso"
    _description = "Objetivo Progreso"

    objetivo_id = fields.Many2one("objetivo", string="Objetivo", required=True, ondelete="cascade")
    fecha = fields.Date(string="Fecha", required=True)
    progreso = fields.Float(string="Progreso", required=True)
    
    comentarios = fields.Text(string="Comentarios", required=True)
