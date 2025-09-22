FROM python:3.12.0

ENV HOME=/home/fast \
    APP_HOME=/home/fast/app \
    PYTHONPATH="$PYTHONPATH:/home/fast" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1


RUN mkdir -p $APP_HOME \
 && groupadd -r fast\
 && useradd -r -g fast fast

WORKDIR $HOME

COPY app app
COPY requirements.txt alembic.ini .

RUN pip install --upgrade pip \
 && pip install -r requirements.txt \
 && chown -R fast:fast .

USER fast