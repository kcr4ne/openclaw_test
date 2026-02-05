import platform
import logging

logger = logging.getLogger("jarvis.core.detect")

class OSDetector:
    @staticmethod
    def get_os_type():
        system = platform.system().lower()
        if system == "linux":
            return "linux"
        elif system == "windows":
            return "windows"
        else:
            return "unknown"

    @staticmethod
    def get_distro():
        if platform.system().lower() == "linux":
            try:
                import distro
                return distro.id()
            except ImportError:
                return "linux_generic"
        return "windows"

    def detect_environment(self):
        os_type = self.get_os_type()
        logger.info(f"Detected OS: {os_type}")
        return os_type
