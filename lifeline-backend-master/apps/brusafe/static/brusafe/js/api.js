$('.send').click(function () {
   $.ajax({
      type: "POST",
      url: this.dataset.url,
      data: {
        'national-registry-number': $(this).siblings('.national-registry-number').val(),
        'code': $(this).siblings('.code').val()
      },
      headers: {'Authorization': `jwt ${this.dataset.token}`},
      success: (data) => {
        $(this).next().html(`<br>Status: <span class="green-text">${data.status}</span><br>${data.responseJSON.detail}`);
      },
      error: (data) => {
        $(this).next().html(`<br>Status: <span class="red-text">${data.status}</span><br>${data.responseJSON.detail}`);
      }
    });
});
