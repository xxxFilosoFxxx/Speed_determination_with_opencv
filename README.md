# A project using OpenCV (computer vision) to recognize the speed of a person in a video stream

### The method with the determination of centroids will be used

- The whole work plan is presented in the diagram
![Image alt](Speed_determination_diagram.jpg)

- First experiment - identification of the persons
![Image alt](test_images/first_detection.jpg)

- Second experiment - identifying people in the video and saving each frame to disk
![Image alt](test_images/test_frames.jpg)


### Deploying

As docker container:

- ```git clone https://github.com/xxxFilosoFxxx/Speed_determination_with_opencv.git```
- ```cd Speed_determination_with_opencv```
- ```docker build build -t speed_detection .```
- ```docker run -it -v ``` (you can forward your base with video) ```--name speed_detection```

Inside the container there is a script ```entrypoint.sh```, use it to process the video.

### Testing

To be continued 