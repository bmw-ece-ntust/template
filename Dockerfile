## Simple reference container image for this template.
##
## - Runs the example rApp service (Python) under `src/main.py`.
## - Exposes a minimal HTTP health endpoint at `/health`.

# Align structure with O-RAN SC `nonrtric-rapp-healthcheck`:
# - `src/requirements.txt` beside the entrypoint script
# - `WORKDIR /src`
FROM python:3.12-slim

WORKDIR /src

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1

COPY src/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src .

EXPOSE 8080

ENTRYPOINT ["python", "main.py"]
CMD []