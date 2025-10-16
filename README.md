# Calculadora que funciona por gestos

Calculadora basada en gestos usando OpenCV y MediaPipe.

**Autor:** Lucía Nistal Palacios  
**Asignatura:** Sistemas Interactivos Inteligentes 

## Requisitos

- Docker
- Cámara en ordenador


## Instalación y Ejecución

### Construir la imagen Docker
```bash
make build
```

### Ejecutar la calculadora
```bash
make run
```

## Ejecución local (sin Docker)

Si Docker no tiene acceso a la cámara:
```bash
pip install -r requirements.txt
python src/gest-calc/calculadora.py
```

## Dependencias

- opencv-python==4.10.0.84
- mediapipe==0.10.14
- numpy==1.26.4

## Gestos

### Números
- **1-5**: Dedos levantados en una mano
- **6-9**: Suma de dedos de ambas manos
- **0**: Gesto OK (una mano, circulo hueco)
- **Punto (.)**: Gesto OK con ambas manos

### Operaciones
- **Suma (+)**: Brazo derecho levantado
- **Resta (-)**: Brazo izquierdo levantado
- **Multiplicación (*)**: Puño cerrado
- **División (/)**: Dos puños cerrados

### Controles
- **Borrar (<)**: Cabeza inclinada a la derecha
- **Limpiar (C)**: Cabeza inclinada a la izquierda
- **Igual (=)**: Esperar 6 segundos

## Uso

- Colócate mínimo a 1 metro de la cámara (sobretodo para que detecte mejor los gestos de los brazos)
- Mantén los gestos estables
- Hay 3 segundos de retardo entre gestos
- Presiona la letra 'q' para salir

## Estructura del proyecto
```
.
├── Dockerfile
├── Makefile
├── README.md
├── requirements.txt
├── memoria.pdf
└── src/
    └── gest-calc/
        ├── webcam_test.py
        └── calculadora.py
```
