$( document ).ready(function () {
  $('.send-email').click(function () {
    $.ajax({
      type: "POST",
      url: this.dataset.url,
      data: {email: this.dataset.email},
      headers: {'language': this.dataset.language},
      success: (data) => {
        alert(`Email has sent to "${this.dataset.email}"`)
      },
      error: (data) => {
        alert(`Error: ${data}`);
      }
    });
  });
});
