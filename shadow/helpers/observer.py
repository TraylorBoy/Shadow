"""This module provides a publisher and subscriber class for observing ShadowBot state transitions"""

import logging

log = logging.getLogger(__name__)


class ShadowObserver:

    """Subscriber class"""

    @property
    def log_factory(self) -> dict:
        """Log level factory"""

        return {
            "info": log.info,
            "warn": log.warning,
            "critical": log.critical,
            "error": log.error,
        }

    def update(self, type: str = "info", **kwargs) -> None:
        """Called when observer sends a notification"""

        if type.lower() not in self.log_factory.keys():  # pragma: no cover
            raise TypeError("Invalid log level")

        # Bind correct log level
        _log = self.log_factory[type.lower()]

        # TODO - Logger format
        formatted_msg = ""

        for key, msg in kwargs.items():
            formatted_msg += f"{key} - {msg}\t"

        _log(formatted_msg)


class Observable:

    """Publisher class"""

    observers = []  # type: list

    def attach_observer(self, observer: ShadowObserver) -> None:
        """Register an observer"""

        if observer not in self.observers:

            self.observers.append(observer)

            self.notify(sender="System", msg=f"Attached observer: {observer}")

    def detach_observer(self, observer: ShadowObserver) -> None:
        """Remove a registered observer"""

        if observer in self.observers:
            self.observers.remove(observer)

    def notify(
        self, log_type: str = "info", sender: str = None, msg: str = None
    ) -> None:
        """Sends msg to all observers"""

        if not msg:  # pragma: no cover
            raise AttributeError("No msg supplied")

        for observer in self.observers:

            notification = {
                "type": log_type,
                "sender": sender,
                "msg": msg,
                "recipient": observer,
            }

            observer.update(**notification)
