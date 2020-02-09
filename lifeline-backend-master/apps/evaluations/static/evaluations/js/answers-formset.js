$( document ).ready(function () {
    const type = $('#id_type');
    const answers_formset_type = $('div[data-formset-prefix="answers"]');
    function answerFormsetShow() {
        if (type.val() === 'choice_filed') {
            answers_formset_type.show()
        } else {
            answers_formset_type.hide()
        }
    }
    type.change(answerFormsetShow);
    answerFormsetShow();
});
