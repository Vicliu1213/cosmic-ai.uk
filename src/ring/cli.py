import cmd
from quantum_ring import QuantumRing

class RingShell(cmd.Cmd):
    intro = "\n✨ 量子手环 CLI 已启动。输入 help 查看命令。\n"
    prompt = "🔐> "

    def __init__(self):
        super().__init__()
        self.ring = QuantumRing()

    def do_init(self, arg):
        """初始化量子身份: init [passphrase]"""
        key = self.ring.initialize(arg if arg else None)
        print(f"✅ 初始化成功！主密钥前缀: {key}")

    def do_auth(self, arg):
        """行为认证: auth"""
        # 生成模拟行为特征（实际中应采集真实数据）
        import numpy as np
        features = list(np.random.randn(10))
        success, conf = self.ring.authenticate(features)
        if success:
            print(f"✅ 认证成功！置信度: {conf:.2%}")
        else:
            print(f"❌ 认证失败，置信度: {conf:.2%}")

    def do_token(self, arg):
        """查看会话令牌: token"""
        token = self.ring.get_session_token()
        if token:
            print(f"会话令牌: {token}")
        else:
            print("未认证或会话已过期")

    def do_encrypt(self, arg):
        """加密消息: encrypt <消息>"""
        if not arg:
            print("请提供要加密的消息")
            return
        try:
            encrypted = self.ring.encrypt(arg)
            print(f"加密结果: {encrypted}")
        except Exception as e:
            print(f"加密失败: {e}")

    def do_decrypt(self, arg):
        """解密消息: decrypt <加密后的base64字符串>"""
        if not arg:
            print("请提供加密的base64字符串")
            return
        try:
            decrypted = self.ring.decrypt(arg)
            print(f"解密结果: {decrypted}")
        except Exception as e:
            print(f"解密失败: {e}")

    def do_status(self, arg):
        """查看手环状态"""
        print(f"用户ID: {self.ring.user_id}")
        print(f"已认证: {self.ring.authenticated}")
        if self.ring.authenticated:
            print(f"会话过期时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.ring.session_expiry))}")
        print(f"主密钥存在: {'是' if self.ring.master_key else '否'}")

    def do_exit(self, arg):
        """退出"""
        print("再见！")
        return True

if __name__ == "__main__":
    RingShell().cmdloop()
