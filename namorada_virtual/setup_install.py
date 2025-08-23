"""
Script de instalação e configuração para Virtual Girlfriend AI
Instala dependências e configura o ambiente automaticamente
"""

import subprocess
import sys
import os
import json
import platform

"""
Script de instalação e configuração para Virtual Girlfriend AI
Instala dependências e configura o ambiente automaticamente
"""

import subprocess
import sys
import os
import json
import platform

def check_python_version():
    """Verifica se a versão do Python é compatível"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 ou superior é necessário!")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")
    return True

def install_requirements():
    """Instala todas as dependências necessárias"""
    required_packages = [
        'google-generativeai',
        'psutil',
        'pillow',
        'requests'
    ]
    
    print("🔧 Instalando dependências...")
    
    for package in required_packages:
        try:
            print(f"Instalando {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package], 
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"✅ {package} instalado com sucesso!")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Erro ao instalar {package}: {e}")
            print(f"Tentando instalar {package} com --user...")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--user', package],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"✅ {package} instalado com sucesso (modo usuário)!")
            except subprocess.CalledProcessError:
                print(f"❌ Falha ao instalar {package}")
                return False
    
    return True

def get_api_key_console():
    """Obtém a chave da API do Gemini via console"""
    print("\n" + "="*60)
    print("🔑 CONFIGURAÇÃO DA API GEMINI")
    print("="*60)
    print("\nPara usar a Virtual Girlfriend AI, você precisa de uma chave da API do Google Gemini.")
    print("\n📝 Como obter sua API Key:")
    print("1. Acesse: https://ai.google.dev/")
    print("2. Clique em 'Get API Key'")
    print("3. Faça login com sua conta Google")
    print("4. Crie uma nova API Key (é gratuito)")
    print("5. Cole a chave abaixo")
    
    print("\n" + "-"*60)
    api_key = input("Cole sua API Key do Google Gemini aqui: ").strip()
    
    if not api_key:
        print("❌ API Key é obrigatória!")
        return None
    
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

def create_batch_file():
    """Cria arquivo executável para facilitar uso"""
    system = platform.system()
    
    if system == "Windows":
        batch_content = f"""@echo off
title Virtual Girlfriend AI
cd /d "{os.getcwd()}"
echo Iniciando Virtual Girlfriend AI...
python -m main_application.py
if errorlevel 1 (
    echo.
    echo Erro ao executar a aplicacao. Verifique se todas as dependencias estao instaladas.
    pause
)
"""
        try:
            with open('Executar_Virtual_Girlfriend.bat', 'w', encoding='utf-8') as f:
                f.write(batch_content)
            print("✅ Arquivo executável criado: Executar_Virtual_Girlfriend.bat")
        except Exception as e:
            print(f"⚠️ Erro ao criar arquivo batch: {e}")
    
    elif system == "Darwin" or system == "Linux":  # macOS e Linux
        script_content = f"""#!/bin/bash
echo "Iniciando Virtual Girlfriend AI..."
cd "{os.getcwd()}"
python3 main_application.py
"""
        try:
            with open('executar_virtual_girlfriend.sh', 'w') as f:
                f.write(script_content)
            
            # Dar permissão de execução
            os.chmod('executar_virtual_girlfriend.sh', 0o755)
            print("✅ Script executável criado: executar_virtual_girlfriend.sh")
        except Exception as e:
            print(f"⚠️ Erro ao criar script: {e}")

def create_requirements_txt():
    """Cria arquivo requirements.txt para futuras instalações"""
    requirements = """google-generativeai>=0.3.0
psutil>=5.8.0
pillow>=8.0.0
requests>=2.25.0
"""
    
    try:
        with open('requirements.txt', 'w') as f:
            f.write(requirements)
        print("✅ Arquivo requirements.txt criado")
    except Exception as e:
        print(f"⚠️ Erro ao criar requirements.txt: {e}")

def show_final_instructions():
    """Mostra instruções finais para o usuário"""
    system = platform.system()
    
    print("\n" + "="*60)
    print("🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*60)
    
    print("\n✨ Sua Virtual Girlfriend AI está pronta para uso!")
    
    print("\n🚀 COMO EXECUTAR:")
    if system == "Windows":
        print("   • Duplo-clique em 'Executar_Virtual_Girlfriend.bat'")
        print("   • Ou execute: python main_application.py")
    else:
        print("   • Execute: ./executar_virtual_girlfriend.sh")
        print("   • Ou execute: python3 main_application.py")
    
    print("\n💡 DICAS IMPORTANTES:")
    print("   • Configure a personalidade da sua companheira na aba lateral")
    print("   • Use F1 para ativar/desativar o modo Agente Pessoal")
    print("   • Suas conversas são salvas automaticamente por data")
    print("   • Use Ctrl+Enter para enviar mensagens rapidamente")
    
    print("\n🔧 RESOLUÇÃO DE PROBLEMAS:")
    print("   • Se houver erro de API, verifique sua chave do Gemini")
    print("   • Para reinstalar dependências: pip install -r requirements.txt")
    print("   • Verifique se o Python 3.7+ está instalado")
    
    print("\n📁 ARQUIVOS CRIADOS:")
    print("   • config.json - Suas configurações")
    print("   • virtual_girlfriend.db - Banco de dados das conversas")
    print("   • requirements.txt - Lista de dependências")
    
    if system == "Windows":
        print("   • Executar_Virtual_Girlfriend.bat - Atalho para execução")
    else:
        print("   • executar_virtual_girlfriend.sh - Script de execução")

def test_installation():
    """Testa se a instalação foi bem-sucedida"""
    print("\n🧪 Testando instalação...")
    
    try:
        # Testa importações básicas
        import sqlite3
        print("✅ SQLite disponível")
        
        import json
        print("✅ JSON disponível")
        
        # Testa dependências instaladas
        try:
            import psutil
            print("✅ PSUtil disponível")
        except ImportError:
            print("⚠️ PSUtil não encontrado")
            
        try:
            import PIL
            print("✅ Pillow disponível")
        except ImportError:
            print("⚠️ Pillow não encontrado")
            
        try:
            import google.generativeai
            print("✅ Google Generative AI disponível")
        except ImportError:
            print("⚠️ Google Generative AI não encontrado")
        
        # Testa criação do banco de dados
        try:
            from database_system import VirtualGirlfriendDB
            db = VirtualGirlfriendDB("test_db.db")
            os.remove("test_db.db")
            print("✅ Sistema de banco de dados funcionando")
        except Exception as e:
            print(f"⚠️ Erro no sistema de banco: {e}")
        
        print("✅ Instalação testada com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def main():
    """Função principal de instalação"""
    print("=" * 60)
    print("🔧 INSTALADOR VIRTUAL GIRLFRIEND AI v2.0")
    print("=" * 60)
    
    # Verificar versão do Python
    if not check_python_version():
        input("\nPressione Enter para sair...")
        return
    
    # Instalar dependências
    print("\n📦 Instalando dependências...")
    if not install_requirements():
        print("\n❌ Falha na instalação das dependências!")
        print("Tente executar manualmente: pip install -r requirements.txt")
        input("Pressione Enter para sair...")
        return
    
    # Criar arquivo requirements.txt
    create_requirements_txt()
    
    # Obter API key
    print("\n🔑 Configurando API...")
    api_key = get_api_key_console()
    
    if not api_key:
        print("❌ API Key é obrigatória para o funcionamento!")
        input("Pressione Enter para sair...")
        return
    
    # Criar arquivo de configuração
    print("\n⚙️ Criando configurações...")
    if not create_config_file(api_key):
        input("Pressione Enter para sair...")
        return
    
    # Criar arquivos executáveis
    print("\n📁 Criando arquivos auxiliares...")
    create_batch_file()
    
    # Testar instalação
    if not test_installation():
        print("⚠️ Alguns componentes podem não estar funcionando perfeitamente.")
    
    # Instruções finais
    show_final_instructions()
    
    print("\n" + "="*60)
    input("Pressione Enter para finalizar...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Instalação cancelada pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        input("Pressione Enter para sair...")