odoo.define('setu_hr_attendance.my_attendances_offline_kisok', function (require) {
    "use strict";

    var core = require('web.core');
    var MyAttendances = require('hr_attendance_face_recognition.my_attendances').FaceRecognitionDialog;
    var QWeb = core.qweb;
    var _t = core._t;


    var MyAttendances = KioskMode.include({
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
                        setTimeout(function () { mymap.invalidateSize() }, 400);
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
    });

});
