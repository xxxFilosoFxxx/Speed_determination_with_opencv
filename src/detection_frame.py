# pylint: disable=import-error, R0902, R0913, R0914
"""
Основной файл
"""
from datetime import datetime
import os
import dlib
from cv2 import cv2
from imutils.video import FPS

from src.idtracker.centroid_tracker import CentroidTracker
from src.idtracker.trackable_object import TrackableObject
from src.search_speed import SearchSpeed

# Путь к обрабатываемому видео
PATH_VIDEO = os.environ.get('VIDEO', 'data_user/Пример_записи_1080.mp4')
# процент распознавания
PERCENT = os.environ.get('PERCENT', 0.2)


class DetectionPeople:
    """
    Основной класс для определения скорости объектов
    -> в реальном времени
    -> с сохранением в видеофайл
    """
    def __init__(self, video):
        self.cap = cv2.VideoCapture(video)
        self.net = cv2.dnn.readNetFromCaffe("MobileNetSSD/MobileNetSSD_deploy.prototxt",
                                            "MobileNetSSD/MobileNetSSD_deploy.caffemodel")
        self.class_name = {15: 'person'}
        self.percent = PERCENT
        self.centroids = SearchSpeed()
        self.frame_count = 0
        self.people_count = 0
        self.skip_frames = self.cap.get(cv2.CAP_PROP_FPS)

    def search_people(self, cols, rows, out, rgb, frame, trackers):
        """
        Основная функция для детектирования объектов
        по назначенным классам
        """
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

    @staticmethod
    def status_tracking(rect, rgb, frame, trackers):
        """
        Функция позволяет обновит позицию
        отслеживаемых объектов
        """
        for tracker in trackers:
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

    def counting_object_and_search_speed(self, rect, objects, frame):
        """
        Функция осуществляет отслеживание, идентификацию,
        подсчет скорости объектов и вывод инфо в заданный файл
        """
        # Добавление центроидов каждую секунду в упорядоченный словарь для нахождения скорости
        if self.frame_count % self.skip_frames == 0:
            self.centroids.save_centroids(objects)
        # цикл по отслеживанию объектов
        for (idx, (object_id, centroid)) in enumerate(objects.items()):
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
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.circle(frame, (centroid[0], centroid[1]), 5, (0, 0, 255), -1)

            if self.frame_count % self.skip_frames == 0 or object_id not in self.centroids.speed:
                # t_width, t_height = int(rect[object_id][2] - rect[object_id][0]),\
                #                     int(rect[object_id][3] - rect[object_id][1])
                print(rect)  # TODO пробовать через расстояние камеры до объекта + качество
                self.centroids.search_delta_speed(1, 1, self.skip_frames, object_id)
                self.centroids.save_speed(int(self.frame_count / self.skip_frames),
                                          object_id, self.centroids.speed[object_id])

            speed_label = str("%d" % self.centroids.speed[object_id]) + " km/hr"
            speed_label_size, base_line = cv2.getTextSize(speed_label,
                                                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            y_left_bottom = max(centroid[1], speed_label_size[1])
            cv2.rectangle(frame,
                          (centroid[0] + 50, centroid[1] - speed_label_size[1] - 100),
                          (centroid[0] - speed_label_size[1] - 35,
                           y_left_bottom + base_line - 100),
                          (255, 255, 255), cv2.FILLED)
            cv2.putText(frame, speed_label, (centroid[0] - 50, y_left_bottom - 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))
            info = "time {}: ID {}: {}".format(int(self.frame_count / self.skip_frames),
                                               int(object_id + 1), speed_label)
            cv2.putText(frame, info, (700, frame.shape[0] - ((idx * 50) + 50)),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 1, cv2.LINE_AA)

    def config(self, frame):
        """
        Функция для задания настроек видеофайла
        """
        blob = cv2.dnn.blobFromImage(frame, 1.0 / 255, (300, 300), 127.5)
        self.net.setInput(blob)
        out = self.net.forward()

        cols = frame.shape[1]
        rows = frame.shape[0]

        return cols, rows, out

    @staticmethod
    def statistics_output(info, frame):
        """
        Функция позволяет выводить или сохранять
        заданную информацию в видеофайл
        """
        text = "{}".format("INFO VIDEO STREAM")
        cv2.putText(frame, text, (20, frame.shape[0] - 240),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 2, cv2.LINE_AA)
        for (idx, (row, column)) in enumerate(info):
            info = "{}: {}".format(row, column)
            cv2.putText(frame, info, (20, frame.shape[0] - ((idx * 50) + 50)),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 1, cv2.LINE_AA)

    def show_video(self):
        """
        Функция позволяет в реальном времени
        обработать видеозафайл
        """
        fps = FPS().start()
        centroid_tracker = CentroidTracker(maxDisappeared=40, maxDistance=60)
        if not self.cap.isOpened():
            print("[INFO] failed to process video")
            return -1
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
                    self.status_tracking(rect, rgb, frame, trackers)
                else:
                    self.status_tracking(rect, rgb, frame, trackers)
                objects = centroid_tracker.update(rect)
                self.counting_object_and_search_speed(rect, objects, frame)
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
        self.cap.release()
        cv2.destroyAllWindows()
        return 0

    def save_frames(self):
        """
        Функция сохраняет файл после обработки
        """
        fps = FPS().start()
        centroid_tracker = CentroidTracker(maxDisappeared=40, maxDistance=60)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        if not self.cap.isOpened():
            print("[INFO] failed to process video")
            return -1
        ret, frame = self.cap.read()
        out_video = cv2.VideoWriter('data_user/output: %r.avi'
                                    % datetime.now().strftime("%d-%m-%Y %H:%M"),
                                    fourcc, self.skip_frames, (frame.shape[1], frame.shape[0]))
        print("[INFO] video quality: {} {}".format(frame.shape[1], frame.shape[0]))
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
                    self.status_tracking(rect, rgb, frame, trackers)
                else:
                    self.status_tracking(rect, rgb, frame, trackers)
                objects = centroid_tracker.update(rect)
                self.counting_object_and_search_speed(rect, objects, frame)

                info = [
                    ("Number of tracked objects", len(objects)),
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
        self.cap.release()
        out_video.release()
        return 0
