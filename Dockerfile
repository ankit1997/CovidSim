FROM continuumio/miniconda3

# RUN pip install virtualenv
# ENV VIRTUAL_ENV=/venv
# RUN virtualenv venv -p python3
# ENV PATH="VIRTUAL_ENV/bin:$PATH"

WORKDIR /app
ADD . /app

COPY environment.yml .
RUN conda env create -f environment.yml
RUN conda activate myenv


# RUN pip install -r requirements.txt
# COPY . /app

ENV PORT 8501

CMD streamlit run app.py

# streamlit-specific commands for config
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
RUN mkdir -p /root/.streamlit
RUN bash -c 'echo -e "\
[general]\n\
email = \"\"\n\
" > /root/.streamlit/credentials.toml'

RUN bash -c 'echo -e "\
[server]\n\
enableCORS = false\n\
" > /root/.streamlit/config.toml'