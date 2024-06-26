from odoo import models, fields, api, _
import secrets


class UsuarioEvaluacionRel(models.Model):
    """
    Modelo para representar la relación entre evaluaciones y usuarios

    :param _name (str): Nombre del modelo en Odoo
    :param _description (str): Descripción del modelo en Odoo
    :param evaluacion_id (int): Identificador de la evaluación
    :param usuario_id (int): Identificador del usuario
    :param contestada (str): Estado de la evaluación
    :param evaluacion_nombre (str): Nombre de la evaluación
    :param evaluacion_estado (str): Estado de la evaluación
    :param evaluacion_tipo (str): Tipo de la evaluación
    :param evaluacion_usuario_ids (list): Lista de usuarios de la evaluación
    :param token (str): Token para la evaluación
    """

    _name = "usuario.evaluacion.rel"
    _description = "Relación entre evaluacion y usuarios"
    _rec_name = "evaluacion_nombre"

    evaluacion_id = fields.Many2one("evaluacion", string="Evaluacion")
    usuario_id = fields.Many2one("res.users", string="Usuario")
    contestada = fields.Selection(
        [
            ("pendiente", "Pendiente"),
            ("contestada", "Contestada"),
        ],
        default="pendiente",
    )

    # Campos relacionados para acceder a atributos de evaluacion
    evaluacion_nombre = fields.Char(
        related="evaluacion_id.nombre", string="Nombre de Evaluación", readonly=True
    )
    evaluacion_estado = fields.Selection(
        related="evaluacion_id.estado", string="Estado de Evaluación", readonly=True
    )
    evaluacion_tipo = fields.Selection(
        related="evaluacion_id.tipo", string="Tipo de Evaluación", readonly=True
    )
    evaluacion_usuario_ids = fields.Many2many(
        related="evaluacion_id.usuario_ids",
        string="Usuarios de Evaluación",
        readonly=True,
    )

    token = fields.Char()

    usuario_externo_id = fields.Many2one("usuario.externo", string="Usuario Externo")

    def _onchange_contestada(self):
        """Método para actualizar el porcentaje de respuestas de la evaluación."""

        self.evaluacion_id._compute_porcentaje_respuestas()

    def action_get_estado(self, evaluacion_id, token):
        """Método para obtener el estado de la evaluación para el usuario.

        :param usuario_id: ID del usuario
        :param evaluacion_id: ID de la evaluación
        :return: estado de la evaluación
        """
        usuario_evaluacion = self.env["usuario.evaluacion.rel"].search(
            [("evaluacion_id.id", "=", evaluacion_id), ("token", "=", token)]
        )

        return usuario_evaluacion.contestada

    def action_update_estado(self, evaluacion_id, token):
        """Método para actualizar el estado de la evaluación para el usuario.

        :param usuario_id: ID del usuario
        :param evaluacion_id: ID de la evaluación
        """

        usuario_evaluacion = self.env["usuario.evaluacion.rel"].search(
            [("evaluacion_id.id", "=", evaluacion_id), ("token", "=", token)]
        )

        usuario_evaluacion.write({"contestada": "contestada"})
        usuario_evaluacion._onchange_contestada()

    def enviar_evaluacion_action(self, evaluacion_id):
        """
        Ejecuta la acción de redireccionar a la lista de evaluaciones y devuelve un diccionario

        Este método utiliza los parámetros necesarios para redireccionar a la lista de evaluaciones

        :return: Un diccionario que contiene todos los parámetros necesarios para redireccionar la
        a una vista de la lista de las evaluaciones.

        """

        length = 32
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        extension_url = "evaluacion/responder"

        usuario_evaluacion = self.env["usuario.evaluacion.rel"].search(
            [("evaluacion_id.id", "=", evaluacion_id)]
        )

        evaluacion = self.env["evaluacion"].browse(evaluacion_id)

        lista_mails = []
        for usuario in usuario_evaluacion:
            token = secrets.token_hex(length)
            if not usuario.token:
                if usuario.usuario_id:
                    correo = usuario.usuario_id.email
                    nombre = usuario.usuario_id.name
                elif usuario.usuario_externo_id:
                    correo = usuario.usuario_externo_id.email
                    nombre = usuario.usuario_externo_id.nombre
                else:
                    raise ValueError(_("No se encontró un usuario asociado"))

                usuario.write({"token": token, "contestada": "pendiente"})
                evaluacion_url = f"{base_url}/{extension_url}/{evaluacion_id}/{token}"
                if evaluacion.contenido_correo:
                    mail = {
                        "subject": "Invitación para completar la evaluación",
                        "email_from": "talent360@cr-organizacional.com",
                        "email_to": correo,
                        "body_html": f"""
                                    {evaluacion.contenido_correo}
                                    <p><a href="{evaluacion_url}">Comenzar {evaluacion.nombre}</a></p>
                                    """ 
                    }
                else:   
                    mail = {
                        "subject": "Invitación para completar la evaluación",
                        "email_from": "talent360@cr-organizacional.com",
                        "email_to": correo,
                        "body_html": 
                            f"""<p>Hola, <strong>{nombre}</strong>,</p>
                            <p>En <strong>{self.env.user.company_id.name}</strong> estamos interesados en que contestes la siguiente evaluación, tu participación nos ayudará a mejorar y crecer como organización. La evaluación estará disponible del <strong>{evaluacion.fecha_inicio}</strong> al <strong>{evaluacion.fecha_final}</strong>. Puedes comenzar la evaluación haciendo clic en el siguiente enlace: <a href="{evaluacion_url}">Comenzar {evaluacion.nombre}</a></p>
                            <p>Gracias por tu colaboración.</p>
                            <p>Atentamente,</p>
                            <p><strong>{self.env.user.name}</strong> from <strong>{self.env.user.company_id.name}</strong></p>
                            <p>Correo de contacto: <a href="mailto:{self.env.user.email}">{self.env.user.email}</a></p>
                            """,
                    }

                lista_mails.append(mail)

        self.env["mail.mail"].create(lista_mails)
