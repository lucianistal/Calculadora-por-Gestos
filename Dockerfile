# can be changed, however this offers a good compromise between recency and compatibility
FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/opt/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

ENV QT_QPA_PLATFORM_PLUGIN_PATH=$VIRTUAL_ENV/lib/python3.9/site-packages/cv2/qt/plugins
ENV QT_X11_NO_MITSHM=1

# Dependencies for OpenCV + GUI
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        libx11-6 \
        libxext6 \
        libxrender1 \
        libqt5gui5 \
        libqt5widgets5 \
        libqt5core5a \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/.venv \
    && /opt/.venv/bin/pip install --upgrade pip \
    && /opt/.venv/bin/pip install --no-cache-dir opencv-python \
    && /opt/.venv/bin/pip install --no-cache-dir mediapipe


WORKDIR /opt