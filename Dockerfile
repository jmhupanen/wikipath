FROM python:3.7-stretch
ADD parser.py /
RUN pip install requests ray
CMD [ "python", "./parser.py" ]