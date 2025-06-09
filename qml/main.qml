import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

ApplicationWindow {
    id: window
    width: 1024
    height: 768
    visible: true
    title: "TIF Viewer (QML)"

    property string currentFile: ""
    property string imagePath: ""

    FileDialog {
        id: fileDialog
        title: "选择TIF文件"
        nameFilters: ["TIF文件 (*.tif *.tiff)", "所有文件 (*)"]
        onAccepted: {
            currentFile = selectedFile.toString().replace("file://", "")
            backend.loadTifFile(currentFile)
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 5

        // 工具栏
        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            Button {
                text: "打开"
                onClicked: fileDialog.open()
            }

            Label {
                text: currentFile ? "当前文件: " + currentFile : "未选择文件"
                elide: Text.ElideMiddle
                Layout.fillWidth: true
            }
        }

        // 图像显示区域
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true

            Image {
                id: tifImage
                source: imagePath
                fillMode: Image.PreserveAspectFit
                cache: false
                asynchronous: true

                onStatusChanged: {
                    if (status === Image.Ready) {
                        statusLabel.text = "图像已加载"
                    } else if (status === Image.Loading) {
                        statusLabel.text = "正在加载图像..."
                    } else if (status === Image.Error) {
                        statusLabel.text = "图像加载错误"
                    }
                }
            }
        }

        // 信息面板
        Pane {
            Layout.fillWidth: true
            implicitHeight: 150

            ScrollView {
                anchors.fill: parent
                TextArea {
                    id: infoText
                    readOnly: true
                    wrapMode: Text.Wrap
                    text: "文件信息将显示在这里"
                }
            }
        }

        // 状态栏
        Label {
            id: statusLabel
            Layout.fillWidth: true
            text: "就绪"
        }
    }

    // 连接后端信号
    Connections {
        target: backend

        function onImageLoaded(filename, path) {
            window.imagePath = path
            window.currentFile = filename
        }

        function onErrorOccurred(message) {
            statusLabel.text = message
        }

        function onInfoUpdated(info) {
            infoText.text = info
        }
    }
}