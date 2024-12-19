FROM python:3.12-slim

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container.
COPY . /app

# Install the application dependencies.
WORKDIR /app
RUN uv sync --frozen --no-cache
# RUN bash -c "source /app/.venv/bin/activate"

# Run the application.
# CMD ["ls", "-aR", "/app/.venv/bin"]
# CMD ["/app/.venv/bin/fastapi", "run", "/app/main.py", "--port", "80", "--host" ,"0.0.0.0"]
CMD ["/app/.venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
