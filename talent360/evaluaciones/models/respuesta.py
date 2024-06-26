from odoo import models, fields
from odoo.http import request


class Respuesta(models.Model):
    """
    Modelo para representar las respuestas a las preguntas

    :param _name (str): Nombre del modelo en Odoo
    :param _description (str): Descripción del modelo en Odoo
    :param pregunta_id (int): Identificador de la pregunta
    :param usuario_id (int): Identificador del usuario
    :param evaluacion_id (int): Identificador de la evaluación
    :param pregunta_texto (str): Texto de la pregunta
    :param respuesta_texto (str): Texto de la respuesta
    :param token (str): Token de la respuesta
    :param opcion_id (int): Identificador de la opción
    :param respuesta_mostrar (str): Respuesta a mostrar
    """

    _name = "respuesta"
    _description = "Respuesta a una pregunta"
    _rec_name = "respuesta_mostrar"

    pregunta_id = fields.Many2one("pregunta", string="Preguntas")
    usuario_id = fields.Many2one("res.users", string="Usuario")
    usuario_externo_id = fields.Many2one("usuario.externo", string="Usuario externo")
    evaluacion_id = fields.Many2one("evaluacion", string="Evaluacion")
    pregunta_texto = fields.Char(related="pregunta_id.pregunta_texto")
    respuesta_texto = fields.Char("Respuesta", size=500)
    token = fields.Char()
    opcion_id = fields.Many2one("opcion", string="Opción")

    respuesta_mostrar = fields.Char(

        string="Respuesta", compute="_compute_respuesta_mostrar", search="_buscar_respuesta_mostrar" 
    )

    valor_respuesta = fields.Float(
        string="Valor de la respuesta",
        compute="_compute_valor_respuesta",
        store=False,
    )

    texto = fields.Char(string="Texto")

    def _buscar_respuesta_mostrar(self, operator, value):
        """
        Método para buscar la respuesta a mostrar en la vista.

        :param operator: Operador de búsqueda
        :param value: Valor a buscar
        :return: Dominio de búsqueda
        """

        return [
            '|',
            '|',
            ('respuesta_texto', operator, value),
            ('opcion_id.opcion_texto', operator, value),
            ('texto', operator, value)
        ]


    def guardar_respuesta_action(
        self, radios, texto, evaluacion_id, usuario_id, pregunta_id, token, escala=False
    ):
        """Método para guardar la respuesta de una pregunta.
        Este método se encarga de guardar la respuesta de una pregunta en la base de datos.

        :param radios (str): Respuesta de tipo radio
        :param texto (str): Respuesta de tipo texto
        :param evaluacion_id (int): Identificador de la evaluación
        :param usuario_id (int): Identificador del usuario
        :param pregunta_id (int): Identificador de la pregunta
        :param token (str): Token del usuario no autenticado
        :param escala (bool): Indica si la pregunta es de tipo escala

        :return: Respuesta guardada en la base de datos
        """

        resp = None

        if usuario_id:
            if escala:
                resp = self.env["respuesta"].create(
                    {
                        "evaluacion_id": evaluacion_id,
                        "usuario_id": usuario_id,
                        "pregunta_id": pregunta_id,
                        "respuesta_texto": radios,
                    }
                )

            elif texto:
                resp = self.env["respuesta"].create(
                    {
                        "evaluacion_id": evaluacion_id,
                        "usuario_id": usuario_id,
                        "pregunta_id": pregunta_id,
                        "respuesta_texto": texto,
                    }
                )

            elif radios:
                resp = self.env["respuesta"].create(
                    {
                        "evaluacion_id": evaluacion_id,
                        "usuario_id": usuario_id,
                        "pregunta_id": pregunta_id,
                        "opcion_id": radios,
                    }
                )

        else:
            usuario_externo_id = self.env["usuario.evaluacion.rel"].search(
                [
                    ("token", "=", token),
                    ("evaluacion_id", "=", evaluacion_id),
                ]
            ).usuario_externo_id

            if escala:
                resp = self.env["respuesta"].create(
                    {
                        "evaluacion_id": evaluacion_id,
                        "token": token,
                        "pregunta_id": pregunta_id,
                        "respuesta_texto": radios,
                        "usuario_externo_id": usuario_externo_id.id,
                    }
                )

            elif texto:
                resp = self.env["respuesta"].create(
                    {
                        "evaluacion_id": evaluacion_id,
                        "token": token,
                        "pregunta_id": pregunta_id,
                        "respuesta_texto": texto,
                        "usuario_externo_id": usuario_externo_id.id,
                    }
                )

            elif radios:
                resp = self.env["respuesta"].create(
                    {
                        "evaluacion_id": evaluacion_id,
                        "token": token,
                        "pregunta_id": pregunta_id,
                        "opcion_id": radios,
                        "usuario_externo_id": usuario_externo_id.id,
                    }
                )

        return resp

    def _compute_respuesta_mostrar(self):
        """
        Método para calcular la respuesta a mostrar en la vista.

        :return: Respuesta a mostrar en la vista
        """

        for registro in self:
            respuesta_texto = "N/A"

            if registro.pregunta_id.tipo == "escala":
                respuesta_texto = registro.pregunta_id.mapeo_valores_escala[
                    registro.pregunta_id.ponderacion
                ][registro.respuesta_texto]

                request.env["respuesta"].sudo().search(
                    [
                        ("pregunta_id", "=", registro.pregunta_id.id),
                        ("evaluacion_id", "=", registro.evaluacion_id.id),
                        ("usuario_id", "=", registro.usuario_id.id),
                    ]
                ).write({"texto": respuesta_texto})
            elif registro.pregunta_id.tipo == "multiple_choice":
                respuesta_texto = registro.opcion_id.opcion_texto
            else:
                respuesta_texto = registro.respuesta_texto

            registro.respuesta_mostrar = respuesta_texto

    def _compute_valor_respuesta(self):
        """
        Método para calcular el valor de la respuesta.

        :return: Valor de la respuesta
        """
        for registro in self:
            if registro.pregunta_id.tipo == "escala":
                registro.valor_respuesta = int(registro.respuesta_texto)
            elif registro.pregunta_id.tipo == "multiple_choice":
                registro.valor_respuesta = registro.opcion_id.valor
            else:
                registro.valor_respuesta = 0