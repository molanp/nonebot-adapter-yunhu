# 首次接入指南

## 首次接入和配置

本指南将引导您完成 `nonebot-adapter-yunhu` 在 Nonebot 中的首次接入和配置。

::: warning
此适配器默认你具有 Nonebot 基础，知道并了解如何使用 Nonebot 适配器。

若不懂，请参考 [Nonebot 官方文档](https://nonebot.dev/docs/quick-start)
:::

## 1. 前置要求：公网访问

云湖平台通过 Webhook 将事件（如消息、成员变动等）推送给您的机器人。

因此，在开始之前，您必须确保 Nonebot 实例能够被公网访问。

:::tip
这意味着您需要具备**以下条件之一**：

- 拥有一个公网 IPv4 或 IPv6 地址。
- 使用内网穿透服务（如 frp, Ngrok, Cloudflare Tunnel 等）将您的本地 Nonebot 服务暴露到公网。
  :::

具体的公网部署方法多样，本指南不详细展开。

请根据您的实际网络环境选择合适的方案。

## 2. 在云湖平台创建机器人

> 下面教程以 云湖 Windows 版客户端 演示

访问 [云湖官网](https://www.yhchat.com/) ，下载对应客户端。

注册并登录账号后，进入设置页面，创建一个新的机器人。

![云湖后台](/assets/2025-12-16_123750.png)

## 3. 获取机器人凭证

下面需要复制机器人账号的两个信息：ID、Token。

1. 打开云湖客户端，在与机器人的聊天对话页面，复制机器人的账号 ID：

- **机器人 ID (app_id)**：这是您机器人的唯一标识。
  ![获取机器人ID](/assets/QQ20251216-124409.png)

2. 打开[官网控制台](https://www.yhchat.com/control)，复制机器人的 Token：

- **机器人 Token**：这是与云湖 API 通信的密钥。
  ![获取机器人Token](/assets/QQ20251216-124215.png)

## 4. 配置 Nonebot 适配器

在你的 Nonebot 运行目录使用命令安装 `nonebot-adpater-yunhu` 适配器。

### 使用 nb-cli 安装

```bash
nb install nonebot-adapter-yunhu
```

### 使用 pip 安装

```bash
pip install nonebot-adapter-yunhu
```

### 使用 nb-cli 创建全新 Bot 项目并安装

```bash
nb create
```

在适配器选择菜单找到 `nonebot-adapter-yunhu` 并选择

然后打开配置文件(一般是`.env.prod`)，将上一步获取的 **机器人 ID** 和 **Token** 填入对应的配置项中。

![Nonebot配置项](/assets/QQ20251216-124633.png)


::: warning
如果你是手动安装的适配器，请打开`bot.py`文件，导入并激活适配器

标准配置文件
```python
import nonebot

from nonebot.adapters.yunhu import Adapter as YunhuAdapter # 导入云湖适配器

nonebot.init()


driver = nonebot.get_driver()
driver.register_adapter(YunhuAdapter) # 激活云湖适配器


# nonebot.load_builtin_plugins("echo") # 激活内置 echo 测试插件
nonebot.load_plugins("plugins") # 加载 plugins 文件夹下的插件

nonebot.run()
```
:::
---

## 5. 确认订阅地址

:::warning
注意 此步骤务必使用**公网地址**访问！
:::

1.  **确认订阅地址**：将您的 Nonebot 公网访问地址与上一步配置的 `app_id` 组合成完整的 Webhook URL。
    - 若未配置端口，则默认为 `8080`
    - 例如，如果您的公网域名是 `http://1.2.3.4`，并且 `app_id` 配置为 `123`，那么完整的订阅地址就是 `http://1.2.3.4:8080/yunhu/123`。
2.  **打开浏览器访问订阅地址**：
    - 如果你可以访问看到 `{"detail":"Method Not Allowed"}` 页面，则说明配置成功！

![{"detail":"Method Not Allowed"}](/assets/QQ20251216-125206.png)

## 6. 配置 Webhook 和事件订阅

回到云湖平台的机器人后台，进行以下配置：

1.  **配置订阅地址**：假设您的订阅地址为 `http://1.2.3.4:8080/yunhu/123`。

2.  **订阅事件**：根据您的需求，勾选需要接收的事件类型。

    - 为了确保机器人能正常响应消息，**「消息事件」** 是必须订阅的。

![配置订阅地址和事件](/assets/QQ20251216-131052.png)

## 7. 测试连接

完成以上所有配置后，您可以对机器人进行一次简单的测试，以验证连接是否成功。

- **私聊** 您的机器人，发送任意消息。
- 如果您的 Nonebot 控制台输出了对应的消息息，则说明机器人已正常接收消息。

---

如果机器人没有响应，请检查以下几点：

- Nonebot 服务是否正常运行？
- 公网地址和 Webhook 路径是否正确？
- 云湖后台的事件订阅是否已开启？
- 检查 Nonebot 的控制台日志，确认是否有来自云湖的请求或任何错误信息。

## 关于「无公网 IP 订阅」的说明

目前，云湖平台的事件订阅机制**强制要求**一个**可公网访问**的 Webhook 地址。

关于未来是否支持如 WebSocket 等长连接方式，您可以关注官方的讨论：

- [能否有一种不需要公网 IP 就能订阅消息的方式？](https://github.com/yhchat/bot-go-sdk/issues/1)
