odoo.define('setu_hr_attendance.my_attendances', function (require) {
    "use strict";

    var Attendances = require('hr_attendance_face_recognition.my_attendances').FaceRecognitionDialog
    var core = require('web.core');


    var _t = core._t;

    Attendances.include({

        check_in_out: function (canvas, employee) {
            $(".o_set_button_employees").removeClass("d-none")
            console.log("check_in_out")
            var debounced = _.debounce(() => {
                this.parent.face_recognition_access = true;

                if(this.face_recognition_mode === "kiosk") {
                    this.parent.employee = employee
                    return
                }
                
                // если нажата кнопка перерыва
                if (this.break)
                    this.parent.update_break_resume();
                else
                    this.parent.update_attendance();
            }, 500, true);
            debounced();
            this.parent.$(".o_hr_attendance_kiosk_welcome_row").addClass("d-none")
            this.parent.$(".o_hr_attendance_kiosk_status_row").removeClass("d-none")
            var new_attendance_state = employee.attendance_state != 'checked_in' ? _t('Check In') : _t('Check Out')
            var color = employee.attendance_state != 'checked_in' ? 'green' : 'red'
            var str = _t("<h2>Welcome</h2><br />") +
                " <h1>" + employee.name + "</h1><br />" +
                _t("Please click on confirm button to <br/>") +
                "<h2><span style=color:" + color + ">" + new_attendance_state + "</span></h2>";
            this.parent.$(".o_hr_attendance_kiosk_status_row").find(".kiosk_status_emp_container").html(str)
            this.destroy()
        },
    })
});
