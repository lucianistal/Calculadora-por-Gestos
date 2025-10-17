import cv2
import mediapipe as mp
import numpy as np
import time
from math import atan2, degrees

# -------- CLASE DE BOTONES (interfaz) --------
class Button:
    def __init__(self, pos, width, height, value):
        self.pos = pos
        self.width = width
        self.height = height
        self.value = value

    def draw(self, img):
        cv2.rectangle(img, self.pos, (self.pos[0] + self.width, self.pos[1] + self.height),
                      (225, 225, 225), cv2.FILLED)
        cv2.rectangle(img, self.pos, (self.pos[0] + self.width, self.pos[1] + self.height),
                      (50, 50, 50), 3)
        text_x = self.pos[0] + self.width // 2 - 15
        text_y = self.pos[1] + self.height // 2 + 15
        cv2.putText(img, self.value, (text_x, text_y),
                    cv2.FONT_HERSHEY_PLAIN, 3, (50, 50, 50), 3)


# ------ CONFIGURACIÓN CÁMARA ------
cap = cv2.VideoCapture(0)
WIDTH, HEIGHT = 1280, 720
cap.set(3, WIDTH)
cap.set(4, HEIGHT)

# ------- BOTONES VISUALES -------
buttonListValues = [['C', '<'],
                    ['7', '8', '9', '/'],
                    ['4', '5', '6', '*'],
                    ['1', '2', '3', '-'],
                    ['0', '.', '=', '+']]

buttonlist = []
for y in range(5):
    for x in range(4):
        if y == 0 and x >= 2:
            break
        xpos = int(WIDTH - 500 + x * 100)
        ypos = int(HEIGHT * 0.15 + y * 100)
        if y == 0 and x == 1:
            xpos += 100
        width = 200 if y == 0 else 100
        buttonlist.append(Button((xpos, ypos), width, 100, buttonListValues[y][x]))

# ---- MEDIAPIPE -----
mp_hands = mp.solutions.hands
mp_face = mp.solutions.face_mesh
mp_pose = mp.solutions.pose
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
face_mesh = mp_face.FaceMesh(min_detection_confidence=0.7)
pose = mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# ------- VARIABLES --------
operation = ""
last_action_time = time.time()
last_detect_time = time.time()
delay_action = 3
auto_equal_time = 6
stable_count = 0
last_gesture = None

# ------ FUNCIONES -------
def contar_dedos(hand_landmarks, hand_label):
    dedos = []
    tip_ids = [4, 8, 12, 16, 20]

    # Pulgar (en eje X)
    if hand_label == "Right":
        dedos.append(1 if hand_landmarks.landmark[tip_ids[0]].x < hand_landmarks.landmark[tip_ids[0] - 1].x else 0)
    else:
        dedos.append(1 if hand_landmarks.landmark[tip_ids[0]].x > hand_landmarks.landmark[tip_ids[0] - 1].x else 0)

    # Otros dedos (en eje Y)
    for id in range(1, 5):
        if hand_landmarks.landmark[tip_ids[id]].y < hand_landmarks.landmark[tip_ids[id] - 2].y:
            dedos.append(1)
        else:
            dedos.append(0)

    return sum(dedos)


def detectar_puño(hand_landmarks):
    tip_ids = [8, 12, 16, 20]
    doblados = [hand_landmarks.landmark[i].y > hand_landmarks.landmark[i - 2].y for i in tip_ids]
    return all(doblados)


def detectar_ok(hand_landmarks):
    """
    Detecta el gesto OK: pulgar e índice formando un círculo,
    otros dedos extendidos.
    """
    # Puntas de los dedos
    pulgar_punta = hand_landmarks.landmark[4]
    indice_punta = hand_landmarks.landmark[8]
    medio_punta = hand_landmarks.landmark[12]
    anular_punta = hand_landmarks.landmark[16]
    meñique_punta = hand_landmarks.landmark[20]
    
    # Bases y nudillos para comparar
    indice_base = hand_landmarks.landmark[5]
    medio_base = hand_landmarks.landmark[9]
    anular_base = hand_landmarks.landmark[13]
    meñique_base = hand_landmarks.landmark[17]
    
    # Calcular distancia entre pulgar e índice
    dx = pulgar_punta.x - indice_punta.x
    dy = pulgar_punta.y - indice_punta.y
    distancia_pulgar_indice = (dx**2 + dy**2)**0.5
    
    # Verificar que pulgar e índice estén cerca (formando círculo)
    circulo = distancia_pulgar_indice < 0.05
    
    # Verificar que medio, anular y meñique estén extendidos (por encima de su base)
    medio_extendido = medio_punta.y < medio_base.y
    anular_extendido = anular_punta.y < anular_base.y
    meñique_extendido = meñique_punta.y < meñique_base.y
    
    return circulo and medio_extendido and anular_extendido


def inclinacion_cabeza(face_landmarks):
    """Devuelve (roll): inclinación lateral"""
    left_eye = face_landmarks.landmark[33]
    right_eye = face_landmarks.landmark[263]
    nose = face_landmarks.landmark[1]
    chin = face_landmarks.landmark[152]

    # Inclinación lateral (roll)
    dx = right_eye.x - left_eye.x
    dy = right_eye.y - left_eye.y
    roll = degrees(atan2(dy, dx))

    return roll


def detectar_brazo_arriba(pose_landmarks):
    """
    Detecta si el brazo derecho o izquierdo está estirado hacia arriba.
    Retorna: 'derecho', 'izquierdo', o None
    """
    if not pose_landmarks:
        return None
    
    # Puntos clave de pose
    hombro_der = pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    codo_der = pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW]
    muñeca_der = pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]
    
    hombro_izq = pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
    codo_izq = pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW]
    muñeca_izq = pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]
    
    nariz = pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE]
    
    # Brazo derecho arriba: muñeca más alta que hombro y codo
    brazo_der_arriba = (muñeca_der.y < hombro_der.y - 0.1 and 
                        muñeca_der.y < codo_der.y and
                        codo_der.y < hombro_der.y + 0.05 and
                        muñeca_der.visibility > 0.5)
    
    # Brazo izquierdo arriba: muñeca más alta que hombro y codo
    brazo_izq_arriba = (muñeca_izq.y < hombro_izq.y - 0.1 and 
                        muñeca_izq.y < codo_izq.y and
                        codo_izq.y < hombro_izq.y + 0.05 and
                        muñeca_izq.visibility > 0.5)
    
    if brazo_der_arriba and not brazo_izq_arriba:
        return 'derecho'
    elif brazo_izq_arriba and not brazo_der_arriba:
        return 'izquierdo'
    
    return None


def detectar_gestos(results_hands, results_face, results_pose):

    # ---Brazos levantados (suma y resta)---
    brazo = detectar_brazo_arriba(results_pose.pose_landmarks if results_pose else None)
    if brazo == 'derecho':
        return "+", "suma (brazo derecho arriba)"
    elif brazo == 'izquierdo':
        return "-", "resta (brazo izquierdo arriba)"

    # --- Cara (borrar / limpiar) ---
    if results_face.multi_face_landmarks:
        for faceLms in results_face.multi_face_landmarks:
            roll = inclinacion_cabeza(faceLms)
            if roll < -15:
                return "<", "borrar (inclinacion izq)"
            elif roll > 15:
                return "C", "limpiar (inclinacion der)"

    # --- Manos ---
    if not results_hands.multi_hand_landmarks:
        return None, None

    manos = []
    for hand_landmarks, handedness in zip(results_hands.multi_hand_landmarks, results_hands.multi_handedness):
        label = handedness.classification[0].label
        dedos = contar_dedos(hand_landmarks, label)
        es_puño = detectar_puño(hand_landmarks)
        manos.append((dedos, es_puño))

    # --- GESTOS OK (0 y punto decimal) ---
    ok_hands = []
    for hand_landmarks, handedness in zip(results_hands.multi_hand_landmarks, results_hands.multi_handedness):
        if detectar_ok(hand_landmarks):
            ok_hands.append(handedness.classification[0].label)

    # Pequeño retardo para confirmar si hay una o dos manos OK
    if len(ok_hands) == 1:
        # Esperar brevemente por si aparece la otra mano
        time.sleep(0.2)
        # Reprocesar para ver si hay 2 manos haciendo OK
        ok_hands2 = []
        for hand_landmarks, handedness in zip(results_hands.multi_hand_landmarks, results_hands.multi_handedness):
            if detectar_ok(hand_landmarks):
                ok_hands2.append(handedness.classification[0].label)
        if len(ok_hands2) == 2:
            return ".", "punto decimal (dos gestos OK)"
        else:
            return "0", "numero 0 (gesto OK)"

    elif len(ok_hands) == 2:
        return ".", "punto decimal (dos gestos OK)"


    # --- GESTOS DE DEDOS / PUÑOS / DOS MANOS ---
    if len(manos) == 1:
        dedos, es_puño = manos[0]
        if es_puño:
            return "*", "multiplicacion"
        if 1 <= dedos <= 5:
            return str(dedos), f"numero {dedos}"
    else:
        dedos_total = sum(m[0] for m in manos)
        puños = sum(1 for _, es_puño in manos if es_puño)

        if puños == 2:
            return "/", "division"
        if 6 <= dedos_total <= 10:
            return str(dedos_total), f"numero {dedos_total}"

    return None, None


# ------- BUCLE PRINCIPAL ------
while True:
    success, img = cap.read()
    if not success:
        break

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results_hands = hands.process(img_rgb)
    results_face = face_mesh.process(img_rgb)
    results_pose = pose.process(img_rgb)

    received_val = None
    current_time = time.time()

    val, tipo = detectar_gestos(results_hands, results_face, results_pose)
    if val:
        if val == last_gesture:
            stable_count += 1
        else:
            stable_count = 0
            last_gesture = val

        if stable_count > 5:
            received_val = val
            stable_count = 0
            last_detect_time = current_time

    # Autoevaluar si no hay gesto en 6 s
    if (current_time - last_detect_time > auto_equal_time) and operation != "":
        received_val = "="

    # Aplicar operación
    if received_val and (current_time - last_action_time > delay_action):
        if received_val == "=":
            try:
                operation = str(eval(operation))
            except:
                operation = "Error"
        elif received_val == "C":
            operation = ""
        elif received_val == "<":
            operation = operation[:-1]
        else:
            operation += received_val

        last_action_time = current_time

    # Dibujar interfaz
    operation_x = int(WIDTH - 500)
    operation_y = int(HEIGHT * 0.05)
    cv2.rectangle(img, (operation_x, operation_y),
                  (operation_x + 400, operation_y + 120),
                  (225, 225, 225), cv2.FILLED)
    cv2.rectangle(img, (operation_x, operation_y),
                  (operation_x + 400, operation_y + 120),
                  (50, 50, 50), 3)

    for button in buttonlist:
        button.draw(img)

    cv2.putText(img, operation, (operation_x + 10, operation_y + 75),
                cv2.FONT_HERSHEY_PLAIN, 3, (50, 50, 50), 3)

    # Mostrar el gesto detectado
    if val and tipo:
        cv2.putText(img, f"Gesto: {tipo}", (20, 40),
                    cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

    cv2.imshow('Calculadora por Gestos', img)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break
