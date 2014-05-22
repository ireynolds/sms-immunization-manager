// Submit the language form every time the language select element is changed
$('#language-select').change(
    function(){
         $(this).closest('form').trigger('submit');
    });