/*
 * Javascript file to implement client side usability for 
 * Operating Systems Desing exercises.
 */
 var api_server_address = "http://34.79.175.189:5001/"

 var get_current_sensor_data = function(){
    $.getJSON( api_server_address+"device_state", function( data ) {
        $.each(data, function( index, item ) {
          $("#"+item.room).data(item.type, item.value)
      });
    });
}

 var get_current_room_data = function(){
    $.getJSON( api_server_address+"room_state", function( data ) {
        $.each(data, function( index, item ) {
          $("#"+item.room).data(item.type,item.value)
      });
    });
    updated_rooms()
}

var draw_rooms = function(){
    $("#rooms").empty()
    var room_index = 1;
    for (var i = 0; i < 8; i++) {
        $("#rooms").append("<tr id='floor"+i+"'></tr>")
        for (var j = 0; j < 5; j++) {
            $("#floor"+i).append("\
                <td \
                data-bs-toggle='modal' \
                data-bs-target='#room_modal' \
                class='room_cell'\
                data-activo= '0'\
                id='Room"+room_index+"'\
                > \
                Room "+room_index+"\
                </td>"
                )
            room_index++
        }
    }
}

var updated_rooms = function(){
    for (var i = 1; i < 41; i++)
    {
        var hab1 = String("Room"+i)
        var rooms= document.getElementById(hab1);
        var hab = String("#Room"+i)
        var cell = $(hab);
        //window.alert(cell.data("connection"));
        if (cell.data("connection") == "online") {
            rooms.className = "room_cell";
            rooms.className += "_activo";
        } else {
            rooms.className = "room_cell";
        }
    }
}

$("#air_conditioner_mode").change(function(){
    var value = $(this).val()
    $.ajax({
        type: "POST",
        url: api_server_address+"device_state",
        data: JSON.stringify({
            "room":$("#room_id").text(),
            "type":"air-conditioner-mode",
            "value":value,
        }),
        contentType: 'application/json'
    });
})

$("#indoor_light_mode").change(function(){
    var value = $(this).val()
    $.ajax({
        type: "POST",
        url: api_server_address+"device_state",
        data: JSON.stringify({
            "room":$("#room_id").text(),
            "type":"indoor-light-mode",
            "value":value,
        }),
        contentType: 'application/json'
    });
})

$("#indoor_light_value").change(function(){
    var value = $(this).val()
    $.ajax({
        type: "POST",
        url: api_server_address+"device_state",
        data: JSON.stringify({
            "room":$("#room_id").text(),
            "type":"indoor-light-value",
            "value":value,
        }),
        contentType: 'application/json'
    });
})

$("#outside_light_mode").change(function(){
    var value = $(this).val()
    $.ajax({
        type: "POST",
        url: api_server_address+"device_state",
        data: JSON.stringify({
            "room":$("#room_id").text(),
            "type":"outside-light-mode",
            "value":value,
        }),
        contentType: 'application/json'
    });
})

$("#outside_light_value").change(function(){
    var value = $(this).val()
    $.ajax({
        type: "POST",
        url: api_server_address+"device_state",
        data: JSON.stringify({
            "room":$("#room_id").text(),
            "type":"outside-light-value",
            "value":value,
        }),
        contentType: 'application/json'
    });
})

$("#blinds_mode").change(function(){
    var value = $(this).val()
    $.ajax({
        type: "POST",
        url: api_server_address+"device_state",
        data: JSON.stringify({
            "room":$("#room_id").text(),
            "type":"blinds-mode",
            "value":value,
        }),
        contentType: 'application/json'
    });
})

$("#blinds_value").change(function(){
    var value = $(this).val()
    $.ajax({
        type: "POST",
        url: api_server_address+"device_state",
        data: JSON.stringify({
            "room":$("#room_id").text(),
            "type":"blinds-value",
            "value":value,
        }),
        contentType: 'application/json'
    });
})

$("#rooms").on("click", "td", function() {
    $("#room_id").text($( this ).attr("id") || "");
    $("#temperature_value").text($( this ).data("temperature") || "");
    $("#presence_value").text($( this ).data("presence") || "0");
    $("#air_conditioner_value").text($( this ).data("air_level") || "");
    $("#air_conditioner_mode").val($( this ).data("air_mode"));
    $("#blinds_value").val($( this ).data("blinds_mode"));
    $("#blinds_mode").val($( this ).data("blind"));
    $("#indoor_light_value").val($( this ).data("indoor_light"));
    $("#indoor_light_mode").val($( this ).data("indoor_mode"));
    $("#outside_light_value").val($( this ).data("outside_light"));
    $("#outside_light_mode").val($( this ).data("outside_mode"));
    $("#room_status").text($( this ).data("connection") || "");
    //window.alert($("#room_status").text());

});

draw_rooms()
setInterval(get_current_sensor_data,2000)
setInterval(get_current_room_data,2000)
//void updated_rooms()