FROM python:3.6
LABEL maintainer="spurrier0@googlemail.com"
COPY . /flask-app/flask_code
WORKDIR /flask-app/flask_code
RUN pip install -r requirements.txt
EXPOSE 8080
ENTRYPOINT ["python"]
CMD ["app1.py"]
