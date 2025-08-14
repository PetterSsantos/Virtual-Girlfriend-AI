import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import json
import os
from datetime import datetime, date
import random
import webbrowser
from typing import Dict, List, Any


# Imports dos módulos que criamos
from namorada_virtual.src.services.database_system import VirtualGirlfriendDB
from namorada_virtual.src.services.ai_personality_system import PersonalityAI
from namorada_virtual.src.services.personal_agent_system import PersonalAgent

class VirtualGirlfriendApp:
    def __init__(self):
        # Configurações
        self.config_file = "config.json"
        self.load_config()
        
        # Inicializar sistemas
        self.db = VirtualGirlfriendDB()
        self.ai = PersonalityAI(self.config.get('gemini_api_key', ''))
        self.agent = PersonalAgent()
        
        # Estado da aplicação
        self.current_personality = self.db.get_current_personality()
        self.current_conversation_id = self.db.get_or_create_today_conversation()
        self.agent_mode = False
        self.is_sending = False
        
        # Criar interface
        self.create_main_window()
        self.load_conversation_history()
        self.show_initial_message()
    
    def load_config(self):
        """Carrega configurações do arquivo"""
        default_config = {
            'gemini_api_key': '',
            'theme': 'modern',
            'auto_save': True,
            'notifications': True
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = {**default_config, **json.load(f)}
            except:
                self.config = default_config
        else:
            self.config = default_config
    
    def save_config(self):
        """Salva configurações no arquivo"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erro ao salvar config: {e}")
    
    def create_main_window(self):
        """Cria a janela principal moderna"""
        self.root = tk.Tk()
        self.root.title("💕 Virtual Girlfriend AI - Sua Companheira Inteligente")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Configurar estilo moderno
        style = ttk.Style()
        style.theme_use('clam')
        
        # Cores modernas
        self.colors = {
            'bg_primary': '#f8f9fa',
            'bg_secondary': '#e9ecef',
            'accent': '#667eea',
            'accent_hover': '#5a6fd8',
            'text_primary': '#212529',
            'text_secondary': '#6c757d',
            'success': '#28a745',
            'warning': '#ffc107',
            'danger': '#dc3545'
        }
        
        self.root.configure(bg=self.colors['bg_primary'])
        
        # Menu superior
        self.create_menu()
        
        # Layout principal
        self.create_layout()
        
        # Atalhos de teclado
        self.root.bind('<Control-Return>', lambda e: self.send_message())
        self.root.bind('<F1>', lambda e: self.toggle_agent_mode())
        
        # Centralizar janela
        self.center_window()
    
    def create_menu(self):
        """Cria menu superior"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Arquivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Nova Conversa", command=self.new_conversation)
        file_menu.add_command(label="Exportar Conversa", command=self.export_conversation)
        file_menu.add_separator()
        file_menu.add_command(label="Configurações", command=self.open_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit)
        
        # Menu Personalidade
        personality_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Personalidade", menu=personality_menu)
        personality_menu.add_command(label="Editar Personalidade", command=self.open_personality_editor)
        personality_menu.add_command(label="Resetar Personalidade", command=self.reset_personality)
        
        # Menu Agente
        agent_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Agente", menu=agent_menu)
        agent_menu.add_command(label="Ativar/Desativar Agente (F1)", command=self.toggle_agent_mode)
        agent_menu.add_command(label="Status do Sistema", command=self.show_system_status)
        agent_menu.add_command(label="Sugestões de Produtividade", command=self.show_productivity_tips)
        
        # Menu Ajuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        help_menu.add_command(label="Como Usar", command=self.show_help)
        help_menu.add_command(label="Atalhos", command=self.show_shortcuts)
        help_menu.add_command(label="Sobre", command=self.show_about)
    
    def create_layout(self):
        """Cria o layout principal"""
        # Container principal
        main_container = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Layout em grid
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_rowconfigure(0, weight=1)
        
        # Sidebar esquerda
        self.create_sidebar(main_container)
        
        # Área de chat principal
        self.create_chat_area(main_container)
    
    def create_sidebar(self, parent):
        """Cria sidebar com conversas e controles"""
        sidebar = tk.Frame(parent, bg='white', relief='solid', bd=1)
        sidebar.grid(row=0, column=0, sticky='nsew', padx=(0, 15))
        sidebar.grid_propagate(False)
        sidebar.configure(width=300)
        
        # Header da sidebar
        header = tk.Frame(sidebar, bg=self.colors['accent'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title_label = tk.Label(header, text="💕 Conversas", 
                              font=('Segoe UI', 14, 'bold'), 
                              fg='white', bg=self.colors['accent'])
        title_label.pack(pady=15)
        
        # Notebook para tabs
        self.sidebar_notebook = ttk.Notebook(sidebar)
        self.sidebar_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab Conversas
        self.create_conversations_tab()
        
        # Tab Personalidade
        self.create_personality_tab()
        
        # Tab Agente
        self.create_agent_tab()
    
    def create_conversations_tab(self):
        """Cria tab de conversas"""
        conv_frame = tk.Frame(self.sidebar_notebook)
        self.sidebar_notebook.add(conv_frame, text="Conversas")
        
        # Lista de conversas
        self.conversations_listbox = tk.Listbox(conv_frame, font=('Segoe UI', 10),
                                               selectmode=tk.SINGLE, height=15)
        self.conversations_listbox.pack(fill=tk.BOTH, expand=True, pady=10)
        self.conversations_listbox.bind('<<ListboxSelect>>', self.on_conversation_select)
        
        # Botões
        btn_frame = tk.Frame(conv_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(btn_frame, text="Nova Conversa", command=self.new_conversation,
                 bg=self.colors['accent'], fg='white', font=('Segoe UI', 9, 'bold')).pack(fill=tk.X, pady=2)
        
        tk.Button(btn_frame, text="Excluir Conversa", command=self.delete_conversation,
                 bg=self.colors['danger'], fg='white', font=('Segoe UI', 9)).pack(fill=tk.X, pady=2)
        
        self.update_conversations_list()
    
    def create_personality_tab(self):
        """Cria tab de personalidade"""
        pers_frame = tk.Frame(self.sidebar_notebook)
        self.sidebar_notebook.add(pers_frame, text="Personalidade")
        
        # Scroll frame para o formulário
        canvas = tk.Canvas(pers_frame)
        scrollbar = ttk.Scrollbar(pers_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Campos do formulário
        self.create_personality_form(scrollable_frame)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_personality_form(self, parent):
        """Cria formulário de personalidade"""
        # Nome
        tk.Label(parent, text="Nome:", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(10, 2))
        self.name_entry = tk.Entry(parent, font=('Segoe UI', 10))
        self.name_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Idade
        tk.Label(parent, text="Idade:", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 2))
        self.age_entry = tk.Entry(parent, font=('Segoe UI', 10))
        self.age_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Traços de personalidade
        tk.Label(parent, text="Personalidade:", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        traits_frame = tk.Frame(parent)
        traits_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.trait_vars = {}
        traits = ['carinhosa', 'timida', 'engracada', 'inteligente', 'curiosa', 'brincalhona', 'teimosa', 'romantica']
        
        for i, trait in enumerate(traits):
            var = tk.BooleanVar()
            self.trait_vars[trait] = var
            cb = tk.Checkbutton(traits_frame, text=trait.capitalize(), variable=var, font=('Segoe UI', 9))
            cb.grid(row=i//2, column=i%2, sticky='w', padx=5, pady=2)
        
        # Campos de texto
        fields = [
            ('Hobbies:', 'hobbies_text'),
            ('Comidas Favoritas:', 'foods_text'),
            ('Medos:', 'fears_text'),
            ('Sonhos:', 'dreams_text')
        ]
        
        for label, attr in fields:
            tk.Label(parent, text=label, font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(5, 2))
            text_widget = tk.Text(parent, height=3, font=('Segoe UI', 9))
            text_widget.pack(fill=tk.X, pady=(0, 10))
            setattr(self, attr, text_widget)
        
        # Botão salvar
        tk.Button(parent, text="Salvar Personalidade", command=self.save_personality,
                 bg=self.colors['success'], fg='white', font=('Segoe UI', 10, 'bold')).pack(fill=tk.X, pady=10)
        
        # Carregar personalidade atual
        self.load_personality_form()
    
    def create_agent_tab(self):
        """Cria tab do agente"""
        agent_frame = tk.Frame(self.sidebar_notebook)
        self.sidebar_notebook.add(agent_frame, text="Agente")
        
        # Status do agente
        status_frame = tk.LabelFrame(agent_frame, text="Status do Agente", font=('Segoe UI', 10, 'bold'))
        status_frame.pack(fill=tk.X, pady=10, padx=5)
        
        self.agent_status_label = tk.Label(status_frame, text="🔴 Inativo", font=('Segoe UI', 10))
        self.agent_status_label.pack(pady=5)
        
        self.toggle_agent_btn = tk.Button(status_frame, text="Ativar Agente", 
                                         command=self.toggle_agent_mode,
                                         bg=self.colors['accent'], fg='white', font=('Segoe UI', 9, 'bold'))
        self.toggle_agent_btn.pack(pady=5)
        
        # Controles rápidos
        controls_frame = tk.LabelFrame(agent_frame, text="Controles Rápidos", font=('Segoe UI', 10, 'bold'))
        controls_frame.pack(fill=tk.X, pady=10, padx=5)
        
        quick_commands = [
            ("Status do Sistema", self.show_system_status),
            ("Screenshot", self.take_screenshot),
            ("Modo Foco", self.activate_focus_mode),
            ("Limpeza Sistema", self.system_cleanup)
        ]
        
        for cmd_name, cmd_func in quick_commands:
            tk.Button(controls_frame, text=cmd_name, command=cmd_func,
                     bg=self.colors['bg_secondary'], font=('Segoe UI', 8)).pack(fill=tk.X, pady=2)
    
    def create_chat_area(self, parent):
        """Cria área principal de chat"""
        chat_container = tk.Frame(parent, bg='white', relief='solid', bd=1)
        chat_container.grid(row=0, column=1, sticky='nsew')
        
        # Header do chat
        self.create_chat_header(chat_container)
        
        # Área de mensagens
        self.create_messages_area(chat_container)
        
        # Área de entrada
        self.create_input_area(chat_container)
    
    def create_chat_header(self, parent):
        """Cria header do chat"""
        header = tk.Frame(parent, bg=self.colors['accent'], height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Info da personalidade
        info_frame = tk.Frame(header, bg=self.colors['accent'])
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        self.header_name_label = tk.Label(info_frame, text=f"💕 {self.current_personality['name']}", 
                                         font=('Segoe UI', 16, 'bold'), fg='white', bg=self.colors['accent'])
        self.header_name_label.pack(anchor='w')
        
        self.header_status_label = tk.Label(info_frame, text="🟢 Online - Pronta para conversar", 
                                           font=('Segoe UI', 10), fg='white', bg=self.colors['accent'])
        self.header_status_label.pack(anchor='w')
        
        # Status do agente
        agent_frame = tk.Frame(header, bg=self.colors['accent'])
        agent_frame.pack(side=tk.RIGHT, padx=20, pady=15)
        
        self.agent_indicator = tk.Label(agent_frame, text="🤖 Agente: Inativo", 
                                       font=('Segoe UI', 9), fg='white', bg=self.colors['accent'])
        self.agent_indicator.pack()
    
    def create_messages_area(self, parent):
        """Cria área de mensagens"""
        messages_frame = tk.Frame(parent)
        messages_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # ScrolledText para as mensagens
        self.messages_text = scrolledtext.ScrolledText(
            messages_frame,
            wrap=tk.WORD,
            font=('Segoe UI', 11),
            bg='#fafbfc',
            fg=self.colors['text_primary'],
            relief='flat',
            padx=15,
            pady=15,
            state=tk.DISABLED
        )
        self.messages_text.pack(fill=tk.BOTH, expand=True)
        
        # Configurar tags para formatação
        self.setup_message_tags()
    
    def setup_message_tags(self):
        """Configura tags para formatação das mensagens"""
        self.messages_text.tag_configure('user', 
            foreground='white', 
            background=self.colors['accent'],
            relief='flat',
            borderwidth=0,
            rmargin=50,
            justify='right'
        )
        
        self.messages_text.tag_configure('ai', 
            foreground=self.colors['text_primary'], 
            background='white',
            relief='solid',
            borderwidth=1,
            lmargin1=0,
            lmargin2=0,
            rmargin=50
        )
        
        self.messages_text.tag_configure('system', 
            foreground=self.colors['text_secondary'], 
            background=self.colors['bg_secondary'],
            font=('Segoe UI', 10, 'italic'),
            justify='center'
        )
        
        self.messages_text.tag_configure('timestamp', 
            foreground=self.colors['text_secondary'], 
            font=('Segoe UI', 8),
            justify='right'
        )
    
    def create_input_area(self, parent):
        """Cria área de entrada de mensagens"""
        input_container = tk.Frame(parent, bg=self.colors['bg_secondary'], height=100)
        input_container.pack(fill=tk.X)
        input_container.pack_propagate(False)
        
        input_frame = tk.Frame(input_container, bg=self.colors['bg_secondary'])
        input_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Text widget para entrada
        self.message_input = tk.Text(
            input_frame,
            height=3,
            font=('Segoe UI', 11),
            wrap=tk.WORD,
            relief='solid',
            borderwidth=1,
            padx=10,
            pady=8
        )
        self.message_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Botão enviar
        self.send_button = tk.Button(
            input_frame,
            text="Enviar\n(Ctrl+Enter)",
            command=self.send_message,
            bg=self.colors['accent'],
            fg='white',
            font=('Segoe UI', 10, 'bold'),
            width=12,
            relief='flat',
            cursor='hand2'
        )
        self.send_button.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind para Enter
        self.message_input.bind('<Control-Return>', lambda e: self.send_message())
        self.message_input.bind('<KeyRelease>', self.on_input_change)
        
        # Focus inicial
        self.message_input.focus()
    
    def center_window(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def show_initial_message(self):
        """Mostra mensagem inicial da IA"""
        initial_message = self.ai.generate_initial_message(self.current_personality)
        self.add_message(initial_message, 'ai')
    
    def load_conversation_history(self):
        """Carrega histórico da conversa atual"""
        messages = self.db.get_conversation_history(self.current_conversation_id)
        
        for msg in messages:
            self.add_message(msg['message'], msg['sender'], show_timestamp=False)
    
    def add_message(self, text: str, sender: str, show_timestamp: bool = True):
        """Adiciona mensagem na área de chat"""
        self.messages_text.config(state=tk.NORMAL)
        
        # Timestamp
        if show_timestamp:
            timestamp = datetime.now().strftime("%H:%M")
            self.messages_text.insert(tk.END, f"[{timestamp}] ", 'timestamp')
        
        # Nome do sender e mensagem
        if sender == 'user':
            self.messages_text.insert(tk.END, "Você: ", 'user')
            self.messages_text.insert(tk.END, f"{text}\n\n", 'user')
        elif sender == 'ai':
            name = self.current_personality['name']
            self.messages_text.insert(tk.END, f"{name}: ", 'ai')
            self.messages_text.insert(tk.END, f"{text}\n\n", 'ai')
        else:  # system
            self.messages_text.insert(tk.END, f"🔧 Sistema: {text}\n\n", 'system')
        
        self.messages_text.config(state=tk.DISABLED)
        self.messages_text.see(tk.END)
    
    def send_message(self):
        """Envia mensagem do usuário"""
        if self.is_sending:
            return
        
        message = self.message_input.get("1.0", tk.END).strip()
        if not message:
            return
        
        self.is_sending = True
        self.send_button.config(state=tk.DISABLED, text="Enviando...")
        self.message_input.delete("1.0", tk.END)
        
        # Adicionar mensagem do usuário
        self.add_message(message, 'user')
        self.db.save_message(self.current_conversation_id, 'user', message)
        
        # Processar resposta em thread separada
        def process_response():
            try:
                # Verificar se é comando do agente
                if self.agent_mode and self.agent.can_execute_command(message):
                    response, success = self.agent.execute_command(message, self.current_personality)
                    self.add_message(response, 'ai')
                    self.db.save_message(self.current_conversation_id, 'ai', response)
                else:
                    # Gerar resposta da IA
                    conversation_history = self.db.get_recent_messages(self.current_conversation_id, 10)
                    response = self.ai.generate_response(
                        self.current_personality, 
                        conversation_history, 
                        message, 
                        self.agent_mode
                    )
                    
                    self.add_message(response, 'ai')
                    self.db.save_message(self.current_conversation_id, 'ai', response)
                
            except Exception as e:
                error_msg = f"Ops, tive um probleminha técnico... 😅 Pode tentar de novo? (Erro: {str(e)})"
                self.add_message(error_msg, 'ai')
            
            finally:
                # Reativar interface
                self.root.after(0, self.reset_input_state)
        
        thread = threading.Thread(target=process_response)
        thread.daemon = True
        thread.start()
    
    def reset_input_state(self):
        """Reseta estado da interface de entrada"""
        self.is_sending = False
        self.send_button.config(state=tk.NORMAL, text="Enviar\n(Ctrl+Enter)")
        self.message_input.focus()
    
    def on_input_change(self, event):
        """Callback para mudanças na entrada de texto"""
        # Auto-resize do texto de entrada
        content = self.message_input.get("1.0", tk.END)
        lines = content.count('\n')
        height = min(max(lines + 1, 3), 8)  # Entre 3 e 8 linhas
        self.message_input.config(height=height)
    
    def toggle_agent_mode(self):
        """Alterna modo agente"""
        self.agent_mode = not self.agent_mode
        
        if self.agent_mode:
            self.agent_status_label.config(text="🟢 Ativo", fg=self.colors['success'])
            self.agent_indicator.config(text="🤖 Agente: Ativo")
            self.toggle_agent_btn.config(text="Desativar Agente", bg=self.colors['danger'])
            
            # Mensagem de ativação
            agent_msg = f"🤖 Modo Agente Pessoal ativado! Agora posso te ajudar com tarefas do computador, {self.current_personality['name']} está aqui para tudo que precisar! ✨"
            self.add_message(agent_msg, 'system')
        else:
            self.agent_status_label.config(text="🔴 Inativo", fg=self.colors['danger'])
            self.agent_indicator.config(text="🤖 Agente: Inativo")
            self.toggle_agent_btn.config(text="Ativar Agente", bg=self.colors['accent'])
            
            # Mensagem de desativação
            agent_msg = f"💕 Modo Agente Pessoal desativado. Voltando ao modo conversa normal com {self.current_personality['name']}!"
            self.add_message(agent_msg, 'system')
    
    def save_personality(self):
        """Salva personalidade personalizada"""
        try:
            # Coletar dados do formulário
            personality_data = {
                'name': self.name_entry.get().strip() or 'Amanda',
                'age': int(self.age_entry.get()) if self.age_entry.get().isdigit() else 19,
                'traits': [trait for trait, var in self.trait_vars.items() if var.get()],
                'hobbies': self.hobbies_text.get("1.0", tk.END).strip(),
                'foods': self.foods_text.get("1.0", tk.END).strip(),
                'fears': self.fears_text.get("1.0", tk.END).strip(),
                'dreams': self.dreams_text.get("1.0", tk.END).strip()
            }
            
            # Salvar no banco
            self.db.save_personality(personality_data)
            self.current_personality = personality_data
            
            # Atualizar interface
            self.header_name_label.config(text=f"💕 {personality_data['name']}")
            
            # Mensagem de confirmação
            self.add_message(f"Personalidade atualizada! {personality_data['name']} agora tem as características que você definiu. ✨", 'system')
            
            messagebox.showinfo("Sucesso", f"Personalidade de {personality_data['name']} salva com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar personalidade: {str(e)}")
    
    def load_personality_form(self):
        """Carrega dados da personalidade no formulário"""
        # Nome e idade
        self.name_entry.insert(0, self.current_personality['name'])
        self.age_entry.insert(0, str(self.current_personality['age']))
        
        # Traits
        for trait in self.current_personality['traits']:
            if trait in self.trait_vars:
                self.trait_vars[trait].set(True)
        
        # Campos de texto
        self.hobbies_text.insert("1.0", self.current_personality['hobbies'])
        self.foods_text.insert("1.0", self.current_personality['foods'])
        self.fears_text.insert("1.0", self.current_personality['fears'])
        self.dreams_text.insert("1.0", self.current_personality['dreams'])
    
    def update_conversations_list(self):
        """Atualiza lista de conversas"""
        self.conversations_listbox.delete(0, tk.END)
        conversations = self.db.get_all_conversations()
        
        for conv in conversations:
            display_text = f"{conv['date_display']} - {conv['last_message'][:30]}..."
            self.conversations_listbox.insert(tk.END, display_text)
    
    def on_conversation_select(self, event):
        """Callback para seleção de conversa"""
        selection = self.conversations_listbox.curselection()
        if selection:
            # Implementar mudança de conversa
            pass
    
    def new_conversation(self):
        """Inicia nova conversa"""
        self.current_conversation_id = self.db.get_or_create_today_conversation()
        self.messages_text.config(state=tk.NORMAL)
        self.messages_text.delete("1.0", tk.END)
        self.messages_text.config(state=tk.DISABLED)
        
        self.show_initial_message()
        self.update_conversations_list()
        
        self.add_message("Nova conversa iniciada! 🎉", 'system')
    
    def delete_conversation(self):
        """Deleta conversa selecionada"""
        selection = self.conversations_listbox.curselection()
        if selection:
            if messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir esta conversa?"):
                # Implementar exclusão
                self.update_conversations_list()
    
    # Comandos do agente
    def show_system_status(self):
        """Mostra status do sistema"""
        if hasattr(self, 'agent'):
            status = self.agent._get_system_status()
            self.add_message(status, 'system')
        else:
            self.add_message("Agente não disponível.", 'system')
    
    def take_screenshot(self):
        """Tira screenshot"""
        if hasattr(self, 'agent'):
            result = self.agent._take_screenshot()
            self.add_message(result, 'system')
        else:
            self.add_message("Agente não disponível.", 'system')
    
    def activate_focus_mode(self):
        """Ativa modo foco"""
        if hasattr(self, 'agent'):
            result = self.agent.execute_macro('foco')
            self.add_message(result, 'system')
        else:
            self.add_message("Agente não disponível.", 'system')
    
    def system_cleanup(self):
        """Inicia limpeza do sistema"""
        if hasattr(self, 'agent'):
            result = self.agent.execute_macro('limpeza')
            self.add_message(result, 'system')
        else:
            self.add_message("Agente não disponível.", 'system')
    
    def show_productivity_tips(self):
        """Mostra dicas de produtividade"""
        if hasattr(self, 'agent'):
            suggestions = self.agent.get_productivity_suggestions()
            for tip in suggestions:
                self.add_message(tip, 'system')
        else:
            self.add_message("Agente não disponível.", 'system')
    
    # Dialogs e janelas auxiliares
    def open_settings(self):
        """Abre janela de configurações"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Configurações")
        settings_window.geometry("400x300")
        settings_window.resizable(False, False)
        
        # Centralizar
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # API Key
        tk.Label(settings_window, text="Chave da API Gemini:", font=('Segoe UI', 10, 'bold')).pack(anchor='w', padx=20, pady=(20, 5))
        api_entry = tk.Entry(settings_window, font=('Segoe UI', 10), show="*", width=50)
        api_entry.pack(padx=20, pady=(0, 10))
        api_entry.insert(0, self.config.get('gemini_api_key', ''))
        
        # Outras configurações
        auto_save_var = tk.BooleanVar(value=self.config.get('auto_save', True))
        tk.Checkbutton(settings_window, text="Salvar automaticamente", 
                      variable=auto_save_var, font=('Segoe UI', 10)).pack(anchor='w', padx=20, pady=5)
        
        notifications_var = tk.BooleanVar(value=self.config.get('notifications', True))
        tk.Checkbutton(settings_window, text="Ativar notificações", 
                      variable=notifications_var, font=('Segoe UI', 10)).pack(anchor='w', padx=20, pady=5)
        
        def save_settings():
            self.config['gemini_api_key'] = api_entry.get()
            self.config['auto_save'] = auto_save_var.get()
            self.config['notifications'] = notifications_var.get()
            self.save_config()
            
            # Reconfigurar AI se necessário
            if api_entry.get().strip():
                self.ai = PersonalityAI(api_entry.get().strip())
            
            settings_window.destroy()
            messagebox.showinfo("Sucesso", "Configurações salvas!")
        
        tk.Button(settings_window, text="Salvar", command=save_settings,
                 bg=self.colors['success'], fg='white', font=('Segoe UI', 10, 'bold')).pack(pady=20)
    
    def open_personality_editor(self):
        """Abre editor de personalidade em janela separada"""
        self.sidebar_notebook.select(1)  # Seleciona tab personalidade
    
    def reset_personality(self):
        """Reseta personalidade para padrão"""
        if messagebox.askyesno("Confirmar", "Isso irá resetar a personalidade para os valores padrão. Confirmar?"):
            # Limpar formulário
            self.name_entry.delete(0, tk.END)
            self.age_entry.delete(0, tk.END)
            for var in self.trait_vars.values():
                var.set(False)
            
            for widget in [self.hobbies_text, self.foods_text, self.fears_text, self.dreams_text]:
                widget.delete("1.0", tk.END)
            
            # Carregar valores padrão
            default_personality = {
                'name': 'Amanda',
                'age': 19,
                'traits': ['carinhosa', 'engracada', 'inteligente', 'curiosa'],
                'hobbies': 'ler livros de romance, assistir séries, jogar Valorant, ouvir música indie',
                'foods': 'chocolate, pizza, sorvete de morango',
                'fears': 'filmes de terror, aranhas',
                'dreams': 'viajar pelo mundo, ter um café próprio, escrever um livro'
            }
            
            self.current_personality = default_personality
            self.load_personality_form()
            self.save_personality()
    
    def export_conversation(self):
        """Exporta conversa atual"""
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")]
        )
        
        if filename:
            try:
                messages = self.db.get_conversation_history(self.current_conversation_id)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"=== Conversa com {self.current_personality['name']} ===\n\n")
                    for msg in messages:
                        sender = "Você" if msg['sender'] == 'user' else self.current_personality['name']
                        f.write(f"[{msg['timestamp']}] {sender}: {msg['message']}\n\n")
                
                messagebox.showinfo("Sucesso", f"Conversa exportada para {filename}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao exportar: {str(e)}")
    
    def show_help(self):
        """Mostra ajuda"""
        help_text = """=== Como Usar a Virtual Girlfriend AI ===

💕 CONVERSA NORMAL:
- Digite sua mensagem e pressione Enter ou clique em Enviar
- A IA responderá baseada na personalidade configurada
- Conversas são salvas automaticamente por data

🤖 MODO AGENTE:
- Pressione F1 ou use o menu para ativar
- Peça comandos como: "abrir chrome", "screenshot", "status do sistema"
- A IA pode executar tarefas básicas no seu computador

🎨 PERSONALIZAÇÃO:
- Use a aba Personalidade para customizar sua companheira
- Defina nome, idade, traços, gostos e sonhos
- Mudanças são aplicadas imediatamente

⌨️ ATALHOS:
- Ctrl+Enter: Enviar mensagem
- F1: Ativar/Desativar Agente
- Ctrl+N: Nova conversa
"""
        
        messagebox.showinfo("Ajuda", help_text)
    
    def show_shortcuts(self):
        """Mostra atalhos do teclado"""
        shortcuts_text = """=== Atalhos do Teclado ===

Ctrl + Enter - Enviar mensagem
F1 - Ativar/Desativar Modo Agente
Ctrl + N - Nova conversa
Ctrl + S - Salvar configurações
Ctrl + E - Exportar conversa
Ctrl + Q - Sair do programa
"""
        messagebox.showinfo("Atalhos", shortcuts_text)
    
    def show_about(self):
        """Mostra informações sobre o programa"""
        about_text = """Virtual Girlfriend AI v2.0

Uma companheira virtual inteligente com personalidade
customizável e funcionalidades de agente pessoal.

Características:
• IA conversacional realística
• Personalidade 100% customizável  
• Modo agente pessoal (Jarvis)
• Conversas salvas por data
• Interface moderna e intuitiva
• Sistema de banco de dados integrado

Desenvolvido com Python, Tkinter e Gemini AI.

© 2024 - Feito com 💕"""
        
        messagebox.showinfo("Sobre", about_text)
    
    def run(self):
        """Inicia a aplicação"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_closing()
    
    def on_closing(self):
        """Callback para fechamento da aplicação"""
        if messagebox.askokcancel("Sair", "Deseja realmente sair?"):
            self.save_config()
            self.root.destroy()

# Script principal
if __name__ == "__main__":
    try:
        app = VirtualGirlfriendApp()
        app.run()
    except Exception as e:
        print(f"Erro crítico: {e}")
        messagebox.showerror("Erro Crítico", f"Erro ao iniciar aplicação: {str(e)}")
