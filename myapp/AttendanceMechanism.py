# import cv2
# from django.http import StreamingHttpResponse, HttpResponse
# import face_recognition
# import numpy as np
# import pickle
# import mysql.connector
# from datetime import datetime
# from django.views.decorators.http import require_POST
# import cv2
# import face_recognition
# import mysql.connector
# import numpy as np
# import pickle
# from datetime import datetime
# from django.http import StreamingHttpResponse



# file = open('face_embeddings.sscan', 'rb')
# employee_embeddings = pickle.load(file)
# file.close()

# encodeListKnown = [emb for (_, _, emb) in employee_embeddings]
# employee_ids = [emp_id for (emp_id, _, _) in employee_embeddings]
# employee_names = [name for (_, name, _) in employee_embeddings]



class AttendanceMechanism:
    """
    A class that represents the attendance mechanism of the StaffScan Portal.

    Attributes:
    conn (mysql.connector.connection_cext.CMySQLConnection): A connection object to the MySQL database.
    cursor (mysql.connector.cursor_cext.CMySQLCursor): A cursor object to execute queries on the MySQL database.
    camera (cv2.VideoCapture): A video capture object to capture frames from the camera.

    Methods:
    generate_data(pickle_file): Generates embeddings for all employees and saves them to a pickle file.
    save_embeddings_to_pickle(embeddings, pickle_file): Saves the embeddings to a pickle file.
    get_frame(): Captures a frame from the camera and processes it to detect faces and recognize employees.
    video_feed(request): Returns a streaming HTTP response with the video feed from the camera.
    """

    def __init__(self):
        """
        Initializes a new instance of the AttendanceMechanism class.
        """
        self.conn = mysql.connector.connect(
            host="localhost",
            user="unknown",
            password="password",
            database="hackathon"
        )
        self.cursor = self.conn.cursor()
        self.camera = cv2.VideoCapture(0)
        self.release_camera = False

    def generate_data(self, pickle_file):
        """
        Generates embeddings for all employees and saves them to a pickle file.

        Args:
        pickle_file (str): The path of the pickle file to save the embeddings to.
        """
        cursor = self.conn.cursor()

        sql_query = "SELECT EmployeeID, Name, faceImage FROM Employee"

        cursor.execute(sql_query)

        employee_data = cursor.fetchall()
        embeddings = []

        for emp_id, name, image_data in employee_data:
            if image_data is not None:
                image_np_array = np.frombuffer(image_data, np.uint8)
                image = cv2.imdecode(image_np_array, cv2.IMREAD_COLOR)

                # Process the image to generate embeddings using face_recognition
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                encode = face_recognition.face_encodings(image)
                if len(encode) > 0:
                    embeddings.append((emp_id, name, encode[0]))

        cursor.close()
        self.conn.close()

        # Save the embeddings to a pickle file
        self.save_embeddings_to_pickle(embeddings, pickle_file)

        print("Embeddings saved to", pickle_file)

        # Save the embeddings to a pickle file
        self.save_embeddings_to_pickle(embeddings, pickle_file)

        print("Embeddings saved to", pickle_file)

    def save_embeddings_to_pickle(self, embeddings, pickle_file):
        """
        Saves the embeddings to a pickle file.

        Args:
        embeddings (list): A list of tuples containing the employee ID, name, and face embeddings.
        pickle_file (str): The path of the pickle file to save the embeddings to.
        """
        file = open(pickle_file, 'wb')
        pickle.dump(embeddings, file)
        file.close()        


    def get_frame(self):
        """
        Captures a frame from the camera and processes it to detect faces and recognize employees.

        Yields:
        bytes: A byte string representing the JPEG-encoded frame.
        """
        while True:
            success, frame = self.camera.read()
            target_region_height = 480
            target_region_width = 640
            if not success:
                break

            frameColor = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            faceCurFrame = face_recognition.face_locations(frameColor)
            encodeCurFrame = face_recognition.face_encodings(frameColor, faceCurFrame)
            frame = cv2.resize(frame, (target_region_width, target_region_height))

            if faceCurFrame:
                for encodeFace in encodeCurFrame:
                    matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                    faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

                    matchIndex = np.argmin(faceDis)
                    id = employee_ids[matchIndex]
                    name = employee_names[matchIndex]
                    print(name)
                    if matches[matchIndex] and faceDis[matchIndex] < 0.6:
                        current_datetime = datetime.now()

                        # Insert the data into the database
                        sql = "INSERT INTO EMPLOYEE_ATTENDANCE (EmployeeID, Start_Time) VALUES (%s, %s)"
                        val = (id, current_datetime)
                        self.cursor.execute(sql, val)
                        self.conn.commit()

                        (w, h), _ = cv2.getTextSize(name, cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                        offset = (414 - w) // 2
                        cv2.putText(frame, name, (808 + offset, 445),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

            ret, buffer = cv2.imencode('.jpg', frame)
            if ret:
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                
    

    def video_feed(self, request):
        """
        Returns a streaming HTTP response with the video feed from the camera.

        Args:
        request (django.http.request.HttpRequest): The HTTP request object.

        Returns:
        django.http.response.StreamingHttpResponse: A streaming HTTP response with the video feed from the camera.
        """
        video_stream = self.camera

        def response_generator():
            for chunk in self.get_frame():
                yield chunk

        response = StreamingHttpResponse(response_generator(), content_type='multipart/x-mixed-replace; boundary=frame')
        return response
    
    def release_camera_if_requested(self):
        if self.release_camera and self.camera.isOpened():
            self.camera.release()
            print("Camera released")

    def set_release_flag(self, release_flag):
        self.release_camera = release_flag


    def __del__(self):
        """
        Releases the camera object when the instance of the AttendanceMechanism class is destroyed.
        """
        
        self.camera.release()


# AttendanceMechanism().


# attendance_system = AttendanceMechanism()
# attendance_system.generate_data('face_embeddings.sscan')
# attendance_system.set_release_flag(True)
# attendance_system.release_camera_if_requested()