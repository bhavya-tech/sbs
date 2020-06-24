//removes the "active" class to .popup and .popup-content when the "Close" button is clicked 
$(".close").on("click", function() {
    $(".modal-overlay, .modal-content").removeClass("active");
});
$(".open").on("click", function() {
    $(".modal-overlay, .modal-content").addClass("active");
});


var timeto = document.getElementById("to");
var timefrom = document.getElementById("from");
var school = document.getElementById("school");
var roomno = document.getElementById("room");
var description = document.getElementById("description");
var datechosen = document.getElementById("dateSelected");
datechosen = document.getElementById("dateSelected").defaultValue = "22-06-2020";
btn.onclick = function() {
    modal.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
button.onclick = function() {
    modal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}