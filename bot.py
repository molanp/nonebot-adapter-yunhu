import nonebot

from nonebot.adapters.yunhu import Adapter

nonebot.init()


driver = nonebot.get_driver()
driver.register_adapter(Adapter)

nonebot.load_builtin_plugins("echo")


if __name__ == "__main__":
    nonebot.run()
