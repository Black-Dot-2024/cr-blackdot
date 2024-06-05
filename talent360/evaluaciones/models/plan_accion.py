from odoo import models, fields


class PlanAccion(models.Model):
    """
    Modelo para representar un plan de acción.
    
    :param _name (str): Nombre del modelo en Odoo
    :param _description (str): Descripción del modelo en Odoo
    
    :param descripcion (str): Descripción del plan de acción generado por IA
    :param evaluacion_id (int): ID de la evaluación a la que pertenece el plan de acción
    """

    _name = "plan.accion"
    _description = "Respuesta a una pregunta"
    plan_accion = fields.Text(string="Plan de acción")
    descripcion = fields.Text(string="Descripción")
    evaluacion_id = fields.Many2one("evaluacion", string="Evaluación", required=True, ondelete="cascade")
    
    def guardar_plan_accion_action(self, evaluacion_id, descripcion):
        """
        Método para guardar un plan de acción.
        Este método guarda un plan de acción en la base de datos.

        :param evaluacion: objeto de la evaluación a guardar el plan de acción
        
        :return: Respuesta guardada en la base de datos
        """
        
        respuesta = None
        
        respuesta = self.env["plan.accion"].create(
            {
                "descripcion": descripcion,
                "evaluacion_id": evaluacion_id,
            }
        )
        
        return respuesta
    

