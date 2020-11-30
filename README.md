# A project using OpenCV (computer vision) to recognize the speed of a person in a video stream

## The method with the determination of centroids will be used

- The scheme for determining the speed of a person for a given video file is shown in the diagram
![Image alt](Scheme_for_determining_the_speed_of_a_person_for_a_given_video_file.png)

- The architecture of the software prototype is shown in the diagram
![Image alt](Software_prototype_architecture.png)

- First experiment - identification of the persons
![Image alt](tests_video_detection/first_detection.jpg)

- Second experiment - identifying people in the video and saving each frame to disk.
An example of the processed file is located [this](tests_video_detection/test_frames.avi).


## Deploying

As docker container:

- ```git clone https://github.com/xxxFilosoFxxx/Speed_determination_with_opencv.git```
- ```cd Speed_determination_with_opencv```
- ```docker build -t speed_detection .```
- ```docker run -it -v ~/data_user:/usr/share/python3/data_user --name speed_detection```

Inside the container there is a script ```entrypoint.sh```, use it to process the video.

## Testing

To be continued 
