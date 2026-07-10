# TruNorth Timesheet Pipeline - Dash app image

FROM python:3.12-slim

WORKDIR /app

# install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy app source
COPY app/ ./app/

EXPOSE 8050

ENV PYTHONPATH=/app
ENV REACT_VERSION=18.2.0
CMD ["python", "-m", "app.main"]
