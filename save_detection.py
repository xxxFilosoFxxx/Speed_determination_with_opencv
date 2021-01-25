from src.detection_frame import DetectionPeople
from src.detection_frame import PATH_VIDEO


if __name__ == '__main__':
    print("[INFO] starting save video...")
    new_video = DetectionPeople(PATH_VIDEO)
    new_video.save_frames()
