## Simple reference container image for this template.
##
## - Runs the example Python service in `src/main.py`.
## - Exposes a minimal HTTP health endpoint at `/health`.
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY src/main.py ./main.py

EXPOSE 8080

CMD ["python", "main.py"]