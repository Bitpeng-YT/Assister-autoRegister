import base58
import json
import time
from datetime import datetime
import requests
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from colorama import init, Fore, Style
import os
from typing import Dict, List, Optional

# 初始化colorama
init()

# 配置文件路径
PRIVATE_KEY_PATH = 'privatekey.txt'
ACCOUNTS_PATH = 'accounts.txt'
PROXY_PATH = 'proxies.txt'

class AssisterRegister:
    def __init__(self):
        self.base_url = "https://api.assisterr.ai"
        self.headers = {
            'accept': 'application/json',
            'origin': 'https://build.assisterr.ai',
            'referer': 'https://build.assisterr.ai/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def log(self, pubkey: str, message: str, msg_type: str = 'info') -> None:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        colors = {
            'success': Fore.GREEN,
            'error': Fore.RED,
            'warning': Fore.YELLOW,
            'system': Fore.CYAN,
            'info': Fore.MAGENTA
        }
        color = colors.get(msg_type, Fore.WHITE)
        
        if msg_type == 'system':
            print(f"{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{timestamp}{Fore.WHITE}] {color}{message}{Style.RESET_ALL}")
        else:
            if message.startswith('处理中') and pubkey and pubkey != 'UNKNOWN':
                print(f"{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{timestamp}{Fore.WHITE}] {color}处理中 {Fore.YELLOW}{pubkey}{Style.RESET_ALL}")
            else:
                print(f"{Fore.WHITE}[{Fore.LIGHTBLACK_EX}{timestamp}{Fore.WHITE}] {color}{message}{Style.RESET_ALL}")

    def read_private_keys(self) -> List[str]:
        try:
            with open(PRIVATE_KEY_PATH, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        except Exception as e:
            self.log('系统', f"读取私钥时出错: {str(e)}", 'error')
            return []

    def read_proxies(self) -> List[str]:
        try:
            with open(PROXY_PATH, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        except:
            return []

    def get_public_key(self, private_key: str) -> str:
        if not private_key:
            return 'UNKNOWN'
        try:
            # 使用solders库来处理密钥对
            keypair = Keypair.from_base58_string(private_key.strip())
            public_key = keypair.pubkey()
            public_key_bytes = bytes(public_key)
            return base58.b58encode(public_key_bytes).decode()
        except Exception as e:
            print(e)
            # 不打印错误信息，静默处理
            return 'UNKNOWN'

    def make_request(self, method: str, endpoint: str, proxy: Optional[str] = None, 
                    **kwargs) -> requests.Response:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        if proxy:
            kwargs['proxies'] = {'http': proxy, 'https': proxy}
        kwargs['headers'] = {**self.headers, **kwargs.get('headers', {})}
        # 打印请求信息
        self.log('', f"请求URL: {url}", 'info')
        self.log('', f"请求方法: {method}", 'info')
        self.log('', f"请求参数: {kwargs}", 'info')

        response = requests.request(method, url, **kwargs)
    
        # 打印响应信息
        self.log('', f"响应状态码: {response.status_code}", 'info')
        self.log('', f"响应内容: {response.text}", 'info')

        return response


    def register_and_login(self, private_key: str, proxy: Optional[str] = None) -> Dict:
        public_key = self.get_public_key(private_key)
        if public_key == 'UNKNOWN':
            self.log('', '私钥无效，跳过处理', 'warning')
            return {}
        try:
            self.log(public_key, '处理中', 'info')

            # 获取登录消息
            resp = self.make_request('GET', '/incentive/auth/login/get_message/', proxy)
            # 新增：检查HTTP状态码
            if resp.status_code != 200:
                self.log('error', f"获取message失败，状态码：{resp.status_code}", 'error')
                return False
            try:
                # 方案1：如果响应是纯字符串（如 "Sign this message..."）
                message = resp.text.strip('"')  # 保留当前逻辑，但需确保服务端返回的是干净字符串
    
                # 方案2：如果响应是JSON（如 {"message": "..."}）
                # response_data = resp.json()
                # message = response_data.get('message')  # 根据实际字段名调整
            
                self.log('', f"获取到的 message: {message}", 'info')
            except Exception as e:
                self.log('error', f"解析message失败: {str(e)}", 'error')
                return False


            # 签名消息
            keypair = Keypair.from_base58_string(private_key.strip())
            print(keypair)
            signature = keypair.sign_message(message.encode())
            signature_base58 = base58.b58encode(bytes(signature)).decode()

            self.log('', f"生成的 signature_base58: {signature_base58}", 'info')
            self.log('', f"对应的 public_key: {public_key}", 'info')

            # 登录
            resp = self.make_request('POST', '/incentive/auth/login/', proxy,
                                   json={'message': message,
                                         'signature': signature_base58,
                                         'key': public_key})
            login_result = resp.json()
            print(login_result)
            if not login_result.get('access_token'):
                raise Exception('登录失败')
            self.log('', '新登录成功', 'success')

            return {
                'token': login_result['access_token'],
                'refreshToken': login_result['refresh_token'],
                'privateKey': private_key
            }
        except Exception as e:
            self.log('', f"错误: {str(e)}", 'error')
            return {}

    def update_account_file(self, accounts: List[Dict]) -> None:
        content = '\n'.join(f"{acc['token']}:{acc['refreshToken']}:{acc['privateKey']}" 
                          for acc in accounts)
        with open(ACCOUNTS_PATH, 'w', encoding='utf-8') as f:
            f.write(content)

    def print_banner(self):
        banner = '''
            ███╗   ██╗██╗███╗   ██╗     ██╗ █████╗ 
            ████╗  ██║██║████╗  ██║     ██║██╔══██╗
            ██╔██╗ ██║██║██╔██╗ ██║     ██║███████║
            ██║╚██╗██║██║██║╚██╗██║██   ██║██╔══██║
            ██║ ╚████║██║██║ ╚████║╚█████╔╝██║  ██║
            ╚═╝  ╚═══╝╚═╝╚═╝  ╚═══╝ ╚════╝ ╚═╝  ╚═╝
                 Assister自动注册登录程序
                作者Github: github.com/Bitpeng-YT
                作者推特: 纸盒忍者@Web3CartonNinja             
        '''
        print(Fore.CYAN + banner + Style.RESET_ALL)

    def main(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        self.print_banner()
        print(Fore.CYAN + '自动注册登录已启动！\n' + Style.RESET_ALL)

        private_keys = self.read_private_keys()
        proxies = self.read_proxies()

        if proxies:
            print(Fore.YELLOW + f"已加载 {len(proxies)} 个代理" + Style.RESET_ALL)
        else:
            print(Fore.RED + '未找到代理，使用直接连接' + Style.RESET_ALL)

        print(Fore.MAGENTA + f"处理 {len(private_keys)} 个私钥\n" + Style.RESET_ALL)

        updated_accounts = []
        for i, private_key in enumerate(private_keys):
            proxy = proxies[i % len(proxies)] if proxies else None
            account = self.register_and_login(private_key, proxy)
            if account:
                updated_accounts.append(account)

        self.update_account_file(updated_accounts)
        print('\n')
        self.log('系统', '所有私钥已处理，等待下一个周期...', 'success')

if __name__ == "__main__":
    import time
    import asyncio

    register = AssisterRegister()
    while True:
        asyncio.run(register.main())
        time.sleep(21600)  # 每6小时运行一次