var sound = new Audio("/static/barcode.wav")
let scanner = new Instascan.Scanner({video:document.getElementById('preview')});
var scanneroff = document.getElementById("offcamara");
var scanon = document.getElementById("oncamera");


// Función para activar la cámara
function startCamera() {
  Instascan.Camera.getCameras().then(function(cameras) {
    if(cameras.length > 0) {
      scanner.start(cameras[0]);
    } else {
      console.error("la camara no funciona");
    }
  }).catch(function(e) {
    console.log(e);
  });
}
// Función para detener la cámara
function stopCamera() {
  scanner.stop();
  // Activa el botón de inicio de cámara
  document.getElementById("oncamera").disabled = false;
};

/* Verifica la información de la clase actual antes de activar la cámara
$.getJSON('/horario_actual', function(data) {
  // Verifica si la información de la clase actual no es null
  if (data.clase != "Aún no hay") {
    // Activa la cámara
    startCamera();
    console.log("XDD");
  
  }
  else{
    console.log("No puede registrar Asistencia");
    stopCamera();
  }
});*/

scanner.addListener('scan', function(content) {
  sound.play();
  $('.site-backdrop').html(content);

  // Obtiene información del horario actual antes de enviar la solicitud Ajax
  $.getJSON('/horario_actual', function(data) {
    // Incluye la información del horario actual y código escaneado en los datos del Ajax
    $.ajax({
      url: '/Asistencia',
      data: {
        Codigo: content,
        clase: data.clase
      },
      success: function(response) {
        console.log('Solicitud Ajax enviada correctamente');
        $('Modal').modal('show');
      },
      error: function(xhr) {
        console.log('Error al enviar la solicitud Ajax');
      }
    });
  });
});

Instascan.Camera.getCameras().then(function(cameras) {
  if(cameras.length > 0) {
    scanner.start(cameras[0]);
  } else {
    console.error("la camara no funciona")
  }
}).catch(function(e) {
  console.log(e);
});

// Maneja el clic del botón de apagado de cámara
scanneroff.onclick = function() {
  stopCamera();
};

// Maneja el clic del botón de inicio de cámara
scanon.onclick = function () {
  startCamera();
};
