$(document).ready(function(){
    var regexp = /((ftp|http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?)/gi;
    $('div.comment').each(function(){
       $(this).html(
            $(this).html().replace(regexp,'<a href="$1">$1</a>')
       );
    });
    $('div#txt').each(function(){
       $(this).html(
            $(this).html().replace(regexp,'<a href="$1">$1</a>')
       );
    })
})


