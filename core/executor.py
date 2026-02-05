import abc
import abc
import asyncio
import logging
import os

logger = logging.getLogger("jarvis.core.executor")

class CommandExecutor(abc.ABC):
    @abc.abstractmethod
    async def update_packages(self) -> str:
        """Update system packages"""
        pass
    
    @abc.abstractmethod
    async def check_firewall(self) -> str:
        """Check firewall status"""
        pass

    @abc.abstractmethod
    async def add_gpg_key(self, key_id: str) -> str:
        """Add missing GPG key"""
        pass

class LinuxExecutor(CommandExecutor):
    async def _run(self, cmd: str, timeout: int = 45) -> str:
        # Dynamic Root Check: If running as root, remove 'sudo' from command
        if os.geteuid() == 0 and cmd.startswith("sudo "):
             cmd = cmd.replace("sudo ", "", 1)
             
        try:
            # Async subprocess execution
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for output with timeout
            try:
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=float(timeout))
            except asyncio.TimeoutError:
                try:
                    proc.kill()
                except:
                    pass
                return f"⚠️ ERROR: Command timed out after {timeout} seconds."
            
            if proc.returncode == 0:
                return f"✅ SUCCESS:\n{stdout.decode()[:500]}" 
            else:
                return f"❌ FAILED (Code {proc.returncode}):\n{stderr.decode()}"
        except Exception as e:
            return f"⚠️ ERROR: {str(e)}"

    async def update_packages(self) -> str:
        # Use non-interactive mode and longer timeout for upgrades
        cmd = "export DEBIAN_FRONTEND=noninteractive && sudo apt update && sudo apt -y -o Dpkg::Options::='--force-confdef' -o Dpkg::Options::='--force-confold' upgrade"
        return await self._run(cmd, timeout=300)

    async def check_firewall(self) -> str:
        return await self._run("sudo iptables -L")

    async def add_gpg_key(self, key_id: str) -> str:
        # Note: apt-key is deprecated but still widely widely used for quick fixes.
        # Ideally: wget -O- https://... | sudo tee /etc/apt/trusted.gpg.d/...
        # But keyserver method is generic.
        if key_id == "EDA3E22630349F1C":
            # ProtonVPN specific robust fix (Direct Download)
            cmd = "wget -q -O - https://repo.protonvpn.com/debian/public_key.asc | sudo apt-key add -"
        else:
            # Fallback for others
            cmd = f"sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys {key_id}"
            
        return await self._run(cmd)

class WindowsExecutor(CommandExecutor):
    async def _run(self, cmd: str, timeout: int = 45) -> str:
        try:
             proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
             stdout, stderr = await proc.communicate()
             return stdout.decode() if proc.returncode == 0 else stderr.decode()
        except Exception as e:
            return str(e)

    async def update_packages(self) -> str:
        return await self._run("winget upgrade --all", timeout=300)

    async def check_firewall(self) -> str:
        return await self._run("netsh advfirewall show allprofiles")

    async def add_gpg_key(self, key_id: str) -> str:
        return "GPG Key management is Linux-specific feature."

class ExecutorFactory:
    @staticmethod
    def get_executor(os_type: str) -> CommandExecutor:
        if os_type == "linux":
            return LinuxExecutor()
        elif os_type == "windows":
            return WindowsExecutor()
        else:
            raise ValueError(f"Unsupported OS: {os_type}")
