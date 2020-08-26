FROM python:3.8

RUN pip install virtualenv
ENV VIRTUAL_ENV=/venv
RUN virtualenv venv -p python3
ENV PATH="VIRTUAL_ENV/bin:$PATH"

WORKDIR /app
ADD . /app

RUN pip install -r requirements.txt
COPY . /app

ENV PORT 8501

CMD streamlit run app.py