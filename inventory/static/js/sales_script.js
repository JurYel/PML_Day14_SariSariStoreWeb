$(document).ready(function(){
//    $(function() {
//        $('input[name="datetimes"]').daterangepicker({
//            timePicker: true,
//            startDate: moment().startOf('hour'),
//            endDate: moment().startOf('hour').add(32, 'hour'),
//            locale: {
//                format: 'M/DD/YYYY hh:mm A'
//            }
//        });
//    });
    $('input[name="datetimes"]').daterangepicker({
        timePicker: true,
        autoUpdateInput: false,
        locale: {
             cancelLabel: 'Clear'
        }
    });

    $('input[name="datetimes"]').on('apply.daterangepicker', function(ev, picker){
        $(this).val(picker.startDate.format('MM/DD/YYYY hh:mm A') + ' - ' + picker.endDate.format('MM/DD/YYYY hh:mm A'));
    });
});