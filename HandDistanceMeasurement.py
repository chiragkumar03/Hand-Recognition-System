import cv2 
import math
import mediapipe as mp
import numpy as np 

mpHands = mp.solutions.hands
hands = mpHands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mpdraw = mp.solutions.drawing_utils

def calculate_distance(x1, y1, x2, y2):
    distance = math.sqrt((x2 - x1)*2 + (y2 - y1)*2)
    return distance

x = [300, 245, 200, 170, 145, 130, 112, 103, 93, 87, 80, 75, 70, 67, 62, 59, 57]
y = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
coff = np.polyfit(x, y, 2)

cap = cv2.VideoCapture(0)
cap.set(3, 720) 
cap.set(4, 480)  
mylmList = []
img_counter=0
while True:
    isopen, frame = cap.read()
    frame = cv2.flip(frame, 1)  
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  
    results = hands.process(img)  
    allHands = []
    h, w, c = frame.shape  
    
    if results.multi_hand_landmarks:
        for handType, handLms in zip(results.multi_handedness, results.multi_hand_landmarks):
            myHand = {}
            mylmList = []
            xList = []
            yList = []
            
            for id, lm in enumerate(handLms.landmark):
                px, py, pz = int(lm.x * w), int(lm.y * h), int(lm.z * w)
                mylmList.append([id, px, py])
                xList.append(px)
                yList.append(py)
            
            xmin, xmax = min(xList), max(xList)
            ymin, ymax = min(yList), max(yList)
            boxW, boxH = xmax - xmin, ymax - ymin
            bbox = xmin, ymin, boxW, boxH
            cx, cy = bbox[0] + (bbox[2] // 2), bbox[1] + (bbox[3] // 2)
            
            myHand["lmList"] = mylmList
            myHand["bbox"] = bbox
            myHand["center"] = (cx, cy)
            myHand["type"] = handType.classification[0].label
            ''' if handType.classification[0].label == "Right":
                        myHand["type"] = "Left"
            else:
                        myHand["type"] = "Right"'''
            allHands.append(myHand)
            
            mpdraw.draw_landmarks(frame, handLms, mpHands.HAND_CONNECTIONS)
            cv2.rectangle(frame, (bbox[0] - 20, bbox[1] - 20), (bbox[0] + bbox[2] + 20, bbox[1] + bbox[3] + 20), (255, 0, 255), 2)
            cv2.putText(frame, myHand["type"], (bbox[0] - 30, bbox[1] - 30), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
            
            if mylmList != 0:
                try:
                    x, y = mylmList[5][1], mylmList[5][2]
                    x2, y2 = mylmList[17][1], mylmList[17][2]
                    dis = calculate_distance(x, y, x2, y2)
         
                    A, B, C = coff
                    distanceCM = A * dis**2 + B * dis + C
                    print(distanceCM)
                    cv2.rectangle(frame, (xmax - 80, ymin - 80), (xmax + 20, ymin - 20), (255, 0, 255), cv2.FILLED)
                    cv2.putText(frame, f"{int(distanceCM)}cm", (xmax - 80, ymin - 40), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 0), 2)
          
                except:
                    pass
    
    cv2.imshow('Hand Distance Measurement', frame)
    k = cv2.waitKey(1)
    if cv2.waitKey(1) & 0xff==ord('q'):
        break        



    