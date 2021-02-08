# pylint: disable=R0912, R0914
"""
Основной скрипт для отслеживания объектов
"""
from collections import OrderedDict
from scipy.spatial import distance as dist
import numpy as np


class CentroidTracker:
    """ Основной класс для отслеживания объектов """
    def __init__(self, max_disappeared=50, max_distance=50):
        self.next_object_id = 0
        self.objects = OrderedDict()
        self.disappeared = OrderedDict()
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance

    def register(self, centroid):
        """
            Добавление новых объектов для отслеживания
        Args:
            centroid: координаты центроида
        """
        self.objects[self.next_object_id] = centroid
        self.disappeared[self.next_object_id] = 0
        self.next_object_id += 1

    def deregister(self, object_id):
        """
            Удаление объектов из числа отслеживаемых
        Args:
            object_id: идентификатор объекта
        """
        del self.objects[object_id]
        del self.disappeared[object_id]

    def update(self, rects):
        """
            Обновление координат отслеживаемых объектов
        Args:
            rects: координаты фигуры объекта
        Returns:
            Словарь отслеживаемых объектов
        """
        if not rects:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            return self.objects

        input_centroids = np.zeros((len(rects), 4), dtype="int")

        for (i, (start_x, start_y, end_x, end_y)) in enumerate(rects):
            c_x = int((start_x + end_x) / 2.0)
            c_y = int((start_y + end_y) / 2.0)
            c_w = int(end_x - start_x)
            c_h = int(end_y - start_y)
            input_centroids[i] = (c_x, c_y, c_w, c_h)

        if not self.objects:
            for i, value in enumerate(input_centroids):
                self.register(value)

        else:
            object_i_ds = list(self.objects.keys())
            object_centroids = list(self.objects.values())

            _d = dist.cdist(np.array(object_centroids), input_centroids)

            rows = _d.min(axis=1).argsort()
            cols = _d.argmin(axis=1)[rows]

            used_rows = set()
            used_cols = set()

            for (row, col) in zip(rows, cols):
                if row in used_rows or col in used_cols:
                    continue
                if _d[row, col] > self.max_distance:
                    continue

                object_id = object_i_ds[row]
                self.objects[object_id] = input_centroids[col]
                self.disappeared[object_id] = 0

                used_rows.add(row)
                used_cols.add(col)

            unused_rows = set(range(0, _d.shape[0])).difference(used_rows)
            unused_cols = set(range(0, _d.shape[1])).difference(used_cols)
            if _d.shape[0] >= _d.shape[1]:
                for row in unused_rows:
                    object_id = object_i_ds[row]
                    self.disappeared[object_id] += 1
                    if self.disappeared[object_id] > self.max_disappeared:
                        self.deregister(object_id)
            else:
                for col in unused_cols:
                    self.register(input_centroids[col])
        return self.objects
