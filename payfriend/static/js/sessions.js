$(document).ready(function() {
  $("#send-payment-form").submit(function(e) {
    e.preventDefault();
    formData = $(e.currentTarget).serialize();

    sendPayment(formData);
  });

  var sendPayment = function(form) {
    $.post("/payments/send", form, function(data) {
      if (data.success) {
        redirectWithMessage('/payments/', 'Your payment has been sent!')
      }
    });
  }

  var redirectWithMessage = function(location, message) {
    var form = $("#redirect_to");
    $("#flash_message").val(message);
    form.attr('action', location)
    form.submit();
  };
});
