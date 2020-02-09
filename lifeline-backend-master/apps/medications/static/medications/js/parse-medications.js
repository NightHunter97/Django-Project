$( document ).ready(function () {
  const upload = $('.upload');
  const loading = $('.loading');
  const validExts = ['.csv'];
  $('.parse-file').click(function () {
    const file = $(".input-upload")[0].files[0]
    if (!file) {
      return;
    }
    const fileExt = file.name.substring(file.name.lastIndexOf('.'));
    if (validExts.indexOf(fileExt) < 0) {
      alert('Only .csv format is valid');
    } else {
      upload.toggle('hidden');
      loading.toggle('hidden');
      $.ajax({
        type: "POST",
        url: this.dataset.url,
        data: $(".input-upload")[0].files[0],
        mimeType: "multipart/form-data",
        processData: false,
        headers: {'Authorization': `jwt ${this.dataset.token}`},
        success: (data) => {
          location.reload()
          alert('File was parsed successfully')
        },
        error: (data) => {
          upload.toggle('hidden')
          loading.toggle('hidden')
          alert(`Error: ${data.responseText}`);
        }
      });
    }
  });
});
