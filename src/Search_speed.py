import numpy as np


class Search_speed:
    def __init__(self):
        self.centroids = np.array([])

    def save_centroids(self, x_left_bottom, y_right_top):
        self.centroids = np.append(self.centroids, [int(x_left_bottom + (x_left_bottom / 2)), int(y_right_top)])
        self.centroids.shape = (-1, 2)
        return self.centroids[-1][0], self.centroids[-1][1]

    def search_speed(self):
        pass
