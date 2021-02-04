# pylint: disable=no-else-return
"""
Основные действия для нахождения скорости после
детектирования и идентификации объектов
"""
from collections import OrderedDict
import math
import copy
import os

PPM = os.environ.get('PPM', 50)  # пиксель на метр


class SearchSpeed:
    """ Основной класс для нахождения скорости объекта """
    def __init__(self):
        self.track = dict()
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

    def search_speed(self, skip_frames, i):
        """
            Основаня функция для поиска скорости объекта за один кадр
        Args:
            skip_frames: частота кадров в секунду на видео
            i: идентификатор объекта

        Returns:
            скорость объекта
        """
        if i in self.centroids and i in self.last_centroids:
            d_pixels = math.sqrt(math.pow(self.last_centroids[i][0] - self.centroids[i][0], 2) +
                                 math.pow(self.last_centroids[i][1] - self.centroids[i][1], 2))
            ppm = PPM * 4
            d_meters = d_pixels / ppm
            fps = skip_frames
            speed = d_meters * fps * 3.6
            return speed  # Средняя скорость идущего человека 5-6 км/ч, бег 10-15 км/ч
        else:
            return 0

    @staticmethod
    def save_speed(timestamp, object_id, speed):
        """
            Функция сохраняет скорость объекта в файл
        Args:
            timestamp: Метка времени
            object_id: id объекта
            speed: скорость объекта
        """
        with open("test_result.txt", "a") as file:
            file.write("timestamp {}: ID {}: speed {:.2f}\n".format(int(timestamp), object_id + 1, speed))
