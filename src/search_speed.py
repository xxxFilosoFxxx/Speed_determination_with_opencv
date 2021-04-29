# pylint: disable=no-else-return, fixme
"""
Основные действия для нахождения скорости после
детектирования и идентификации объектов
"""
from collections import OrderedDict
import math
import copy
import os

# Дельта скорости объекта
DELTA = os.environ.get('DELTA', 0)
# Длина шага объекта (ширина полосы движения)
WIDTH = os.environ.get('WIDTH', 0.5)


class SearchSpeed:
    """ Основной класс для нахождения скорости объекта """
    def __init__(self):
        self.track = dict()
        self.speed = OrderedDict()
        self.centroids = OrderedDict()
        self.last_centroids = OrderedDict()

    def save_centroids(self, objects):
        """
            Функция для запоминания координат
            центроидов настоящего и прошлого кадра
        Args:
            objects: упорядоченный словарь

        Returns:
            копии (копию) упорядоченного словаря
        """
        if not self.centroids:
            self.centroids = copy.deepcopy(objects)
            return self.centroids

        if not self.last_centroids and self.centroids:
            self.last_centroids = copy.deepcopy(objects)
            return self.last_centroids

        self.centroids = copy.deepcopy(self.last_centroids)
        self.last_centroids = copy.deepcopy(objects)
        return self.last_centroids

    def search_speed(self, width, skip_frames, i):
        """
            Основаня функция для поиска скорости объекта
        Args:
            width: ширина выделенной фигуры объекта
            skip_frames: частота кадров в секунду на видео
            i: идентификатор объекта

        Returns:
            скорость объекта
        """
        # TODO: по расстоянию Евклида на основе локационной привязки определить скорость объекта
        if i in self.centroids and i in self.last_centroids:
            d_pixels = math.sqrt(math.pow(self.last_centroids[i][0] - self.centroids[i][0], 2) +
                                 math.pow(self.last_centroids[i][1] - self.centroids[i][1], 2))
            ppm = (width / WIDTH) * 10
            # определение через параметры не корректно!!!
            # в силу разницы углов камеры на каждом видео
            d_meters = d_pixels / ppm
            fps = skip_frames
            speed = d_meters * fps * 3.6
            return int(speed)  # Средняя скорость идущего человека 5-6 км/ч, бег 10-15 км/ч
        else:
            return 0

    def search_delta_speed(self, width, skip_frames, i):
        """
            Функция для записи текущей скорости и высчитывание дельты
        Args:
            width: ширина выделенной фигуры объекта
            skip_frames: частота кадров в секунду на видео
            i: идентификатор объекта
        """
        speed = self.search_speed(width, skip_frames, i)
        if i in self.speed:
            delta = speed - self.speed[i]
            if abs(delta) > DELTA:  # Дельта скорости объекта
                self.speed[i] = speed
        else:
            self.speed[i] = speed

    @staticmethod
    def save_speed(filename, timestamp, object_id, speed):
        """
            Функция сохраняет скорость объекта в файл
        Args:
            filename: Имя файла
            timestamp: Метка времени
            object_id: id объекта
            speed: скорость объекта
        """
        with open(filename, mode="a", encoding='utf-8') as file:
            file.write("{};{};{}\r\n".format(timestamp, object_id + 1, speed))
