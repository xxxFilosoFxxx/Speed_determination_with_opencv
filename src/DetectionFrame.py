from src.idtracker.CentroidTracker import CentroidTracker
from src.idtracker.TrackableObject import TrackableObject
from src.SearchSpeed import SearchSpeed
from imutils.video import FPS
from datetime import datetime
from cv2 import cv2
import dlib
import os

PATH_VIDEO = os.environ.get('VIDEO', 'data_base/Тестовый_вариант.mp4')


class DetectionPeople:
    def __init__(self, video):
        self.cap = cv2.VideoCapture(video)
        self.net = cv2.dnn.readNetFromCaffe("MobileNetSSD/MobileNetSSD_deploy.prototxt",
                                            "MobileNetSSD/MobileNetSSD_deploy.caffemodel")
        self.class_name = {15: 'person'}
        self.percent = 0.2  # Можно задать аргументом
        self.centroids = SearchSpeed()
        self.frame_count = 0
        self.people_count = 0
        self.skip_frames = 25

    def search_people(self, cols, rows, out, rgb, frame, trackers):
        for i in range(0, out.shape[2]):
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

                # Создаем прямоугольник объекта с помошью dlib из ограничивающего
                # Поле координат, а затем запустить корреляцию dlib трекер
                tracker_id = dlib.correlation_tracker()
                rect = dlib.rectangle(x_left_bottom, y_left_bottom, x_right_top, y_right_top)
                tracker_id.start_track(rgb, rect)
                # Добавить трекер в наш список трекеров, чтобы мы могли
                # Использовать его во время пропуска кадров
                trackers.append(tracker_id)

                # Лэйбл с % точностью определения человека
                # label = self.class_name[class_id] + ": " + str(confidence)
                # cv2.putText(frame, label, (x_left_bottom, y_right_top + 15),
                #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))

    def status_tracking_speed(self, rect, rgb, frame, trackers):
        for index, tracker in enumerate(trackers):
            # Обновить трекер и получить обновленную позицию
            tracker.update(rgb)
            position = tracker.get_position()
            # Позиция объекта
            x_left_bottom, x_right_top = int(position.left()), int(position.right())
            y_left_bottom, y_right_top = int(position.top()), int(position.bottom())
            # добавить координаты ограничивающего прямоугольника в список прямоугольников
            rect.append((x_left_bottom, y_left_bottom, x_right_top, y_right_top))
            cv2.rectangle(frame, (x_left_bottom, y_left_bottom), (x_right_top, y_right_top),
                          (0, 255, 0))  # Определение контура человека
            # Добавление центроидов
            x_c, y_c = self.centroids.save_centroids(index, x_left_bottom, x_right_top, y_right_top)
            # Центроид
            cv2.circle(frame, (int(x_c), int(y_c)), 5, (0, 0, 255), -1)

            speed = self.centroids.search_speed(index)
            if speed != 0:
                speed_label = str("%.2f" % speed) + " km/hr"
                speed_label_size, base_line = cv2.getTextSize(speed_label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)

                y_left_bottom = max(y_left_bottom, speed_label_size[1])
                cv2.rectangle(frame, (x_left_bottom, y_left_bottom - speed_label_size[1]),
                              (x_left_bottom + speed_label_size[0], y_left_bottom + base_line),
                              (255, 255, 255), cv2.FILLED)
                cv2.putText(frame, speed_label, (x_left_bottom, y_left_bottom),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))
                # cv2.putText(frame, str(index), (x_left_bottom, y_left_bottom),
                #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))

    def counting_object(self, objects, frame):
        # цикл по отслеживанию объектов
        for (object_id, centroid) in objects.items():
            # проверить, существует ли отслеживаемый объект для текущего
            # идентификатор объекта
            add_object = self.centroids.track.get(object_id, None)

            # если не существует отслеживаемого объекта, создаем его
            if add_object is None:
                add_object = TrackableObject(object_id, centroid)
            else:
                add_object.centroids.append(centroid)
                if not add_object.counted:  # проверяем, был ли объект подсчитан
                    add_object.counted = True

            self.centroids.track[object_id] = add_object
            self.people_count = int(object_id + 1)
            cv2.putText(frame, str(object_id + 1), (centroid[0] - 10, centroid[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.circle(frame, (centroid[0], centroid[1]), 5, (0, 255, 0), -1)

    def config(self, frame):
        blob = cv2.dnn.blobFromImage(frame, 1.0 / 255, (300, 300), 127.5)
        self.net.setInput(blob)
        out = self.net.forward()

        cols = frame.shape[1]
        rows = frame.shape[0]

        return cols, rows, out

    def statistics_output(self, info, frame):
        text = "{}".format("INFO VIDEO STREAM")
        cv2.putText(frame, text, (20, frame.shape[0] - 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2, cv2.LINE_AA)
        for (idx, (row, column)) in enumerate(info):
            info = "{}: {}".format(row, column)
            cv2.putText(frame, info, (20, frame.shape[0] - ((idx * 20) + 20)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1, cv2.LINE_AA)

    def show_video(self):
        print("[INFO] starting video stream...")
        fps = FPS().start()
        ct = CentroidTracker(maxDisappeared=40, maxDistance=60)
        trackers = list()
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_resized = cv2.resize(rgb, (300, 300))

                rect = list()
                if self.frame_count % self.skip_frames == 0:
                    trackers = list()
                    cols, rows, out = self.config(frame_resized)
                    self.search_people(cols, rows, out, rgb, frame, trackers)
                else:
                    self.status_tracking_speed(rect, rgb, frame, trackers)
                objects = ct.update(rect)
                self.counting_object(objects, frame)
                self.frame_count += 1

                cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
                cv2.imshow("frame", frame)
                if cv2.waitKey(1) >= 0:  # Break with ESC
                    break
                fps.update()
            else:
                break
        fps.stop()
        print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
        print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

    def save_frames(self):
        print("[INFO] starting save video...")
        fps = FPS().start()
        ct = CentroidTracker(maxDisappeared=40, maxDistance=40)
        fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
        ret, frame = self.cap.read()
        out_video = cv2.VideoWriter('tests_video_detection/output: %r.avi' % datetime.now().strftime("%d-%m-%Y %H:%M"),
                                    fourcc, 25.0, (frame.shape[1], frame.shape[0]))
        trackers = list()
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_resized = cv2.resize(frame, (300, 300))

                rect = list()
                if self.frame_count % self.skip_frames == 0:
                    trackers = list()
                    cols, rows, out = self.config(frame_resized)
                    self.search_people(cols, rows, out, rgb, frame, trackers)
                else:
                    self.status_tracking_speed(rect, rgb, frame, trackers)
                objects = ct.update(rect)
                self.counting_object(objects, frame)

                info = [
                    ("Count people", self.people_count),
                    ("Recognition percentage", self.percent),
                    ("Recognition object", self.class_name[15])
                ]

                self.statistics_output(info, frame)
                self.frame_count += 1

                fps.update()
                out_video.write(frame)
            else:
                break
        fps.stop()
        print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
        print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
