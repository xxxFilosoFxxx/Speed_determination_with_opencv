"""
Тесты для файлов detection_frame.py и search_speed.py
"""
import unittest
import math
from collections import OrderedDict
from src.detection_frame import DetectionPeople
from src.search_speed import SearchSpeed
from src.search_speed import PPM


class TestFrame(unittest.TestCase):
    """
    Основной класс тестов
    """
    def test_speed_with_dict(self):
        """
        Тест определения скорости
        с помощью искусственного словаря
        """
        test_dict = OrderedDict()
        test_class_speed = SearchSpeed()

        # Возьмем объект с идентификатором '0'
        test_dict[0] = (100, 100)
        centroids = test_class_speed.save_centroids(test_dict)
        self.assertEqual(centroids, test_dict)

        test_dict[0] = (150, 150)
        last_centroids = test_class_speed.save_centroids(test_dict)
        self.assertEqual(last_centroids, test_dict)

        test_speed = test_class_speed.search_speed(0)

        d_pixels = math.sqrt(math.pow(last_centroids[0][0] - centroids[0][0], 2) +
                             math.pow(last_centroids[0][1] - centroids[0][1], 2))
        ppm = PPM * 4
        d_meters = d_pixels / ppm
        fps = 30
        speed = d_meters * fps * 3.6
        self.assertEqual(test_speed, speed)

        update_last_centroids = test_class_speed.save_centroids(test_dict)
        self.assertEqual(update_last_centroids, test_dict)

        zero_speed = test_class_speed.search_speed(1)
        self.assertEqual(zero_speed, 0)

    def test_full_search_show(self):
        """
        Тест на сохранение и обработку итогового видеофайла
        """
        people = DetectionPeople('data_user/парковка.mp4')
        self.assertTrue(people.cap.isOpened())
        self.assertEqual(people.save_frames(), 0)

    def test_full_search_save(self):
        """
        Тест на обработку вывод на экран итогового видеофайла
        """
        people = DetectionPeople('data_user/парковка.mp4')
        self.assertTrue(people.cap.isOpened())
        self.assertEqual(people.show_video(), 0)

    def test_video(self):
        """
        Тест на ошибочно выбранный
        (или не существующий) файл
        """
        people = DetectionPeople('000')
        self.assertFalse(people.cap.isOpened())
        self.assertEqual(people.save_frames(), -1)
        self.assertEqual(people.show_video(), -1)
