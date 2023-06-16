setInterval(function clase() {
    $.getJSON('/horario_actual', function (data) {
        $('#hora_final').text('Finaliza a las ' + data.final);
        $('#clase_Actual').text(data.clase);
    });
}, 20000);

