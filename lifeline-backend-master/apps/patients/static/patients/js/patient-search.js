$( document ).ready(function () {

    $(searchIdBar).keypress(function(e) {
        if (e.keyCode == 13) {
            const urlParams = new URLSearchParams(window.location.search);
            if (e.target.value) {
                var params = {'patient_id': e.target.value};
                for (var p of urlParams.entries()) {
                    if (p[0] === 'patient_id') {
                        params[p[0]] = e.target.value
                        continue
                    }
                    params[p[0]] = p[1];
                }
            } else {
                var params = {};
                for (var p of urlParams.entries()) {
                    if (p[0] === 'patient_id') {
                        continue
                    }
                    params[p[0]] = p[1];
                }
            }
            var paramsStr = $.param( params );
            window.location = $(location).attr('href').split("?")[0] + '?' + paramsStr;
            return false;
        }
    });

     $(searchDateBar).keypress(function(e) {
        if (e.keyCode == 13) {
            const urlParams = new URLSearchParams(window.location.search);
            if (e.target.value) {
                var params = {'birth_date': e.target.value};
                for (var p of urlParams.entries()) {
                    if (p[0] === 'birth_date') {
                        params[p[0]] = e.target.value
                        continue
                    }
                    params[p[0]] = p[1];
                }
            } else {
                var params = {};
                for (var p of urlParams.entries()) {
                    if (p[0] === 'birth_date') {
                        continue
                    }
                    params[p[0]] = p[1];
                }
            }
            var paramsStr = $.param( params );
            window.location = $(location).attr('href').split("?")[0] + '?' + paramsStr;
            return false;
        }
    })


    $('.searchByIdIcon').click(() => {
        var e = $.Event('keypress', { keyCode: 13 });
        $(searchIdBar).trigger(e);
    });

    $('.searchByDateIcon').click(() => {
        var e = $.Event('keypress', { keyCode: 13 });
        $(searchDateBar).trigger(e);
    });

    const urlParams = new URLSearchParams(window.location.search);
    $(searchIdBar).val(urlParams.get('patient_id'));
    $(searchDateBar).val(urlParams.get('birth_date'));
});
