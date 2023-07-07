FROM render.com/images/jvm
FROM  python:3.7
WORKDIR /app

COPY . /app/
COPY requirements.txt .

RUN pip install numpy padelpy==0.1.10 pandas Pillow scikit_learn streamlit protobuf install-jdk
# ENV PORT=8080
EXPOSE 8080
ENTRYPOINT ["streamlit", "run"]
CMD ["app_c_P.py"]