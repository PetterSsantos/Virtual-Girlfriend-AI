
"""
Script de instalação e configuração para Virtual Girlfriend AI
Instala dependências e configura o ambiente automaticamente
"""

import subprocess
import sys
import os
import json
import tkinter as tk
from tkinter import messagebox, simpledialog

def install_requirements():
    """Instala todas as dependências necessárias"""
    required_packages = [
        'google-generativeai',
        'tkinter',  # Já vem com Python
        'psutil',
        'pillow',
        'opencv-python',
        'numpy',
        'requests'
    ]
    
    print("🔧 Instalando dependências...")
    
    for package in required_packages:
        if package == 'tkinter':
            continue  # tkinter já vem com Python
            
        try:
            print(f"Instalando {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} instalado com sucesso!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao instalar {package}: {e}")
            return False
    
    return True

def get_api_key():
    """Obtém a chave da API do Gemini do usuário"""
    root = tk.Tk()
    root.withdraw()  # Esconde janela principal
    
    messagebox.showinfo(
        "Configuração da API", 
        "Para usar a Virtual Girlfriend AI, você precisa de uma chave da API do Google Gemini.\n\n"
        "1. Vá para: https://ai.google.dev/\n"
        "2. Clique em 'Get API Key'\n"
        "3. Crie uma conta Google AI (gratuita)\n"
        "4. Gere sua API Key\n"
        "5. Cole a chave na próxima tela"
    )
    
    api_key = simpledialog.askstring(
        "API Key do Gemini",
        "Cole sua API Key do Google Gemini:",
        show='*'
    )
    
    root.destroy()
    return api_key

def create_config_file(api_key):
    """Cria arquivo de configuração inicial"""
    config = {
        'gemini_api_key': api_key,
        'theme': 'modern',
        'auto_save': True,
        'notifications': True,
        'first_run': True
    }
    
    try:
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print("✅ Arquivo de configuração criado!")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar configuração: {e}")
        return False

def create_desktop_shortcut():
    """Cria atalho na área de trabalho (Windows)"""
    try:
        if sys.platform == 'win32':
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            path = os.path.join(desktop, "Virtual Girlfriend AI.lnk")
            target = os.path.join(os.getcwd(), "main_application.py")
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = f'"{target}"'
            shortcut.WorkingDirectory = os.getcwd()
            shortcut.IconLocation = sys.executable
            shortcut.save()
            
            print("✅ Atalho criado na área de trabalho!")
    except Exception as e:
        print(f"⚠️  Não foi possível criar atalho: {e}")

def show_welcome_message():
    """Mostra mensagem de boas-vindas"""
    root = tk.Tk()
    root.withdraw()
    
    welcome_text = """🎉 Instalação Concluída!

Sua Virtual Girlfriend AI está pronta para uso!

🚀 Para começar:
1. Execute o arquivo 'main_application.py'
2. Configure a personalidade da sua companheira
3. Comece a conversar!

💡 Dicas:
• Use F1 para ativar o modo Agente Pessoal
• Personalize completamente sua companheira na aba Personalidade
• Suas conversas são salvas automaticamente por data

Divirta-se! 💕"""
    
    messagebox.showinfo("Instalação Completa", welcome_text)
    root.destroy()

def check_python_version():
    """Verifica se a versão do Python é compatível"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 ou superior é necessário!")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")
    return True

def create_batch_file():
    """Cria arquivo batch para facilitar execução (Windows)"""
    if sys.platform == 'win32':
        batch_content = f"""@echo off
cd /d "{os.getcwd()}"
python main_application.py
pause
"""
        try:
            with open('Executar_Virtual_Girlfriend.bat', 'w') as f:
                f.write(batch_content)
            print("✅ Arquivo executável criado: Executar_Virtual_Girlfriend.bat")
        except Exception as e:
            print(f"⚠️  Erro ao criar arquivo batch: {e}")

def main():
    """Função principal de instalação"""
    print("=" * 50)
    print("🔧 INSTALADOR VIRTUAL GIRLFRIEND AI")
    print("=" * 50)
    
    # Verificar versão do Python
    if not check_python_version():
        input("Pressione Enter para sair...")
        return
    
    # Instalar dependências
    print("\n📦 Instalando dependências...")
    if not install_requirements():
        print("❌ Falha na instalação das dependências!")
        input("Pressione Enter para sair...")
        return
    
    # Obter API key
    print("\n🔑 Configurando API...")
    api_key = get_api_key()
    
    if not api_key or not api_key.strip():
        print("❌ API Key é obrigatória para o funcionamento!")
        input("Pressione Enter para sair...")
        return
    
    # Criar arquivo de configuração
    print("\n⚙️  Criando configurações...")
    if not create_config_file(api_key.strip()):
        input("Pressione Enter para sair...")
        return
    
    # Criar arquivos auxiliares
    create_batch_file()
    create_desktop_shortcut()
    
    # Mensagem de sucesso
    print("\n✅ Instalação concluída com sucesso!")
    show_welcome_message()
    
    print("\n🚀 Para executar a aplicação:")
    if sys.platform == 'win32':
        print("   • Duplo-clique em 'Executar_Virtual_Girlfriend.bat'")
        print("   • Ou execute: python main_application.py")
    else:
        print("   • Execute: python3 main_application.py")
    
    input("\nPressione Enter para finalizar...")

if __name__ == "__main__":
    main()
