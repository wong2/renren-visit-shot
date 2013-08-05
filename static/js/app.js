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
    }
});

$('#set-target-btn').click(function(e){
    e.stopPropagation();
    $('#target-num').editable('toggle');
});
