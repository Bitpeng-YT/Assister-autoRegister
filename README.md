# Assister 自动注册登录程序
使用私钥自动注册并抓取账户accessToken和refreshToken保存到本地文件中。

## 功能特点
- 自动注册登录 Assister 账户。
- 自动抓取 access_token 和 refresh_token。
- 自动保存账户信息。

## 运行方式
- 读取私钥文件 (`privatekey.txt`) 中的私钥。
- 读取代理文件 (`proxies.txt`) 中的代理。
- 使用私钥生成公钥发送签名。
- 通过 Assister API 进行注册和登录。
- 将登录后抓取到的 access_token 和 refresh_token 保存到账户文件 (`accounts.txt`) 中。

## 安装步骤

1. 确保已安装Python 3.7或更高版本

2. 安装依赖包：
   ```bash
   pip install -r requirements.txt
   ```

## 运行方法

1. 创建 `privatekey.txt` 文件，每行包含一个私钥信息

2. 创建 `proxies.txt` 文件，每行一个代理地址，格式为：
   ```
   http://user:pass@host:port
   ```
   或
   ```
   http://host:port
   ```

3. 运行脚本：
   ```bash
   python register.py
   ```

## 注意事项

- 请妥善保管您的私钥和令牌信息
- 建议使用代理服务器以避免IP限制
- 脚本会自动处理令牌过期和刷新
- 如果遇到问题，请查看控制台输出的错误信息

## 免责声明

本脚本仅供学习和研究使用，使用本脚本所产生的任何女巫后果由使用者自行承担。