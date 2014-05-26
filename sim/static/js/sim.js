// Submit the language form each time the language link is clicked
$('.language-link').click(
    function(event){
        // Prevent the browser from navigating to the link location
        event.preventDefault();

        // Submit the form
        $(this).closest('form').trigger('submit');
    });

// Submit the language form each time the language select is changed
$('#language-select').change(
    function(){
        $(this).closest('form').trigger('submit');
    });

// Activate Bootstrap's tooltips
$(document).ready(function () {
    $('.label').tooltip();
});