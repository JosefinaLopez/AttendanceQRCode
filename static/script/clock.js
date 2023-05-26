function clock() {
    //Variables
    var now = new Date();
    var H = now.getHours();
    var M = now.getMinutes();
    var S = now.getSeconds();
    //Aqui divide la hora x 12 y identifica si es AM O PM
    const amp = H >= 12 ? 'PM' :'AM';
    h = H % 12;
    h = h ? h : 12;

    //En base a eso se crea una cade con el formato 3:30 PM
    var time = h + ':' + (M < 10 ? '0' : '') + M +" "+ amp;
    //Se agrega al elemento con id 'clock'
    document.getElementById('clock').innerHTML = time;
    
    //Para usarla , la variable se envia al index 
    $.ajax({
        url: '/',
        data: {
            time: time
        },
        success: function(response) {
            console.log(response);
        }
    });
}

// Llamar a la función clock() una vez al abrir la página
clock();

// Actualizar la hora cada minuto
setInterval(clock, 60000);
