$(document).ready(function () {

  var err_msg = '';
  var received = $('#received');
  var socket = new WebSocket("ws://<web_ip>:<web_port>/ws");

  socket.onmessage = function (message) {
    let data = received.val();
    received.val(data + message.data + '\n');
    /*received.append('<br>');*/
  };

  var sendMessage = function (message) {
    socket.send(message.data);
  };

  // send a command to the serial port
  $("#cmd_send").click(function (ev) {
    ev.preventDefault();
    var cmd = $('#cmd_value').val();
    sendMessage({ 'data': cmd });
    $('#cmd_value').val('');
  });

  $('#clear').click(function () {
    received.val('');
  });

  function asleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  function sleep(milliseconds) {
    var start = new Date().getTime();
    for (var i = 0; i < 1e7; i++) {
      if ((new Date().getTime() - start) > milliseconds) {
        break;
      }
    }
  }

  // pendulum calibration commands
  async function calibrate(cmd, str) {
    wt = 500; // wait time in ms
    sendMessage({ 'data': cmd });
    let regex = new RegExp(str.toUpperCase().trim() + ".+OK$", "m");
    let data = received.val();
    let timeout = 0;
    let ok = false;
    while (timeout < 30) {
      timeout += 1;
      if (regex.test(data)) {
        ok = true;
        break;
      }
      await asleep(wt);
      data = received.val();
    }
    if (!ok) {
      err_msg += '• ' + cmd + '<br>';
      $("#ok-msg").attr("style", "display:none");
      $("#alert-msg-text").html(err_msg);
      $("#alert-msg").attr("style", "display:block");
    } else {
      $("#alert-msg-text").html(err_msg);
      $("#alert-msg").attr("style", "display:none");
      $("#ok-msg").attr("style", "display:block");
    }

  }

  $("#cal1_send").click(function (ev) {

    ev.preventDefault();

    err_msg = '';

    let id_string = $('#id_string').val();
    if (id_string) {
      cmd = 'set ID string ' + id_string.trim();
      calibrate(cmd, 'ID string');
    }


    let max_pos = $('#max_pos').val();
    if (max_pos) {
      cmd = 'set maximum position ' + parseFloat(max_pos.trim());
      sleep(200);
      calibrate(cmd, 'maximum position');
    }

    let vert_pos = $('#vert_pos').val();
    if (vert_pos) {
      cmd = 'set vertical position ' + parseFloat(vert_pos.trim());
      sleep(200);
      calibrate(cmd, 'vertical position');
    }

    let diameter = $('#diameter').val();
    if (diameter) {
      cmd = 'set sphere diameter ' + parseFloat(diameter.trim());
      sleep(200);
      calibrate(cmd, 'sphere diameter');
    }

    let pulley = $('#pulley').val();
    if (pulley) {
      cmd = 'set pulley diameter ' + parseFloat(pulley.trim());
      sleep(200);
      calibrate(cmd, 'pulley diameter');
    }

    let length = $('#length').val();
    if (length) {
      cmd = 'set pendulum length ' + parseFloat(length.trim());
      sleep(200);
      calibrate(cmd, 'pendulum length');
    }

    let photo_pos = $('#photo_pos').val();
    if (photo_pos) {
      cmd = 'set photodiode position ' + parseFloat(photo_pos.trim());
      sleep(200);
      calibrate(cmd, 'photodiode position');
    }

    let ori_pos = $('#ori_pos').val();
    if (ori_pos) {
      cmd = 'set origin position ' + parseFloat(ori_pos.trim());
      sleep(200);
      calibrate(cmd, 'origin position');
    }

    $('#cmdModal').modal('show');

  });

  // goto origin
  $("#goto_origin").click(function (ev) {
    ev.preventDefault();
    sendMessage({ 'data': 'go to origin 2 2' });
  });
});