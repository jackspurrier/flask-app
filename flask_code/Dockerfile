FROM python:3.6
LABEL maintainer="spurrier0@googlemail.com"
COPY . /flask-app
WORKDIR /flask-app
RUN pip install -r requirements.txt
EXPOSE 8080
ENTRYPOINT ["python"]
CMD ["app/app.py"]
