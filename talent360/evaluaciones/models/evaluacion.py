from odoo import api, models, fields


class Evaluacion(models.Model):
    """
    Modelo para representar una evaluación de personal en Odoo.

    :param _name (str): Nombre del modelo en Odoo.
    :param _description (str): Descripción del modelo en Odoo.
    :param nombre (fields.Char): Nombre de la evaluación. Es un campo obligatorio.
    :param estado (fields.Selection): Estado de la evaluación con opciones 'borrador', 'publicado' y 'finalizado'. Por defecto, es 'borrador'.
    :param pregunta_ids (fields.Many2many): Relación de muchos a muchos con el modelo 'pregunta' para almacenar las preguntas asociadas a la evaluación.
    :param competencia_ids (fields.Many2many): Relación de muchos a muchos con el modelo 'competencia' para almacenar las competencias asociadas a la evaluación.
    :param usuario_ids (fields.Many2many): Relación de muchos a muchos con el modelo 'res.users' para asignar usuarios a la evaluación.
    """

    _name = "evaluacion"
    _description = "Evaluacion de pesonal"

    nombre = fields.Char(required=True)

    tipo = fields.Selection(
        [
            ("CLIMA", "Clima Organizacional"),
            ("NOM_035", "NOM 035"),
            ("competencia", "Competencia"),
        ],
        required=True,
        default="competencia",
    )
    descripcion = fields.Text()
    estado = fields.Selection(
        [
            ("borrador", "Borrador"),
            ("publicado", "Publicado"),
            ("finalizado", "Finalizado"),
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

    fecha_inicio = fields.Date()
    fecha_final = fields.Date()

    
    # Método para copiar preguntas de la plantilla a la evaluación
    def copiar_preguntas_de_template(self):
        """
        Copia preguntas de un template de evaluación predeterminado a una nueva evaluación.

        Este método verifica si el objeto actual está vacío (self). Si lo está, crea una nueva
        evaluación con un nombre predeterminado y asigna este nuevo objeto a self. Luego, limpia
        las preguntas existentes y copia todas las preguntas de un template con ID predefinido
        (en este caso, 332) al objeto evaluación actual.

        Returns:
        object: Retorna el objeto evaluación actualizado con las preguntas copiadas del template.
        """

        if not self:

            new_evaluation = self.env["evaluacion"].create(
                {
                    "nombre": "",
                    "descripcion": "La evaluación Clima es una herramienta de medición de clima organizacional, cuyo objetivo es conocer la percepción que tienen las personas que laboran en los centros de trabajo, sobre aquellos aspectos sociales que conforman su entorno laboral y que facilitan o dificultan su desempeño.",
                    "tipo": "CLIMA",
                }
            )
            self = new_evaluation

        self.pregunta_ids = [(5,)]

        template_id = self.env["ir.model.data"]._xmlid_to_res_id(
            "evaluaciones.template_clima"
        )

        if template_id:
            template = self.env["template"].browse(template_id)
            if template:
                pregunta_ids = template.pregunta_ids.ids
                print("IDs de preguntas:", pregunta_ids)
                self.pregunta_ids = [(6, 0, pregunta_ids)]

        return self

    def copiar_preguntas_de_template_nom035(self):
        """
        Copia preguntas de un template de evaluación predeterminado a una nueva evaluación.

        Este método verifica si el objeto actual está vacío (self). Si lo está, crea una nueva
        evaluación con un nombre predeterminado y asigna este nuevo objeto a self. Luego, limpia
        las preguntas existentes y copia todas las preguntas de un template con ID predefinido
        (en este caso, 331) al objeto evaluación actual.

        :return: object: Retorna el objeto evaluación actualizado con las preguntas copiadas del template.
        """

        if not self:
            new_evaluation = self.env["evaluacion"].create(
                {
                    "nombre": "",
                    "descripcion": "La NOM 035 tiene como objetivo establecer los elementos para identificar, analizar y prevenir los factores de riesgo psicosocial, así como para promover un entorno organizacional favorable en los centros de trabajo.",
                    "tipo": "NOM_035",
                }
            )
            self = new_evaluation

        self.pregunta_ids = [(5,)]

        template_id = self.env["ir.model.data"]._xmlid_to_res_id(
            "evaluaciones.template_nom035"
        )

        if template_id:
            template = self.env["template"].browse(template_id)
            if template:
                pregunta_ids = template.pregunta_ids.ids
                self.pregunta_ids = [(6, 0, pregunta_ids)]

        return self

    def evaluacion_clima_action_form(self):
        """
        Ejecuta la acción de copiar preguntas de un template a la evaluación actual y devuelve
        un diccionario con los parámetros necesarios para abrir una ventana de acción en Odoo.

        Este método utiliza `copiar_preguntas_de_template_nom035` para asegurarse de que la evaluación
        actual tenga las preguntas correctas, y luego configura y devuelve un diccionario con
        los detalles para abrir esta evaluación en una vista de formulario específica.

        Returns:
        dict: Un diccionario que contiene todos los parámetros necesarios para abrir la
        evaluación en una vista de formulario específica de Odoo.

        """

        self = self.copiar_preguntas_de_template()

        # Retornar la acción con la vista como destino
        return {
            "type": "ir.actions.act_window",
            "name": "Evaluación Clima",
            "res_model": "evaluacion",
            "view_mode": "form",
            "view_id": self.env.ref("evaluaciones.evaluacion_clima_view_form").id,
            "target": "current",
            "res_id": self.id,
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
        self = self.copiar_preguntas_de_template_nom035()

        return {
            "type": "ir.actions.act_window",
            "name": "NOM 035",
            "res_model": "evaluacion",
            "view_mode": "form",
            "view_id": self.env.ref("evaluaciones.evaluacion_nom035_view_form").id,
            "target": "current",
            "res_id": self.id,
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

    def abrir_evaluacion_form(self):
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

    def action_reporte_generico(self):
        """
        Genera una acción de URL para el reporte genérico de la evaluación.

        Esta función genera un URL para redirigir
        a un reporte específico de la evaluación actual.

        :return: una acción de redirección al reporte de la evaluación

        """

        url_base = "/evaluacion/reporte/"
        if self.tipo == "CLIMA":
            url_base = "/evaluacion/reporte-clima/"
        else:
            url_base = "/evaluacion/reporte/"

        return {
            "type": "ir.actions.act_url",
            "url": f"{url_base}{self.id}",
            "target": "new",
        }

    def action_generar_datos_reporte_generico(self):
        """
        Genera los datos necesarios para el reporte genérico de la evaluación.

        Esta función genera los parámetros requeridos para generar un reporte genérico de la evaluación actual,
        incluyendo las preguntas y las respuestas tabuladas.

        :return: Los parámetros necesarios para generar el reporte.

        """
        parametros = {
            "evaluacion": self,
            "preguntas": [],
        }

        respuesta_tabulada = {}

        for pregunta in self.pregunta_ids:

            respuestas = []
            respuestas_tabuladas = []

            for respuesta in pregunta.respuesta_ids:
                if respuesta.evaluacion_id.id != self.id:
                    continue

                respuestas.append(respuesta.respuesta_texto)

                for i, respuesta_tabulada in enumerate(respuestas_tabuladas):
                    if respuesta_tabulada["nombre"] == respuesta.respuesta_texto:
                        respuestas_tabuladas[i]["valor"] += 1
                        break
                else:
                    respuestas_tabuladas.append(
                        {"nombre": respuesta.respuesta_texto, "valor": 1}
                    )

            datos_pregunta = {
                "pregunta": pregunta,
                "respuestas": respuestas,
                "respuestas_tabuladas": respuestas_tabuladas,
                "datos_grafica": str(respuestas_tabuladas).replace("'", '"'),
            }

            parametros["preguntas"].append(datos_pregunta)

        return parametros

    def action_get_evaluaciones(self, evaluacion_id):
        """
        Obtiene las preguntas asociadas a la evaluación.

        Este método obtiene las preguntas asociadas a la evaluación actual y las devuelve en un diccionario.

        :return: Un diccionario con las preguntas asociadas a la evaluación.

        """

        return {
            "evaluacion": self,
            "pregunta": self.pregunta_ids,
        }
    
    def action_enviar_evaluacion(self):
        usuarios = []

        for usuario in self.usuario_ids:
            usuarios.append(usuario.partner_id.name)
        self.env['usuario.evaluacion.rel'].action_enviar_evaluacion(evaluacion_id=self.id)
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
        

    def action_get_evaluaciones(self, evaluacion_id):
        """
        Obtiene las preguntas asociadas a la evaluación.

        Este método obtiene las preguntas asociadas a la evaluación actual y las devuelve en un diccionario.

        :return: Un diccionario con las preguntas asociadas a la evaluación.

        """

        return {
            "evaluacion": self,
            "pregunta": self.pregunta_ids,
        }
    
    def action_enviar_evaluacion(self):
        usuarios = []

        for usuario in self.usuario_ids:
            usuarios.append(usuario.partner_id.name)
        self.env['usuario.evaluacion.rel'].action_enviar_evaluacion(evaluacion_id=self.id)
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
        


    def action_generar_datos_reporte_NOM_035(self):
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
            categoria = dict(pregunta._fields["categoria"].selection).get(pregunta.categoria)
            dominio = dict(pregunta._fields["dominio"].selection).get(pregunta.dominio)

            valor_pregunta = 0

            for respuesta in pregunta.respuesta_ids:
                valor_respuesta = int(respuesta.respuesta_texto)
                valor_pregunta += valor_respuesta
                final += valor_respuesta

            # Acumular el valor de la pregunta en la categoría y el dominio correspondientes
            if categoria in categorias:
                categorias[categoria] += valor_pregunta
            if dominio in dominios:
                dominios[dominio] += valor_pregunta

        # Organizar los parámetros en el orden deseado
        parametros = {
            "evaluacion": self,
            "categorias": [{"nombre": nombre, "valor": categorias[nombre]} for nombre in categorias_orden],
            "dominios": [{"nombre": nombre, "valor": dominios[nombre]} for nombre in dominios_orden],
            "final": final,
        }

        print(parametros)
        return parametros
    
    def action_generar_datos_reporte_clima(self):
        """
        Genera los datos necesarios para un reporte de evaluación de clima.

        :return: Los parámetros necesarios para generar el reporte.
        """
        
        # Definir estructura de categorías
        categorias_orden = [
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
        
        categorias = [{"nombre": categoria, "valor": 0, "puntos": 0, "puntos_maximos": 0, "departamentos": []} for categoria in categorias_orden]
        total = 0
        maximo_posible = 0
    
        for pregunta in self.pregunta_ids:
            #Ignorar preguntas sin gategoría
            if not pregunta.categoria:
                continue

            categoria_texto = dict(pregunta._fields["categoria"].selection).get(pregunta.categoria)
            if not categoria_texto in categorias_orden:
                continue

            valor_pregunta = 0
            maximo_pregunta = 0

            categoria = None

            for cat in categorias:
                if cat["nombre"] == categoria_texto:
                    categoria = cat
                    break


            if pregunta.tipo == "escala":
                maximo_pregunta += 4

                for respuesta in pregunta.respuesta_ids:
                    valor_respuesta = int(respuesta.respuesta_texto)
                    valor_pregunta += valor_respuesta
                    
                    if not respuesta.user_id:
                        continue

                    employee = self.env['hr.employee'].search([('user_id', '=', respuesta.user_id.id)], limit=1)
                    departamento_nombre = employee.department_id.name

                    departamento = list(filter(lambda cat: cat["nombre"] == departamento_nombre, categoria["departamentos"]))
                    if not departamento:
                        departamento = {
                            "nombre": departamento_nombre,
                            "puntos": 0,
                            "puntos_maximos": 0,
                        }
                        categoria["departamentos"].append(departamento)
                    else:
                        departamento = departamento[0]


                    departamento["puntos"] += valor_respuesta
                    departamento["puntos_maximos"] += 4
                
                valor_pregunta = (valor_pregunta / len(pregunta.respuesta_ids))
            
            #TODO:vincular a cambio de opcionID
            elif pregunta.tipo == "multiple_choice":
                maximo_pregunta = max([opcion.valor for opcion in pregunta.opcion_ids])
                for respuesta in pregunta.respuesta_ids:
                    if respuesta.respuesta_texto == "Sí":
                        valor_pregunta += 1
                
                valor_pregunta = valor_pregunta / len(pregunta.respuesta_ids)

            total += valor_pregunta
            maximo_posible += maximo_pregunta
            
                            #Acumular el valor de cada pregunta en la categoría correspondiente

            categoria["puntos"] += valor_pregunta
            categoria["puntos_maximos"] += maximo_pregunta

        for categoria in categorias:
            if categoria["puntos_maximos"] > 0:
                categoria["valor"] = (categoria["puntos"] / categoria["puntos_maximos"]) * 100
            else:
                categoria["valor"] = 0

            for departamento in categoria["departamentos"]:
                if departamento["puntos_maximos"] > 0:
                    departamento["valor"] = (departamento["puntos"] / departamento["puntos_maximos"]) * 100
                else:
                    departamento["valor"] = 0

        total_porcentaje = 0

        if maximo_posible > 0:
            total_porcentaje = (total / maximo_posible) * 100

        # Ingresar los datos a parámetros
        parametros = {
            "evalacion": self,
            "categorias": [categorias],
            "total": total,
            "total_maximo": maximo_posible,
            "total_porcentaje": total_porcentaje,
        }
        
        print(parametros)
        return parametros