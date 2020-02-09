$( document ).ready(function () {
  const upload = $('.upload');
  const loading = $('.loading');
  $('.parse-file').click(function () {
   upload.toggle('hidden');
   loading.toggle('hidden');
   $.ajax({
      type: "POST",
      url: this.dataset.url,
      data: {id: this.dataset.id, label: this.dataset.label},
      headers: {'Authorization': `jwt ${this.dataset.token}`},
      success: (data) => {
        upload.toggle('hidden')
        loading.toggle('hidden')
        alert(data.success)
      },
      error: (data) => {
        upload.toggle('hidden')
        loading.toggle('hidden')
        alert(`Error: ${data.responseJSON}`);
      }
    });
  });
});
