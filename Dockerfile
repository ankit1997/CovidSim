FROM continuumio/miniconda3

WORKDIR /app

COPY requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

EXPOSE 8080

COPY . /app

CMD streamlit run --server.port 8080 --server.enableCORS false app.py

# streamlit-specific commands for config
# ENV LC_ALL=C.UTF-8
# ENV LANG=C.UTF-8
# RUN mkdir -p /root/.streamlit
# RUN bash -c 'echo -e "\
# [general]\n\
# email = \"\"\n\
# " > /root/.streamlit/credentials.toml'

# RUN bash -c 'echo -e "\
# [server]\n\
# enableCORS = false\n\
# " > /root/.streamlit/config.toml'