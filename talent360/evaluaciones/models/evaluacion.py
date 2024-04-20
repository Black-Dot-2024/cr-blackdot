from odoo import models, fields

# Creamos el modelo de la evaluación
class Evaluacion(models.Model):

    # Definimos el nombre y la descripción de la tabla
    _name = "evaluacion"
    _description = "Evaluacion de pesonal"

    # Heredamos el modelo mail.thread para poder enviar mensajes
    _inherit = "mail.thread"

    # Definimos el nombre y el estado de la evaluación
    nombre = fields.Char(required=True)
    estado = fields.Selection(
        [
            ("borrador", "Borrador"),
            ("publicado", "Publicado"),
            ("finalizado", "Finalizado"),
        ],
        default="borrador",
        required=True,
    )

    # Relaciones con otros modelos
    # Definimos una relación muchos a muchos con el modelo pregunta
    pregunta_ids = fields.Many2many(
        "pregunta",
        "pregunta_evaluacion_rel",
        "evaluacion_id",
        "pregunta_id",
        string="Preguntas",
    )

    # Definimos una relación muchos a muchos con el modelo competencia
    competencia_ids = fields.Many2many(
        "competencia",
        "competencia_evaluacion_rel",
        "evaluacion_id",
        "competencia_id",
        string="Competencias",
    )

    # Definimos una relación muchos a muchos con el modelo usuario
    usuario_ids = fields.Many2many(
        "res.users",
        "usuario_evaluacion_rel",
        "evaluacion_id",
        "usuario_id",
        string="Asignados",
    )
    
    # Método para enviar la evaluación a los usuarios asignados
    def enviar_evaluacion(self):
        # Creamos una lista para almacenar los nombres de los usuarios
        usuarios = []

        # Enviamos un mensaje a cada usuario asignado
        for usuario in self.usuario_ids:
            self.message_post(
                body=f"Se te ha asignado la evaluación: {self.nombre}",
                partner_ids=[usuario.partner_id.id],
            )
            usuarios.append(usuario.partner_id.name)
        
        self.estado = "publicado"

        # Mostrar una notificación con los usuarios a los que se les ha asignado la evaluación
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "¡Has enviado una evaluación!",
                "type": "success",
                "message": f"Se ha asignado la evaluación {self.nombre} a {', '.join(usuarios)}",
                "sticky": False,
            }
        }