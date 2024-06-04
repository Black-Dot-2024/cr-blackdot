odoo.define('evaluaciones.generar_plan_accion', function (require) {
    "use strict";
    
    const ajax = require('web.ajax');
    
    document.addEventListener('DOMContentLoaded', function() {
        const btnGenerarPlan = document.getElementById('generar_plan_accion');
        
        if (btnGenerarPlan) {
            btnGenerarPlan.addEventListener('click', function() {
                const evaluacionId = this.getAttribute('data-evaluacion-id');
                const url = `/plan_accion/reporte/${evaluacionId}`;
                
                fetch(url, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'text/plain',
                    },
                })
                .then(response => response.text())
                .then(result => {
                    const textarea = document.getElementById('plan_accion_textarea');
                    if (textarea) {
                        textarea.value = result;
                    }
                })
                .catch(error => {
                    console.error("Error al generar el plan de acción:", error);
                });
            });
        }
    });
});
