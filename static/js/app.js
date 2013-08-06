$('#target-num').editable({
    type: 'text',
    placement: 'bottom',
    url: '/set_target',
    pk: 1,
    title: '设置目标',
    validate: function(value) {
        value = $.trim(value);
        if (value == '') {
            return '目标不能是空啊亲';
        }
        value = parseInt(value, 10);
        if (isNaN(value)) {
            return '目标必须是数字';
        }
        if (value < window.visit_count) {
            return '目标不能比现在的来访数小啊亲';
        }
    },
    success: function(response) {
        if (response.first_time) {
            show_job_status(true);
        }
    }
});

$('#set-target-btn').click(function(e){
    e.stopPropagation();
    $('#target-num').editable('toggle');
});

var show_job_status = function(running) {
    function show_status(running) {
        alert(running);
    }

    if (!running) {
        $.getJSON('/status', function(data) {
            show_status(data.running);
        });
    } else {
        show_status(running);
    }
};

if (!window.current_target) {
    $('#target-num').editable('toggle');
} else {
    show_job_status();
}
