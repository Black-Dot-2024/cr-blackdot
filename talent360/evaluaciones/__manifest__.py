{
    "name": "Talent360 - Evaluaciones",
    "application": True,
    "data": [
        "security/evaluaciones_groups.xml",
        "security/evaluaciones_security.xml",
        "security/ir.model.access.csv",
        "views/evaluaciones_views.xml",
        "views/crear_evaluaciones_360.xml",
        "views/objetivos_views.xml",
        "views/evaluaciones_menus.xml",
        "views/evaluaciones_templates.xml",
        "views/evaluaciones_clima_responder.xml",
        "data/pregunta.csv",
        "data/competencia.csv",
        "data/opcion.csv",
        "data/template.csv",
    ],
    "depends": ["base", "mail"],
    "assets": {
        "evaluaciones.evaluaciones_assets": [
            ("include", "web.chartjs_lib"),
            "evaluaciones/static/src/js/survey_print.js",
            "evaluaciones/static/src/js/survey_result.js",
            ("include", "web._assets_helpers"),
            ("include", "web._assets_frontend_helpers"),
            "web/static/src/scss/pre_variables.scss",
            "web/static/lib/bootstrap/scss/_variables.scss",
            "evaluaciones/static/src/scss/survey_templates_form.scss",
            "evaluaciones/static/src/scss/survey_templates_results.scss",
        ],
    },
}
