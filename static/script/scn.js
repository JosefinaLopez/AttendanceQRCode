var sound = new Audio("/static/barcode.wav");
var scanner = new Instascan.Scanner({ video: document.getElementById('preview') });
var scanneroff = document.getElementById("offcamara");
var scanon = document.getElementById("oncamera");

// Función para activar la cámara
function startCamera() {
  Instascan.Camera.getCameras().then(function (cameras) {
    if (cameras.length > 0) {
      scanner.start(cameras[0]);
    } else {
      console.error("La cámara no funciona");
    }
  }).catch(function (e) {
    console.log(e);
  });
}
// Función para detener la cámara
function stopCamera() {
  scanner.stop();
  // Activa el botón de inicio de cámara
  document.getElementById("oncamera").disabled = false;
}

scanner.addListener('scan', function (content) {
  sound.play();
  $('.site-backdrop').html(content);

  // Obtiene información del horario actual antes de enviar la solicitud Ajax
  $.getJSON('/horario_actual', function (data) {
    // Incluye la información del horario actual y el código escaneado en los datos del Ajax
    $.ajax({
      url: '/Asistencia',
      data: {
        Codigo: content,
        clase: data.clase
      },
      success: function (response) {
        console.log("Éxito");
      },
      error: function (xhr) {
        console.log('Error al enviar la solicitud Ajax');
      }
    });
  });
});
$.getJSON('/horario_actual', function (data) {
  $.ajax({
    url: '/ViewAsis',
    data: {
      clase: data.clase
    },
    success: function (response) {
      const tabla = document.getElementById('tabla');
      tabla.innerHTML = '';

      response.attendance.forEach(registro => {
        const fila = tabla.insertRow();
        fila.insertCell().innerText = registro.id;
        fila.insertCell().innerText = registro.student;
        fila.insertCell().innerText = registro.carnet;
        fila.insertCell().innerText = registro.gmail;
        fila.insertCell().innerText = registro.telefono;
      });

      $('#confirm').text(response.confirmacion);
    }
  });
});


// Obtener las cámaras disponibles y empezar a escanear
Instascan.Camera.getCameras().then(function (cameras) {
  if (cameras.length > 0) {
    scanner.start(cameras[0]);
  } else {
    console.error("La cámara no funciona");
  }
}).catch(function (e) {
  console.log(e);
});

// Maneja el clic del botón de apagado de cámara
scanneroff.onclick = function () {
  stopCamera();
};

// Maneja el clic del botón de inicio de cámara
scanon.onclick = function () {
  startCamera();
};

