from odoo import http, _
from odoo.http import request
from odoo.exceptions import AccessError, UserError
import json
import werkzeug


class EvaluacionesController(http.Controller):
    """Controlador para manejar las solicitudes relacionadas con las evaluaciones."""

    @http.route(
        "/evaluacion/reporte/<model('evaluacion'):evaluacion>", type="http", auth="user", website=True
    )
    def reporte_controller(self, evaluacion, filtros=None):
        """Método para generar y mostrar un reporte de evaluación.
        Este método verifica que el usuario tenga los permisos necesario, obtiene los datos
        del modelo de evaluaciones y renderiza el reporte con esos datos.

        :param evaluacion: objeto de la evaluación a generar el reporte
        :param filtros: filtros a aplicar al reporte

        :return: html renderizado del template con los datos del reporte
        """

        # Verificar permisos de usuario
        if not request.env.user.has_group(
            "evaluaciones.evaluaciones_cliente_cr_group_user"
        ):
            raise AccessError(_("No tienes permitido acceder a este recurso."))

        # Parsear filtros
        if filtros:
            filtros = json.loads(filtros)
            filtros = {
                categoria: valores for categoria, valores in filtros.items() if valores
            }

        parametros = evaluacion.generar_datos_reporte_generico_action(filtros)

        parametros["filtros"] = filtros

        tiene_respuestas = True

        for pregunta in parametros["preguntas"]:
            if not pregunta["respuestas"]:
                tiene_respuestas = False
                break
    
        if not tiene_respuestas:
            return request.render("evaluaciones.encuestas_reporte_no_respuestas", parametros)        

        if evaluacion.incluir_demograficos:
            datos_demograficos = evaluacion.generar_datos_demograficos(filtros)
            mapeo_categorias = {
                "departamento": "Departamento",
                "generacion": "Generación",
                "puesto": "Puesto",
                "genero": "Género",
            }
            
            parametros["datos_demograficos"] = []

            for categoria, valores in datos_demograficos.items():
                # Si todos los datos son N/A, omitir la categoría
                if len(valores) == 1 and valores[0]["nombre"] == "N/A":
                    continue

                if categoria in ["nombre", "anio_nacimiento"]:
                    continue

                nombre = mapeo_categorias.get(categoria, categoria)
                parametros["datos_demograficos"].append(
                    {
                        "categoria": nombre,
                        "valores": valores,
                    }
                )
                
            parametros.update(datos_demograficos)
        if evaluacion.tipo == "NOM_035":
            parametros.update(evaluacion.generar_datos_reporte_NOM_035_action(filtros))
            return request.render("evaluaciones.encuestas_reporte_nom_035", parametros)
        elif evaluacion.tipo == "CLIMA":
            parametros.update(evaluacion.generar_datos_reporte_clima_action(filtros))
            return request.render("evaluaciones.encuestas_reporte_clima", parametros)
        elif evaluacion.tipo == "generico":
            return request.render("evaluaciones.encuestas_reporte_generico", parametros)
        else:
            raise ValueError(_("Tipo de evaluación no soportado para reporte."))

    @http.route(
        "/evaluacion/responder/<int:evaluacion_id>/<string:token>",
        type="http",
        auth="public",
        website=True,
    )
    def responder_evaluacion_controller(self, evaluacion_id, token):
        """Método para desplegar el formulario de permitir al usuario responder una evaluación.
        Este método verifica que el usuario tenga los permisos necesario, obtiene los datos
        del modelo de evaluaciones y renderiza el formulario con esos datos.

        :return: html renderizado del template con los datos del formulario
        """
        usuario_eva_mod = request.env["usuario.evaluacion.rel"]

        evaluacion = request.env["evaluacion"].sudo().browse(evaluacion_id)

        usuario_eval_relacion = usuario_eva_mod.sudo().search(
            [("evaluacion_id", "=", evaluacion.id), ("token", "=", token)]
        )

        if not usuario_eval_relacion:
            return request.render("evaluaciones.evaluacion_responder_form_draft")

        es_link_externo = bool(usuario_eval_relacion.usuario_externo_id)

        if not es_link_externo and usuario_eval_relacion.usuario_id != request.env.user:
            return request.render("evaluaciones.evaluacion_responder_form_draft")

        # Obtén la evaluación basada en el ID
        parametros = evaluacion.get_evaluaciones_action(evaluacion_id)

        parametros["contestada"] = usuario_eva_mod.sudo().action_get_estado(
            evaluacion_id, token
        )

        parametros["token"] = token

        # Renderiza la plantilla con la evaluación
        return request.render("evaluaciones.evaluaciones_responder", parametros)

    @http.route("/evaluacion/contestada", type="http", auth="public", website=True)
    def evaluacion_contestada_controller(self, **post):
        """Método para desplegar un mensaje de que la evaluación ya fue contestada.
        Este método renderiza un mensaje indicando que la evaluación ya fue contestada.

        :return: html renderizado del template con el mensaje
        """

        return request.render("evaluaciones.evaluacion_responder_form_done")

    @http.route(
        "/evaluacion/responder",
        type="http",
        auth="public",
        website=True,
        methods=["POST"],
        csrf=False,
    )
    def responder_evaluacion_controller_post(self, **post):
        """Método para procesar la respuesta del formulario de evaluación.
        Este método verifica que el usuario tenga los permisos necesario, obtiene los datos
        del modelo de evaluaciones y guarda la respuesta del usuario.

        :return: redirección a la página de inicio
        """

        post_data = json.loads(request.httprequest.data)

        valores_radios = post_data.get("radioValues")
        valores_radios_escala = post_data.get("radioValuesScale")
        valores_textarea = post_data.get("textareaValues")
        evaluacion_id = post_data.get("evaluacion_id")
        respuesta_modelo = request.env["respuesta"]
        token = post_data.get("token")

        usuario_evaluacion_rel = (
            request.env["usuario.evaluacion.rel"]
            .sudo()
            .search([("token", "=", token), ("evaluacion_id.id", "=", evaluacion_id)])
        )

        if usuario_evaluacion_rel.contestada == "contestada":
            raise UserError("La evaluación ya fue contestada.")

        es_link_externo = bool(usuario_evaluacion_rel.usuario_externo_id)

        if (
            not es_link_externo
            and usuario_evaluacion_rel.usuario_id != request.env.user
        ):
            raise AccessError("No tienes permiso para contestar esta evaluación.")
        else:
            usuario_id = usuario_evaluacion_rel.usuario_id.id

        for pregunta_id, valor_radio in valores_radios.items():
            if pregunta_id in valores_radios:
                valor_radio = valores_radios[pregunta_id]
                if not es_link_externo:
                    resp = respuesta_modelo.sudo().guardar_respuesta_action(
                        valor_radio,
                        None,
                        int(evaluacion_id),
                        int(usuario_id),
                        int(pregunta_id),
                        None,
                        False,
                    )
                else:
                    resp = respuesta_modelo.sudo().guardar_respuesta_action(
                        valor_radio,
                        None,
                        int(evaluacion_id),
                        None,
                        int(pregunta_id),
                        token,
                        False,
                    )
            else:
                continue

        for pregunta_id, valor_textarea in valores_textarea.items():
            if pregunta_id in valores_textarea:
                valor_textarea = valores_textarea[pregunta_id]
                if not es_link_externo:
                    resp = respuesta_modelo.sudo().guardar_respuesta_action(
                        None,
                        valor_textarea,
                        int(evaluacion_id),
                        int(usuario_id),
                        int(pregunta_id),
                        None,
                        False,
                    )
                else:
                    resp = respuesta_modelo.sudo().guardar_respuesta_action(
                        None,
                        valor_textarea,
                        int(evaluacion_id),
                        None,
                        int(pregunta_id),
                        token,
                        False,
                    )
            else:
                continue

        for pregunta_id, valor_radio in valores_radios_escala.items():
            if pregunta_id in valores_radios_escala:
                valor_radio = valores_radios_escala[pregunta_id]
                if not es_link_externo:
                    resp = respuesta_modelo.sudo().guardar_respuesta_action(
                        valor_radio,
                        None,
                        int(evaluacion_id),
                        int(usuario_id),
                        int(pregunta_id),
                        None,
                        True,
                    )
                else:
                    resp = respuesta_modelo.sudo().guardar_respuesta_action(
                        valor_radio,
                        None,
                        int(evaluacion_id),
                        None,
                        int(pregunta_id),
                        token,
                        True,
                    )
            else:
                continue

        # Actualiza el estado de la evaluación para el usuario
        usuario_eva_mod = request.env["usuario.evaluacion.rel"]

        usuario_eva_mod.sudo().action_update_estado(evaluacion_id, token)
