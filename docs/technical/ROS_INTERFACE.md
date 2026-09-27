# 📡 API Reference

**Ucaotech DOFbot TRC2025 - Documentation API ROS**

---

## 📋 Table des Matières

1. [Topics ROS](#topics-ros)
2. [Services ROS](#services-ros)
3. [Messages Personnalisés](#messages-personnalisés)
4. [Paramètres ROS](#paramètres-ros)
5. [Actions](#actions)
6. [API WebSocket](#api-websocket)
7. [Exemples d'Utilisation](#exemples-dutilisation)

---

## 📨 Topics ROS

### Topics Publiés

#### `/camera/color/image_raw`
```yaml
Type: sensor_msgs/Image
Fréquence: 30 Hz
Description: Image couleur brute de la caméra RealSense
Dimensions: 1280x720 (RGB8)
```

**Exemple d'utilisation**:
```python
import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

bridge = CvBridge()

def image_callback(msg):
    cv_image = bridge.imgmsg_to_cv2(msg, "bgr8")
    # Traiter l'image
    
rospy.Subscriber('/camera/color/image_raw', Image, image_callback)
```

#### `/camera/depth/image_rect_raw`
```yaml
Type: sensor_msgs/Image
Fréquence: 30 Hz
Description: Image de profondeur rectifiée
Dimensions: 640x480 (16UC1)
Unité: Millimètres
```

#### `/detected_objects`
```yaml
Type: custom_msgs/DetectedObjects
Fréquence: 15 Hz
Description: Liste des objets détectés par le système de vision
```

**Structure**:
```python
Header header
DetectedObject[] objects

# Chaque DetectedObject contient:
string class_name          # "carton", "plastique", "metal"
float32 confidence         # 0.0 - 1.0
geometry_msgs/Point position       # Position 3D (m)
geometry_msgs/Quaternion orientation
geometry_msgs/Vector3 dimensions   # Largeur, hauteur, profondeur (m)
int32 tracking_id          # ID unique pour suivi
```

**Exemple**:
```python
from custom_msgs.msg import DetectedObjects

def objects_callback(msg):
    for obj in msg.objects:
        print(f"Objet: {obj.class_name}")
        print(f"Confiance: {obj.confidence:.2f}")
        print(f"Position: x={obj.position.x:.3f}, y={obj.position.y:.3f}, z={obj.position.z:.3f}")
        
rospy.Subscriber('/detected_objects', DetectedObjects, objects_callback)
```

#### `/object_pose`
```yaml
Type: geometry_msgs/PoseStamped
Fréquence: 15 Hz
Description: Pose 3D de l'objet cible
Frame: base_link
```

#### `/joint_states`
```yaml
Type: sensor_msgs/JointState
Fréquence: 50 Hz
Description: État actuel des joints du robot
```

**Structure**:
```python
Header header
string[] name              # ["joint1", "joint2", ..., "joint6"]
float64[] position         # Angles en radians
float64[] velocity         # Vitesses angulaires (rad/s)
float64[] effort           # Couple (N·m)
```

**Exemple**:
```python
from sensor_msgs.msg import JointState

def joint_states_callback(msg):
    for i, name in enumerate(msg.name):
        print(f"{name}: {msg.position[i]:.3f} rad")
        
rospy.Subscriber('/joint_states', JointState, joint_states_callback)
```

#### `/arm_trajectory`
```yaml
Type: trajectory_msgs/JointTrajectory
Fréquence: 10 Hz
Description: Trajectoire désirée pour le bras robotique
```

#### `/cmd_vel`
```yaml
Type: geometry_msgs/Twist
Fréquence: 20 Hz
Description: Commandes de vélocité pour la base mobile
```

**Structure**:
```python
Vector3 linear    # Vitesse linéaire (m/s)
  float64 x       # Avant/Arrière
  float64 y       # Gauche/Droite (si holonome)
  float64 z       # Haut/Bas (généralement 0)
Vector3 angular   # Vitesse angulaire (rad/s)
  float64 x       # Roulis
  float64 y       # Tangage
  float64 z       # Lacet
```

#### `/debug_image`
```yaml
Type: sensor_msgs/Image
Fréquence: 15 Hz
Description: Image de debug avec visualisations (bounding boxes, etc.)
Dimensions: 640x640 (RGB8)
```

#### `/control_status`
```yaml
Type: std_msgs/String
Fréquence: 5 Hz
Description: Statut actuel du contrôleur
Valeurs: "IDLE", "MOVING", "PICKING", "PLACING", "ERROR"
```

#### `/gripper_command`
```yaml
Type: std_msgs/Float64
Fréquence: 10 Hz
Description: Commande d'ouverture du gripper
Range: 0.0 (fermé) - 1.0 (ouvert)
```

---

## 🛠️ Services ROS

### `/vision/set_detection_mode`
```yaml
Type: std_srvs/SetBool
Description: Active/désactive la détection d'objets
```

**Requête**:
```python
bool data  # True: activer, False: désactiver
```

**Réponse**:
```python
bool success
string message
```

**Exemple**:
```python
from std_srvs.srv import SetBool
import rospy

rospy.wait_for_service('/vision/set_detection_mode')
set_detection = rospy.ServiceProxy('/vision/set_detection_mode', SetBool)

try:
    response = set_detection(True)
    if response.success:
        print("Détection activée")
except rospy.ServiceException as e:
    print(f"Erreur: {e}")
```

### `/planning/pick_object`
```yaml
Type: custom_srvs/PickObject
Description: Planifie et exécute la prise d'un objet
```

**Requête**:
```python
int32 object_id           # ID de l'objet à saisir
geometry_msgs/Pose target_pose  # Pose de l'objet
string approach_direction # "top", "side", "front"
float64 grasp_force       # Force de préhension (0.0-1.0)
```

**Réponse**:
```python
bool success
string message
float64 execution_time    # Temps d'exécution (secondes)
```

**Exemple**:
```python
from custom_srvs.srv import PickObject, PickObjectRequest
from geometry_msgs.msg import Pose

rospy.wait_for_service('/planning/pick_object')
pick_object = rospy.ServiceProxy('/planning/pick_object', PickObject)

req = PickObjectRequest()
req.object_id = 1
req.target_pose.position.x = 0.3
req.target_pose.position.y = 0.0
req.target_pose.position.z = 0.1
req.approach_direction = "top"
req.grasp_force = 0.7

try:
    response = pick_object(req)
    if response.success:
        print(f"Objet saisi en {response.execution_time:.2f}s")
except rospy.ServiceException as e:
    print(f"Erreur: {e}")
```

### `/planning/place_object`
```yaml
Type: custom_srvs/PlaceObject
Description: Planifie et exécute le dépôt d'un objet
```

**Requête**:
```python
geometry_msgs/Pose target_pose  # Pose de destination
string release_method     # "open", "drop"
float64 release_height    # Hauteur de lâcher (m)
```

**Réponse**:
```python
bool success
string message
float64 execution_time
```

### `/control/emergency_stop`
```yaml
Type: std_srvs/Trigger
Description: Arrêt d'urgence du robot
```

**Requête**: Vide

**Réponse**:
```python
bool success
string message
```

**Exemple**:
```python
from std_srvs.srv import Trigger

rospy.wait_for_service('/control/emergency_stop')
emergency_stop = rospy.ServiceProxy('/control/emergency_stop', Trigger)

try:
    response = emergency_stop()
    print(response.message)
except rospy.ServiceException as e:
    print(f"Erreur: {e}")
```

### `/control/home_position`
```yaml
Type: std_srvs/Trigger
Description: Retour à la position de repos
```

**Exemple**:
```python
from std_srvs.srv import Trigger

rospy.wait_for_service('/control/home_position')
go_home = rospy.ServiceProxy('/control/home_position', Trigger)

try:
    response = go_home()
    if response.success:
        print("Robot en position de repos")
except rospy.ServiceException as e:
    print(f"Erreur: {e}")
```

### `/vision/calibrate_camera`
```yaml
Type: custom_srvs/CalibrateCamera
Description: Lance la calibration de la caméra
```

**Requête**:
```python
int32 num_images          # Nombre d'images à capturer
float64 capture_interval  # Intervalle entre captures (s)
string pattern_type       # "chessboard", "circles", "aruco"
```

**Réponse**:
```python
bool success
string message
float64[] intrinsic_matrix    # Matrice 3x3 aplatie
float64[] distortion_coeffs   # Coefficients de distorsion
float64 reprojection_error    # Erreur RMS
```

---

## 📦 Messages Personnalisés

### DetectedObjects.msg
```python
# custom_msgs/DetectedObjects.msg
Header header
DetectedObject[] objects
```

### DetectedObject.msg
```python
# custom_msgs/DetectedObject.msg
string class_name          # Classe de l'objet
float32 confidence         # Score de confiance
geometry_msgs/Point position       # Position 3D
geometry_msgs/Quaternion orientation
geometry_msgs/Vector3 dimensions   # Dimensions (m)
int32 tracking_id          # ID de suivi
float64 timestamp          # Timestamp de détection
```

### ArmCommand.msg
```python
# custom_msgs/ArmCommand.msg
Header header
float64[] joint_angles     # Angles des joints (rad)
float64 gripper_position   # Position gripper (0-1)
float64 execution_time     # Temps d'exécution souhaité (s)
bool wait_for_completion   # Attendre la fin du mouvement
```

### RobotStatus.msg
```python
# custom_msgs/RobotStatus.msg
Header header
string state               # État actuel du robot
bool is_moving             # Robot en mouvement
bool is_error              # Erreur détectée
string error_message       # Message d'erreur
float64 battery_voltage    # Tension batterie (V)
float64 cpu_temperature    # Température CPU (°C)
int32 objects_detected     # Nombre d'objets détectés
int32 objects_picked       # Nombre d'objets saisis
```

---

## ⚙️ Paramètres ROS

### Paramètres Vision

```yaml
# Namespace: /vision_node

# Détection
~confidence_threshold: 0.75      # Seuil de confiance
~nms_threshold: 0.4              # Seuil NMS
~max_detections: 10              # Nombre max d'objets
~model_path: "~/models/yolov8n_waste.pt"

# Classes
~class_names: ["carton", "plastique", "metal"]
~class_colors: [[255,0,0], [0,255,0], [0,0,255]]

# Caméra
~camera_topic: "/camera/color/image_raw"
~depth_topic: "/camera/depth/image_rect_raw"
~camera_frame: "camera_color_optical_frame"

# Performance
~inference_device: "cuda"        # "cuda" ou "cpu"
~enable_tracking: true
~tracking_max_age: 30            # Frames
```

**Récupération**:
```python
confidence = rospy.get_param('~confidence_threshold', 0.75)
model_path = rospy.get_param('~model_path')
```

**Modification dynamique**:
```python
rospy.set_param('/vision_node/confidence_threshold', 0.8)
```

### Paramètres Contrôle

```yaml
# Namespace: /control_node

# Limites joints
~joint_velocity_limits: [1.0, 1.0, 1.0, 1.5, 1.5, 2.0]  # rad/s
~joint_acceleration_limits: [2.0, 2.0, 2.0, 3.0, 3.0, 4.0]  # rad/s²
~joint_position_limits_min: [0, 0, 0, 0, 0, 0]  # rad
~joint_position_limits_max: [3.14, 3.14, 3.14, 3.14, 3.14, 3.14]

# Contrôleur
~control_frequency: 50.0         # Hz
~position_tolerance: 0.01        # rad
~velocity_tolerance: 0.05        # rad/s

# Gripper
~gripper_open_position: 135      # degrés
~gripper_close_position: 45
~gripper_force_threshold: 0.8    # N
```

### Paramètres Planification

```yaml
# Namespace: /planning_node

# Cinématique inverse
~ik_solver: "kdl"                # "kdl", "trac_ik"
~ik_timeout: 0.05                # secondes
~ik_attempts: 10

# Trajectoire
~trajectory_smoothing: true
~max_trajectory_points: 100
~default_execution_time: 2.0     # secondes

# Sécurité
~collision_checking: true
~safety_margin: 0.05             # mètres
~workspace_bounds: [-0.5, 0.5, -0.5, 0.5, 0.0, 0.6]  # x_min, x_max, ...
```

---

## 🎬 Actions

### `/arm_controller/follow_joint_trajectory`
```yaml
Type: control_msgs/FollowJointTrajectoryAction
Description: Exécute une trajectoire complète
```

**Goal**:
```python
trajectory_msgs/JointTrajectory trajectory
duration goal_time_tolerance
```

**Feedback**:
```python
Header header
string[] joint_names
float64[] desired        # Position désirée
float64[] actual         # Position actuelle
float64[] error          # Erreur de position
```

**Result**:
```python
int32 error_code
string error_string
```

**Exemple**:
```python
import actionlib
from control_msgs.msg import FollowJointTrajectoryAction, FollowJointTrajectoryGoal
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

client = actionlib.SimpleActionClient(
    '/arm_controller/follow_joint_trajectory',
    FollowJointTrajectoryAction
)
client.wait_for_server()

goal = FollowJointTrajectoryGoal()
goal.trajectory.joint_names = ['joint1', 'joint2', 'joint3', 'joint4', 'joint5', 'joint6']

point = JointTrajectoryPoint()
point.positions = [1.57, 0.0, -1.57, 0.0, 1.57, 0.0]
point.time_from_start = rospy.Duration(2.0)
goal.trajectory.points.append(point)

client.send_goal(goal)
client.wait_for_result()
result = client.get_result()
```

---

## 🌐 API WebSocket

### Connexion

```javascript
const ws = new WebSocket('ws://ROBOT_IP:8765');

ws.onopen = () => {
    console.log('Connecté au robot');
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    handleMessage(data);
};

ws.onerror = (error) => {
    console.error('Erreur WebSocket:', error);
};

ws.onclose = () => {
    console.log('Connexion fermée');
};
```

### Messages Client → Serveur

#### Déplacement Servo
```json
{
    "action": "move_servo",
    "servo": 1,
    "angle": 90
}
```

#### Déplacement Multiple
```json
{
    "action": "move_all",
    "angles": [90, 90, 90, 90, 90, 90]
}
```

#### Sauvegarde Configuration
```json
{
    "action": "save_config",
    "name": "position_repos",
    "angles": [90, 90, 90, 90, 90, 90]
}
```

#### Chargement Configuration
```json
{
    "action": "load_config",
    "name": "position_repos"
}
```

#### Demande Status
```json
{
    "action": "get_status"
}
```

#### Demande Positions
```json
{
    "action": "get_positions"
}
```

### Messages Serveur → Client

#### Status Général
```json
{
    "type": "status",
    "connected": true,
    "timestamp": "2025-10-16T10:30:00Z"
}
```

#### Positions Actuelles
```json
{
    "type": "positions",
    "angles": [90, 90, 90, 90, 90, 90],
    "timestamp": "2025-10-16T10:30:00Z"
}
```

#### Log
```json
{
    "type": "log",
    "level": "info",
    "message": "Servo 1 déplacé à 90°",
    "timestamp": "2025-10-16T10:30:00Z"
}
```

#### Erreur
```json
{
    "type": "error",
    "code": 400,
    "message": "Angle hors limites",
    "details": "Angle 200° > limite max 180°"
}
```

---

## 💡 Exemples d'Utilisation

### Exemple 1: Node Simple de Détection

```python
#!/usr/bin/env python3
import rospy
from custom_msgs.msg import DetectedObjects

class SimpleDetector:
    def __init__(self):
        rospy.init_node('simple_detector')
        
        # Subscriber
        self.sub = rospy.Subscriber(
            '/detected_objects',
            DetectedObjects,
            self.objects_callback
        )
        
        self.objects_count = {'carton': 0, 'plastique': 0, 'metal': 0}
    
    def objects_callback(self, msg):
        for obj in msg.objects:
            if obj.confidence > 0.8:
                self.objects_count[obj.class_name] += 1
                rospy.loginfo(f"Détecté: {obj.class_name} à ({obj.position.x:.2f}, {obj.position.y:.2f})")
    
    def run(self):
        rospy.spin()

if __name__ == '__main__':
    detector = SimpleDetector()
    detector.run()
```

### Exemple 2: Contrôle Manuel du Bras

```python
#!/usr/bin/env python3
import rospy
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

class ArmController:
    def __init__(self):
        rospy.init_node('arm_controller')
        
        # Publisher
        self.pub = rospy.Publisher(
            '/arm_trajectory',
            JointTrajectory,
            queue_size=10
        )
        
        # Subscriber
        self.sub = rospy.Subscriber(
            '/joint_states',
            JointState,
            self.joint_callback
        )
        
        self.current_positions = None
    
    def joint_callback(self, msg):
        self.current_positions = msg.position
    
    def move_to(self, target_positions, duration=2.0):
        """Déplace le bras vers une position cible"""
        traj = JointTrajectory()
        traj.joint_names = ['joint1', 'joint2', 'joint3', 'joint4', 'joint5', 'joint6']
        
        point = JointTrajectoryPoint()
        point.positions = target_positions
        point.time_from_start = rospy.Duration(duration)
        
        traj.points.append(point)
        self.pub.publish(traj)
        
        rospy.loginfo(f"Commande envoyée: {target_positions}")
    
    def home(self):
        """Retourne à la position de repos"""
        home_position = [1.57, 0.0, -1.57, 0.0, 1.57, 0.0]
        self.move_to(home_position)

if __name__ == '__main__':
    controller = ArmController()
    rospy.sleep(1.0)  # Attendre l'initialisation
    
    # Exemple d'utilisation
    controller.home()
    rospy.sleep(3.0)
    
    target = [0.5, 0.5, -0.5, 0.0, 0.5, 0.0]
    controller.move_to(target, duration=3.0)
    
    rospy.spin()
```

### Exemple 3: Interface WebSocket Complète

```javascript
class RobotCalibrationInterface {
    constructor(robotIP) {
        this.ws = new WebSocket(`ws://${robotIP}:8765`);
        this.currentAngles = [90, 90, 90, 90, 90, 90];
        
        this.setupWebSocket();
        this.setupUI();
    }
    
    setupWebSocket() {
        this.ws.onopen = () => {
            console.log('Connecté au robot');
            this.requestStatus();
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };
    }
    
    handleMessage(data) {
        switch(data.type) {
            case 'positions':
                this.updateSliders(data.angles);
                break;
            case 'log':
                this.addLog(data.message);
                break;
            case 'error':
                this.showError(data.message);
                break;
        }
    }
    
    moveServo(servoId, angle) {
        const command = {
            action: 'move_servo',
            servo: servoId,
            angle: angle
        };
        this.ws.send(JSON.stringify(command));
    }
    
    moveAll(angles) {
        const command = {
            action: 'move_all',
            angles: angles
        };
        this.ws.send(JSON.stringify(command));
    }
    
    saveConfiguration(name) {
        const command = {
            action: 'save_config',
            name: name,
            angles: this.currentAngles
        };
        this.ws.send(JSON.stringify(command));
    }
    
    requestStatus() {
        this.ws.send(JSON.stringify({action: 'get_status'}));
        this.ws.send(JSON.stringify({action: 'get_positions'}));
    }
}

// Utilisation
const robot = new RobotCalibrationInterface('192.168.1.100');
robot.moveServo(1, 45);
robot.saveConfiguration('position_prise');
```

---

## 📚 Références

- **ROS Messages**: http://wiki.ros.org/msg
- **ROS Services**: http://wiki.ros.org/Services
- **ROS Actions**: http://wiki.ros.org/actionlib
- **WebSocket API**: https://developer.mozilla.org/en-US/docs/Web/API/WebSocket

---

## 📞 Support

Pour plus d'informations : voir [docs/INDEX.md](../INDEX.md)

**Dernière mise à jour : 16 octobre 2025**
