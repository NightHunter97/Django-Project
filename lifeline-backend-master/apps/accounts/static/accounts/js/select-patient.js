$( document ).ready(function () {

  function validateDate() {
    const startActivity = $('.start-activity');
    const endActivity = $('.end-activity');
    const errorMessage = $('.upload-user form .error');
    if (startActivity && endActivity) {
      const start = Date.parse(startActivity.val());
      const end = Date.parse(endActivity.val());
      if (start > end) {
        endActivity.addClass('invalid');
        endActivity.css('color', 'red');
        $('.user-activity').attr('disabled', 'disabled')
        errorMessage.show()
        return
      }
    }
    endActivity.removeClass('invalid');
    endActivity.css('color', 'inherit');
    $('.user-activity').removeAttr('disabled')
    errorMessage.hide();
  }

  function getHref(type, prev, next) {
    if (prev) {
        if (next) {
            return $('.user-activity').attr('href').replace(prev[0], `&${type}=${next}`);
        } else {
            return $('.user-activity').attr('href').replace(prev[0], '');
        }
    }
    return $('.user-activity').attr('href') + `&${type}=${next}`;
  }

  $('.select-patient').change(function () {
    patient = new RegExp('[\?&]patient=([^&#]*)').exec($('.user-activity').attr('href'));
    $('.user-activity').attr('href', getHref('patient', patient, this.value));
  });
  $('.start-activity').change(function () {
    start = new RegExp('[\?&]start=([^&#]*)').exec($('.user-activity').attr('href'));
    $('.user-activity').attr('href', getHref('start', start, this.value));
    validateDate();
  });
  $('.end-activity').change(function () {
    end = new RegExp('[\?&]end=([^&#]*)').exec($('.user-activity').attr('href'));
    $('.user-activity').attr('href', getHref('end', end, this.value));
    validateDate();
  });

 $('.patient-input').on('keypress input', function() {
    const ul = $('.select-patient .select-dropdown');
    if (!ul.hasClass('active')) {
      ul.trigger('click');
    }
    var inputVal = $(this).val();
    $('.upload-user .select-dropdown').val('---------');
    patient = new RegExp('[\?&]patient=([^&#]*)').exec($('.user-activity').attr('href'));
    if (patient) {
        $('.user-activity').attr('href', getHref('patient', patient, ''));
    }
    $('.upload-user .select-dropdown').find('li').each(function() {
         if (!$(this).text().toLowerCase().includes(inputVal.toLowerCase())) {
            $(this).hide();
         } else {
            $(this).show();
         }
      });
    });
  $('.patient-input').on('blur', function() {
    $('.select-patient .select-dropdown').trigger('click');
  });
});
