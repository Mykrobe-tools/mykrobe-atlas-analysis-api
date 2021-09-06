FROM python:3.6

WORKDIR /usr/src/app
COPY . .
RUN pip install -r requirements.txt -r test_requirements.txt

CMD ["python", "-m", "pytest", "tests"]