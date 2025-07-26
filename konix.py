import sys
import cv2
import numpy as np
from PyQt5 import QtWidgets, QtGui, QtCore

class WebcamWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Webcam")
        self.setGeometry(100, 100, 800, 600)

        # Initialisation de la webcam
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            QtWidgets.QMessageBox.critical(self, "Erreur", "Webcam non disponible")
            self.close()
            return

        # Configuration de la mise en page
        self.layout = QtWidgets.QVBoxLayout(self)

        # Label pour afficher la vidéo
        self.video_label = QtWidgets.QLabel(self)
        self.video_label.setAlignment(QtCore.Qt.AlignCenter)  # Centrer la vidéo
        self.layout.addWidget(self.video_label)

        # Bouton pour activer/désactiver l'effet de style Obama
        self.obama_button = QtWidgets.QPushButton("Activer Style Poster")
        self.obama_button.setCheckable(True)
        self.obama_button.clicked.connect(self.toggle_obama_effect)
        self.layout.addWidget(self.obama_button)

        # Bouton pour activer/désactiver l'effet Halftone
        self.halftone_button = QtWidgets.QPushButton("Activer Halftone")
        self.halftone_button.setCheckable(True)
        self.halftone_button.clicked.connect(self.toggle_halftone_effect)
        self.layout.addWidget(self.halftone_button)

        # Timer pour la mise à jour de la vidéo
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # 30 ms pour un FPS d'environ 33

        # Paramètres de réglage
        self.brightness = 128
        self.contrast = 128
        self.sharpness = 0
        self.blur = 0
        self.hue = 0
        self.obama_effect = False
        self.halftone_effect = False
        self.halftone_size = 5  # Taille par défaut des points Halftone

    def update_frame(self):
        """Met à jour l'image de la webcam."""
        ret, frame = self.cap.read()
        if ret:
            # Appliquer les réglages
            frame = cv2.convertScaleAbs(frame, alpha=self.contrast / 128, beta=self.brightness - 128)

            # Appliquer la netteté
            if self.sharpness > 0:
                kernel = np.array([[-1, -1, -1],
                                   [-1, 9 + self.sharpness / 20, -1],
                                   [-1, -1, -1]])
                frame = cv2.filter2D(frame, -1, kernel)

            # Appliquer le flou
            if self.blur > 0:
                frame = cv2.GaussianBlur(frame, (2 * self.blur + 1, 2 * self.blur + 1), 0)

            # Appliquer l'effet de style poster si activé
            if self.obama_effect:
                frame = self.apply_obama_effect(frame)

            # Appliquer l'effet Halftone si activé
            if self.halftone_effect:
                frame = self.apply_halftone_effect(frame)

            # Appliquer la teinte
            hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            hsv_image[:, :, 0] = (hsv_image[:, :, 0] + self.hue) % 180  # Ajuster la teinte
            frame = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)

            # Convertir l'image pour l'affichage
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            q_img = QtGui.QImage(frame.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)

            # Afficher l'image dans le QLabel
            self.video_label.setPixmap(QtGui.QPixmap.fromImage(q_img).scaled(
                self.video_label.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

    def apply_obama_effect(self, image):
        """Applique un effet de style poster rouge et bleu à l'image."""
        # Convertir l'image en BGR
        b, g, r = cv2.split(image)

        # Appliquer un filtre de couleur pour le style poster
        b = cv2.add(b, 50)  # Augmenter le bleu
        r = cv2.add(r, 50)  # Augmenter le rouge
        g = cv2.add(g, -30)  # Diminuer le vert

        # Appliquer un seuil pour créer un effet de poster
        _, b = cv2.threshold(b, 150, 255, cv2.THRESH_BINARY)
        _, g = cv2.threshold(g, 150, 255, cv2.THRESH_BINARY)
        _, r = cv2.threshold(r, 150, 255, cv2.THRESH_BINARY)

        # Fusionner les canaux
        return cv2.merge((b, g, r))

    def apply_halftone_effect(self, image):
        """Applique un effet halftone à l'image."""
        # Convertir l'image en niveaux de gris
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        halftone_image = np.zeros_like(image)

        # Appliquer l'effet halftone
        for y in range(0, gray_image.shape[0], self.halftone_size):
            for x in range(0, gray_image.shape[1], self.halftone_size):
                gray_value = gray_image[y, x]
                color = (int(gray_value), int(gray_value), int(gray_value))  # Noir et blanc
                cv2.circle(halftone_image, (x, y), self.halftone_size // 2, color, -1)  # Dessiner le point

        return halftone_image

    def toggle_obama_effect(self):
        """Active ou désactive l'effet de style poster."""
        self.obama_effect = not self.obama_effect
        if self.obama_effect:
            self.obama_button.setText("Désactiver Style Poster")
        else:
            self.obama_button.setText("Activer Style Poster")

    def toggle_halftone_effect(self):
        """Active ou désactive l'effet Halftone."""
        self.halftone_effect = not self.halftone_effect
        if self.halftone_effect:
            self.halftone_button.setText("Désactiver Halftone")
        else:
            self.halftone_button.setText("Activer Halftone")

    def closeEvent(self, event):
        """Arrêt propre de la webcam."""
        self.cap.release()
        event.accept()

class MainApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main App")
        self.setGeometry(100, 100, 400, 300)

        # Configuration de la mise en page
        self.layout = QtWidgets.QVBoxLayout(self)

        # Bouton pour ouvrir la fenêtre de webcam
        self.open_webcam_button = QtWidgets.QPushButton("Ouvrir Webcam")
        self.open_webcam_button.clicked.connect(self.open_webcam)
        self.layout.addWidget(self.open_webcam_button)

        # Curseurs de réglage
        self.brightness_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.brightness_slider.setRange(0, 255)
        self.brightness_slider.setValue(128)
        self.layout.addWidget(QtWidgets.QLabel("Luminosité"))
        self.layout.addWidget(self.brightness_slider)

        self.contrast_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.contrast_slider.setRange(0, 255)
        self.contrast_slider.setValue(128)
        self.layout.addWidget(QtWidgets.QLabel("Contraste"))
        self.layout.addWidget(self.contrast_slider)

        self.sharpness_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.sharpness_slider.setRange(0, 100)
        self.sharpness_slider.setValue(0)
        self.layout.addWidget(QtWidgets.QLabel("Netteté"))
        self.layout.addWidget(self.sharpness_slider)

        self.blur_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.blur_slider.setRange(0, 20)
        self.blur_slider.setValue(0)
        self.layout.addWidget(QtWidgets.QLabel("Flou"))
        self.layout.addWidget(self.blur_slider)

        self.halftone_size_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.halftone_size_slider.setRange(1, 50)
        self.halftone_size_slider.setValue(5)
        self.layout.addWidget(QtWidgets.QLabel("Taille Halftone"))
        self.layout.addWidget(self.halftone_size_slider)

        self.hue_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.hue_slider.setRange(0, 360)
        self.hue_slider.setValue(0)
        self.layout.addWidget(QtWidgets.QLabel("Teinte"))
        self.layout.addWidget(self.hue_slider)

        # Connecter les signaux des curseurs
        self.brightness_slider.valueChanged.connect(self.update_webcam_params)
        self.contrast_slider.valueChanged.connect(self.update_webcam_params)
        self.sharpness_slider.valueChanged.connect(self.update_webcam_params)
        self.blur_slider.valueChanged.connect(self.update_webcam_params)
        self.halftone_size_slider.valueChanged.connect(self.update_webcam_params)
        self.hue_slider.valueChanged.connect(self.update_webcam_params)

        # Bouton Quitter
        self.quit_button = QtWidgets.QPushButton("Quitter")
        self.quit_button.clicked.connect(self.close)
        self.layout.addWidget(self.quit_button)

    def open_webcam(self):
        """Ouvre la fenêtre de la webcam en pop-up."""
        self.webcam_window = WebcamWindow()
        self.webcam_window.brightness = self.brightness_slider.value()
        self.webcam_window.contrast = self.contrast_slider.value()
        self.webcam_window.sharpness = self.sharpness_slider.value()
        self.webcam_window.blur = self.blur_slider.value()
        self.webcam_window.hue = self.hue_slider.value()
        self.webcam_window.halftone_size = self.halftone_size_slider.value()
        self.webcam_window.show()

    def update_webcam_params(self):
        """Met à jour les paramètres de la webcam lorsque les curseurs sont déplacés."""
        if hasattr(self, 'webcam_window') and self.webcam_window.isVisible():
            self.webcam_window.brightness = self.brightness_slider.value()
            self.webcam_window.contrast = self.contrast_slider.value()
            self.webcam_window.sharpness = self.sharpness_slider.value()
            self.webcam_window.blur = self.blur_slider.value()
            self.webcam_window.hue = self.hue_slider.value()
            self.webcam_window.halftone_size = self.halftone_size_slider.value()

    def closeEvent(self, event):
        """Ferme proprement l'application et la fenêtre webcam si elle est ouverte."""
        if hasattr(self, 'webcam_window') and self.webcam_window.isVisible():
            self.webcam_window.close()
        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec_())
