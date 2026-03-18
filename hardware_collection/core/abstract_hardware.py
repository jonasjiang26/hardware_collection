import abc
import yaml
import os
import warnings


class _NullPublisher:
    def __init__(self, topic: str):
        self.topic = topic

    def publish(self, _message) -> None:
        return


def _import_pyzlc():
    try:
        import pyzlc  # type: ignore

        return pyzlc, None
    except Exception as exc:  # pragma: no cover - import-time env dependent
        return None, exc

class AbstractHardware:
    """Abstract base class for hardware components using ZeroLanCom Publisher."""

    def __init__(self, device_name: str, config_path: str):
        """Initialize with pyzlc Publisher.

        Args:
            device_name (str): Topic name to publish data via ZeroLanCom.
            config_path (str): Path to the ZeroLanCom configuration file.
        """
        self.device_name = device_name

        pyzlc, import_error = _import_pyzlc()
        if pyzlc is None:
            warnings.warn(
                "ZeroLanCom publishing is disabled because `pyzlc` could not be imported "
                f"({import_error!r}). Install/repair `pyzlc` to enable publishing.",
                RuntimeWarning,
            )
            self.config = {}
            self.publisher = _NullPublisher(self.device_name)
            return

        print(f"Loading ZLC config from: {os.path.join(os.getcwd(), config_path)}")
        with open(os.path.join(os.getcwd(), config_path), 'r') as f:
            self.config = yaml.load(f, Loader=yaml.SafeLoader)
        pyzlc.init(self.device_name, self.config["local_ip"], group_name=self.config["group_name"], group_port=self.config["group_port"], group=self.config["group"])
        self.publisher = pyzlc.Publisher(self.device_name)

    @abc.abstractmethod
    def initialize(self) -> None:
        """Initialize any required ZeroLanCom nodes."""
        raise NotImplementedError("Subclasses must implement initialize method.")
