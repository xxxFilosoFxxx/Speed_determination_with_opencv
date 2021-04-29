# pylint: disable=E0401, R0902, R0913, R0914, C0103, W0613, W0603
"""
Основной скрипт для распознавания и подсчета скорости объекта
"""
from datetime import datetime
import os
import numpy as np
import dlib
from cv2 import cv2
from imutils.video import FPS

from src.idtracker.centroid_tracker import CentroidTracker
from src.idtracker.trackable_object import TrackableObject
from src.search_speed import SearchSpeed

# Путь к обрабатываемому видео
PATH_VIDEO = os.environ.get('VIDEO', 'data_user/видеонаблюдение.mp4')
# процент распознавания
PERCENT = os.environ.get('PERCENT', 0.2)
# интервал времени, в котором выполняется поиск скорости
TIME = os.environ.get('TIME', 1)

# глобальные переменные для обработки событий мыши
PT1 = (0, 0)
PT2 = (0, 0)
START_POINT = False
END_POINT = False


def draw_line(event, x, y, flags, param):
    """
    Функция обрабатывающая события мыши
    """
    global PT1, PT2, START_POINT, END_POINT

    if event == cv2.EVENT_LBUTTONDOWN:
        if START_POINT and END_POINT:
            START_POINT = False
            END_POINT = False
            PT1 = (0, 0)
            PT2 = (0, 0)

        if not START_POINT:
            PT1 = (x, y)
            START_POINT = True
        elif not END_POINT:
            PT2 = (x, y)
            END_POINT = True


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
        self.class_name = {0: 'background', 1: 'aeroplane', 2: 'bicycle', 3: 'bird',
                           4: 'boat', 5: 'bottle', 6: 'bus', 7: 'car', 8: 'cat',
                           9: 'chair', 10: 'cow', 11: 'diningtable', 12: 'dog',
                           13: 'horse', 14: 'motorbike', 15: 'person', 16: 'pottedplant',
                           17: 'sheep', 18: 'sofa', 19: 'train', 20: 'tvmonitor'}
        self.percent = PERCENT
        self.centroids = SearchSpeed()
        self.frame_count = 0
        self.people_count = 0
        self.skip_frames = self.cap.get(cv2.CAP_PROP_FPS)

    def search_people(self, wight, height, out, rgb, trackers):
        """
        Основная функция для детектирования объектов
        по назначенным классам
        """
        for i in range(0, out.shape[2]):
            confidence = out[0, 0, i, 2]
            if confidence > self.percent:
                class_id = int(out[0, 0, i, 1])
                if self.class_name[class_id] != "person":
                    continue

                # вычислить координаты ограничительной рамки для объекта
                box = out[0, 0, i, 3:7] * np.array([wight, height, wight, height])
                (x_left_bottom, y_left_bottom, x_right_top, y_right_top) = box.astype("int")
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

    def object_and_speed(self, filename, objects, frame):
        """
        Функция осуществляет отслеживание, идентификацию,
        подсчет скорости объектов и вывод инфо в заданный файл
        """
        # Добавление центроидов каждую секунду в упорядоченный словарь для нахождения скорости
        if self.frame_count % (int(self.skip_frames) * TIME) == 0:
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

            if self.frame_count % (int(self.skip_frames) * TIME) == 0 or \
                    object_id not in self.centroids.speed:
                # берем высотку и ширину выделенной фигуры объекта для нахождения скорсоти
                self.centroids.search_delta_speed(centroid[2], self.skip_frames, object_id)
                self.centroids.save_speed(filename, int(self.frame_count / self.skip_frames),
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
            cv2.putText(frame, info, (int(frame.shape[1] / 2), frame.shape[0] - ((idx * 50) + 50)),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 1, cv2.LINE_AA)

    def config(self, frame):
        """
        Функция для задания настроек видеофайла
        """
        wight = frame.shape[1]
        height = frame.shape[0]

        blur = cv2.medianBlur(frame, 3)

        blob = cv2.dnn.blobFromImage(blur, 0.007843, (wight, height), 127.5)
        self.net.setInput(blob)
        out = self.net.forward()

        return wight, height, out

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
        обработать видеозапись
        """
        key = True
        fps = FPS().start()
        centroid_tracker = CentroidTracker(max_disappeared=50, max_distance=50)
        if not self.cap.isOpened():
            print("[INFO] failed to process video")
            return -1
        filename_csv = 'data_user/output_csv: %r.csv' % datetime.now().strftime("%d-%m-%Y %H:%M")
        with open(filename_csv, mode="w", encoding='utf-8') as file:
            file.write("timestamp;ID;speed\r\n")
        trackers = list()

        cv2.namedWindow("frames", cv2.WINDOW_NORMAL)
        cv2.setMouseCallback("frames", draw_line)

        while self.cap.isOpened():
            ret, frame = self.cap.read()
            while ret and key:
                cv2.imshow("frames", frame)
                if START_POINT:
                    cv2.circle(frame, PT1, 3, (0, 0, 255), -1)
                if START_POINT and END_POINT:
                    cv2.line(frame, PT1, PT2, (0, 0, 255), 3)

                if cv2.waitKey(1) & 0xFF == ord('c'):
                    key = False
                    break

            if ret:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                rect = list()
                if self.frame_count % int(self.skip_frames) == 0:
                    trackers = list()
                    wight, height, out = self.config(frame)
                    self.search_people(wight, height, out, rgb, trackers)
                else:
                    self.status_tracking(rect, rgb, frame, trackers)
                objects = centroid_tracker.update(rect)
                self.object_and_speed(filename_csv, objects, frame)
                self.frame_count += 1

                cv2.imshow("frames", frame)

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
        Функция сохраняет видеозапись после обработки
        """
        fps = FPS().start()
        centroid_tracker = CentroidTracker(max_disappeared=50, max_distance=60)
        fourcc = cv2.VideoWriter_fourcc(*'H264')
        if not self.cap.isOpened():
            print("[INFO] failed to process video")
            return -1
        ret, frame = self.cap.read()
        filename = 'data_user/output_video: %r.mp4' % datetime.now().strftime("%d-%m-%Y %H:%M")
        filename_csv = 'data_user/output_csv: %r.csv' % datetime.now().strftime("%d-%m-%Y %H:%M")

        out_video = cv2.VideoWriter(filename, fourcc, self.skip_frames,
                                    (frame.shape[1], frame.shape[0]))
        with open(filename_csv, mode="w", encoding='utf-8') as file:
            file.write("timestamp;ID;speed\r\n")
        print("[INFO] video quality: {} {}".format(frame.shape[1], frame.shape[0]))
        trackers = list()
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                rect = list()
                if self.frame_count % int(self.skip_frames) == 0:
                    trackers = list()
                    wight, height, out = self.config(frame)
                    self.search_people(wight, height, out, rgb, trackers)
                else:
                    self.status_tracking(rect, rgb, frame, trackers)
                objects = centroid_tracker.update(rect)
                self.object_and_speed(filename_csv, objects, frame)

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
