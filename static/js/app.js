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
        show_job_status(true);
    }
});

$('#set-target-btn').click(function(e){
    e.stopPropagation();
    $('#target-num').editable('toggle');
});

var job_status_container = $('#job-status-container');
job_status_container.on('click', '.job-start-btn', function(){
    $.post('/resume', function(){
        set_job_status(true);
    });
});
job_status_container.on('click', '.job-pause-btn', function(){
    $.post('/pause', function(){
        set_job_status(false);
    });
});

var set_job_status = function(running) {
    $('#job-status-text').text(running ? '运行中' : '已暂停')
                         .attr('class', running ? 'job-running' : 'job-stopping');

    $('#job-status-set-btn').text(running ? '暂停' : '开始')
                            .attr('class', running ? 'job-pause-btn' : 'job-start-btn');
};

var show_job_status = function(running) {
    function show_status(running) {
        set_job_status(running);
        $('#job-status-container').show();
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
