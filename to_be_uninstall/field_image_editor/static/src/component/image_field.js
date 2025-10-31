/** @odoo-module **/
import { ImageField } from '@web/views/fields/image/image_field';
import { patch } from 'web.utils';

patch(ImageField.prototype, 'field_image_editor_tui', {
    on_magic: function (e) {
        // Load an image and tell our tui imageEditor instance the new and the old image size:
        // var data = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7';
        let data = "/web/static/img/placeholder.png"
        if (this.props.value)
            data = this.getUrl(this.props.name)
        this.tui_image_open(data, {});
    },

    tui_image_open: function (data, file) {
        let tui_div = jQuery('<div/>', {
            id: 'tui-image-editor-container',
        })
        tui_div.appendTo($('body'));
        // Create an instance of the tui imageEditor, loading a blank image
        $(".o-main-components-container").width = "100%"
        const imageEditor = new tui.ImageEditor('#tui-image-editor-container', {
            includeUI: {
                loadImage: {
                    path: 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7',
                    name: 'Blank'
                },
                theme: blackTheme,
                initMenu: 'filter',
                menuBarPosition: 'left'
            },
        });
        $(".tui-image-editor-menu").css("z-index", "9999999")
        $("#tui-image-editor-container").css("position", "absolute")
        $("#tui-image-editor-container").css("height", "100%")
        $("#tui-image-editor-container").css("width", "100%")
        $('#tui-image-editor-container').fadeIn('show');


        const save = $('<div class="tui-image-editor-save-btn" style="background-color: #fff;border: 1px solid #ddd;color: #222;font-family: "Noto Sans", sans-serif;font-size: 12px">Save</div>');
        const close = $('<div class="tui-image-editor-close-btn" style="background-color: #fff;border: 1px solid #ddd;color: #222;font-family: "Noto Sans", sans-serif;font-size: 12px">Close</div>');
        close.insertAfter($('.tui-image-editor-download-btn'));
        save.insertAfter($('.tui-image-editor-download-btn'));
        $('.tui-image-editor-close-btn').click(function () {
            $('#tui-image-editor-container').fadeOut();
        });
        $('.tui-image-editor-save-btn').click(() => {
            let data = imageEditor.toDataURL();
            data = data.split(',')[1];
            this.props.update(data)
            $('#tui-image-editor-container').fadeOut();
        });

        // Patch the loadImageFromURL of our tui imageEditor instance:
        imageEditor.loadImageFromURL = (function () {
            let cached_function = imageEditor.loadImageFromURL;

            function waitUntilImageEditorIsUnlocked(imageEditor) {
                return new Promise((resolve, reject) => {
                    const interval = setInterval(() => {
                        if (!imageEditor._invoker._isLocked) {
                            clearInterval(interval);
                            resolve();
                        }
                    }, 100);
                })
            }
            return function () {
                return waitUntilImageEditorIsUnlocked(imageEditor).then(() => cached_function.apply(this, arguments));
            };
        })();

        imageEditor.loadImageFromURL(data, "SampleImage").then(result => {
            imageEditor.ui.resizeEditor({
                imageSize: {
                    oldWidth: result.oldWidth,
                    oldHeight: result.oldHeight,
                    newWidth: result.newWidth,
                    newHeight: result.newHeight
                },
            });
        }).catch(err => {
            console.error("Something went wrong:", err);
        })

        // Auto resize the editor to the window size:
        window.addEventListener("resize", function () {
            imageEditor.ui.resizeEditor()
        })
    },
});

