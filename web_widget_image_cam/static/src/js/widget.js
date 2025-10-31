/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";

import { ImageField, imageField } from '@web/views/fields/image/image_field';
import { Dialog } from "@web/core/dialog/dialog";
import { Component, xml, onMounted } from "@odoo/owl";


class ImgCaptureDialog extends Component {
    static template = xml`<Dialog header="true" size="'lg'">
            <div><div class="container-fluid">
                            <div class="row" style="text-align: center;">
                                <div class="col-md-5">
                                    <video id="camera" autoplay="true"></video>
                                </div>
                                <div class="col-md-2"></div>
                                <div class="col-md-5">
                                    <canvas id="photo"></canvas>
                                </div>
                            </div>
                        </div></div>
            <t t-set-slot="footer">
                <button id="captureImage" class="btn btn-primary captureImage">Capture Image</button>
                <button class="btn btn-primary" t-on-click="saveClose">Save &amp; Close</button>
                <button class="btn btn-secondary" t-on-click="discard">Close</button>
            </t>
        </Dialog>`;
    static components = { Dialog };


    setup() {
        super.setup();
        var self = this
        console.log("this..........", this)
        onMounted(async function () {

            const video = document.getElementById('camera');
            const canvas = document.getElementById('photo');
            const captureBtn = document.getElementById('captureImage');
            const context = canvas.getContext('2d');

            video.setAttribute("width", 320)
            video.setAttribute("height", 240)

            canvas.setAttribute("width", 320)
            canvas.setAttribute("height", 240)

            // Request access to the user's camera
            navigator.mediaDevices.getUserMedia({ video: true })
                .then((stream) => {
                    video.srcObject = stream;
                })
                .catch((error) => {
                    console.error("Error accessing the camera: ", error);
                });

            // Capture photo on button click
            captureBtn.addEventListener('click', () => {
                canvas.width = 320;
                canvas.height = 240;
                context.drawImage(video, 0, 0, canvas.width, canvas.height);
            });
            // console.log("ddddsaaaaaaaaa", Webcam)
            // Webcam.set({
            //     width: 320,
            //     height: 240,
            //     image_format: 'jpeg',
            //     jpeg_quality: 100,
            //     force_flash: false,
            //     fps: 30,
            //     flip_horiz: false,
            // });
            // // setTimeout(function(){
            // Webcam.attach('live_cam_img');
            // // self.webcam = Webcam

            // // }, 5000)
            // var btnStart = document.getElementById("captureImage");
            // btnStart.addEventListener("click", function () {
            //     console.log("capture image")
            //     Webcam.snap(function (data) {
            //         console.log("data", data)
            //         img_data = data;
            //         $(".webcam_img").html('<img src="' + img_data + '"/>');
            //     });
            //     if (self.webcam.live) {
            //         $('.save_close_btn').removeAttr('disabled');
            //     }
            // });

            // $(".captureImage").on("click", function () {
            //     console.log("capture image")
            //     Webcam.snap(function (data) {
            //         console.log("data", data)
            //         img_data = data;
            //         $(".webcam_img").html('<img src="' + img_data + '"/>');
            //     });
            //     if (self.webcam.live) {
            //         $('.save_close_btn').removeAttr('disabled');
            //     }
            // })
        })
    }

    captureImage() {
        // console.log("capture image")
        // self.webcam.snap(function (data) {
        //     console.log("data", data)
        //     img_data = data;
        //     $(".webcam_img").html('<img src="' + img_data + '"/>');
        // });
        // if (self.webcam.live) {
        //     $('.save_close_btn').removeAttr('disabled');
        // }
    }

    saveClose() {
        console.log("Close ,,,,")
        var canvas = document.getElementById('photo');

        const img_data = canvas.toDataURL('image/png');

        var img_data_base64 = img_data.split(',')[1];
        var approx_img_size = 3 * (img_data_base64.length / 4) - (img_data_base64.match(/=+$/g) || []).length;
        this.props.aaaa.onFileUploaded({
            name: "web-cam-preview.jpeg",
            size: approx_img_size,
            type: "image/jpeg",
            data: img_data_base64,
        })
        var  video = document.getElementById('camera');

        try {
            var mediaStream = video.srcObject;
            //                console.log("mediaStream", mediaStream)
            var tracks = mediaStream.getTracks();
            tracks.forEach(track => track.stop())
        }
        catch (err) {
            console.error(err)
        }
        this.props.close()



    }
    discard() {
        var  video = document.getElementById('camera');

        try {
            var mediaStream = video.srcObject;
            //                console.log("mediaStream", mediaStream)
            var tracks = mediaStream.getTracks();
            tracks.forEach(track => track.stop())
        }
        catch (err) {
            console.error(err)
        }
        this.props.close()
    }

}

patch(ImageField.prototype, {
    setup() {
        super.setup();
        this.dialog = useService("dialog");
    },

    onCaptureImage() {
        var self = this

        // var CameraDialog = xml` <div><div class="container-fluid">
        //                         <div class="row" style="text-align: center;">
        //                             <div class="col-md-5">
        //                                 <span class="live_cam_img"/>
        //                             </div>
        //                             <div class="col-md-2"></div>
        //                             <div class="col-md-5">
        //                                 <span class="webcam_img"/>
        //                             </div>
        //                         </div>
        //                     </div></div>`
        // Webcam.set({
        //     width: 320,
        //     height: 240,
        //     image_format: 'jpeg',
        //     jpeg_quality: 100,
        //     force_flash: false,
        //     fps: 30,
        //     flip_horiz: false,
        // });
        var img_data
        this.dialog.add(ImgCaptureDialog, {
            "aaaa":self

        })
        console.log("ddddddddddddddd", this)
        // var dialog = new Dialog(this, Object.assign({
        //     size: 'large',
        //     dialogClass: 'o_act_window',
        //     title: "Camera",
        //     $content: CameraDialog,
        //     buttons: [
        //         {
        //             text: "Capture Image", classes: 'btn-primary',
        //             click: function () {
        //                 Webcam.snap(function (data) {
        //                     img_data = data;
        //                     $(".webcam_img").html('<img src="' + img_data + '"/>');
        //                 });
        //                 if (Webcam.live) {
        //                     $('.save_close_btn').removeAttr('disabled');
        //                 }
        //             }
        //         },
        //         {
        //             text: "Save & Close", classes: 'btn-primary save_close_btn', close: true,
        //             click: function () {
        //                 var img_data_base64 = img_data.split(',')[1];
        //                 var approx_img_size = 3 * (img_data_base64.length / 4) - (img_data_base64.match(/=+$/g) || []).length;
        //                 self.onFileUploaded({
        //                     name: "web-cam-preview.jpeg",
        //                     size: approx_img_size,
        //                     type: "image/jpeg",
        //                     data: img_data_base64,
        //                 })
        //             }
        //         },
        //         {
        //             text: "Close", close: true
        //         }
        //     ]
        // }))
        // dialog.open();
        // dialog.opened().then(function () {
        //     Webcam.attach('.live_cam_img');
        //     $('.save_close_btn').attr('disabled', 'disabled');
        //     $(".webcam_img").html('<img src="/web/static/img/placeholder.png"/>');
        // });
    }
})

// patch(Dialog.prototype, {
//     close: function () {
//         Webcam.reset();
//         this.destroy();
//     },
// })




