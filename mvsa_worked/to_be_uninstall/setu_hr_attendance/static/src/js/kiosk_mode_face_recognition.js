odoo.define('setu_hr_attendance_face_recognition.kiosk_mode', function (require) {
    "use strict";

    var core = require('web.core');
    var KioskMode = require('hr_attendance.kiosk_mode');
    var FaceRecognitionDialog = require('hr_attendance_face_recognition.my_attendances').FaceRecognitionDialog;
    var Session = require('web.session');
    var framework = require('web.framework');

    var QWeb = core.qweb;

    var FaceRecognitionKioskMode = KioskMode.include({

        events: {
            "click .o_hr_attendance_button_employees": '_onattendance_button_click',
            "click .o_fetch_button_employees": '_onfetch_button_click',
            "click .o_set_button_employees": '_onset_button_click',
            "click .o_hr_attendance_back_screen": '_onBackScreen',
        },

        _onBackScreen: function () {
            debugger
            var self = this;
            var menu = window.location.href.indexOf('menu_id') >0 ? window.location.href.split('menu_id')[1] : ''
            if (menu.indexOf('&')!=-1){
                menu = menu.substr(0, menu.indexOf('&'))
            }
            window.location.href = '/web#action=hr_attendance_my_attendances&menu_id'+menu
            return self.do_action({
                type: 'ir.actions.client',
                tag: 'reload',
            })
        },
        update_attendance: async function () {
            var self = this;
            var new_attendance_state = self.employee.attendance_state == 'checked_in' ? 'checked_out' : 'checked_in'
            self.employee.attendance_state = new_attendance_state
            var online = await self.checkOnlineStatus();
            if (online) {
                self.parse_data_geo();
                self.geolocation();
                self.att_data.push({
                    'employee_id': self.employee.id,
                    'att_date_time': new Date().toISOString(),
                    'location': self.latitude + ' ' + self.longitude
                })
            } else {
                self.att_data.push({
                    'employee_id': self.employee.id,
                    'att_date_time': new Date().toISOString()
                })
            }
            sessionStorage.setItem("attendace", JSON.stringify(self.att_data))
            var online = await self.checkOnlineStatus();
            if (online) {
                self._save_attendance()
            }


        },

        _onset_button_click: function () {
            framework.blockUI();
            var self = this;
            $(".o_set_button_employees").addClass("d-none")
            $.when(this.update_attendance()).then(function () {
                self.$(".o_hr_attendance_kiosk_welcome_row").removeClass("d-none")
                self.$(".o_hr_attendance_kiosk_status_row").addClass("d-none")
                framework.unblockUI();
            });

        },

        _onfetch_button_click: function () {
            var self = this
            $(".o_set_button_employees").removeClass("d-none")
            console.log("heyyy buddy lets click selfie .... ¯\_(ツ)_/¯ ")
            self.parse_data_face_recognition();
            return $.when(self.data).then(
                result => {
                    this.promise_face_recognition.then(
                        result => {
                            this.state_save.then(
                                result => {
                                    if (this.face_photo)
                                        new FaceRecognitionDialog(this, {
                                            labels_ids: this.labels_ids,
                                            descriptor_ids: this.descriptor_ids,
                                            labels_ids_emp: this.labels_ids_emp,
                                            face_recognition_mode: 'kiosk'
                                        }).open();
                                    else
                                        Swal.fire({
                                            title: 'No one images/photos uploaded',
                                            text: "Please go to your profile and upload 1 photo",
                                            icon: 'error',
                                            confirmButtonColor: '#3085d6',
                                            confirmButtonText: 'Ok'
                                        });
                                })
                        })
                })


        },


        checkOnlineStatus: async function () {
            try {
                var online = await fetch(window.location.href);
                return online.status >= 200 && online.status < 300; // either true or false
            } catch (err) {
                return false; // definitely offline
            }
        },


        set_status: async function () {
            var self = this
            this.$(".o_hr_attendance_network_status").show()

            this.set_status_start = setInterval(async function () {
                var online = await self.checkOnlineStatus();
                if (online) {
                    self.$(".o_hr_attendance_network_status").text("Online");
                    self.online = true
                    self._save_attendance()
                    console.log("hey you are online :)")
                } else {

                    self.$(".o_hr_attendance_network_status").text("Offline");
                    self.online = false
                    console.log("hey you are offline :(")
                }
            }, 60000);
        },
        _save_attendance: function () {
            var self = this
            var attendace = sessionStorage.getItem("attendace") || '{}'
            this._rpc({
                model: 'hr.employee',
                method: 'save_attendance',
                args: [[], attendace],
            })
                .then(function (result) {
                    sessionStorage.removeItem("attendace");
                    self.att_data = []
                });
        },
        // parse data setting from server
        parse_data_geo: function () {
            var self = this;

            self.state_read.then(function (data) {
                var data = self.data;
                self.geo_enable = data.geo_enable;
                self.state_save.resolve();
            });
        },

        // get geolocation position
        geolocation: function () {
            var self = this;
            if (navigator.geolocation) {
                //self.geo_access = true;
                navigator.geolocation.getCurrentPosition(geo_success, geo_error, self.geo_options);
            } else {
                self.$("#geo-info").text("Geolocation is not supported by this browser");
                self.geo_access = false;
            }

            function geo_success(position) {
                self.geo_success(position);
            }

            function geo_error(err) {
                self.geo_error(err)
                self.geo_coords = $.Deferred();
            }
        },

        geo_success: function (position) {
            var self = this;
            // get coords
            self.latitude = position.coords.latitude;
            self.longitude = position.coords.longitude;
            self.geo_coords.resolve();

            // display coords in view
            self.$el.find('#latitude').html(self.latitude);
            self.$el.find('#longitude').html(self.longitude);

            //when parent start is end, display map
            self.state_render.then(function (data) {
                if (self.$('#mapid').length && self.latitude && self.longitude) {
                    var wh = window.innerHeight;
                    self.$('#openDiv').on('click', function (event) {
                        self.$('#mapid').toggle('show');
                        setTimeout(function () {
                            mymap.invalidateSize()
                        }, 400);
                    });
                    self.geo_access = true;
                    self.color_geo_success();
                    // set size map
                    self.$('#mapid').css('height', wh / 3);
                    // test on container Leaflet duplicate or already display
                    var container = L.DomUtil.get('mapid');
                    if (container != null) {
                        container._leaflet_id = null;
                    }
                    // display map with current marker user
                    self.point = new L.LatLng(self.latitude, self.longitude);
                    self.mymap = L.map(self.$('#mapid')[0]).setView(self.point, 13);
                    self.mymap.addControl(new L.Control.Fullscreen());
                    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                        attribution: 'Map data © <a href="http://openstreetmap.org">OpenStreetMap</a> contributors'
                    }).addTo(self.mymap);
                    var marker = L.marker(self.point).addTo(self.mymap);
                }
            });
        },

        color_geo_error: function () {
            // dynamic change color to denied mode geolocation
            var self = this;
            if (self.$("#icon-geo").hasClass('fa-check')) {
                self.$("#icon-geo").removeClass('fa-check');
                self.$("#icon-geo").addClass('fa-times');
            }
            if (self.geo_enable) {
                self.$("#geo-access").addClass("hr-attendance-base-denied");
                self.$('#state-geo').css("border", "2px solid #f27474");
                self.$("#icon-geo").addClass("hr-attendance-base-denied");
            }
        },

        color_geo_success: function () {
            // dynamic change color to success mode geolocation
            var self = this;
            //self.$el.html(QWeb.render("HrAttendanceMyMainMenu", {widget: self}));
            if (self.$("#icon-geo").hasClass('fa-times')) {
                self.$("#icon-geo").removeClass('fa-times');
                self.$("#icon-geo").addClass('fa-check');
            }
            if (self.geo_enable) {
                self.$("#geo-access").removeClass("hr-attendance-base-denied");
                self.$("#geo-access").css("color", "green");
                self.$('#state-geo').css("border", "2px solid green");
                self.$("#icon-geo").removeClass("hr-attendance-base-denied");
                self.$("#icon-geo").css("color", "green");
            }
        },

        geo_error: function (error) {
            var self = this;
            self.color_geo_error();
            self.geo_access = false;
            switch (error.code) {
                case error.PERMISSION_DENIED:
                    self.$("#geo-info").text("User denied the request for Geolocation.HINT: enable and refresh page");
                    /*                    Swal.fire({
                                          title: 'Geolocation error',
                                          text: "User denied the request for Geolocation.HINT: enable and refresh page",
                                          icon: 'error',
                                          confirmButtonColor: '#3085d6',
                                          confirmButtonText: 'Ok'
                                        });*/
                    //geo_ip(self.ip);
                    break;
                case error.POSITION_UNAVAILABLE:
                    self.$("#geo-info").text("Location information is unavailable.");
                    /*                    Swal.fire({
                                          title: 'Geolocation error',
                                          text: "Location information is unavailable.",
                                          icon: 'error',
                                          confirmButtonColor: '#3085d6',
                                          confirmButtonText: 'Ok'
                                        });*/
                    //geo_ip(self.ip);
                    break;
                case error.TIMEOUT:
                    self.$("#geo-info").text("The request to get user location timed out.");
                    /*                    Swal.fire({
                                          title: 'Geolocation error',
                                          text: "The request to get user location timed out.",
                                          icon: 'error',
                                          confirmButtonColor: '#3085d6',
                                          confirmButtonText: 'Ok'
                                        });*/
                    //geo_ip(self.ip);
                    break;
                case error.UNKNOWN_ERROR:
                    self.$("#geo-info").text("An unknown error occurred.");
                    /*                    Swal.fire({
                                          title: 'Geolocation error',
                                          text: "An unknown error occurred.",
                                          icon: 'error',
                                          confirmButtonColor: '#3085d6',
                                          confirmButtonText: 'Ok'
                                        });*/
                    //geo_ip(self.ip);
                    break;
            }
        },
        start: async function () {
            var self = this
            debugger
            this.geo_coords = $.Deferred();
            self.geo_options = {
                //a boolean by default false, requires a position with the highest level
                // of accuracy possible (which might take more time and more power)
                enableHighAccuracy: true,
                // to set the maximum “age” of the position cached by the browser.
                // We don’t accept one older than the set amount of milliseconds
                maximumAge: 30000,
                // to set the number of milliseconds before the request errors out
                timeout: 27000
            };
            self.geo_access = false;
            self.parse_data_geo();
            self.geolocation();
            self.state_render.then(function (data) {
                self.$("#geo-icon").on("click", function () {
                    if (self.$("#geo-icon").hasClass('fa-angle-double-down')) {
                        self.$("#geo-icon").removeClass('fa-angle-double-down');
                        self.$("#geo-icon").addClass('fa-angle-double-up');
                    } else {
                        self.$("#geo-icon").removeClass('fa-angle-double-up');
                        self.$("#geo-icon").addClass('fa-angle-double-down');
                    }
                    self.$("#geo-info").fadeToggle();
                    self.$('#mapid').toggle('show');
                    setTimeout(function () {
                        self.mymap.invalidateSize()
                    }, 400);
                });
            });
            self.att_data = [];
            self.session = Session;
            const session_cid = self.session.company_id;
            const company_id = self.session.user_context.allowed_company_ids[0];
            self.set_status()
            var company_data = []
            self.onoff_interval = setInterval(async () => {
                self.online_status = await self.checkOnlineStatus();
                console.log(self.online_status ? "Online" : "OFFline")
                if (!self.online_status) {
                    self._save_attendance()
                }
            }, 60000);
            var online_status = await self.checkOnlineStatus();
            if (online_status) {
                var def = self._rpc({
                    model: 'res.company',
                    method: 'search_read',
                    args: [[], ['name']],
                })
                    .then(function (res) {
                        $.each(res, function (i, v) {
                            company_data.push(v)
                        })
                        var match = company_data.filter(result => result.id === company_id)
                        if (match) {
                            self.company_name = match[0].name;
                            self.company_image_url = self.session.url('/web/image', {
                                model: 'res.company',
                                id: match[0].id,
                                field: 'logo',
                            });
                            self.company_image_url_kiosk = self.session.url('/web/image', {
                                model: 'res.company',
                                id: match[0].id,
                                field: 'kiosk_mode_logo',
                            });
                        }
                        sessionStorage.setItem("company_data", JSON.stringify(company_data))
                        self.$el.html(QWeb.render("HrAttendanceKioskMode", {widget: self}));
                        self.start_clock();
                    });
            } else if (sessionStorage.hasOwnProperty("company_data")) {
                company_data = JSON.parse(sessionStorage.getItem("company_data"))
                var match = company_data.filter(result => result.id === session_cid)
                if (match) {
                    self.company_name = match[0].name;
                    self.company_image_url = self.session.url('/web/image', {
                        model: 'res.company',
                        id: match[0].id,
                        field: 'logo',
                    });
                    self.company_image_url_kiosk = self.session.url('/web/image', {
                                model: 'res.company',
                                id: match[0].id,
                                field: 'kiosk_mode_logo',
                            });
                }
                self.$el.html(QWeb.render("HrAttendanceKioskMode", {widget: self}));
                self.start_clock();
            } else {
                console.log("you are offline")
            }

            var def_hr_attendance_base = this._rpc({
                route: '/hr_attendance_base',
                params: {
                    face_recognition_mode: 'kiosk'
                },
            }).then(function (data) {
                self.data = data;
                console.log("datag")
                console.log(self.data)
                self.state_read.resolve();
                self.state_save.then(function () {
                    self.state_render.resolve();
                });
            });
        },
    });
    return FaceRecognitionKioskMode
});
