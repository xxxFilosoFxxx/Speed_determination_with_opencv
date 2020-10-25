from cv2 import cv2
import os

PATH_VIDEO = os.environ.get('VIDEO', 'data_base/Dance.mp4')


class Detection_people:
    def __init__(self, video):
        self.cap = cv2.VideoCapture(video)
        self.net = cv2.dnn.readNetFromCaffe("MobileNetSSD/MobileNetSSD_deploy.prototxt",
                                            "MobileNetSSD/MobileNetSSD_deploy.caffemodel")
        self.class_name = {15: 'person'}

    def search_peaple(self, cols, rows, out, frame):
        for i in range(out.shape[2]):
            confidence = out[0, 0, i, 2]
            class_id = int(out[0, 0, i, 1])
            if confidence > 0.2 and class_id == 15.0:
                x_left_bottom = int(out[0, 0, i, 3] * cols)
                y_left_bottom = int(out[0, 0, i, 4] * rows)
                x_right_top = int(out[0, 0, i, 5] * cols)
                y_right_top = int(out[0, 0, i, 6] * rows)

                height_factor = frame.shape[0] / 300.0
                width_factor = frame.shape[1] / 300.0

                x_left_bottom = int(width_factor * x_left_bottom)
                y_left_bottom = int(height_factor * y_left_bottom)
                x_right_top = int(width_factor * x_right_top)
                y_right_top = int(height_factor * y_right_top)

                cv2.rectangle(frame, (x_left_bottom, y_left_bottom), (x_right_top, y_right_top),
                              (0, 255, 0))

                label = self.class_name[class_id] + ": " + str(confidence)
                label_size, base_line = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)

                y_left_bottom = max(y_left_bottom, label_size[1])
                cv2.rectangle(frame, (x_left_bottom, y_left_bottom - label_size[1]),
                              (x_left_bottom + label_size[0], y_left_bottom + base_line),
                              (255, 255, 255), cv2.FILLED)
                cv2.putText(frame, label, (x_left_bottom, y_left_bottom),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))
                print(label)

    def show_video(self):
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame_resized = cv2.resize(frame, (300, 300))

                blob = cv2.dnn.blobFromImage(frame_resized, 0.01, (300, 300), (127.5, 127.5, 127.5), False)
                self.net.setInput(blob)
                out = self.net.forward()

                cols = frame_resized.shape[1]
                rows = frame_resized.shape[0]

                self.search_peaple(cols, rows, out, frame)

                cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
                cv2.imshow("frame", frame)
                if cv2.waitKey(1) >= 0:  # Break with ESC
                    break
            else:
                break

    def save_frames(self):
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        ret, frame = self.cap.read()
        out_video = cv2.VideoWriter('data_base/output.avi', fourcc, 20.0, (frame.shape[1], frame.shape[0]))
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame_resized = cv2.resize(frame, (300, 300))

                blob = cv2.dnn.blobFromImage(frame_resized, 0.01, (300, 300), (127.5, 127.5, 127.5), False)
                self.net.setInput(blob)
                out = self.net.forward()

                cols = frame_resized.shape[1]
                rows = frame_resized.shape[0]

                self.search_peaple(cols, rows, out, frame)

                out_video.write(frame)
            else:
                break
