function getHref(button, type, prev, next) {
  if (prev) {
      if (next) {
          return button.attr('href').replace(prev[0], `${type}=${next}`);
      } else {
          return button.attr('href').replace(prev[0], '');
      }
  }
  return button.attr('href') + `&${type}=${next}`;
}


function setActivityExportParams(event, param) {
    const exportButton = $('.users-activity');
    const link = exportButton.attr('href');

    const paramValue = new RegExp(`${param}=([^&#]*)`).exec(link);
    exportButton.attr('href', getHref(exportButton, param, paramValue, event.target.value));
}
