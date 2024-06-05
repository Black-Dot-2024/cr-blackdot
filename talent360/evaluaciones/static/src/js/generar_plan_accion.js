function generarPlanAccion() {
    console.log("generando plan")

    var evaluacion_id = document.querySelector('input[name="evaluacion_id"]').value;

    // Envía los valores a la base de datos
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/plan_accion/reporte/' + evaluacion_id, true);
    xhr.setRequestHeader('Content-Type', 'application/json');

    var textarea = document.querySelector('#plan_accion_textarea');

    xhr.onload = function() {
        if (xhr.status >= 200 && xhr.status < 400) {

            var response = xhr.responseText; 

            if (textarea) {
                textarea.value = response;
            } else {
                console.error("No se encontró el textarea con id 'plan_accion_textarea'");
            }
        } else {

            // Errores del request
            console.error("Error en la solicitud: " + xhr.status);
        }
    };

    xhr.onerror = function() {
        // Aquí manejas los errores de la conexión
        console.error("Error de conexión");
    };

    xhr.send();


}


"Guardar plan de accion modificado"

function guardarPlanAccion() {
    console.log("guardando plan")

    var evaluacion_id = document.querySelector('input[name="evaluacion_id"]').value;
    var plan_accion = document.querySelector('#plan_accion_textarea').value;

    var data = {
        plan_accion: plan_accion
    };

    // Envía los valores a la base de datos
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/plan_accion/guardar/' + evaluacion_id, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify(data));

    // xhr.onload = function() {
    //     if (xhr.status >= 200 && xhr.status < 400) {

    //         var response = xhr.responseText; 

    //         console.log(response);

    //     } else {

    //         // Errores del request
    //         console.error("Error en la solicitud: " + xhr.status);
    //     }
    // };

    // xhr.onerror = function() {
    //     // Aquí manejas los errores de la conexión
    //     console.error("Error de conexión");
    // };

    // xhr.send(JSON.stringify(data));
}

