import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from utils.font_loader import load_font

def main():
    app = QApplication(sys.argv)
    
    # Load font and get font family
    font_family = load_font(app)
    
    # Load QSS stylesheet
    try:
        with open("styles.qss", "r", encoding="utf-8") as qss_file:
            app.setStyleSheet(qss_file.read())
    except Exception as e:
        print(f"Error loading stylesheet: {str(e)}")
    
    window = MainWindow(font_family=font_family)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
