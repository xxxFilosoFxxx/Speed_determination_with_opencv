from cv2 import cv2


def blob_image(old_image):
    resize_image = cv2.resize(old_image, (300, 300))

    blob = cv2.dnn.blobFromImage(resize_image, 0.01, (300, 300), (127.5, 127.5, 127.5), False)
    print("[INFO] loading model...")

    net = cv2.dnn.readNetFromCaffe("MobileNetSSD_deploy.prototxt", "MobileNetSSD_deploy.caffemodel")
    net.setInput(blob)
    out = net.forward()
    return resize_image, out


def search_peaple(resized_image, ready_out):
    class_names = {0: 'background', 15: 'person'}

    cols = resized_image.shape[1]
    rows = resized_image.shape[0]

    for i in range(ready_out.shape[2]):
        confidence = ready_out[0, 0, i, 2]
        if confidence > 0.2:
            class_id = int(ready_out[0, 0, i, 1])
            x_left_bottom = int(ready_out[0, 0, i, 3] * cols)
            y_left_bottom = int(ready_out[0, 0, i, 4] * rows)
            x_right_top = int(ready_out[0, 0, i, 5] * cols)
            y_right_top = int(ready_out[0, 0, i, 6] * rows)

            height_factor = image.shape[0] / 300.0
            width_factor = image.shape[1] / 300.0

            x_left_bottom = int(width_factor * x_left_bottom)
            y_left_bottom = int(height_factor * y_left_bottom)
            x_right_top = int(width_factor * x_right_top)
            y_right_top = int(height_factor * y_right_top)

            cv2.rectangle(image, (x_left_bottom, y_left_bottom), (x_right_top, y_right_top),
                          (0, 255, 0))

            if class_id in class_names:
                label = class_names[class_id] + ": " + str(confidence)
                label_size, base_line = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)

                y_left_bottom = max(y_left_bottom, label_size[1])
                cv2.rectangle(image, (x_left_bottom, y_left_bottom - label_size[1]),
                              (x_left_bottom + label_size[0], y_left_bottom + base_line),
                              (255, 255, 255), cv2.FILLED)
                cv2.putText(image, label, (x_left_bottom, y_left_bottom),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))

                print(label)


def view_image():
    # cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
    cv2.imshow("Image", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    image = cv2.imread("business-people-walking.jpg")
    resize_image, out = blob_image(image)
    search_peaple(resize_image, out)
    view_image()

