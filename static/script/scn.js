var sound = new Audio("/static/barcode.wav")
  let scanner = new Instascan.Scanner({video:document.getElementById('preview')});
  var scanneroff = document.getElementById("offcamara");
  
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
  
  scanneroff.onclick = function(cameras) {
    scanner.stop(cameras[0]);
  }
