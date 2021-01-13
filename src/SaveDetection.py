from src.DetectionFrame import DetectionPeople
from src.DetectionFrame import PATH_VIDEO


if __name__ == '__main__':
    new_video = DetectionPeople(PATH_VIDEO)
    new_video.save_frames()
