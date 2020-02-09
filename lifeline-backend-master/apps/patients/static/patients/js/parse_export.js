$( document ).ready(function () {
  $('.parse-file').click(function () {
      $.ajax({
        type: "POST",
        url: this.dataset.url,
        data: JSON.stringify({'patient': this.dataset.object}),
        contentType: "application/json;charset=utf-8",
        headers: {'Authorization': `jwt ${this.dataset.token}`},
        success: (data) => {
          location.reload()
          alert('Generation export file was started')
        },
        error: (data) => {
          alert(`Error: ${data.responseText}`);
        }
      });
  });
});
