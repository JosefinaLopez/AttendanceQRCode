function clock()
{
    var now = new Date();
    var H = now.getHours();
    var M = now.getMinutes();
    var S = now.getSeconds();
    const amp =H >= 12? 'PM' :'AM';

    h = H%12;
    h = H ? h :12;

    var time = h + ':' + (M < 10 ? '0' : '') + M + ':' + (S < 10 ? '0' : '') + S +  " " + amp;
    document.getElementById('clock').innerHTML = time;
    //console.log(x);
}
setInterval(clock, 1000);