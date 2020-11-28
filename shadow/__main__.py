"""Main script for the Shadow package"""

from shadow import Shadow

if __name__ == "__main__":
    """Entry point to the Shadow package"""

    shadow = Shadow()

    shadowbot = shadow.build(name="TestBot")

    observer = shadow.observe(shadowbot)

    shadowbot.state.revive()  # type: ignore
