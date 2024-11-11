$(document).ready(function() {
    $('#resumeForm').on('submit', function(event) {
        event.preventDefault();
        var formData = new FormData(this);
        $('#spinner').show();
        $('#results').empty();

        $.ajax({
            url: '/optimize_resume',
            type: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            success: function(response) {
                $('#spinner').hide();
                if (response.error) {
                    $('#results').html('<div class="alert alert-danger">' + response.error + '</div>');
                } else {
                    $('#results').html('<h3>Optimized Resume</h3><pre>' + response.optimized_resume + '</pre>');
                }
            },
            error: function() {
                $('#spinner').hide();
                $('#results').html('<div class="alert alert-danger">An error occurred while optimizing the resume.</div>');
            }
        });
    });
});
