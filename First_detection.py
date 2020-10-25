from Detection_frame import Detection_people
from Detection_frame import PATH_VIDEO


if __name__ == '__main__':
    new_video = Detection_people(PATH_VIDEO)
    new_video.save_frames()
