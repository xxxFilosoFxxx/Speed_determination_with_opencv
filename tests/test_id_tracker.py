"""
Тесты для файлов в папке idtracker
"""
import unittest
from collections import OrderedDict
import numpy as np
from src.idtracker.centroid_tracker import CentroidTracker


class TestIdTracker(unittest.TestCase):
    """
    Класс тестов для остлеживание объектов
    """
    def test_update_tracker(self):
        """
        Тест для проверки трекера
        """
        centroid_tracker = CentroidTracker(max_disappeared=1)
        objects = OrderedDict()
        rect = list()

        ct_objects = centroid_tracker.update(rect)
        self.assertEqual(objects, ct_objects)

        rect.append((100, 150, 200, 250))
        ct_objects = centroid_tracker.update(rect)
        c_x = int((100 + 200) / 2.0)
        c_y = int((150 + 250) / 2.0)
        input_centroids = np.array([c_x, c_y])
        objects[0] = input_centroids
        self.assertEqual(objects[0][0], ct_objects[0][0])
        self.assertEqual(objects[0][1], ct_objects[0][1])

        ct_objects = centroid_tracker.update(rect)
        self.assertEqual(objects[0][0], ct_objects[0][0])
        self.assertEqual(objects[0][1], ct_objects[0][1])

        rect.clear()
        for _ in 1, 2:
            ct_objects = centroid_tracker.update(rect)
        self.assertEqual(OrderedDict(), ct_objects)
