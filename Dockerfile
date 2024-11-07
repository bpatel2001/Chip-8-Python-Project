FROM python:3.11
WORKDIR /CHIP-8

RUN apt-get update
RUN apt-get install python3-pygame -y
RUN pip3 install pygame

COPY . .

ENV DISPLAY=host.docker.internal:0.0

CMD ["python", "chip8.py"]