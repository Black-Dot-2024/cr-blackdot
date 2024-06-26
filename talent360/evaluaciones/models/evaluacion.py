from venv import logger
from odoo import api, models, fields, _
from collections import defaultdict, Counter
from odoo import exceptions
from datetime import timedelta
from io import BytesIO
import pandas as pd
import base64
from odoo.exceptions import ValidationError
import logging


_logger = logging.getLogger(__name__)
class Evaluacion(models.Model):
    """
    Modelo para representar una evaluación de personal en Odoo.

    :param _name (str): Nombre del modelo en Odoo.
    :param _description (str): Descripción del modelo en Odoo.
    :param nombre (fields.Char): Nombre de la evaluación. Es un campo obligatorio.
    :param tipo (fields.Selection): Tipo de evaluación con opciones 'CLIMA', 'NOM_035' y 'competencia'. Por defecto, es 'competencia'.
    :param descripcion (fields.Text): Descripción de la evaluación.
    :param estado (fields.Selection): Estado de la evaluación con opciones 'borrador', 'publicado' y 'finalizado'. Por defecto, es 'borrador'.
    :param pregunta_ids (fields.Many2many): Relación de muchos a muchos con el modelo 'pregunta' para almacenar las preguntas asociadas a la evaluación.
    :param competencia_ids (fields.Many2many): Relación de muchos a muchos con el modelo 'competencia' para almacenar las competencias asociadas a la evaluación.
    :param usuario_ids (fields.Many2many): Relación de muchos a muchos con el modelo 'res.users' para asignar usuarios a la evaluación.
    :param usuario_externo_ids (fields.Many2many): Relación de muchos a muchos con el modelo 'usuario.externo' para asignar usuarios externos a la evaluación.
    :param fecha_inicio (fields.Date): Fecha de inicio de la evaluación. Es un campo obligatorio.
    :param fecha_final (fields.Date): Fecha de finalización de la evaluación. Es un campo obligatorio.
    :param mensaje (fields.Text): Mensaje de bienvenida para la evaluación.
    :param incluir_demograficos (fields.Boolean): Campo booleano para indicar si se incluirán datos demográficos en el reporte. Por defecto, es True.
    """

    _name = "evaluacion"
    _description = "Evaluacion de personal"
    _rec_name = "nombre"
    nombre = fields.Char(string="Título de la evaluación", required=True, size=50)
    escalar_format = fields.Selection([
        ("numericas", "Numéricas"),
        ("textuales", "Textuales"),
        ("caritas", "LIKERT"),
        ("estrellas", "Estrellas")
    ], string="Formato para las preguntas escalares", required=True, default="numericas")

    tipo = fields.Selection(
        [
            ("CLIMA", "Clima Organizacional"),
            ("NOM_035", "NOM 035"),
            ("competencia", "Competencia"),
            ("generico", "Genérico"),
        ],
        required=True,
        default="generico",
    )
    descripcion = fields.Text(string="Descripción", size=300)
    estado = fields.Selection(
        [
            ("borrador", "Borrador"),
            ("publicado", "Abierta"),
            ("finalizado", "Cerrada"),
        ],
        default="borrador",
        required=True,
    )

    pregunta_ids = fields.Many2many(
        "pregunta",
        "pregunta_evaluacion_rel",
        "evaluacion_id",
        "pregunta_id",
        string="Preguntas",
    )

    competencia_ids = fields.Many2many(
        "competencia",
        "competencia_evaluacion_rel",
        "evaluacion_id",
        "competencia_id",
        string="Competencias",
    )

    usuario_ids = fields.Many2many(
        "res.users",
        "usuario_evaluacion_rel",
        "evaluacion_id",
        "usuario_id",
        string="Asignados",
    )

    usuario_externo_ids = fields.Many2many(
        "usuario.externo",
        "usuario_evaluacion_rel",
        "evaluacion_id",
        "usuario_externo_id",
        string="Asignados Externos",
    )

    niveles = fields.One2many(
        "niveles",
        "evaluacion_id",
        string="Niveles",
    )

    fecha_inicio = fields.Date(string="Fecha de inicio", required=True)
    fecha_final = fields.Date(string="Fecha de finalización", required=True)
    mensaje_bienvenida = fields.Text(
        string="Mensaje de bienvenida",
    )
    contenido_correo = fields.Text(
        string="Contenido del correo",
    )
    mensaje_agradecimiento = fields.Text(
        string="Mensaje de agradecimiento",
    )

    incluir_demograficos = fields.Boolean(
        string="Incluir datos demográficos", default=True
    )
    
    plan_accion = fields.Text(string="Plan de acción")

    @api.constrains("descripcion")
    def _checar_largo(self):
        for registro in self:
            if len(registro.descripcion or "") > 300:
                raise ValidationError(_("La descripción no puede tener más de 300 caracteres."))


    @api.constrains("fecha_inicio", "fecha_final")
    def checar_fechas(self):
        """
        Valida que la fecha de inicio sea anterior a la fecha final.
        """
        for registro in self:

            # Si ya se creo, se compara contra la fecha de creación
            if registro.create_date:
                fecha_creacion = registro.create_date.date() - timedelta(days=1)
                if registro.fecha_inicio < fecha_creacion:
                    raise exceptions.ValidationError(
                        _(
                            f"La fecha de inicio debe ser igual o posterior a la fecha de creación de la evaluación ({fecha_creacion.strftime('%d/%m/%Y')})."
                        )
                    )
            # Si es nuevo, se compara contra la fecha actual
            else:
                fecha_actual = fields.Date.today() - timedelta(days=1)
                if registro.fecha_inicio:
                    # Verifica que la fecha de inicio no sea menor a la fecha actual
                    if registro.fecha_inicio < fecha_actual:
                        raise exceptions.ValidationError(
                            _(
                                "La fecha de inicio debe ser igual o posterior a la fecha actual."
                            )
                        )

            if registro.fecha_inicio and registro.fecha_final:
                # Verifica que la fecha de inicio sea antes de la fecha final
                if registro.fecha_inicio > registro.fecha_final:
                    raise exceptions.ValidationError(
                        _("La fecha de inicio debe ser anterior a la fecha final")
                    )

    @api.constrains("pregunta_ids")
    def checar_preguntas(self):
        """
        Valida que la evaluación tenga al menos una pregunta.
        """
        for registro in self:
            if not registro.pregunta_ids:
                raise exceptions.ValidationError(
                    _("La evaluación debe tener al menos una pregunta.")
                )
                
    @api.constrains("niveles")
    def checar_niveles(self):
        for registro in self:
            for nivel in registro.niveles:
                if nivel.descripcion_nivel == "Cambiar descripción":
                    raise exceptions.ValidationError(
                        _("En la semaforización, debes cambiar las descripciones de los niveles con descripción de 'Cambiar descripción'.")
                    )

    @api.model
    def default_get(self, fields_list):
        defaults = super(Evaluacion, self).default_get(fields_list)

        # Obtener tipo del contexto
        tipo = self._context.get("tipo", "generico")

        defaults["fecha_inicio"] = fields.Date.today()
        defaults["fecha_final"] = fields.Date.today()

        template_id = False

        if tipo == "clima":
            defaults["descripcion"] = "La evaluación Clima es una herramienta de medición de clima organizacional, cuyo objetivo es conocer la percepción que tienen las personas que laboran en los centros de trabajo, sobre aquellos aspectos sociales que conforman su entorno laboral y que facilitan o dificultan su desempeño."
            defaults["tipo"] = "CLIMA"

            defaults["niveles"] = [
                (0, 0, {"descripcion_nivel": "Muy malo", "techo": 20, "color": "#ff4747"}),
                (0, 0, {"descripcion_nivel": "Malo", "techo": 40, "color": "#ffa446"}),
                (0, 0, {"descripcion_nivel": "Regular", "techo": 60, "color": "#ebae14"}),
                (0, 0, {"descripcion_nivel": "Bueno", "techo": 80, "color": "#5aaf2b"}),
                (0, 0, {"descripcion_nivel": "Muy bueno", "techo": 100, "color": "#2894a7"}),
            ]
            template_id = self.env["ir.model.data"]._xmlid_to_res_id(
                "evaluaciones.template_clima"
            )

        elif tipo == "nom035":
            defaults["descripcion"] = "La NOM 035 tiene como objetivo establecer los elementos para identificar, analizar y prevenir los factores de riesgo psicosocial, así como para promover un entorno organizacional favorable en los centros de trabajo."
            defaults["tipo"] = "NOM_035"
            defaults["fecha_inicio"] = fields.Date.today()
            defaults["fecha_final"] = fields.Date.today()
            template_id = self.env["ir.model.data"]._xmlid_to_res_id(
                "evaluaciones.template_nom035"
            )
        elif tipo == "generico":
            defaults["tipo"] = "generico"

        if template_id:
            template = self.env["template"].browse(template_id)
            if template:
                pregunta_ids = template.pregunta_ids.copy_multi().ids
                defaults["pregunta_ids"] = [(6, 0, pregunta_ids)]

        return defaults

    def evaluacion_clima_action_form(self):
        """
        Ejecuta la acción de copiar preguntas de un template a la evaluación actual y devuelve
        un diccionario con los parámetros necesarios para abrir una ventana de acción en Odoo.

        Nos basamos en el método de `copiar_preguntas_de_template_nom035` para asegurarse de que la evaluación
        actual tenga las preguntas correctas, y luego configura y devuelve un diccionario con
        los detalles para abrir esta evaluación en una vista de formulario específica.

        :return: Un diccionario que contiene todos los parámetros necesarios para abrir la
        evaluación en una vista de formulario específica de Odoo.

        """

        # Retornar la acción con la vista como destino
        return {
            "type": "ir.actions.act_window",
            "name": "Evaluación Clima",
            "res_model": "evaluacion",
            "view_mode": "form",
            "view_id": self.env.ref("evaluaciones.evaluacion_clima_view_form").id,
            "target": "current",
            "context": {"tipo": "clima"},
        }

    def evaluacion_nom035_action_form(self):
        """
        Ejecuta la acción de copiar preguntas de un template a la evaluación actual y devuelve
        un diccionario con los parámetros necesarios para abrir una ventana de acción en Odoo.

        Este método utiliza `copiar_preguntas_de_template_nom035` para asegurarse de que la evaluación
        actual tenga las preguntas correctas, y luego configura y devuelve un diccionario con
        los detalles para abrir esta evaluación en una vista de formulario específica.

        :return: Un diccionario que contiene todos los parámetros necesarios para abrir la
        evaluación en una vista de formulario específica de Odoo.

        """
        return {
            "type": "ir.actions.act_window",
            "name": "NOM 035",
            "res_model": "evaluacion",
            "view_mode": "form",
            "view_id": self.env.ref("evaluaciones.evaluacion_nom035_view_form").id,
            "target": "current",
            "context": {"tipo": "nom035"},
        }

    def evaluacion_360_action_form(self):
        """
        Ejecuta la acción de redireccionar a la evaluación 360 y devuelve un diccionario

        Este método utiliza los parámetros necesarios para redireccionar a la evaluación 360

        :return: Un diccionario que contiene todos los parámetros necesarios para redireccionar la
        a una vista de la evaluación 360.

        """
        self.tipo = "competencia"
        return {
            "type": "ir.actions.act_window",
            "name": "360",
            "res_model": "evaluacion",
            "view_mode": "form",
            "view_id": self.env.ref("evaluaciones.evaluacion_360_view_form").id,
            "target": "current",
            "res_id": self.id,
        }

    def evaluacion_action_tree(self):
        """
        Ejecuta la acción de redireccionar a la lista de evaluaciones y devuelve un diccionario

        Este método utiliza los parámetros necesarios para redireccionar a la lista de evaluaciones

        :return: Un diccionario que contiene todos los parámetros necesarios para redireccionar la
        a una vista de la lista de las evaluaciones.

        """

        return {
            "name": "Evaluación",
            "type": "ir.actions.act_window",
            "res_model": "evaluacion",
            "view_mode": "tree",
            "target": "current",
        }

    def abrir_evaluacion_action_form(self):
        """
        Abre la evaluación en una vista de formulario.

        Este método configura y devuelve un diccionario con los detalles para abrir la evaluación
        actual en una vista de formulario específica dependiendo de su tipo.

        :return: Un diccionario que contiene todos los parámetros necesarios para abrir la
        evaluación en una vista de formulario específica de Odoo.

        """

        if self.tipo == "competencia":
            action = self.env["ir.actions.act_window"]._for_xml_id(
                "evaluaciones.evaluacion_competencias_action"
            )
        else:
            action = self.env["ir.actions.act_window"]._for_xml_id(
                "evaluaciones.evaluacion_generica_action"
            )

        action["res_id"] = self.id

        return action

    def reporte_generico_action(self):
        """
        Genera una acción de URL para el reporte genérico de la evaluación.

        Esta función genera un URL para redirigir
        a un reporte específico de la evaluación actual.

        :return: una acción de redirección al reporte de la evaluación

        """

        if self.porcentaje_respuestas <= 0:
            raise exceptions.ValidationError(
                _("No se puede generar un reporte para una evaluación sin respuestas.")
            )

        return {
            "type": "ir.actions.act_url",
            "url": f"/evaluacion/reporte/{self.id}",
            "target": "new",
        }

    def filtros_reporte_action(self):
        """
        Genera filtros para el reporte de la evaluación.

        Esta función genera filtros para el reporte de la evaluación actual
        y sigue con el proceso de renderización del reporte.

        :return: una acción de redirección al modal creación de filtros
        """

        # Validar si existen respuestas
        if self.porcentaje_respuestas <= 0:
            raise exceptions.ValidationError(
                _("No se puede generar un reporte para una evaluación sin respuestas.")
            )

        datos_demograficos = self.generar_datos_demograficos()

        filtros_ids = []

        mapeo_categorias = {
            "departamento": "Departamento",
            "generacion": "Generación",
            "puesto": "Puesto",
            "genero": "Género",
        }

        for categoria, valores in datos_demograficos.items():
            if categoria in ["nombre", "anio_nacimiento"]:
                continue

            nombre = mapeo_categorias.get(categoria, categoria)

            filtro_id = self.env["filtro.wizard"].create(
                {
                    "categoria": nombre,
                    "categoria_interna": categoria,
                }
            )
            filtros_ids.append(filtro_id.id)

            self.env["filtro.seleccion.wizard"].create(
                [
                    {
                        "texto": valor["nombre"],
                        "categoria": nombre,
                        "filtro_original_id": filtro_id.id,
                    }
                    for valor in valores
                ]
            )

        filtros_wizard = self.env["crear.filtros.wizard"].create(
            {"filtros_ids": [(6, 0, filtros_ids)]}
        )

        return {
            "name": "Filtrar Reporte",
            "type": "ir.actions.act_window",
            "res_model": "crear.filtros.wizard",
            "view_mode": "form",
            "target": "new",
            "res_id": filtros_wizard.id,
            "context": {"actual_evaluacion_id": self.id},
        }

    def generar_datos_reporte_generico_action(self, filtros=None):
        """
        Genera los datos necesarios para el reporte genérico de la evaluación.

        Esta función genera los parámetros requeridos para generar un reporte genérico de la evaluación actual,
        incluyendo las preguntas y las respuestas tabuladas.

        :param filtros: Los filtros a aplicar al reporte.

        :return: Los parámetros necesarios para generar el reporte.

        """
        parametros = {
            "evaluacion": self,
            "preguntas": [],
        }

        for pregunta in self.pregunta_ids:

            respuesta_ids = self.env["respuesta"].search(
                [
                    ("pregunta_id.id", "=", pregunta.id),
                    ("evaluacion_id.id", "=", self.id),
                ]
            )
            if filtros:
                respuesta_ids = respuesta_ids.filtered(
                    lambda r: self.validar_filtro(filtros, r)
                )

            respuestas = [
                respuesta.respuesta_mostrar for respuesta in respuesta_ids]
            respuestas_tabuladas = dict(Counter(respuestas))
            datos_pregunta = {
                "pregunta": pregunta,
                "respuestas": respuestas,
                "respuestas_tabuladas": [
                    {"nombre": nombre, "valor": valor}
                    for nombre, valor in respuestas_tabuladas.items()
                ],
            }

            parametros["preguntas"].append(datos_pregunta)

        return parametros

    def generar_datos_reporte_NOM_035_action(self, filtros=None):
        """
        Genera los datos necesarios para el reporte genérico de la evaluación.

        Esta función genera los parámetros requeridos para generar un reporte genérico de la evaluación actual,
        incluyendo las preguntas y las respuestas tabuladas, agrupadas por categoría y dominio.

        :return: Los parámetros necesarios para generar el reporte.
        """
        # Definir estructura de categorías y dominios
        categorias_orden = [
            "Ambiente de Trabajo",
            "Factores propios de la actividad",
            "Organización del tiempo de trabajo",
            "Liderazgo y relaciones en el trabajo",
        ]
        dominios_orden = [
            "Condiciones en el ambiente de trabajo",
            "Carga de trabajo",
            "Falta de control sobre el trabajo",
            "Jornada de trabajo",
            "Interferencia en la relación trabajo-familia",
            "Liderazgo",
            "Relaciones en el trabajo",
            "Violencia",
        ]

        categorias = {nombre: 0 for nombre in categorias_orden}
        dominios = {nombre: 0 for nombre in dominios_orden}

        final = 0

        for pregunta in self.pregunta_ids:
            if not pregunta.categoria:
                continue
            categoria = dict(pregunta._fields["categoria"].selection).get(
                pregunta.categoria
            )
            dominio = dict(pregunta._fields["dominio"].selection).get(
                pregunta.dominio)
            valor_pregunta = 0

            respuesta_ids = self.env["respuesta"].search(
                [
                    ("pregunta_id.id", "=", pregunta.id),
                    ("evaluacion_id.id", "=", self.id),
                ]
            )

            for respuesta in respuesta_ids:
                if filtros and not self.validar_filtro(filtros, respuesta):
                    continue

                valor_respuesta = respuesta.valor_respuesta
                valor_pregunta += valor_respuesta
                final += valor_respuesta

            # Acumular el valor de la pregunta en la categoría y el dominio correspondientes
            if categoria in categorias:
                categorias[categoria] += valor_pregunta
            if dominio in dominios:
                dominios[dominio] += valor_pregunta

        # Función para asignar color

        # Asignar color a las categorías y dominios
        for categoria in categorias_orden:
            categorias[categoria] = {
                "nombre": categoria,
                "valor": categorias[categoria],
                "color": self.asignar_color(categorias[categoria], categoria=categoria),
            }

        for dominio in dominios_orden:
            dominios[dominio] = {
                "nombre": dominio,
                "valor": dominios[dominio],
                "color": self.asignar_color(dominios[dominio], dominio=dominio),
            }

            # Organizar los parámetros en el orden deseado
        parametros = {
            "evaluacion": self,
            "categorias": [categorias[nombre] for nombre in categorias_orden],
            "dominios": [dominios[nombre] for nombre in dominios_orden],
            "final": final,
        }

        return parametros

    def generar_datos_reporte_clima_action(self, filtros=None):
        """
        Genera los datos necesarios para el reporte de clima organizacional de la evaluación.
        Calcula el porcentaje de satisfacción para cada categoría y departamento.

        :param filtros: Los filtros a aplicar al reporte.

        :return: Los parámetros necesarios para generar el reporte.
        """
        # Categorías para el reporte de clima laboral
        categorias_clima = [
            "Reclutamiento y Selección de Personal",
            "Formación y Capacitación",
            "Permanencia y Ascenso",
            "Corresponsabilidad en la Vida Laboral, Familiar y Personal",
            "Clima Laboral Libre de Violencia",
            "Acoso y Hostigamiento",
            "Accesibilidad",
            "Respeto a la Diversidad",
            "Condiciones Generales de Trabajo",
        ]

        departamentos = []

        # Estructura de datos para las categorías
        detalles_categorias = [
            {
                "nombre": cat,
                "valor": 0,
                "color": "#2894a7",
                "puntuacion": 0,
                "puntuacion_maxima": 0,
                "departamentos": [],
            }
            for cat in categorias_clima
        ]

        # Variables para acumular totales
        total_puntuacion = 0
        total_maximo_posible = 0

        for pregunta in self.pregunta_ids:
            if (
                not pregunta.categoria
                or dict(pregunta._fields["categoria"].selection).get(pregunta.categoria)
                not in categorias_clima
            ):
                continue

            categoria_actual = next(
                (
                    cat
                    for cat in detalles_categorias
                    if cat["nombre"]
                    == dict(pregunta._fields["categoria"].selection).get(
                        pregunta.categoria
                    )
                ),
                None,
            )

            if categoria_actual is None:
                continue

            valor_pregunta = 0
            maximo_pregunta = 0

            for respuesta in pregunta.respuesta_ids:
                if filtros and not self.validar_filtro(filtros, respuesta):
                    continue

                valor_respuesta = respuesta.valor_respuesta
                valor_pregunta += valor_respuesta
                maximo_pregunta += pregunta._calculate_valor_maximo()

                if respuesta.usuario_id:
                    nombre_departamento = (
                        respuesta.usuario_id.department_id.name
                        if respuesta.usuario_id.department_id
                        else "Sin departamento"
                    )
                elif respuesta.usuario_externo_id:
                    usuario_externo = respuesta.usuario_externo_id
                    nombre_departamento = (
                        usuario_externo.departamento
                        if usuario_externo.departamento
                        else "Sin departamento"
                    )
                else:
                    nombre_departamento = "Sin Usuario"

                departamento = next(
                    (
                        dept
                        for dept in categoria_actual["departamentos"]
                        if dept["nombre"] == nombre_departamento
                    ),
                    None,
                )
                if departamento is None:
                    departamentos.append(nombre_departamento)
                    departamento = {
                        "nombre": nombre_departamento,
                        "color": "#2894a7",
                        "puntos": 0,
                        "puntos_maximos": 0,
                    }
                    categoria_actual["departamentos"].append(departamento)

                departamento["puntos"] += valor_respuesta
                departamento["puntos_maximos"] += pregunta._calculate_valor_maximo()

            total_puntuacion += valor_pregunta
            total_maximo_posible += maximo_pregunta
            categoria_actual["puntuacion"] += valor_pregunta
            categoria_actual["puntuacion_maxima"] += maximo_pregunta

        for categoria in detalles_categorias:
            if categoria["puntuacion_maxima"] > 0:
                categoria["valor"] = (
                    categoria["puntuacion"] / categoria["puntuacion_maxima"]
                ) * 100
                categoria["color"] = self.asignar_color_clima(
                    categoria["valor"])

            for departamento in departamentos:
                if not departamento in [
                    dept["nombre"] for dept in categoria["departamentos"]
                ]:
                    categoria["departamentos"].append(
                        {
                            "nombre": departamento,
                            "color": "#2894a7",
                            "puntos": 0,
                            "puntos_maximos": 0,
                        }
                    )

            for dept in categoria["departamentos"]:
                if dept["puntos_maximos"] > 0:
                    dept["valor"] = (dept["puntos"] /
                                     dept["puntos_maximos"]) * 100
                    dept["color"] = self.asignar_color_clima(dept["valor"])
                else:
                    dept["valor"] = 0

        total_porcentaje = round(
            (
                (total_puntuacion / total_maximo_posible) * 100
                if total_maximo_posible > 0
                else 0
            ),
            2,
        )

        # Organizar los parámetros en el orden deseado
        parametros = {
            "evaluacion": self,
            "categorias": detalles_categorias,
            "total": total_puntuacion,
            "total_maximo": total_maximo_posible,
            "total_porcentaje": total_porcentaje,
        }

        return parametros

    def validar_filtro(self, filtros, respuesta=None, datos_demograficos=None):
        """
        Valida si una respuesta cumple con los filtros especificados.

        :param filtros: Los filtros a aplicar.
        :param respuesta: La respuesta a validar.
        :param datos_demograficos: Los datos demográficos del usuario.

        :return: True si la respuesta cumple con los filtros, False en caso contrario.
        """

        if not filtros:
            return True

        if not datos_demograficos:
            if not respuesta:
                return False

            if respuesta.usuario_id:
                datos_demograficos = respuesta.usuario_id.obtener_datos_demograficos()
            elif respuesta.usuario_externo_id:
                datos_demograficos = (
                    respuesta.usuario_externo_id.obtener_datos_demograficos()
                )
            else:
                return False

        for _, filtro in filtros.items():
            categoria = filtro["categoria_interna"]
            if not (categoria in datos_demograficos.keys()):
                continue

            if not datos_demograficos[categoria] in filtro["valores"]:
                return False

        return True

    def generar_datos_demograficos(self, filtros=None):
        """
        Genera los datos demográficos de la evaluación.

        :return: Los datos demográficos de los usuarios asignados a la evaluación. Incuye departamentos, generaciones, puestos y géneros.
        """
        datos_demograficos = []
        # SQL
        usuario_evaluacion = self.env["usuario.evaluacion.rel"].search(
            [
                ("evaluacion_id.id", "=", self.id),
                ("contestada", "=", "contestada"),
                ("usuario_id.id", "in", self.usuario_ids.mapped("id")),
            ]
        )

        for usuario in usuario_evaluacion.mapped("usuario_id"):
            datos_demograficos_usuario = usuario.obtener_datos_demograficos()
            if filtros and not self.validar_filtro(
                filtros, datos_demograficos=datos_demograficos_usuario
            ):
                continue

            datos_demograficos.append(datos_demograficos_usuario)

        usuario_evaluacion_externo = self.env["usuario.evaluacion.rel"].search(
            [
                ("evaluacion_id.id", "=", self.id),
                ("contestada", "=", "contestada"),
                ("usuario_externo_id.id", "in", self.usuario_externo_ids.ids),
            ]
        )

        for usuario_externo in usuario_evaluacion_externo.mapped("usuario_externo_id"):
            datos_demograficos_usuario = usuario_externo.obtener_datos_demograficos()
            if filtros and not self.validar_filtro(
                filtros, datos_demograficos=datos_demograficos_usuario
            ):
                continue

            datos_demograficos.append(datos_demograficos_usuario)

        atributos = defaultdict(lambda: defaultdict(int))

        for dato in datos_demograficos:
            for categoria, valor in dato.items():
                atributos[categoria][valor] += 1

        respuestas = {}
        for categoria, valores in atributos.items():
            respuestas[categoria] = [
                {"nombre": nombre, "valor": conteo}
                for nombre, conteo in valores.items()
            ]

        return respuestas

    def asignar_color(self, valor, categoria=None, dominio=None):
        """
        Asigna un color a un valor numérico.

        Este método asigna un color a un valor numérico basado en una escala predefinida.

        :param valor: El valor numérico al que se le asignará un color.
        :param categoria: La categoría de la pregunta.
        :param dominio: El dominio de la pregunta.

        :return: El color asignado al valor.
        """

        if categoria:
            if categoria == "Ambiente de Trabajo":
                if valor < 3:
                    return "#2894a7"  # Azul clarito
                elif 3 <= valor < 5:
                    return "#5aaf2b"  # Verde
                elif 5 <= valor < 7:
                    return "#ebae14"  # Amarillo
                elif 7 <= valor < 9:
                    return "#ffa446"  # Naranja
                else:
                    return "#ff4747"  # Rojo
            elif categoria == "Factores propios de la actividad":
                if valor < 10:
                    return "#2894a7"  # Azul clarito
                elif 10 <= valor < 20:
                    return "#5aaf2b"  # Verde
                elif 20 <= valor < 30:
                    return "#ebae14"  # Amarillo
                elif 30 <= valor < 40:
                    return "#ffa446"  # Naranja
                else:
                    return "#ff4747"  # Rojo
            elif categoria == "Organización del tiempo de trabajo":
                if valor < 4:
                    return "#2894a7"  # Azul clarito
                elif 4 <= valor < 6:
                    return "#5aaf2b"  # Verde
                elif 6 <= valor < 9:
                    return "#ebae14"  # Amarillo
                elif 9 <= valor < 12:
                    return "#ffa446"  # Naranja
                else:
                    return "#ff4747"  # Rojo
            elif categoria == "Liderazgo y relaciones en el trabajo":
                if valor < 10:
                    return "#2894a7"  # Azul clarito
                elif 10 <= valor < 18:
                    return "#5aaf2b"  # Verde
                elif 18 <= valor < 28:
                    return "#ebae14"  # Amarillo
                elif 28 <= valor < 38:
                    return "#ffa446"  # Naranja
                else:
                    return "#ff4747"  # Rojo
        elif dominio:
            if dominio == "Condiciones en el ambiente de trabajo":
                if valor < 3:
                    return "#2894a7"  # Azul clarito
                elif 3 <= valor < 5:
                    return "#5aaf2b"  # Verde
                elif 5 <= valor < 7:
                    return "#ebae14"  # Amarillo
                elif 7 <= valor < 9:
                    return "#ffa446"  # Naranja
                else:
                    return "#ff4747"  # Rojo
            elif dominio == "Carga de trabajo":
                if valor < 12:
                    return "#2894a7"  # Azul clarito
                elif 12 <= valor < 16:
                    return "#5aaf2b"  # Verde
                elif 16 <= valor < 20:
                    return "#ebae14"  # Amarillo
                elif 20 <= valor < 24:
                    return "#ffa446"  # Naranja
                else:
                    return "#ff4747"  # Rojo
            elif dominio == "Falta de control sobre el trabajo":
                if valor < 5:
                    return "#2894a7"  # Azul clarito
                elif 5 <= valor < 8:
                    return "#5aaf2b"  # Verde
                elif 8 <= valor < 11:
                    return "#ebae14"  # Amarillo
                elif 11 <= valor < 14:
                    return "#ffa446"  # Naranja
                else:
                    return "#ff4747"  # Rojo
            elif dominio == "Jornada de trabajo":
                if valor < 1:
                    return "#2894a7"  # Azul clarito
                elif 1 <= valor < 2:
                    return "#5aaf2b"  # Verde
                elif 2 <= valor < 4:
                    return "#ebae14"  # Amarillo
                elif 4 <= valor < 6:
                    return "#ffa446"  # Naranja
                else:
                    return "#ff4747"  # Rojo
            elif dominio == "Interferencia en la relación trabajo-familia":
                if valor < 1:
                    return "#2894a7"  # Azul clarito
                elif 1 <= valor < 2:
                    return "#5aaf2b"  # Verde
                elif 2 <= valor < 4:
                    return "#ebae14"  # Amarillo
                elif 4 <= valor < 6:
                    return "#ffa446"  # Naranja
                else:
                    return "#ff4747"  # Rojo
            elif dominio == "Liderazgo":
                if valor < 3:
                    return "#2894a7"  # Azul clarito
                elif 3 <= valor < 5:
                    return "#5aaf2b"  # Verde
                elif 5 <= valor < 8:
                    return "#ebae14"  # Amarillo
                elif 8 <= valor < 11:
                    return "#ffa446"  # Naranja
                else:
                    return "#ff4747"  # Rojo
            elif dominio == "Relaciones en el trabajo":
                if valor < 5:
                    return "#2894a7"  # Azul clarito
                elif 5 <= valor < 8:
                    return "#5aaf2b"  # Verde
                elif 8 <= valor < 11:
                    return "#ebae14"  # Amarillo
                elif 11 <= valor < 14:
                    return "#ffa446"  # Naranja
                else:
                    return "#ff4747"  # Rojo
            elif dominio == "Violencia":
                if valor < 7:
                    return "#2894a7"  # Azul clarito
                elif 7 <= valor < 10:
                    return "#5aaf2b"  # Verde
                elif 10 <= valor < 13:
                    return "#ebae14"  # Amarillo
                elif 13 <= valor < 16:
                    return "#ffa446"  # Naranja
                else:
                    return "#ff4747"  # Rojo
        else:
            if valor < 20:
                return "#2894a7"  # Azul clarito
            elif 20 <= valor < 45:
                return "#5aaf2b"  # Verde
            elif 45 <= valor < 70:
                return "#ebae14"  # Amarillo
            elif 70 <= valor < 90:
                return "#ffa446"  # Naranja
            else:
                return "#ff4747"  # Rojo

    def asignar_color_clima(self, valor):
        """
        Asigna un color a un valor numérico.

        Este método asigna un color a un valor numérico basado en una escala predefinida.

        :param valor: El valor numérico al que se le asignará un color.

        :return: El color asignado al valor.
        """

        for nivel in self.niveles:
            if valor <= nivel.techo:
                return nivel.color
                
    def get_evaluaciones_action(self, evaluacion_id):
        """
        Obtiene las preguntas asociadas a la evaluación.

        Este método obtiene las preguntas asociadas a la evaluación actual y las devuelve en un diccionario.

        :return: Un diccionario con las preguntas asociadas a la evaluación.

        """

        return {
            "evaluacion": self,
            "pregunta": self.pregunta_ids,
        }

    def enviar_evaluacion_action(self):
        """
        Envía la evaluación a los usuarios asignados.

        :return: Un mensaje de notificación que indica que la evaluación ha sido enviada y los usuarios a los que se les ha enviado.
        """

        if self.estado != "publicado":
            return

        usuarios = []

        for usuario in self.usuario_ids:
            usuarios.append(usuario.partner_id.name)

        for usuario_externo in self.usuario_externo_ids:
            usuarios.append(usuario_externo.nombre)

        self.env["usuario.evaluacion.rel"].enviar_evaluacion_action(
            evaluacion_id=self.id
        )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": f"Evaluación {self.nombre} fue enviada!",
                "type": "success",
                "message": f"La evaluación ha sido enviada a {', '.join(usuarios)}.",
                "sticky": False,
            },
        }

    def write(self, vals):
        """
        Sobrescribe el método write para incluir el envío de enlaces al guardar de forma automática
        o manual la evaluación.

        :return: Sobreescribe la asignación de usuarios si hubo cambio en ellos.
        """
        resultado = super(Evaluacion, self).write(vals)
        self.enviar_evaluacion_action()

        # Si se está eliminando un usuario o usuario externo, eliminar sus respuestas

        if "usuario_ids" in vals:
            usuarios_eliminados = list(map(
                lambda val: val[1], filter(
                    lambda val: val[0] == 3, vals["usuario_ids"])
            ))

            if usuarios_eliminados:
                respuestas = self.env["respuesta"].search(
                    [
                        ("usuario_id.id", "in", usuarios_eliminados),
                        ("evaluacion_id.id", "=", self.id),
                    ]
                )

                respuestas.unlink()

        if "usuario_externo_ids" in vals:
            usuarios_eliminados = list(map(
                lambda val: val[1],
                filter(lambda val: val[0] == 3, vals["usuario_externo_ids"]),
            ))

            if usuarios_eliminados:
                respuestas = self.env["respuesta"].search(
                    [
                        ("usuario_externo_id.id", "in", usuarios_eliminados),
                        ("evaluacion_id.id", "=", self.id),
                    ]
                )
                respuestas.unlink()


        return resultado

    def action_asignar_usuarios_externos(self):
        """
        Abre la ventana para asignar usuarios externos a la evaluación.

        :return: Una acción para abrir la ventana de asignación de usuarios externos.
        """
        return {
            "name": "Asignar usuarios externos",
            "type": "ir.actions.act_window",
            "res_model": "asignar.usuario.externo.wizard",
            "view_mode": "form",
            "target": "new",
        }
    
    @api.constrains("niveles")
    def checar_techo(self):
        """
        Verifica que los valores de la ponderación sean válidos.
        Validación 1: Verifica que si haya niveles en la ponderación.
        Validación 2: Verifica que mínimo haya dos niveles en la ponderación.
        Validación 3: Verifica que el valor de la ponderación no sea menor o igual a 0.
        Validación 4: Verifica que no haya valores duplicados en la ponderación.
        Validación 5: Verifica que no haya más de 10 techos.
        Validación 6: Verifica que los valores de la ponderación estén en orden ascendente.
        Validación 7: Verifica que el valor de las ponderaciones no sean mayores a 100 y que el último sea 100.

        """

        for registro in self:
            if len(registro.niveles) == 0:
                raise ValidationError(_("Debe haber al menos un nivel en la ponderación."))

            if len(registro.niveles) < 2:
                raise ValidationError(
                    _("Debe haber al menos dos niveles en la ponderación.")
                )

            for nivel in registro.niveles:
                
                if nivel.techo <= 0:
                    raise ValidationError(
                        _("El valor de la ponderación no debe ser menor o igual a 0.")
                    )

                techos = registro.niveles.filtered(lambda n: n.id != nivel.id).mapped("techo")

                if nivel.techo in techos:
                    raise ValidationError(
                        _("No puede haber valores duplicados en la ponderación.")
                    )

            todos_techos = registro.niveles.mapped("techo")

            if len(todos_techos) > 10:
                raise ValidationError(
                    _("No puede haber más de 10 valores de ponderación.")
                )
            
            if todos_techos != sorted(todos_techos):
                raise ValidationError(
                    _("Los valores de la ponderación deben estar en orden ascendente.")
                )

            if todos_techos[-1] > 100:
                raise ValidationError(
                    _("El valor de la ponderación no puede ser mayor a 100.")
                )
            if todos_techos[-1] != 100:
                raise ValidationError(_("El último valor de la ponderación debe ser 100."))

    @api.constrains("niveles")
    def checar_color(self):
        """
        Verifica que los valores de los colores sean válidos.

        """
        for registro in self:
            for nivel in registro.niveles:

                colores = registro.niveles.filtered(lambda n: n.id != nivel.id).mapped("color")
                if nivel.color in colores:
                    raise ValidationError(
                        _("No puede haber colores duplicados en la ponderación.")
                    )


    def actualizar_estados_eval(self):
        """
        Actualiza el estado de las evaluaciones según la fecha actual.

        - Si la fecha actual está dentro del rango de fechas de inicio y finalización,
        se cambia el estado a 'publicado' (Abierta).
        - De lo contrario, pasa a 'finalizado' (Cerrada).

        :return: None
        """

        hoy = fields.Date.today()
        hora = fields.Datetime.now().strftime("%H:%M:%S")

        # asignar 11:59pm como hora de cierre de evaluaciones
        hora_cierre = "23:59:55"

        # Asignar la hora de apertura de las evaluaciones 12:01am
        hora_apertura = "00:00:55"

        evaluaciones = self.search([])

        # Actualizar el estado de las evaluaciones según la fecha y hora actual
        for evaluacion in evaluaciones:
            try:
                if evaluacion.fecha_inicio <= hoy <= evaluacion.fecha_final:
                    if hoy == evaluacion.fecha_inicio and hora < hora_apertura:
                        evaluacion.estado = "borrador"
                    elif hoy == evaluacion.fecha_final and hora > hora_cierre:
                        evaluacion.estado = "finalizado"
                    else:
                        evaluacion.estado = "publicado"
                elif evaluacion.fecha_final < hoy:
                    evaluacion.estado = "finalizado"
                elif evaluacion.fecha_inicio > hoy:
                    evaluacion.estado = "borrador"
            except Exception as e:
                _logger.error(f"Error al actualizar el estado de la evaluación: {e}")
                
    def evaluacion_general_action_form(self):
        """
        Ejecuta la acción de redireccionar a la evaluación general y devuelve un diccionario

        Este método utiliza los parámetros necesarios para redireccionar a la evaluación general

        :return: Un diccionario que contiene todos los parámetros necesarios para redireccionar la
        a una vista de la evaluación general.

        """

        return {
            "type": "ir.actions.act_window",
            "name": "General",
            "res_model": "evaluacion",
            "view_mode": "form",
            "view_id": self.env.ref("evaluaciones.evaluacion_general_view_form").id,
            "target": "current",
            "context": {"default_tipo": "generico"},
        }

    def get_escalar_format(self):
        """
        Devuelve el formato escalar seleccionado para la evaluación actual.

        :return: El formato escalar seleccionado para la evaluación.
        """
        return self.escalar_format

    def generar_reporte(self):
        """
        Devuelve las fechas de inicio y final que el usuario acordo al realizar la evaluación.

        :return: Las fechas de inicio y final.
        """
        return {

            "type": "ir.actions.report",
            "report_name": "evaluaciones.reporte_template",
            "context": {
                "evaluacion_id": self.id,
                "fecha_inicio": self.fecha_inicio,
                "fecha_final": self.fecha_final,
            }
        }

    def action_importar_preguntas_clima(self):
        """
        Abre la ventana para importar preguntas de clima laboral.

        :return: Una acción para abrir la ventana de importación de preguntas
        """
        return {
            "name": "Importar preguntas de clima laboral",
            "type": "ir.actions.act_window",
            "res_model": "importar.preguntas.wizard",
            "view_mode": "form",
            "target": "new",
        }

    def existen_respuestas(self):
        """
        Verifica si existen respuestas para la evaluación.

        :return: True si existen respuestas, False en caso contrario.
        """
        return self.env["respuesta"].search_count(
            [("evaluacion_id.id", "=", self.id)]) > 0

    def get_datos_pregunta(self):
        """
        Obtiene los datos de las preguntas de la evaluación.

        :return: Los datos de las preguntas de la evaluación. Incluye las respuestas a cada pregunta y las respuestas tabuladas.
        """

        preguntas_data = []

        for pregunta in self.pregunta_ids:
            respuesta_ids = self.env["respuesta"].search(
                [
                    ("pregunta_id.id", "=", pregunta.id),
                    ("evaluacion_id.id", "=", self.id),
                ]
            )

            respuestas = []
            for respuesta in respuesta_ids:
                id = None

                if respuesta.usuario_externo_id:
                    id = "E" + respuesta.usuario_externo_id.id.__str__()

                elif respuesta.usuario_id:
                    id = respuesta.usuario_id.id.__str__()

                respuestas.append({
                    "usuarioID": id,
                    "respuesta": respuesta.respuesta_mostrar
                })

            respuestas_tabuladas = dict(
                Counter([r["respuesta"] for r in respuestas]))

            datos_pregunta = {
                "pregunta": pregunta,
                "respuestas": respuestas,
                "respuestas_tabuladas": [
                    {"nombre": nombre, "valor": valor}
                    for nombre, valor in respuestas_tabuladas.items()
                ],
            }

            preguntas_data.append(datos_pregunta)

        return preguntas_data

    def generar_datos_demograficos_individuales(self):
        """
        Genera los datos demográficos de la evaluación.

        :return: Los datos demográficos de los usuarios asignados a la evaluación. Incuye departamentos, generaciones, puestos y géneros.
        """
        datos_demograficos = []

        usuario_evaluacion = self.env["usuario.evaluacion.rel"].search(
            [
                ("evaluacion_id.id", "=", self.id),
                ("contestada", "=", "contestada"),
                ("usuario_id.id", "in", self.usuario_ids.mapped("id")),
            ]
        )

        for usuario in usuario_evaluacion.mapped("usuario_id"):
            datos_demograficos_usuario = usuario.obtener_datos_demograficos()
            datos_demograficos_usuario["id"] = usuario.id.__str__()
            datos_demograficos.append(datos_demograficos_usuario)

        usuario_evaluacion_externo = self.env["usuario.evaluacion.rel"].search(
            [
                ("evaluacion_id.id", "=", self.id),
                ("contestada", "=", "contestada"),
                ("usuario_externo_id.id", "in", self.usuario_externo_ids.ids),
            ]
        )

        for usuario_externo in usuario_evaluacion_externo.mapped("usuario_externo_id"):
            datos_demograficos_usuario = usuario_externo.obtener_datos_demograficos()
            datos_demograficos_usuario["id"] = "E" + \
                usuario_externo.id.__str__()
            datos_demograficos.append(datos_demograficos_usuario)

        return datos_demograficos

    def generar_excel(self, preguntas, demograficos):
        """
        Genera un archivo de Excel con las respuestas de la evaluación.

        :param preguntas: Los datos de las preguntas de la evaluación.
        :param demograficos: Los datos demográficos de la evaluación.

        :return: Un archivo de Excel con las respuestas de la evaluación.
        """

        datos_preguntas = []
        for pregunta in preguntas:
            for respuesta in pregunta["respuestas"]:
                datos_preguntas.append({
                    "UsuarioID": respuesta["usuarioID"],
                    "Pregunta": pregunta["pregunta"].pregunta_texto,
                    "Respuesta": respuesta["respuesta"],
                })

        df_respuestas = pd.DataFrame(datos_preguntas)

        datos_demograficos = []

        for demografico in demograficos:
            entrada = {
                "UsuarioID": demografico["id"],
            }
            for categoria, valor in demografico.items():
                if categoria != "id":
                    entrada[categoria] = valor

            datos_demograficos.append(entrada)

        df_demograficos = pd.DataFrame(datos_demograficos)

        output = BytesIO()

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_respuestas.to_excel(writer, index=False,
                                   sheet_name="Respuestas")
            df_demograficos.to_excel(
                writer, index=False, sheet_name="Datos Demográficos")

        output.seek(0)

        attachment = self.env['ir.attachment'].create({
            'name': 'Respuestas.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'res_model': 'evaluacion',
            'res_id': self.id,
        })

        return attachment

    def action_exportar_excel(self):
        """
        Exporta las respuestas de la evaluación a un archivo de Excel.

        :return: Una acción para exportar las respuestas a un archivo de Excel.
        """

        if not self.existen_respuestas():
            raise exceptions.ValidationError(
                _("No hay respuestas para exportar."))

        datos_preguntas = self.get_datos_pregunta()
        datos_demograficos = self.generar_datos_demograficos_individuales()
        attachment = self.generar_excel(datos_preguntas, datos_demograficos)

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }

    def previsualizacion_action(self):
        """
        Este método genera una previsualización de la evaluación.

        :return: una acción de redirección a la previsualización de la evaluación.

        """

        return {
            "type": "ir.actions.act_url",
            "url": f"/evaluacion/previsualizar/{self.id}",
            "target": "new",
        }
