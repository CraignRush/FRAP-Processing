FROM python:3.9.7
WORKDIR /app_home
COPY . .
VOLUME /app_home/data
#RUN apt-get update
#RUN apt-get install software-properties-common 
#RUN add-apt-repository ppa:deadsnakes/ppa
#RUN apt-get install python3.9
#RUN apt-get install python3-tk
#RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.9 1
#RUN update-alternatives --config python 
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "./main.py"]