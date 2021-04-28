"""
Тесты для файлов detection_frame.py и search_speed.py
"""
import unittest
import math
import glob
import csv
from collections import OrderedDict
from src.detection_frame import DetectionPeople
from src.search_speed import SearchSpeed


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

        width = 10  # Возьмем статическую ширину
        fps = 30  # Возьмем статическую частоту кадров
        test_speed = test_class_speed.search_speed(width, fps, 0)

        d_pixels = math.sqrt(math.pow(last_centroids[0][0] - centroids[0][0], 2) +
                             math.pow(last_centroids[0][1] - centroids[0][1], 2))
        ppm = (width / 0.5) * 10
        speed = int((d_pixels / ppm) * fps * 3.6)
        self.assertEqual(test_speed, speed)

        update_last_centroids = test_class_speed.save_centroids(test_dict)
        self.assertEqual(update_last_centroids, test_dict)

        zero_speed = test_class_speed.search_speed(width, fps, 1)
        self.assertEqual(zero_speed, 0)

    def test_full_search_save(self):
        """
        Тест на сохранение и обработку итогового видеофайла
        """
        people = DetectionPeople('data_user/видеонаблюдение.mp4')
        self.assertTrue(people.cap.isOpened())
        self.assertEqual(people.save_frames(), 0)

    def test_speed_with_delta(self):
        """
        Тест на определение допустимого диапазона скорости
        """
        file = glob.glob("data_user/*.csv")
        if len(file) == 1 or len(file) == 2:
            result = True
            with open(str(file[0]), encoding='utf-8') as r_file:
                file_reader = csv.reader(r_file, delimiter=";")
                count = 0
                for row in file_reader:
                    if count == 0:
                        pass
                    else:
                        # Средняя скорость идущего человека 5-6 км/ч, бег 10-15 км/ч
                        if int(row[2]) > 15 or int(row[2]) < 0:
                            result = False
                    count += 1
            self.assertTrue(result)

        elif len(file) > 2:
            self.fail("Пожалуйста, удалите все файлы `.csv` из папки `data_user` "
                      "для точного тестирования.")
        else:
            self.fail("Тест не пройден, так как в папке `data_user` отсутвуют файлы со скоростью.")

    def test_full_search_show(self):
        """
        Тест на обработку вывод на экран итогового видеофайла
        """
        people = DetectionPeople('data_user/видеонаблюдение.mp4')
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
