"""Build ShadowBots"""

from shadow import ShadowTask, ShadowBot, ShadowSignal

def main():
    """Entry Point
    """

    # Build signals
    task_list: ShadowTask = ShadowTask()
    task_list.add(name="echo", task=ShadowSignal.TEST["echo"], msg="Hello, world!")

    # Instantiate ShadowBot
    ShadowBot(name="EchoBot", shadow_task=task_list)


if __name__ == '__main__':
    main()
