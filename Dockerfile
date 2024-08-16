FROM python:3.12.2-bookworm


RUN pip install poetry==1.8.2

WORKDIR /graphrag

COPY . /graphrag/


RUN pip install . && pip install flask


EXPOSE 5000


CMD python ./searchMethod/service_start_search.py
