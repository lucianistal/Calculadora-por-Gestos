IMAGE := gest-calc

build:
	docker build -t $(IMAGE) .

run:
	docker run -it \
		--shm-size=24g \
		-e DISPLAY=:0 \
		-e QT_QPA_PLATFORM_PLUGIN_PATH=/opt/.venv/lib/python3.11/site-packages/cv2/qt/plugins \
		-e QT_X11_NO_MITSHM=1 \
		-v ./:/opt/project \
		-v /tmp/.X11-unix:/tmp/.X11-unix \
		-v /dev/:/dev/ \
		--privileged \
		--gpus all \
		--rm \
		$(IMAGE) python /opt/project/src/gest-calc/calculadora.py

shell:
	docker run -it \
		--shm-size=24g \
		-e DISPLAY=:0 \
		-e QT_QPA_PLATFORM_PLUGIN_PATH=/opt/.venv/lib/python3.11/site-packages/cv2/qt/plugins \
		-e QT_X11_NO_MITSHM=1 \
		-v ./:/opt/project \
		-v /tmp/.X11-unix:/tmp/.X11-unix \
		-v /dev/:/dev/ \
		--privileged \
		--gpus all \
		--rm \
		$(IMAGE) /bin/bash
