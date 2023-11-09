from django.db import models
from django.shortcuts import render, HttpResponse
from django.db import models

class Employee(models.Model):
    name = models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=15)
    email = models.EmailField()
    employee_image = models.ImageField(upload_to='employee_images/')

    class Meta:
        app_label = 'myapp'

class Frame(models.Model):
    frame_data = models.BinaryField()

    class Meta:
        app_label = 'myapp'

def some_other_view(request):
    frames = Frame.objects.all()  # Retrieve all frames
    # Process frames as needed
    print("works")
    return render(request, 'cameraSetup.html', {'frames': frames})

    class Meta:
        app_label = 'myapp'



class VideoFrame(models.Model):
    frame = models.ImageField(upload_to='video_frames/')

    class Meta:
        app_label = 'myapp'


from django.db import models
