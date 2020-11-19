import numpy as np


class Search_speed:
    def __init__(self):
        self.centroids = np.array([])
        self.max = 0

    def save_centroids(self, i, x_left_bottom, x_right_top, y_right_top) -> (int, int):
        self.centroids = np.append(self.centroids, [i, [int(x_left_bottom + ((x_right_top - x_left_bottom) / 2)),
                                                        int(y_right_top)]])
        self.centroids.shape = (-1, 2)
        if self.max < i:
            self.max = i
        return self.centroids[-1][1][0], self.centroids[-1][1][1]

    def search_distance(self, i) -> (int, int):
        if i == self.centroids[i - self.max - 1][0] and self.centroids.__len__() > i + 1:
            return np.sqrt((self.centroids[i - self.max*2 - 2][1][0] - self.centroids[i - self.max - 1][1][0])**2), \
                   np.sqrt((self.centroids[i - self.max*2 - 2][1][1] - self.centroids[i - self.max - 1][1][1])**2)
        else:
            return 0, 0
