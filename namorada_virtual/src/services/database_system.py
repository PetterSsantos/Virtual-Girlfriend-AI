import sqlite3
import json
from datetime import datetime, date
from typing import List, Dict, Any
import os

class VirtualGirlfriendDB:
    def __init__(self, db_path: str = "virtual_girlfriend.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa o banco de dados com as tabelas necessárias"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela para personalidades
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS personalities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER,
                traits TEXT, -- JSON string
                hobbies TEXT,
                foods TEXT,
                fears TEXT,
                dreams TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela para conversas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL, -- YYYY-MM-DD format
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela para mensagens
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER,
                sender TEXT NOT NULL, -- 'user' or 'ai'
                message TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id)
            )
        ''')
        
        # Tabela para configurações
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_personality(self, personality_data: Dict[str, Any]) -> int:
        """Salva ou atualiza a personalidade"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Primeiro, verifica se já existe uma personalidade
        cursor.execute("SELECT id FROM personalities ORDER BY updated_at DESC LIMIT 1")
        existing = cursor.fetchone()
        
        traits_json = json.dumps(personality_data.get('traits', []))
        
        if existing:
            # Atualiza a personalidade existente
            cursor.execute('''
                UPDATE personalities 
                SET name=?, age=?, traits=?, hobbies=?, foods=?, fears=?, dreams=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            ''', (
                personality_data['name'],
                personality_data['age'],
                traits_json,
                personality_data['hobbies'],
                personality_data['foods'],
                personality_data['fears'],
                personality_data['dreams'],
                existing[0]
            ))
            personality_id = existing[0]
        else:
            # Cria nova personalidade
            cursor.execute('''
                INSERT INTO personalities (name, age, traits, hobbies, foods, fears, dreams)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                personality_data['name'],
                personality_data['age'],
                traits_json,
                personality_data['hobbies'],
                personality_data['foods'],
                personality_data['fears'],
                personality_data['dreams']
            ))
            personality_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return personality_id
    
    def get_current_personality(self) -> Dict[str, Any]:
        """Retorna a personalidade atual"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT name, age, traits, hobbies, foods, fears, dreams 
            FROM personalities 
            ORDER BY updated_at DESC LIMIT 1
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            try:
                traits = json.loads(result[2]) if result[2] else []
            except (json.JSONDecodeError, TypeError):
                traits = ['carinhosa', 'inteligente']
            
            return {
                'name': result[0] or 'Cortana',
                'age': result[1] or 19,
                'traits': traits,
                'hobbies': result[3] or 'ler livros de romance, assistir séries, jogar Valorant, ouvir música indie',
                'foods': result[4] or 'chocolate, pizza, sorvete de morango',
                'fears': result[5] or 'filmes de terror, aranhas',
                'dreams': result[6] or 'viajar pelo mundo, ter um café próprio, escrever um livro'
            }
        else:
            # Personalidade padrão
            return {
                'name': 'Cortana',
                'age': 19,
                'traits': ['carinhosa', 'engracada', 'inteligente', 'curiosa'],
                'hobbies': 'ler livros de romance, assistir séries, jogar Valorant, ouvir música indie',
                'foods': 'chocolate, pizza, sorvete de morango',
                'fears': 'filmes de terror, aranhas',
                'dreams': 'viajar pelo mundo, ter um café próprio, escrever um livro'
            }
    
    def get_or_create_today_conversation(self) -> int:
        """Retorna o ID da conversa de hoje, criando uma nova se necessário"""
        today = date.today().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM conversations WHERE date = ?", (today,))
        result = cursor.fetchone()
        
        if result:
            conversation_id = result[0]
        else:
            cursor.execute("INSERT INTO conversations (date) VALUES (?)", (today,))
            conversation_id = cursor.lastrowid
            conn.commit()
        
        conn.close()
        return conversation_id
    
    def save_message(self, conversation_id: int, sender: str, message: str):
        """Salva uma mensagem no banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO messages (conversation_id, sender, message)
            VALUES (?, ?, ?)
        ''', (conversation_id, sender, message))
        
        conn.commit()
        conn.close()
    
    def get_conversation_history(self, conversation_id: int) -> List[Dict[str, str]]:
        """Retorna o histórico de mensagens de uma conversa"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT sender, message, timestamp 
            FROM messages 
            WHERE conversation_id = ? 
            ORDER BY timestamp ASC
        ''', (conversation_id,))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                'sender': row[0],
                'message': row[1],
                'timestamp': row[2]
            })
        
        conn.close()
        return messages
    
    def get_all_conversations(self) -> List[Dict[str, Any]]:
        """Retorna todas as conversas com preview da última mensagem"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.id, c.date, c.created_at,
                   (SELECT message FROM messages WHERE conversation_id = c.id ORDER BY timestamp DESC LIMIT 1) as last_message
            FROM conversations c
            ORDER BY c.date DESC
        ''')
        
        conversations = []
        for row in cursor.fetchall():
            # Formatar data para exibição
            try:
                conv_date = datetime.strptime(row[1], '%Y-%m-%d').date()
            except ValueError:
                conv_date = date.today()
                
            today = date.today()
            
            if conv_date == today:
                date_display = "Hoje"
            elif conv_date == date.fromordinal(today.toordinal() - 1):
                date_display = "Ontem"
            else:
                date_display = conv_date.strftime('%d/%m/%Y')
            
            conversations.append({
                'id': row[0],
                'date': row[1],
                'date_display': date_display,
                'last_message': row[3] or "Conversa iniciada",
                'created_at': row[2]
            })
        
        conn.close()
        return conversations
    
    def get_recent_messages(self, conversation_id: int, limit: int = 10) -> List[Dict[str, str]]:
        """Retorna as últimas mensagens para contexto da IA"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT sender, message 
            FROM messages 
            WHERE conversation_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (conversation_id, limit))
        
        messages = []
        for row in reversed(cursor.fetchall()):  # Reverter para ordem cronológica
            messages.append({
                'sender': row[0],
                'message': row[1]
            })
        
        conn.close()
        return messages
    
    def set_setting(self, key: str, value: str):
        """Define uma configuração"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (key, value))
        
        conn.commit()
        conn.close()
    
    def get_setting(self, key: str, default: str = None) -> str:
        """Retorna uma configuração"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        result = cursor.fetchone()
        
        conn.close()
        return result[0] if result else default
    
    def delete_conversation(self, conversation_id: int):
        """Deleta uma conversa e todas suas mensagens"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
        cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
        
        conn.commit()
        conn.close()
    
    def get_conversation_stats(self) -> Dict[str, int]:
        """Retorna estatísticas das conversas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total de conversas
        cursor.execute("SELECT COUNT(*) FROM conversations")
        total_conversations = cursor.fetchone()[0]
        
        # Total de mensagens
        cursor.execute("SELECT COUNT(*) FROM messages")
        total_messages = cursor.fetchone()[0]
        
        # Mensagens do usuário
        cursor.execute("SELECT COUNT(*) FROM messages WHERE sender = 'user'")
        user_messages = cursor.fetchone()[0]
        
        # Mensagens da IA
        cursor.execute("SELECT COUNT(*) FROM messages WHERE sender = 'ai'")
        ai_messages = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_conversations': total_conversations,
            'total_messages': total_messages,
            'user_messages': user_messages,
            'ai_messages': ai_messages
        }
    
    def cleanup_old_conversations(self, days_to_keep: int = 30):
        """Remove conversas antigas além do período especificado"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = date.today() - datetime.timedelta(days=days_to_keep)
        cutoff_str = cutoff_date.strftime('%Y-%m-%d')
        
        # Buscar IDs das conversas antigas
        cursor.execute("SELECT id FROM conversations WHERE date < ?", (cutoff_str,))
        old_conversations = cursor.fetchall()
        
        # Deletar mensagens das conversas antigas
        for conv_id in old_conversations:
            cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conv_id[0],))
        
        # Deletar conversas antigas
        cursor.execute("DELETE FROM conversations WHERE date < ?", (cutoff_str,))
        
        conn.commit()
        conn.close()
        
        return len(old_conversations)
    
    def backup_database(self, backup_path: str = None):
        """Cria backup do banco de dados"""
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backup_virtual_girlfriend_{timestamp}.db"
        
        try:
            # Conectar ao banco original
            source = sqlite3.connect(self.db_path)
            
            # Criar backup
            backup = sqlite3.connect(backup_path)
            source.backup(backup)
            
            backup.close()
            source.close()
            
            return backup_path
        except Exception as e:
            raise Exception(f"Erro ao criar backup: {str(e)}")
    
    def restore_from_backup(self, backup_path: str):
        """Restaura banco de dados de um backup"""
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Arquivo de backup não encontrado: {backup_path}")
        
        try:
            # Fazer backup do arquivo atual
            current_backup = self.backup_database(f"current_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
            
            # Conectar ao backup
            backup = sqlite3.connect(backup_path)
            
            # Conectar ao banco atual
            current = sqlite3.connect(self.db_path)
            
            # Restaurar
            backup.backup(current)
            
            current.close()
            backup.close()
            
            return current_backup
        except Exception as e:
            raise Exception(f"Erro ao restaurar backup: {str(e)}")
    
    def get_database_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tamanho do arquivo
        file_size = os.path.getsize(self.db_path) / (1024 * 1024)  # MB
        
        # Informações das tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        table_info = {}
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            table_info[table] = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'file_path': self.db_path,
            'file_size_mb': round(file_size, 2),
            'tables': table_info,
            'last_modified': datetime.fromtimestamp(os.path.getmtime(self.db_path))
        }