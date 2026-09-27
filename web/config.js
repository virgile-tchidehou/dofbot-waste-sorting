// 🔧 CONFIGURATION SERVEUR - Interface de Calibration DOFbot
// DOFBOT waste-sorting calibration interface

/**
 * INSTRUCTIONS :
 * 
 * 1. Pour utiliser en LOCAL (sur le même PC que le serveur) :
 *    → Garder SERVER_IP = 'localhost'
 * 
 * 2. Pour utiliser depuis un AUTRE PC/Tablette/Smartphone :
 *    → Trouver l'IP du Jetson Nano : `hostname -I`
 *    → Remplacer 'localhost' par l'IP, exemple : '192.168.1.100'
 * 
 * 3. Sauvegarder ce fichier et rafraîchir la page web
 */

// ========================================
// CONFIGURATION PRINCIPALE
// ========================================

/**
 * Adresse IP du serveur de calibration
 * 
 * Exemples :
 * - 'localhost'         → Utilisation locale (PC et serveur sur la même machine)
 * - '192.168.1.100'     → Jetson Nano sur réseau domestique
 * - '192.168.43.100'    → Jetson Nano via hotspot smartphone
 * - '10.0.0.5'          → Réseau d'entreprise/université
 */
const SERVER_IP = 'localhost';

/**
 * Port du serveur WebSocket
 * (Ne pas modifier sauf si vous changez dans calibration_server.py)
 */
const SERVER_PORT = 8765;

/**
 * URL complète de connexion WebSocket
 * (Générée automatiquement à partir de SERVER_IP et SERVER_PORT)
 */
const WEBSOCKET_URL = `ws://${SERVER_IP}:${SERVER_PORT}`;

// ========================================
// CONFIGURATION AVANCÉE (Optionnel)
// ========================================

/**
 * Délai de reconnexion automatique (en millisecondes)
 * 0 = désactivé
 */
const AUTO_RECONNECT_DELAY = 5000; // 5 secondes

/**
 * Nombre maximum de tentatives de reconnexion
 * 0 = illimité
 */
const MAX_RECONNECT_ATTEMPTS = 3;

/**
 * Afficher les messages de debug dans la console du navigateur
 */
const DEBUG_MODE = false;

// ========================================
// EXPORT DE LA CONFIGURATION
// ========================================

// Rendre la configuration accessible globalement
window.CALIBRATION_CONFIG = {
    SERVER_IP: SERVER_IP,
    SERVER_PORT: SERVER_PORT,
    WEBSOCKET_URL: WEBSOCKET_URL,
    AUTO_RECONNECT_DELAY: AUTO_RECONNECT_DELAY,
    MAX_RECONNECT_ATTEMPTS: MAX_RECONNECT_ATTEMPTS,
    DEBUG_MODE: DEBUG_MODE
};

// Log de la configuration au chargement
if (DEBUG_MODE) {
    console.log('🔧 Configuration chargée :');
    console.log('   - Serveur : ' + WEBSOCKET_URL);
    console.log('   - Reconnexion auto : ' + (AUTO_RECONNECT_DELAY > 0 ? 'Activée' : 'Désactivée'));
    console.log('   - Mode debug : ' + (DEBUG_MODE ? 'ON' : 'OFF'));
}

// ========================================
// EXEMPLES DE CONFIGURATION
// ========================================

/*
// ✅ EXEMPLE 1 : Utilisation locale (défaut)
const SERVER_IP = 'localhost';
const SERVER_PORT = 8765;

// ✅ EXEMPLE 2 : Jetson Nano sur réseau Wi-Fi
const SERVER_IP = '192.168.1.100';
const SERVER_PORT = 8765;

// ✅ EXEMPLE 3 : Hotspot smartphone
const SERVER_IP = '192.168.43.100';
const SERVER_PORT = 8765;

// ✅ EXEMPLE 4 : Connexion Ethernet directe
const SERVER_IP = '192.168.0.1';
const SERVER_PORT = 8765;

// ✅ EXEMPLE 5 : Réseau d'entreprise
const SERVER_IP = '10.42.0.100';
const SERVER_PORT = 8765;
*/

// ========================================
// AIDE AU DÉPANNAGE
// ========================================

/*
❌ PROBLÈME : "WebSocket connection failed"

✅ SOLUTIONS :
1. Vérifier que le serveur est démarré :
   python3 scripts/calibration_server.py

2. Vérifier l'IP du Jetson :
   hostname -I

3. Tester le ping depuis votre PC :
   ping 192.168.1.100

4. Vérifier le pare-feu :
   sudo ufw allow 8765/tcp

5. Vérifier que SERVER_IP correspond à l'IP du Jetson

6. Ouvrir la console du navigateur (F12) pour voir les erreurs
*/
