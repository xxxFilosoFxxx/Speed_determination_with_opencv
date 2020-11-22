from cv2 import cv2
from src.Search_speed import Search_speed
import os

PATH_VIDEO = os.environ.get('VIDEO', 'data_base/Видеонаблюдение.mp4')


class Detection_people:
    def __init__(self, video):
        self.cap = cv2.VideoCapture(video)
        self.net = cv2.dnn.readNetFromCaffe("MobileNetSSD/MobileNetSSD_deploy.prototxt",
                                            "MobileNetSSD/MobileNetSSD_deploy.caffemodel")
        self.class_name = {15: 'person'}
        self.percent = 0.2
        self.centroids = Search_speed()

    def search_people(self, cols, rows, out, frame):
        for i in range(out.shape[2]):
            confidence = out[0, 0, i, 2]
            class_id = int(out[0, 0, i, 1])
            if confidence > self.percent and class_id in self.class_name:
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

                # Определение контура человека
                cv2.rectangle(frame, (x_left_bottom, y_left_bottom), (x_right_top, y_right_top),
                              (0, 255, 0))

                # Добавление центроидов
                x_c, y_c = self.centroids.save_centroids(i, x_left_bottom, x_right_top, y_right_top)

                # Центроид
                cv2.circle(frame, (int(x_c), int(y_c)), 5, (0, 0, 255), -1)

                # Обработка скорости
                # self.centroids.search_distance(i) -> возвращает скорость объекта
                speed = self.centroids.search_distance(i)
                if speed != 0:
                    speed_label = str("%.2f" % speed) + " km/hr"
                    speed_label_size, base_line = cv2.getTextSize(speed_label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)

                    y_left_bottom = max(y_left_bottom, speed_label_size[1])
                    cv2.rectangle(frame, (x_left_bottom, y_left_bottom - speed_label_size[1]),
                                  (x_left_bottom + speed_label_size[0], y_left_bottom + base_line),
                                  (255, 255, 255), cv2.FILLED)
                    cv2.putText(frame, speed_label, (x_left_bottom, y_left_bottom),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))

                # Лэйбл с % точностью определения человека
                label = self.class_name[class_id] + ": " + str(confidence)
                cv2.putText(frame, label, (x_left_bottom, y_right_top + 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))
                # print(label)
                print(speed)
                # print(x_c, y_c)

    def config(self, frame):
        frame_resized = cv2.resize(frame, (300, 300))

        blob = cv2.dnn.blobFromImage(frame_resized, 0.01, (300, 300), (127.5, 127.5, 127.5), False)
        self.net.setInput(blob)
        out = self.net.forward()

        cols = frame_resized.shape[1]
        rows = frame_resized.shape[0]

        return cols, rows, out, frame

    def show_video(self):
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                cols, rows, out, frame = self.config(frame)
                self.search_people(cols, rows, out, frame)

                cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
                cv2.imshow("frame", frame)
                if cv2.waitKey(1) >= 0:  # Break with ESC
                    break
            else:
                break

    def save_frames(self):
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        ret, frame = self.cap.read()
        out_video = cv2.VideoWriter('tests_video_detection/output.avi', fourcc, 25.0, (frame.shape[1], frame.shape[0]))
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                cols, rows, out, frame = self.config(frame)
                self.search_people(cols, rows, out, frame)

                out_video.write(frame)
            else:
                break
