FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt constraints.txt ./
RUN pip install --no-cache-dir pip==26.2.2 setuptools==84.2.1 \
    && pip install --no-cache-dir -r requirements.txt -c constraints.txt
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir --no-deps --no-build-isolation . \
    && useradd --create-home --uid 10001 ojisan \
    && mkdir /runtime && chown ojisan:ojisan /runtime
USER ojisan
WORKDIR /runtime
CMD ["uvicorn", "ojisan.entrypoints.web:app", "--host", "0.0.0.0", "--port", "8195"]
