// import { session } from "@web/session";
import { patch } from "@web/core/utils/patch";
import kioskAttendanceApp from "@hr_attendance/public_kiosk/public_kiosk_app";
import { onWillStart } from "@odoo/owl";
import { useService } from '@web/core/utils/hooks';
import { rpc } from "@web/core/network/rpc";
import { _t } from "@web/core/l10n/translation";

/** ==================  CARGA SEGURA DE FACE‑API Y MODELOS  ================== */
// Carga segura del script si no existe (no duplica si ya está cargado)
let __faceApiLoadPromise = null;
async function ensureFaceApiLoaded() {
    if (window.faceapi) return;
    if (!__faceApiLoadPromise) {
        __faceApiLoadPromise = new Promise((resolve, reject) => {
            const s = document.createElement('script');
            s.src = "/face_recognition_hr_attendance/static/src/js/face-api.min.js";
            s.async = true;
            s.onload = () => resolve();
            s.onerror = () => reject(new Error("No se pudo cargar face-api.min.js"));
            document.head.appendChild(s);
        });
    }
    await __faceApiLoadPromise;
}

// Carga única de modelos; reusa la promesa para evitar “load model before inference”
let __modelsLoadPromise = null;
async function ensureModelsLoaded() {
    await ensureFaceApiLoaded();
    const nets = faceapi.nets;
    if (nets.tinyFaceDetector.isLoaded && nets.faceLandmark68Net.isLoaded && nets.faceExpressionNet.isLoaded) return;

    if (!__modelsLoadPromise) {
        const base = "/face_recognition_hr_attendance/static/src/assets/models";
        __modelsLoadPromise = Promise.all([
            nets.tinyFaceDetector.loadFromUri(base),
            nets.faceLandmark68Net.loadFromUri(base),
            nets.faceExpressionNet.loadFromUri(base),
        ]);
    }
    await __modelsLoadPromise;
}
/** ======================================================================== */

var interval = [];
var timerId = [];
var recognizedBarcode = null;
var recognizedEmployeeId = null;
var isScanning = false;

// ⛔️ Elimina tu inyección anterior de face-api.min.js.
// (Este archivo ya lo carga de forma segura con ensureFaceApiLoaded())

patch(kioskAttendanceApp.kioskAttendanceApp.prototype, {

    setup() {
        super.setup();
        var self = this;

        onWillStart(async () => {
            if (this.props.kioskMode === 'facial_recognition') {
                try {
                    // 🔒 Garantiza faceapi + modelos listos ANTES de seguir
                    await ensureModelsLoaded();
                    console.log("Modelos de FaceAPI cargados.");

                    // si quieres, puedes iniciar la cámara aquí, o dejar que otro flujo la arranque
                    setTimeout(() => this.startCam(), 300);
                } catch (error) {
                    console.error("Error al cargar Face-API o modelos:", error);
                    $("#web_cam_error").html("Error al cargar modelos de detección facial. Por favor, recargue la página.").show();
                }
            }
        });
    },

    prepareScan() {
        timerId.forEach(inter => clearInterval(inter));
        $("#video_box").show();
        $("#loader_img").show();
        $("#error_message").hide();
        $("#scan_again").hide();
        $("#photo_action_buttons").hide();
        $("#photo").attr('src', "#");
        recognizedBarcode = null;
        recognizedEmployeeId = null;
        isScanning = false;
    },

    async startCam() {
        // 🔒 Antes de tocar faceapi, confirma que todo esté cargado
        try {
            await ensureModelsLoaded();
        } catch (e) {
            console.error(e);
            $("#web_cam_error").text("Modelos de Face-API no disponibles.").show();
            return;
        }

        const videoEl = document.getElementById('video');
        const canvasEl = document.getElementById('cam_canvas');
        if (!videoEl || !canvasEl) {
            console.error("Elementos de video o canvas no encontrados.");
            return;
        }

        this._stopVideo(); // limpia cualquier stream/interval previo

        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            videoEl.srcObject = stream;
            this.mediaStream = stream;

            videoEl.addEventListener('loadeddata', () => {
                const displaySize = { width: videoEl.videoWidth || videoEl.width, height: videoEl.videoHeight || videoEl.height };
                faceapi.matchDimensions(canvasEl, displaySize);

                interval.forEach(clearInterval);
                interval = [];

                const faceDetectionInterval = setInterval(async () => {
                    if (isScanning) return;

                    // 🔒 NO llamamos a inferencia si los modelos no están cargados
                    if (!faceapi.nets.tinyFaceDetector.isLoaded) return;

                    const detections = await faceapi
                        .detectAllFaces(videoEl, new faceapi.TinyFaceDetectorOptions())
                        .withFaceLandmarks()
                        .withFaceExpressions();

                    const resizedDetections = faceapi.resizeResults(detections, displaySize);
                    const ctx = canvasEl.getContext('2d');
                    ctx.clearRect(0, 0, canvasEl.width, canvasEl.height);
                    faceapi.draw.drawDetections(canvasEl, resizedDetections);
                    faceapi.draw.drawFaceLandmarks(canvasEl, resizedDetections);
                    faceapi.draw.drawFaceExpressions(canvasEl, resizedDetections);

                    if (detections.length >= 1 && detections[0].detection.score > 0.9 && recognizedBarcode === null) {
                        // confianza alta → captura y procesa
                        isScanning = true;
                        this.takepicture();
                    }
                }, 120);
                interval.push(faceDetectionInterval);

                $("#loader_img").hide();
                $("#video_box").show();
                $("#web_cam_error").hide();
            }, { once: true });

        } catch (err) {
            console.error("Error al acceder a la cámara:", err);
            $("#web_cam_error").show();
        }
    },

    takepicture() {
        const videoEl = document.getElementById('video');
        const canvasPhotoEl = document.getElementById('canvas_photo');
        const photoEl = document.getElementById('photo');

        if (videoEl?.videoWidth && videoEl?.videoHeight) {
            canvasPhotoEl.width = videoEl.videoWidth;
            canvasPhotoEl.height = videoEl.videoHeight;
            const context = canvasPhotoEl.getContext('2d');
            context.drawImage(videoEl, 0, 0, videoEl.videoWidth, videoEl.videoHeight);

            const data = canvasPhotoEl.toDataURL('image/png');
            photoEl.setAttribute('src', data);

            if (photoEl.getAttribute("src") !== "#") {
                this.sendForRecognition(data);
            }
        } else {
            console.warn("Video aún no listo para capturar frame.");
        }
    },

    sendForRecognition(imageData) {
        $("#btn_confirm").attr("disabled", true).text("Processing...");

        $.post("/emp/attendance/img", { img: imageData, token: this.props.token }, respTxt => {
            isScanning = false;
            let resp;
            try { resp = JSON.parse(respTxt); } catch (e) { resp = { error: "Respuesta inválida del servidor." }; }

            if (resp.error) {
                $("#btn_confirm").attr("disabled", false).text("Confirm");
                $("#error_message").html(resp.error).show();
                $("#loader_img").hide();
                $("#scan_again").show();
                $("#timer_sec").html("Scan again in 05 seconds").show();
                timerId.forEach(i => clearInterval(i));
                if (this.use_timer) {
                    this.reScan();
                }
            } else {
                $("#btn_confirm").attr("disabled", false);
                recognizedBarcode = resp.barcode;
                recognizedEmployeeId = resp.employee_id;
                this.showButtons(resp.name || "Confirm");
            }
        }).fail(err => {
            isScanning = false;
            $("#btn_confirm").attr("disabled", false).text("Confirm");
            $("#error_message").html("No se pudo comunicar con el servidor.").show();
            console.error("POST /emp/attendance/img falló:", err);
        });
    },

    showButtons(empName){
        $("#btn_confirm").attr("disabled", false).text(`Confirm (${empName})`);
        $("#photo_action_buttons").show();
        $("#video_box").hide();
        $("#loader_img").hide();
        $("#scan_again").hide();
        $("#error_message").hide();
        $("#exampleModalLongTitle").hide();
        this.setupActionButtons();
    },

    setupActionButtons() {
        const btnBox = document.getElementById("photo_action_buttons");
        const retrieveBtn = document.getElementById("btn_retrieve");
        const confirmBtn = document.getElementById("btn_confirm");
        if (!btnBox || !retrieveBtn || !confirmBtn) return;

        retrieveBtn.onclick = () => {
            document.getElementById('photo').setAttribute('src', "#");
            btnBox.style.display = "none";
            recognizedBarcode = null;
            recognizedEmployeeId = null;
            $("#video_box").show();
            $("#loader_img").show();
            $("#exampleModalLongTitle").show();
            this.startCam();
        };

        confirmBtn.onclick = () => {
            const photoSrc = document.getElementById('photo').getAttribute('src');
            if (photoSrc && photoSrc !== "#" && recognizedBarcode) {
                console.log("Enviando el barcode para registro:", recognizedBarcode);
                this.onBarcodeScanned(recognizedBarcode);
                this._stopVideo();
            }
        };
    },

    async onBarcodeScanned(barcode) {
        this.lockScanner = true;
        const result = await rpc('attendance_barcode_scanned', {
            'barcode': barcode,
            'token': this.props.token
        });
        if (result && result.employee_name) {
            this.employeeData = result;
            this.switchDisplay('greet');
        } else {
            this.displayNotification(_t("No employee corresponding to Badge ID '%(barcode)s.'", { barcode }));
        }
        this.lockScanner = false;
    },

    _stopVideo() {
        timerId.forEach(inter => clearInterval(inter));
        interval.forEach(inter => clearInterval(inter));

        try {
            const videoEl = document.getElementById('video');
            if (videoEl && videoEl.srcObject) {
                videoEl.srcObject.getTracks().forEach(track => track.stop());
                videoEl.srcObject = null;
            }
        } catch (err) {
            console.error("Error al detener el video:", err);
        }

        $("#face_scan_popup").modal('hide');
        $("#video_box").show();
        $("#error_message").hide();
        $("#photo_action_buttons").hide();
        recognizedBarcode = null;
        recognizedEmployeeId = null;
        isScanning = false;
    }
});