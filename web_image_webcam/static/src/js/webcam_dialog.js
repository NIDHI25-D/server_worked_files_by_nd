debugger
/** @odoo-module */
const { Component, useRef, useState } = owl;
import { Dialog } from "@web/core/dialog/dialog";
import { session } from '@web/session';
import { _t } from "@web/core/l10n/translation";
import { sprintf } from "@web/core/utils/strings";
import { loadBundle } from "@web/core/assets";

class WebcamDialog extends Component {

    async setup() {
        debugger
        super.setup();
        this.state = useState({
            snapshot: ""
        });
        this.video = useRef("video");
        this.saveButton = useRef("saveButton");
        this.selectCamera = useRef("selectCamera");
        await this.initSelectCamera();
        await this.startVideo();
    }

    async initSelectCamera() {
        debugger
        // добавляем все доступные камеры в селекшен
        const devices = await navigator.mediaDevices.enumerateDevices();
        const videoDevices = devices.filter(device => device.kind === 'videoinput');
        videoDevices.map(videoDevice => {
            let opt = document.createElement('option');
            opt.value = videoDevice.deviceId;
            opt.innerHTML = videoDevice.label;
            this.selectCamera.el.append(opt);
            return opt;
        });
    }

    onChangeDevice(e) {
        debugger
        // добавляем обработчик смены камеры
        const device = $(e.target).val();
        this.stopVideo()
        this.startVideo(device)
    }

    takeSnapshot(video) {
        debugger
        const canvas = document.createElement("canvas");
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const canvasContext = canvas.getContext("2d");
        canvasContext.drawImage(video, 0, 0);
        return canvas.toDataURL('image/jpeg');
    }

    async handleStream(stream) {
        debugger
        const def = $.Deferred();

        // устанавливаем выбранную камеру в селекшене
        if (stream && stream.getVideoTracks().length)
            this.selectCamera.el.value = stream.getVideoTracks()[0].getSettings().deviceId;

        // отображаем видео в диалоге
        this.video.el.srcObject = stream;

        this.video.el.addEventListener("canplay", () => {
            this.video.el.play();
        });

        this.video.el.addEventListener("loadedmetadata", () => {
            this.streamStarted = true;
            def.resolve();
        }, false);

        return def
    }

    async startVideo(device = null) {
        debugger
        try {
            let config = {
                width: { min: 640, ideal: session.am_webcam_width ? session.am_webcam_width : 1280 },
                height: { min: 480, ideal: session.am_webcam_height ? session.am_webcam_height : 720 },
                facingMode: this.props.mode ? 'user' : 'environment',
            }
            if (device)
                config.deviceId = { exact: device }

            const videoStream = await navigator.mediaDevices.getUserMedia({
                video: config
            })
            await this.handleStream(videoStream)
        } catch (e) {
            console.error('*** getUserMedia', e)
        } finally {
        }
    }

    stopVideo() {
        debugger
        // останавливае видео поток
        this.streamStarted = false;
        this.video.el.srcObject.getTracks().forEach((track) => {
            track.stop();
        });
    }

    /**
     * @returns {string}
     */
    getBody() {
        debugger
        return sprintf(
            _t(`You can setting default photo size and quality in general settings`),
        );
    }

    /**
     * @returns {string}
     */
    getTitle() {
        debugger
        return _t("Attachments manager Webcam");
    }

    urltoFile(url, filename, mimeType) {
        debugger
        return (fetch(url)
            .then(function (res) { return res.arrayBuffer(); })
            .then(function (buf) { return new File([buf], filename, { type: mimeType }); })
        );
    }

    async onwebcm(base64, mimetype) {
        debugger
        await this.props.onWebcamCallback(base64);
    }

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _onClickCancel(ev) {
        debugger
        ev.stopPropagation();
        ev.preventDefault();
        this.stopVideo();
        this.props.close();
    }

    _onWebcamSnapshot() {
        debugger
        this.state.snapshot = this.takeSnapshot(this.video.el)
    }

    async _onWebcamSave(ev) {
        debugger
        if (!this.state.snapshot)
            return;

        await this.onwebcm(this.state.snapshot.split(',')[1], "image/jpeg");
        this._onClickCancel(ev);

    }

}

WebcamDialog.props = {
    mode: { type: Boolean, optional: true },
    onWebcamCallback: { type: Function, optional: true },
    close: Function,
};

WebcamDialog.components = {
    Dialog,
};

WebcamDialog.defaultProps = {
    mode: false,
    onWebcamCallback: () => { },
};

WebcamDialog.template = 'web_image_webcam.WebcamDialog'

export default WebcamDialog;