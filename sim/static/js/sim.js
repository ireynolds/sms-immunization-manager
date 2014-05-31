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

// Hide/show a table of message effects
$('.message-effect-show').click(
    function() {
        $(this).parent().next("table").show()
        $(this).siblings(".message-effect-hide").show()
        $(this).hide()
    });

$('.message-effect-hide').click(
    function() {
        $(this).parent().next("table").hide()
        $(this).siblings(".message-effect-show").show()
        $(this).hide()
    });

// Activate Bootstrap's tooltips. Every element containing a tooltip must have
// tooltip() called on it. Elements without tooltips may have tooltip() called,
// but for efficiency we try to narrow the set of elelments that are called.
$(document).ready(function () {
    $('.label').tooltip();
    $('.conversation-icon').tooltip();
    $('a').tooltip();
    $('button').tooltip();
});