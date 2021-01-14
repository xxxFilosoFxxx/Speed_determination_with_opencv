import math


class SearchSpeed:
    def __init__(self):
        self.rect = list()
        self.trackers = list()
        self.track = dict()
        self.centroids = dict()
        self.last_centroids = dict()

    def save_centroids(self, i, x_left_bottom, x_right_top, y_right_top) -> (int, int):
        if i not in self.centroids:
            self.centroids[i] = [int(x_left_bottom + ((x_right_top - x_left_bottom) / 2)), int(y_right_top)]
            return self.centroids[i][0], self.centroids[i][1]

        if i not in self.last_centroids and i in self.centroids:
            self.last_centroids[i] = [int(x_left_bottom + ((x_right_top - x_left_bottom) / 2)), int(y_right_top)]
            return self.last_centroids[i][0], self.last_centroids[i][1]

        self.centroids[i] = self.last_centroids[i]
        self.last_centroids[i] = [int(x_left_bottom + ((x_right_top - x_left_bottom) / 2)), int(y_right_top)]

        return self.last_centroids[i][0], self.last_centroids[i][1]

    def search_speed(self, i):
        if i in self.centroids and i in self.last_centroids:
            d_pixels = math.sqrt(math.pow(self.last_centroids[i][0] - self.centroids[i][0], 2) +
                                 math.pow(self.last_centroids[i][1] - self.centroids[i][1], 2))
            ppm = 100  # TODO: стоит определять динамически
            d_meters = d_pixels / ppm
            fps = 25
            speed = d_meters * fps * 3.6
            return speed  # Средняя скорость идущего человека 5-6 км/ч, бег 10-15 км/ч
        else:
            return 0
