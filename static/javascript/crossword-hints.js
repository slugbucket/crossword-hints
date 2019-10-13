var ready = function() {
  var max_fields = 10;
  var wrapper = $("#cue_word_set"); //Input fields wrapper
  var save_cue = $("#save_cue_word"); // Add cuw word class or ID

  $("#save_cue_word").click(function(e) {
    e.preventDefault();
    var cword = $("#cue_word").val(); 
    var cmean = $("#cue_meaning").val();
    var dataString = 'cue_word='+cword+'&meaning='+cmean;
    $.ajax({
      type:'POST',
      data:dataString,
      url:'/cue-words/new',
      success:function(data) {
        //alert(data);
        $("#cue_word_flash").css("visibility", "visible");
        $("#cue_word_flash").html("Saved new cue word: "+cword);
        // Reset the form fields to allow another submission
        $("#cue_word").val('');
        $("#cue_meaning").val('');
      }
    });
  });
  $("#soltypehints").click(function(e) {
    $.ajax({
      type:'GET',
      url:'/solution-types/index.json',
      //url:'/solution-types/index.ajax.html',
      success:function(data) {
        //console.log("Retrieved the following JSON: "+data);
        // Modal dialog from https://www.w3schools.com/howto/howto_css_modals.asp
        // Get the modal
        var modal = document.getElementById("solution-types");
        // Get the button that opens the modal
        //var btn = document.getElementById("myBtn");
        var btn = document.getElementById("soltypehints");
        // Get the <span> element that closes the modal
        var span = document.getElementsByClassName("close")[0];
        // When the user clicks on the button, open the modal
        btn.onclick = function() {
          modal.style.display = "block";
        }
        // When the user clicks on <span> (x), close the modal
        span.onclick = function() {
          modal.style.display = "none";
        }

        // When the user clicks anywhere outside of the modal, close it
        window.onclick = function(event) {
          if (event.target == modal) {
            modal.style.display = "none";
          }
        }
        var content="The table below describes the meaning of each solution type.<br /><table class='solution-types-table'>\n<tr class='solution-types-table'><th>Name</th><th>Description</th>\n";
        for (var i=0; i<data.length; i++) {
          rcls="ma_row_dark";
          if(i % 2 == 1) {rcls="ma_row_light"; }
          content=content+"<tr class='"+rcls+"'><td>"+data[i].name+"</td><td>"+data[i].description+"</td></tr>";
        }
        content=content+"</table>";
        $("#solution-types-table").html(content);
        // Direct render of HTML table to avoid constructing it from AJAX request to JSON list
        //$("#solution-types-table").html(data);
      }
    });
  });
  $("#dialog").dialog(
    {
     bgiframe: true,
     autoOpen: false,
     height: 100,
     modal: true,
     close: function(event, ui) {
        $(this).remove();
      }
    }
  );
  setTimeout(initOverLabels, 50);
  initOverLabels();
}; // Used with var ready = function() 
$(document).ready(ready);
$(document).on('page:load', ready);
//
// Functions for cute form appearance
// Lifted from http://www.alistapart.com/articles/makingcompactformsmoreaccessible
//
function initOverLabels () {
  if (!document.getElementById) return;

  var labels, id, field;

  // Set focus and blur handlers to hide and show labels with 'overlabel' class names.
  labels = document.getElementsByTagName('label');
  for (var i = 0; i < labels.length; i++) {

    if (labels[i].className == 'overlabel') {

      // Skip labels that do not have a named association with another field.
      id = labels[i].htmlFor || labels[i].getAttribute ('for');
      if (!id || !(field = document.getElementById(id))) {
        continue;
      }

      // Change the applied class to hover the label over the form field.
      labels[i].className = 'overlabel-apply';

      // Hide any fields having an initial value.
      if (field.value !== '') {
        hideLabel(field.getAttribute('id'), true);
      }

      // Set handlers to show and hide labels.
      field.onfocus = function () {
        hideLabel(this.getAttribute('id'), true);
      };
      field.onblur = function () {
        if (this.value === '') {
          hideLabel(this.getAttribute('id'), false);
        }
      }

      // Handle clicks to label elements (for Safari).
      labels[i].onclick = function () {
        var id, field;
        id = this.getAttribute('for');
        if (id && (field = document.getElementById(id))) {
          field.focus();
        }
      }

    }
  }
}

function hideLabel (field_id, hide) {
  var field_for;
  var labels = document.getElementsByTagName('label');
  for (var i = 0; i < labels.length; i++) {
    field_for = labels[i].htmlFor || labels[i]. getAttribute('for');
    if (field_for == field_id) {
      labels[i].style.textIndent = (hide) ? '1000px' : '0px';
      return true;
    }
  }
}