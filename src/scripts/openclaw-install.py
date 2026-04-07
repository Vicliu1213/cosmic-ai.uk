#!/usr/bin/env python3
"""
OpenClaw 安装器 - Python 版本
适用于 Ubuntu 移动设备和所有 Linux 系统
"""

import os
import sys
import subprocess
import urllib.request
import urllib.error
import json
import platform
from pathlib import Path
from typing import Optional, Tuple

# 颜色定义
COLORS = {
    'BOLD': '\033[1m',
    'ACCENT': '\033[38;2;255;77;77m',      # coral-bright
    'INFO': '\033[38;2;136;146;176m',      # text-secondary
    'SUCCESS': '\033[38;2;0;229;204m',     # cyan-bright
    'WARN': '\033[38;2;255;176;32m',       # amber
    'ERROR': '\033[38;2;230;57;70m',       # coral-mid
    'MUTED': '\033[38;2;90;100;128m',      # text-muted
    'NC': '\033[0m'  # No Color
}

class OpenClawInstaller:
    def __init__(self):
        self.os_type = self.detect_os()
        self.arch = platform.machine()
        
    def detect_os(self) -> str:
        """检测操作系统"""
        system = platform.system()
        if system == 'Darwin':
            return 'macos'
        elif system == 'Linux':
            return 'linux'
        else:
            return 'unknown'
    
    def print_header(self):
        """打印安装器标题"""
        print(f"{COLORS['ACCENT']}{COLORS['BOLD']}")
        print("  🦞 OpenClaw 安装器 (Python 版本)")
        print(f"{COLORS['NC']}{COLORS['INFO']}  All your chats, one OpenClaw.{COLORS['NC']}")
        print()
    
    def info(self, msg: str):
        """打印信息"""
        print(f"{COLORS['MUTED']}·{COLORS['NC']} {msg}")
    
    def warn(self, msg: str):
        """打印警告"""
        print(f"{COLORS['WARN']}!{COLORS['NC']} {msg}")
    
    def success(self, msg: str):
        """打印成功"""
        print(f"{COLORS['SUCCESS']}✓{COLORS['NC']} {msg}")
    
    def error(self, msg: str):
        """打印错误"""
        print(f"{COLORS['ERROR']}✗{COLORS['NC']} {msg}")
    
    def check_command(self, cmd: str) -> bool:
        """检查命令是否存在"""
        try:
            subprocess.run(['which', cmd], capture_output=True, check=True)
            return True
        except:
            return False
    
    def get_command_version(self, cmd: str) -> Optional[str]:
        """获取命令版本"""
        try:
            if cmd == 'node':
                result = subprocess.run([cmd, '--version'], capture_output=True, text=True)
                return result.stdout.strip()
            elif cmd == 'npm':
                result = subprocess.run([cmd, '--version'], capture_output=True, text=True)
                return result.stdout.strip()
            elif cmd == 'git':
                result = subprocess.run([cmd, '--version'], capture_output=True, text=True)
                return result.stdout.strip()
        except:
            pass
        return None
    
    def detect_system_info(self):
        """检测系统信息"""
        self.info(f"操作系统: {platform.system()}")
        self.info(f"架构: {self.arch}")
        
        # 尝试读取发行版信息
        try:
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    if line.startswith('PRETTY_NAME'):
                        pretty_name = line.split('=')[1].strip().strip('"')
                        self.info(f"发行版: {pretty_name}")
                    elif line.startswith('VERSION_ID'):
                        version_id = line.split('=')[1].strip().strip('"')
                        self.info(f"版本 ID: {version_id}")
        except:
            pass
        print()
    
    def check_dependencies(self) -> Tuple[bool, list]:
        """检查依赖"""
        print("检查依赖...")
        missing = []
        
        # 检查 curl
        if self.check_command('curl'):
            self.success("curl 已安装")
        else:
            self.warn("curl 未安装")
            missing.append('curl')
        
        # 检查 wget
        if self.check_command('wget'):
            self.success("wget 已安装")
        else:
            self.info("wget 未安装（可选）")
        
        # 检查 git
        if self.check_command('git'):
            self.success("git 已安装")
        else:
            self.warn("git 未安装（可选）")
        
        # 检查 Node.js
        if self.check_command('node'):
            version = self.get_command_version('node')
            self.success(f"Node.js 已安装: {version}")
        else:
            self.error("Node.js 未安装")
            missing.append('node')
        
        # 检查 npm
        if self.check_command('npm'):
            version = self.get_command_version('npm')
            self.success(f"npm 已安装: {version}")
        else:
            self.error("npm 未安装")
            missing.append('npm')
        
        print()
        return len(missing) == 0, missing
    
    def install_node_ubuntu(self):
        """在 Ubuntu 上安装 Node.js"""
        self.warn("正在安装 Node.js...")
        
        try:
            # 检查是否有 apt
            if not self.check_command('apt-get'):
                self.error("找不到 apt-get，无法继续")
                return False
            
            # 下载 NodeSource 设置脚本
            self.info("下载 NodeSource 仓库设置...")
            setup_url = 'https://deb.nodesource.com/setup_20.x'
            setup_file = '/tmp/nodesource-setup.sh'
            
            try:
                urllib.request.urlretrieve(setup_url, setup_file)
                self.success("已下载 NodeSource 设置")
            except urllib.error.URLError as e:
                self.error(f"下载失败: {e}")
                return False
            
            # 运行设置脚本
            self.info("配置 NodeSource 仓库...")
            try:
                subprocess.run(['sudo', 'bash', setup_file], check=True)
            except subprocess.CalledProcessError:
                self.error("配置仓库失败")
                return False
            
            # 安装 Node.js
            self.info("安装 Node.js...")
            try:
                subprocess.run(['sudo', 'apt-get', 'update'], check=True, capture_output=True)
                subprocess.run(['sudo', 'apt-get', 'install', '-y', 'nodejs'], check=True)
            except subprocess.CalledProcessError as e:
                self.error(f"安装 Node.js 失败: {e}")
                return False
            
            self.success("Node.js 安装完成")
            return True
        except Exception as e:
            self.error(f"安装过程出错: {e}")
            return False
    
    def install_openclaw(self) -> bool:
        """安装 OpenClaw"""
        print()
        self.info("通过 npm 安装 OpenClaw...")
        
        if not self.check_command('npm'):
            self.error("npm 未找到，无法继续")
            return False
        
        try:
            subprocess.run(['npm', 'install', '-g', 'openclaw'], check=True)
            self.success("OpenClaw 安装成功！")
            return True
        except subprocess.CalledProcessError as e:
            self.error(f"OpenClaw 安装失败: {e}")
            return False
    
    def verify_installation(self) -> bool:
        """验证安装"""
        print()
        self.info("验证安装...")
        
        if self.check_command('openclaw'):
            self.success("OpenClaw 命令可用")
            
            try:
                result = subprocess.run(['openclaw', '--version'], capture_output=True, text=True)
                version = result.stdout.strip()
                self.info(f"OpenClaw 版本: {version}")
                return True
            except:
                self.warn("OpenClaw 命令可用但无法获取版本")
                return True
        else:
            self.error("OpenClaw 命令不可用")
            return False
    
    def show_next_steps(self):
        """显示下一步"""
        print()
        print(f"{COLORS['BOLD']}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{COLORS['NC']}")
        self.success("安装完成！")
        print(f"{COLORS['BOLD']}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{COLORS['NC']}")
        print()
        self.info("下一步:")
        print("  1. 运行 OpenClaw:")
        print("     openclaw")
        print()
        print("  2. 查看帮助:")
        print("     openclaw --help")
        print()
        print("  3. 查看版本:")
        print("     openclaw --version")
        print()
        print("  4. 访问官方网站:")
        print("     https://openclaw.ai")
        print()
    
    def run(self):
        """运行安装"""
        self.print_header()
        
        # 检测系统
        self.detect_system_info()
        
        # 检查依赖
        deps_ok, missing = self.check_dependencies()
        
        if not deps_ok:
            self.warn("缺少某些必需依赖")
            
            if 'node' in missing or 'npm' in missing:
                if self.os_type == 'linux':
                    self.info("尝试自动安装 Node.js...")
                    if not self.install_node_ubuntu():
                        self.error("无法自动安装 Node.js")
                        return False
                else:
                    self.error("请手动安装 Node.js: https://nodejs.org")
                    return False
        
        # 安装 OpenClaw
        if not self.install_openclaw():
            self.error("安装过程中出错")
            return False
        
        # 验证安装
        if not self.verify_installation():
            self.warn("安装验证失败")
            return False
        
        # 显示下一步
        self.show_next_steps()
        self.success("所有步骤完成！")
        return True


def main():
    """主函数"""
    try:
        installer = OpenClawInstaller()
        
        # 检查操作系统
        if installer.os_type == 'unknown':
            print(f"{COLORS['ERROR']}✗ 不支持的操作系统{COLORS['NC']}")
            print("本安装器支持 macOS 和 Linux（包括 WSL）")
            return 1
        
        # 运行安装
        success = installer.run()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n已取消安装")
        return 1
    except Exception as e:
        print(f"{COLORS['ERROR']}✗ 安装过程出错: {e}{COLORS['NC']}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
