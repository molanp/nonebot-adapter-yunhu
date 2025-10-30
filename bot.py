import nonebot

# from nonebot.adapters.discord import Adapter as DiscordAdapter
# from nonebot.adapters.dodo import Adapter as DoDoAdapter
# from nonebot.adapters.kaiheila import Adapter as KaiheilaAdapter
from nonebot.adapters.yunhu import Adapter

nonebot.init()


driver = nonebot.get_driver()
driver.register_adapter(Adapter)
# driver.register_adapter(KaiheilaAdapter)
# driver.register_adapter(DoDoAdapter)
# driver.register_adapter(DiscordAdapter)

nonebot.load_builtin_plugins("echo")


if __name__ == "__main__":
    nonebot.run()
