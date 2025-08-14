import os
import subprocess
import platform
import psutil
import json
import requests
from typing import Dict, List, Any, Tuple
import re
from datetime import datetime
import webbrowser
from PIL import ImageGrab
import cv2
import numpy as np

class PersonalAgent:
    def __init__(self):
        self.system_info = self._get_system_info()
        self.commands_history = []
        
    def _get_system_info(self) -> Dict[str, Any]:
        """Coleta informações básicas do sistema"""
        return {
            'os': platform.system(),
            'os_version': platform.version(),
            'processor': platform.processor(),
            'ram_total': psutil.virtual_memory().total // (1024**3),  # GB
            'ram_available': psutil.virtual_memory().available // (1024**3),  # GB
            'disk_usage': psutil.disk_usage('/').percent if platform.system() != 'Windows' else psutil.disk_usage('C:\\').percent
        }
    
    def can_execute_command(self, user_message: str) -> bool:
        """Verifica se a mensagem contém um comando executável"""
        command_keywords = [
            'abrir', 'abra', 'executar', 'execute', 'rodar', 'iniciar',
            'fechar', 'feche', 'parar', 'matar', 'terminar',
            'mostrar', 'listar', 'ver', 'verificar', 'checar',
            'screenshot', 'capturar', 'foto da tela',
            'música', 'tocar', 'pausar', 'parar música',
            'volume', 'aumentar', 'diminuir', 'mutar',
            'sistema', 'processador', 'memória', 'disco',
            'clima', 'tempo', 'previsão',
            'pesquisar', 'buscar', 'google', 'youtube'
        ]
        
        message_lower = user_message.lower()
        return any(keyword in message_lower for keyword in command_keywords)
    
    def execute_command(self, user_message: str, personality: Dict[str, Any]) -> Tuple[str, bool]:
        """Executa comandos do sistema e retorna resposta personalizada"""
        
        message_lower = user_message.lower()
        success = True
        
        try:
            # Comandos de aplicações
            if any(word in message_lower for word in ['abrir', 'abra', 'executar', 'iniciar']):
                result = self._handle_open_command(message_lower)
            
            # Comandos de informações do sistema
            elif any(word in message_lower for word in ['sistema', 'processador', 'memória', 'ram', 'disco']):
                result = self._get_system_status()
            
            # Screenshots
            elif any(word in message_lower for word in ['screenshot', 'capturar', 'foto da tela', 'print']):
                result = self._take_screenshot()
            
            # Controle de volume
            elif any(word in message_lower for word in ['volume', 'som']):
                result = self._handle_volume_control(message_lower)
            
            # Pesquisas
            elif any(word in message_lower for word in ['pesquisar', 'buscar', 'google', 'youtube']):
                result = self._handle_search(message_lower)
            
            # Clima
            elif any(word in message_lower for word in ['clima', 'tempo', 'previsão']):
                result = self._get_weather_info()
            
            # Listar processos
            elif any(word in message_lower for word in ['processos', 'apps', 'aplicativos', 'programas']):
                result = self._list_running_processes()
            
            # Fechar aplicações
            elif any(word in message_lower for word in ['fechar', 'feche', 'matar', 'terminar']):
                result = self._handle_close_command(message_lower)
            
            else:
                result = "Não consegui identificar o comando específico. Pode me explicar melhor o que você quer que eu faça?"
                success = False
                
        except Exception as e:
            result = f"Ops, deu um erro aqui: {str(e)}. Pode tentar de novo?"
            success = False
        
        # Personalizar resposta baseado na personalidade
        personalized_response = self._personalize_response(result, personality, success)
        
        # Salvar no histórico
        self.commands_history.append({
            'command': user_message,
            'result': result,
            'success': success,
            'timestamp': datetime.now().isoformat()
        })
        
        return personalized_response, success
    
    def _handle_open_command(self, message: str) -> str:
        """Lida com comandos para abrir aplicações"""
        
        apps_map = {
            'brave': ['brave', 'google chrome', 'navegador', 'chorme'],
            'chorme': ['brave', 'google chrome', 'navegador', 'chorme'],
            'firefox': ['firefox', 'mozilla'],
            'notepad': ['bloco de notas', 'notepad', 'editor'],
            'calculator': ['calculadora', 'calc'],
            'cmd': ['cmd', 'prompt', 'terminal'],
            'explorer': ['explorer', 'pasta', 'arquivos'],
            'spotify': ['spotify', 'música'],
            'discord': ['discord'],
            'steam': ['steam', 'jogos'],
            'code': ['vscode', 'visual studio code', 'vs code', 'code'],
        }
        
        for app, keywords in apps_map.items():
            if any(keyword in message for keyword in keywords):
                return self._open_application(app)
        
        # Tentar extrair nome da aplicação da mensagem
        words = message.split()
        for i, word in enumerate(words):
            if word in ['abrir', 'abra', 'executar', 'iniciar'] and i + 1 < len(words):
                app_name = words[i + 1]
                return self._open_application(app_name)
        
        return "Não consegui identificar qual aplicação você quer abrir. Pode me dizer o nome específico?"
    
    def _open_application(self, app_name: str) -> str:
        """Abre uma aplicação específica"""
        try:
            system = platform.system()
            
            if system == "Windows":
                if app_name in ['chrome', 'google chrome']:
                    subprocess.Popen(['start', 'chrome'], shell=True)
                elif app_name == 'notepad':
                    subprocess.Popen(['notepad'])
                elif app_name == 'calculator':
                    subprocess.Popen(['calc'])
                elif app_name == 'cmd':
                    subprocess.Popen(['cmd'])
                elif app_name == 'explorer':
                    subprocess.Popen(['explorer'])
                else:
                    subprocess.Popen(['start', app_name], shell=True)
                    
            elif system == "Darwin":  # macOS
                subprocess.Popen(['open', '-a', app_name])
                
            elif system == "Linux":
                subprocess.Popen([app_name])
                
            return f"Abri o {app_name} pra você! 😊"
            
        except Exception as e:
            return f"Não consegui abrir o {app_name}. Tem certeza que ele tá instalado?"
    
    def _get_system_status(self) -> str:
        """Retorna status detalhado do sistema"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/' if platform.system() != 'Windows' else 'C:\\')
        
        status = f"""Aqui está o status do seu sistema:
        
🖥️ Processador: {cpu_percent}% de uso
🧠 Memória RAM: {memory.percent}% usado ({memory.used // (1024**3)}GB de {memory.total // (1024**3)}GB)
💾 Disco: {disk.percent}% usado ({disk.used // (1024**3)}GB de {disk.total // (1024**3)}GB)
⚡ Sistema: {platform.system()} {platform.release()}"""
        
        return status
    
    def _take_screenshot(self) -> str:
        """Captura screenshot da tela"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            
            screenshot = ImageGrab.grab()
            screenshot.save(filename)
            
            return f"Screenshot salva como {filename}! 📸"
            
        except Exception as e:
            return "Não consegui capturar a tela. Verifique as permissões."
    
    def _handle_volume_control(self, message: str) -> str:
        """Controla volume do sistema"""
        try:
            if 'aumentar' in message or 'subir' in message:
                if platform.system() == "Windows":
                    subprocess.run(['nircmd.exe', 'changesysvolume', '6500'])
                return "Volume aumentado! 🔊"
                
            elif 'diminuir' in message or 'abaixar' in message:
                if platform.system() == "Windows":
                    subprocess.run(['nircmd.exe', 'changesysvolume', '-6500'])
                return "Volume diminuído! 🔉"
                
            elif 'mutar' in message or 'silenciar' in message:
                if platform.system() == "Windows":
                    subprocess.run(['nircmd.exe', 'mutesysvolume', '2'])
                return "Som mutado! 🔇"
                
        except Exception:
            return "Não consegui controlar o volume. Você pode fazer isso manualmente por agora."
        
        return "Não entendi o comando de volume. Quer aumentar, diminuir ou mutar?"
    
    def _handle_search(self, message: str) -> str:
        """Realiza pesquisas na web"""
        try:
            # Extrair termo de pesquisa
            search_terms = ['pesquisar', 'buscar', 'google', 'youtube']
            search_term = None
            
            for term in search_terms:
                if term in message:
                    parts = message.split(term, 1)
                    if len(parts) > 1:
                        search_term = parts[1].strip()
                        break
            
            if not search_term:
                return "O que você quer pesquisar?"
            
            if 'youtube' in message:
                url = f"https://www.youtube.com/results?search_query={search_term.replace(' ', '+')}"
                webbrowser.open(url)
                return f"Abri o YouTube pesquisando por '{search_term}'! 🎥"
            else:
                url = f"https://www.google.com/search?q={search_term.replace(' ', '+')}"
                webbrowser.open(url)
                return f"Abri o Google pesquisando por '{search_term}'! 🔍"
                
        except Exception as e:
            return "Não consegui fazer a pesquisa. Tenta abrir o navegador manualmente."
    
    def _get_weather_info(self) -> str:
        """Obtém informações do clima (funcionalidade básica)"""
        # Nota: Para funcionar completamente, você precisa de uma API key do OpenWeatherMap
        return "Para informações de clima, recomendo que você abra um site de previsão do tempo. Quer que eu abra o Google Weather pra você?"
    
    def _list_running_processes(self) -> str:
        """Lista processos em execução (principais)"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
            try:
                if proc.info['memory_percent'] > 1.0:  # Só processos que usam mais de 1% da RAM
                    processes.append({
                        'name': proc.info['name'],
                        'memory': round(proc.info['memory_percent'], 1)
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Ordenar por uso de memória
        processes = sorted(processes, key=lambda x: x['memory'], reverse=True)[:10]
        
        result = "Principais aplicações rodando:\n\n"
        for proc in processes:
            result += f"• {proc['name']}: {proc['memory']}% RAM\n"
            
        return result
    
    def _handle_close_command(self, message: str) -> str:
        """Fecha aplicações específicas"""
        
        # Apps comuns para fechar
        close_map = {
            'chrome': ['chrome.exe', 'Google Chrome'],
            'firefox': ['firefox.exe', 'Firefox'],
            'notepad': ['notepad.exe', 'Notepad'],
            'calculator': ['calc.exe', 'Calculator'],
            'spotify': ['Spotify.exe', 'Spotify'],
            'discord': ['Discord.exe', 'Discord'],
            'steam': ['Steam.exe', 'Steam']
        }
        
        for app, process_names in close_map.items():
            if app in message:
                return self._close_process(process_names, app)
        
        return "Qual aplicação você quer fechar? Me diga o nome específico."
    
    def _close_process(self, process_names: List[str], app_name: str) -> str:
        """Fecha um processo específico"""
        try:
            closed = False
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] in process_names:
                    proc.terminate()
                    closed = True
            
            if closed:
                return f"Fechei o {app_name} pra você! ✅"
            else:
                return f"O {app_name} não estava rodando."
                
        except Exception as e:
            return f"Não consegui fechar o {app_name}. Tenta fechar manualmente."
    
    def _personalize_response(self, result: str, personality: Dict[str, Any], success: bool) -> str:
        """Personaliza a resposta baseado na personalidade"""
        
        name = personality.get('name', 'Amanda')
        traits = personality.get('traits', [])
        
        if not success:
            # Respostas para falhas baseadas na personalidade
            if 'timida' in traits:
                prefixes = ["Desculpa, ", "Ops, ", "Ah não, "]
                return random.choice(prefixes) + result.lower()
            elif 'engracada' in traits:
                prefixes = ["Eita, deu ruim! ", "Opa, bugou aqui! ", "Xiii, não rolou! "]
                return random.choice(prefixes) + result
            else:
                return result
        
        # Respostas para sucessos
        if 'carinhosa' in traits:
            suffixes = [" 💕", " 😊", " ✨"]
            if not any(emoji in result for emoji in ['💕', '😊', '✨', '🔊', '🔉', '🔇', '📸', '🎥', '🔍']):
                result += random.choice(suffixes)
        
        if 'brincalhona' in traits and success:
            playful_additions = [
                " Fácil demais! 😎",
                " Tá aí, mágica! ✨",
                " Pronto, como você pediu! 😄",
                " Mission accomplished! 🎯"
            ]
            if random.random() < 0.3:  # 30% de chance
                result += random.choice(playful_additions)
        
        return result
    
    def analyze_screen_activity(self) -> str:
        """Analisa atividade da tela (funcionalidade básica)"""
        try:
            # Pega janela ativa
            if platform.system() == "Windows":
                import win32gui
                active_window = win32gui.GetWindowText(win32gui.GetForegroundWindow())
                if active_window:
                    return f"Você está usando: {active_window}"
            
            return "Está trabalhando no computador"
            
        except Exception:
            return "Não consegui ver o que você está fazendo"
    
    def get_productivity_suggestions(self) -> List[str]:
        """Sugere melhorias de produtividade baseado no uso"""
        suggestions = []
        
        # Análise de uso de RAM
        memory = psutil.virtual_memory()
        if memory.percent > 80:
            suggestions.append("Sua RAM tá meio cheia... quer que eu feche alguns apps que não tá usando?")
        
        # Análise de CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 70:
            suggestions.append("Processador tá trabalhando pesado! Talvez seja hora de uma pausa? ☕")
        
        # Análise de disco
        disk = psutil.disk_usage('/' if platform.system() != 'Windows' else 'C:\\')
        if disk.percent > 85:
            suggestions.append("Seu disco tá quase cheio! Quer ajuda pra limpar arquivos antigos?")
        
        # Sugestões baseadas no horário
        hour = datetime.now().hour
        if 12 <= hour <= 14:
            suggestions.append("Que tal fazer uma pausa pro almoço? 🍽️")
        elif hour >= 22:
            suggestions.append("Já tá tarde... não esquece de descansar! 😴")
        
        return suggestions if suggestions else ["Tudo funcionando perfeitamente! 😊"]
    
    def execute_macro(self, macro_name: str) -> str:
        """Executa macros pré-definidos"""
        macros = {
            'foco': self._focus_mode,
            'pausa': self._break_mode,
            'limpeza': self._cleanup_system,
            'backup': self._quick_backup
        }
        
        if macro_name in macros:
            return macros[macro_name]()
        else:
            return "Macro não encontrado. Disponíveis: foco, pausa, limpeza, backup"
    
    def _focus_mode(self) -> str:
        """Ativa modo foco - fecha distrações"""
        try:
            distracting_apps = ['Discord.exe', 'Spotify.exe', 'chrome.exe']
            closed_apps = []
            
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] in distracting_apps:
                    proc.terminate()
                    closed_apps.append(proc.info['name'])
            
            return f"Modo foco ativado! Fechei: {', '.join(closed_apps)} 🎯"
            
        except Exception:
            return "Não consegui ativar o modo foco completamente."
    
    def _break_mode(self) -> str:
        """Sugere uma pausa"""
        break_suggestions = [
            "Hora da pausa! Que tal um alongamento? 🧘‍♀️",
            "Pausa estratégica! Bebe uma água e descansa os olhos 💧",
            "Break time! Levanta, caminha um pouco e volta renovado! 🚶‍♂️"
        ]
        return random.choice(break_suggestions)
    
    def _cleanup_system(self) -> str:
        """Realiza limpeza básica do sistema"""
        try:
            if platform.system() == "Windows":
                # Limpar arquivos temporários
                subprocess.run(['cleanmgr', '/sagerun:1'], shell=True)
                return "Iniciando limpeza do sistema... isso pode demorar alguns minutos! 🧹"
            else:
                return "Limpeza automática disponível apenas no Windows por enquanto."
                
        except Exception:
            return "Não consegui iniciar a limpeza. Tenta manualmente pelo Limpeza de Disco."
    
    def _quick_backup(self) -> str:
        """Lembra sobre backup"""
        return "Lembrete: quando foi seu último backup? 💾 Seus arquivos importantes estão seguros?"