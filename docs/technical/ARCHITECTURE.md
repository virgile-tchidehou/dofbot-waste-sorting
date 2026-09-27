# 🏗️ Architecture Système

> **Historical validation note:** performance figures in this document come from the 2025 project notes. The complete training dataset and trained weights are not distributed in this public repository, so those figures should not be treated as independently reproducible benchmarks from the repository alone.

**Ucaotech DOFbot TRC2025 - Documentation Technique**

---

## 📋 Table des Matières

1. [Vue d'Ensemble](#vue-densemble)
2. [Architecture ROS](#architecture-ros)
3. [Pipeline Vision](#pipeline-vision)
4. [Modèles Machine Learning](#modèles-machine-learning)
5. [Système de Calibration](#système-de-calibration)
6. [Architecture Logicielle](#architecture-logicielle)
7. [Communication](#communication)
8. [Diagrammes](#diagrammes)

---

## 🎯 Vue d'Ensemble

### Composants Principaux

```
┌─────────────────────────────────────────────────────────────┐
│                    SYSTÈME UCAOTECH DOFBOT                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Vision     │  │   Control    │  │  Navigation  │      │
│  │   System     │──│   System     │──│   System     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                         │                                    │
│                    ┌────▼────┐                               │
│                    │   ROS   │                               │
│                    │  Core   │                               │
│                    └────┬────┘                               │
│                         │                                    │
│         ┌───────────────┼───────────────┐                   │
│         │               │               │                   │
│    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐              │
│    │ Camera  │    │  DOFbot │    │ Sensors │              │
│    │ Intel   │    │ 6-axis  │    │ Various │              │
│    └─────────┘    └─────────┘    └─────────┘              │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Stack Technologique

| Couche | Technologies |
|--------|-------------|
| **Hardware** | DOFbot 6-axis, Jetson Nano, Intel RealSense D435 |
| **OS** | Ubuntu 20.04 LTS (ARM64) |
| **Middleware** | ROS Noetic |
| **Vision** | OpenCV 4.5+, MediaPipe, Intel RealSense SDK |
| **ML/AI** | YOLOv8, TensorFlow Lite, PyTorch |
| **Control** | Yahboom Arm_Lib, Custom PID controllers |
| **Web** | WebSocket, HTML5, JavaScript ES6+ |
| **Language** | Python 3.8+, C++ (ROS nodes) |

---

## 🤖 Architecture ROS

### Graphe des Nœuds

```
                    ┌──────────────────┐
                    │   /camera_node   │
                    │   (realsense)    │
                    └────────┬─────────┘
                             │ /camera/color/image_raw
                             │ /camera/depth/image_rect
                             │
                    ┌────────▼─────────┐
                    │  /vision_node    │
                    │  (detection)     │
                    └────────┬─────────┘
                             │ /detected_objects
                             │ /object_pose
                             │
                    ┌────────▼─────────┐
                    │ /planning_node   │
                    │ (decision)       │
                    └────────┬─────────┘
                             │ /arm_command
                             │ /gripper_command
                             │
                    ┌────────▼─────────┐
                    │  /control_node   │
                    │  (execution)     │
                    └────────┬─────────┘
                             │ /joint_states
                             │
                    ┌────────▼─────────┐
                    │   /dofbot_hw     │
                    │   (hardware)     │
                    └──────────────────┘
```

### Nœuds ROS Détaillés

#### 1. **camera_node** (realsense2_camera)
```yaml
Type: C++ (librealsense)
Rôle: Acquisition images couleur + profondeur
Frequency: 30 Hz
Topics publiés:
  - /camera/color/image_raw (sensor_msgs/Image)
  - /camera/depth/image_rect_raw (sensor_msgs/Image)
  - /camera/color/camera_info (sensor_msgs/CameraInfo)
Parameters:
  - depth_width: 640
  - depth_height: 480
  - color_width: 1280
  - color_height: 720
  - fps: 30
```

#### 2. **vision_node** (custom)
```yaml
Type: Python 3
Rôle: Détection et classification objets
Frequency: 15 Hz
Topics souscrits:
  - /camera/color/image_raw
  - /camera/depth/image_rect_raw
Topics publiés:
  - /detected_objects (custom_msgs/DetectedObjects)
  - /object_pose (geometry_msgs/PoseStamped)
  - /debug_image (sensor_msgs/Image)
Services:
  - /vision/set_detection_mode (std_srvs/SetBool)
Parameters:
  - confidence_threshold: 0.75
  - nms_threshold: 0.4
  - model_path: ~/models/yolov8n_waste.pt
```

#### 3. **planning_node** (custom)
```yaml
Type: Python 3
Rôle: Planification trajectoire et décision
Frequency: 10 Hz
Topics souscrits:
  - /detected_objects
  - /joint_states
Topics publiés:
  - /arm_trajectory (trajectory_msgs/JointTrajectory)
  - /gripper_command (std_msgs/Float64)
Services:
  - /planning/pick_object (custom_srvs/PickObject)
  - /planning/place_object (custom_srvs/PlaceObject)
```

#### 4. **control_node** (custom)
```yaml
Type: Python 3
Rôle: Contrôle bas niveau bras robotique
Frequency: 50 Hz
Topics souscrits:
  - /arm_trajectory
  - /gripper_command
Topics publiés:
  - /joint_states (sensor_msgs/JointState)
  - /control_status (std_msgs/String)
Services:
  - /control/emergency_stop (std_srvs/Trigger)
  - /control/home_position (std_srvs/Trigger)
```

#### 5. **navigation_node** (custom)
```yaml
Type: Python 3
Rôle: Navigation autonome et évitement obstacles
Frequency: 20 Hz
Topics souscrits:
  - /camera/depth/image_rect_raw
  - /odom (nav_msgs/Odometry)
Topics publiés:
  - /cmd_vel (geometry_msgs/Twist)
  - /obstacles (sensor_msgs/PointCloud2)
```

### Messages Personnalisés

#### DetectedObjects.msg
```python
Header header
DetectedObject[] objects

# DetectedObject
string class_name       # "carton", "plastique", "metal"
float32 confidence      # 0.0 - 1.0
geometry_msgs/Point position  # Position 3D
geometry_msgs/Quaternion orientation
```

#### ArmCommand.msg
```python
Header header
float64[] joint_angles   # [servo1, servo2, ..., servo6]
float64 gripper_position # 0.0 (fermé) - 1.0 (ouvert)
float64 execution_time   # Temps d'exécution en secondes
```

---

## 👁️ Pipeline Vision

### Flux de Traitement

```
┌──────────────┐
│ Caméra       │
│ RealSense    │
└──────┬───────┘
       │ Image RGB 1280x720 @30fps
       │ Image Depth 640x480 @30fps
       │
┌──────▼───────────────────────────────────────┐
│ Prétraitement                                 │
│ - Redimensionnement (640x640)                │
│ - Normalisation (0-1)                        │
│ - Réduction bruit (Gaussian Blur)            │
└──────┬───────────────────────────────────────┘
       │
┌──────▼───────────────────────────────────────┐
│ Détection YOLOv8                             │
│ - Bounding boxes                             │
│ - Classes (3): carton, plastique, métal      │
│ - Scores de confiance                        │
└──────┬───────────────────────────────────────┘
       │
┌──────▼───────────────────────────────────────┐
│ Filtrage NMS                                 │
│ - Non-Maximum Suppression                    │
│ - IoU threshold: 0.4                         │
│ - Confidence threshold: 0.75                 │
└──────┬───────────────────────────────────────┘
       │
┌──────▼───────────────────────────────────────┐
│ Estimation 3D                                │
│ - Projection pixels → coordonnées 3D         │
│ - Utilisation depth image                    │
│ - Calibration caméra (intrinsèque)          │
└──────┬───────────────────────────────────────┘
       │
┌──────▼───────────────────────────────────────┐
│ Transformation Coordonnées                   │
│ - Caméra frame → Robot base frame            │
│ - Matrice de transformation 4x4              │
│ - TF (ROS Transform)                         │
└──────┬───────────────────────────────────────┘
       │
┌──────▼───────────────────────────────────────┐
│ Publication ROS                              │
│ - /detected_objects (liste objets)           │
│ - /object_pose (pose 3D)                     │
│ - /debug_image (visualisation)               │
└──────────────────────────────────────────────┘
```

### Modèle YOLOv8

**Architecture**: YOLOv8n (nano - optimisé pour embarqué)

```python
# Configuration modèle
Model: yolov8n_waste.pt
Input: 640x640x3 RGB
Classes: 3 (carton, plastique, métal)
Backbone: CSPDarknet53
Neck: PANet
Head: YOLOv8 Detection Head

# Performance
Inference time: ~35ms (Jetson Nano)
FPS: ~28 images/sec
mAP@0.5: 0.92
mAP@0.5:0.95: 0.78

# Dataset entraînement
Images: 2500 (train) + 500 (val)
Augmentations: flip, rotate, scale, color jitter
Epochs: 100
Batch size: 16
```

---

## 🧠 Modèles Machine Learning

### Structure Modèles

```
trc2025_train_models/
├── models/
│   ├── yolov8n_waste.pt          # Modèle principal
│   ├── yolov8n_waste_best.pt     # Meilleure version
│   ├── classifier_backup.h5       # Backup TensorFlow
│   └── config/
│       ├── yolo_config.yaml
│       └── training_params.json
├── data/
│   ├── train/                     # 2500 images
│   ├── val/                       # 500 images
│   ├── test/                      # 200 images
│   └── annotations/
│       ├── train.json             # Format COCO
│       └── val.json
└── scripts/
    ├── train_yolo.py
    ├── evaluate_model.py
    └── export_tflite.py
```

### Pipeline Entraînement

```python
# 1. Préparation données
├─ Collecte images (webcam, datasets publics)
├─ Annotation (LabelImg, CVAT)
├─ Augmentation (Albumentations)
└─ Split train/val/test (70/20/10)

# 2. Entraînement
├─ Initialisation YOLOv8n pretrained (COCO)
├─ Fine-tuning sur dataset déchets
├─ Early stopping (patience: 20 epochs)
├─ Learning rate: cosine annealing
└─ Optimiseur: AdamW

# 3. Évaluation
├─ Métriques: mAP, Precision, Recall, F1
├─ Validation croisée k-fold (k=5)
├─ Tests sur images réelles compétition
└─ Analyse erreurs (confusion matrix)

# 4. Déploiement
├─ Export ONNX/TensorRT (optimisation)
├─ Quantization (FP32 → FP16)
├─ Tests performance embarqué
└─ Intégration ROS node
```

### Métriques Performance

| Classe | Precision | Recall | F1-Score | Support |
|--------|-----------|--------|----------|---------|
| Carton | 0.94 | 0.91 | 0.92 | 350 |
| Plastique | 0.93 | 0.89 | 0.91 | 280 |
| Métal | 0.96 | 0.93 | 0.94 | 220 |
| **Moyenne** | **0.94** | **0.91** | **0.92** | **850** |

---

## 🎛️ Système de Calibration

### Architecture Calibration

```
┌─────────────────────────────────────────────┐
│         Système de Calibration              │
├─────────────────────────────────────────────┤
│                                             │
│  Interface Console  ◄─────┐                │
│  (clavier direct)          │                │
│                            │                │
│  Interface Web     ◄───────┼─── WebSocket  │
│  (réseau WiFi)             │    Server     │
│                            │                │
│  Configuration     ◄───────┘                │
│  (fichiers YAML)                            │
│                                             │
└─────────────┬───────────────────────────────┘
              │
              ▼
     ┌────────────────┐
     │  Arm_Lib API   │
     │  (DOFbot SDK)  │
     └────────┬───────┘
              │
              ▼
     ┌────────────────┐
     │  DOFbot HW     │
     │  (6 servos)    │
     └────────────────┘
```

### Serveur WebSocket

**Fichier**: `scripts/calibration_server.py`

```python
# Architecture serveur
class CalibrationServer:
    def __init__(self):
        self.arm = Arm_Lib.Arm_Device()
        self.websocket_server = None
        self.current_angles = [90, 90, 90, 90, 90, 90]
        
    async def handle_client(self, websocket):
        # Gestion connexions clients
        # Traitement commandes
        # Envoi status temps réel
        
    def move_servo(self, servo_id, angle):
        # Contrôle servomoteur
        # Validation limites
        # Enregistrement position
```

**Protocole Messages**:
```json
// Client → Serveur
{
  "action": "move_servo",
  "servo": 1,
  "angle": 45
}

// Serveur → Client
{
  "type": "status",
  "servo": 1,
  "angle": 45,
  "timestamp": "2025-10-16T10:30:00Z"
}
```

### Interface Web

**Fichier**: `web/calibration_interface.html`

```javascript
// Architecture interface
class CalibrationInterface {
    constructor() {
        this.ws = null;
        this.sliders = [];
        this.config = {};
    }
    
    connectWebSocket() {
        // Connexion serveur
        // Gestion reconnexion automatique
    }
    
    setupSliders() {
        // Création sliders HTML
        // Event listeners
        // Synchronisation état
    }
    
    sendCommand(action, data) {
        // Envoi commandes WebSocket
        // Gestion erreurs
    }
}
```

**Composants UI**:
- 6 sliders (1 par servo) : 0-180°
- Affichage angles temps réel
- Boutons positions prédéfinies
- Configuration IP dynamique
- Logs activité
- Status connexion

---

## 💻 Architecture Logicielle

### Structure Projet

```
ucaotech_dofbot_trc2025/
├── config/
│   ├── calibration/
│   │   ├── default_positions.yaml
│   │   └── servo_limits.yaml
│   ├── vision/
│   │   ├── camera_calibration.yaml
│   │   └── detection_params.yaml
│   └── robot/
│       ├── dofbot_config.yaml
│       └── kinematics.yaml
├── launch/
│   ├── full_system.launch
│   ├── vision_only.launch
│   └── calibration.launch
├── scripts/
│   ├── nodes/
│   │   ├── vision_node.py
│   │   ├── control_node.py
│   │   ├── planning_node.py
│   │   └── navigation_node.py
│   ├── calibration_server.py
│   └── utils/
│       ├── transforms.py
│       ├── kinematics.py
│       └── logger.py
├── src/
│   ├── vision/
│   │   ├── detector.py
│   │   ├── tracker.py
│   │   └── depth_processor.py
│   ├── control/
│   │   ├── arm_controller.py
│   │   ├── gripper_controller.py
│   │   └── trajectory_planner.py
│   └── navigation/
│       ├── obstacle_avoidance.py
│       └── path_planner.py
├── tests/
│   ├── test_vision_node.py
│   ├── test_control_node.py
│   └── test_integration.py
└── web/
    ├── calibration_interface.html
    ├── css/
    └── js/
```

### Patterns de Conception

#### 1. **Observer Pattern** (Messages ROS)
```python
class VisionNode:
    def __init__(self):
        # Publishers
        self.object_pub = rospy.Publisher('/detected_objects', ...)
        
        # Subscribers
        rospy.Subscriber('/camera/color/image_raw', self.image_callback)
    
    def image_callback(self, msg):
        # Traitement
        # Publication résultats
        self.object_pub.publish(detected_objects)
```

#### 2. **State Machine** (Contrôle robot)
```python
class RobotStateMachine:
    states = ['IDLE', 'SEARCHING', 'APPROACHING', 'PICKING', 'PLACING']
    
    def transition(self, event):
        if self.current_state == 'IDLE' and event == 'object_detected':
            self.current_state = 'APPROACHING'
```

#### 3. **Factory Pattern** (Création objets)
```python
class DetectorFactory:
    @staticmethod
    def create_detector(detector_type):
        if detector_type == 'yolo':
            return YOLODetector()
        elif detector_type == 'ssd':
            return SSDDetector()
```

---

## 📡 Communication

### Flux de Données

```
Caméra (30Hz)
    ↓
Vision Node (15Hz)
    ↓
Planning Node (10Hz)
    ↓
Control Node (50Hz)
    ↓
Hardware (100Hz)
```

### Latences Typiques

| Étape | Latence | Notes |
|-------|---------|-------|
| Acquisition image | ~33ms | 30 FPS caméra |
| Détection YOLO | ~35ms | Jetson Nano |
| Planification | ~10ms | Calculs cinématiques |
| Contrôle | ~2ms | Commande servos |
| **Total Pipeline** | **~80ms** | 12.5 Hz effectif |

### Synchronisation

```python
# Utilisation ROS Time
import rospy
from std_msgs.msg import Header

def publish_with_timestamp(data):
    msg = CustomMsg()
    msg.header.stamp = rospy.Time.now()
    msg.data = data
    pub.publish(msg)

# Synchronisation multi-topics
from message_filters import ApproximateTimeSynchronizer

sync = ApproximateTimeSynchronizer(
    [image_sub, depth_sub],
    queue_size=10,
    slop=0.1  # 100ms tolérance
)
sync.registerCallback(callback)
```

---

## 📊 Diagrammes

### Diagramme de Séquence - Pick & Place

```
User     Vision    Planning   Control   Robot
 │         │          │          │        │
 │─Start──>│          │          │        │
 │         │─Detect──>│          │        │
 │         │<─Object──│          │        │
 │         │          │─Plan────>│        │
 │         │          │<─Traj────│        │
 │         │          │          │─Move──>│
 │         │          │          │<─Done──│
 │         │          │─Grip────>│        │
 │         │          │          │─Close─>│
 │         │          │<─Success─│        │
 │<─Done───│          │          │        │
```

### Diagramme de Déploiement

```
┌────────────────────────────────────────────┐
│         Jetson Nano (Ubuntu 20.04)    │
├────────────────────────────────────────────┤
│                                            │
│  ┌──────────────┐  ┌──────────────┐       │
│  │  ROS Noetic  │  │   Python 3   │       │
│  │   (Core)     │  │   (Nodes)    │       │
│  └──────┬───────┘  └──────┬───────┘       │
│         │                 │                │
│         └────────┬────────┘                │
│                  │                         │
│         ┌────────▼────────┐                │
│         │  Linux Kernel   │                │
│         └────────┬────────┘                │
│                  │                         │
└──────────────────┼─────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
┌───────▼────────┐   ┌────────▼────────┐
│  Intel         │   │    DOFbot       │
│  RealSense D435│   │    6-axis Arm   │
│  (USB 3.0)     │   │    (Serial)     │
└────────────────┘   └─────────────────┘
```

---

## 🔧 Configuration Performance

### Optimisations Jetson Nano

```bash
# Mode performance maximale
sudo nvpmodel -m 0
sudo jetson_clocks

# Configuration TensorRT
export TRT_LOGGER_LEVEL=WARNING
export CUDA_VISIBLE_DEVICES=0

# Optimisation ROS
export ROS_HOSTNAME=localhost
export ROS_MASTER_URI=http://localhost:11311
```

### Paramètres Tuning

```yaml
# vision_params.yaml
detection:
  confidence_threshold: 0.75
  nms_threshold: 0.4
  max_detections: 10
  
camera:
  fps: 30
  resolution: [1280, 720]
  auto_exposure: true
  
control:
  velocity_limit: 0.5  # rad/s
  acceleration_limit: 2.0  # rad/s²
  position_tolerance: 0.01  # rad
```

---

## 📚 Références

- **ROS Noetic**: http://wiki.ros.org/noetic
- **YOLOv8**: https://docs.ultralytics.com/
- **Intel RealSense**: https://github.com/IntelRealSense/librealsense
- **DOFbot SDK**: https://github.com/YahboomTechnology/Dofbot-Jetson-Nano

---

## 📞 Support

Pour questions techniques : voir [docs/INDEX.md](../INDEX.md)

**Dernière mise à jour : 16 octobre 2025**
