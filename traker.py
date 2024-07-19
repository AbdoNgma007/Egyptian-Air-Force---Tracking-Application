import cv2

capture = cv2.VideoCapture("video.mp4")

tracker = cv2.legacy.TrackerMOSSE_create()
_, first_image = capture.read()
first_image = cv2.resize(first_image, (1280, 720))
bbox = cv2.selectROI("Object Target", first_image, False)
tracker.init(first_image, bbox)

while True:

    timer = cv2.getTickCount()
    success, image = capture.read()

    image = cv2.resize(image, (1280, 720))

    check, new_bbox = tracker.update(image)

    if check:
        x,y,w,h = int(new_bbox[0]),int(new_bbox[1]),int(new_bbox[2]),int(new_bbox[3])
        cv2.rectangle(image, (x,y), (x+w, y+h), (0,255,0), 2, 1)
        cv2.putText(image, "Found", (25,50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
    else:
        cv2.putText(image, "Not Found", (25,50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
    
    fps = cv2.getTickFrequency() / ( cv2.getTickCount() - timer )
    cv2.putText(image, str(int(fps)), (25,25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)

    cv2.imshow("Tracking", image)
    
    if cv2.waitKey(1) & 0xff == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()
