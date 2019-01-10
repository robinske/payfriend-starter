$(document).ready(function() {
  $("#send-payment-form").submit(function(e) {
    e.preventDefault();
    formData = $(e.currentTarget).serialize();
    attemptOneTouchVerification(formData);
  });

  var attemptOneTouchVerification = function(form) {
    $.post("/payments/send", form, function(data) {
      if (data.success) {
        $(".auth-ot").fadeIn();
        checkForOneTouch(data.payment_id);
        
        // display SMS option after 15 seconds
        setTimeout(function() {
          $("#payment_id").val(data.payment_id);
          $(".auth-sms").fadeIn();
        }, 15000);
      }
    });
  };

  var checkForOneTouch = function(payment_id) {
    $.get("/payments/status?payment_id=" + payment_id, function(data) {
      if (data == "approved") {
        redirectWithMessage('/payments/', 'Your payment has been approved!')
      } else if (data == "denied") {
        redirectWithMessage('/payments/send', 'Your payment request has been denied.');
      } else {
        setTimeout(checkForOneTouch(payment_id), 3000);
      }
    });
  };

  var redirectWithMessage = function(location, message) {
    var form = $("#redirect_to");
    $("#flash_message").val(message);
    form.attr('action', location)
    form.submit();
  };
});
