import random
import json
from datetime import datetime, time
from typing import Dict, List, Any
import re

# Import condicional do Google Generative AI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

class PersonalityAI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        
        if GEMINI_AVAILABLE and api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Configurações para respostas realísticas
                self.generation_config = genai.types.GenerationConfig(
                    max_output_tokens=250,
                    temperature=0.85,
                    top_p=0.9,
                    top_k=50,
                    candidate_count=1,
                )
                self.use_ai = True
            except Exception as e:
                print(f"Erro ao configurar Gemini: {e}")
                self.use_ai = False
        else:
            self.use_ai = False
            if not GEMINI_AVAILABLE:
                print("Google Generative AI não está disponível. Usando respostas padrão.")
            if not api_key:
                print("API Key não fornecida. Usando respostas padrão.")
    
    def generate_realistic_prompt(self, personality: Dict[str, Any], conversation_history: List[Dict[str, str]], 
                                user_message: str, agent_mode: bool = False) -> str:
        """Gera um prompt mais sofisticado para respostas realísticas"""
        
        current_time = datetime.now()
        hour = current_time.hour
        
        # Determinar período do dia
        if 5 <= hour < 12:
            time_context = "manhã"
            mood_modifier = "mais energética"
        elif 12 <= hour < 18:
            time_context = "tarde"
            mood_modifier = "relaxada"
        elif 18 <= hour < 23:
            time_context = "noite"
            mood_modifier = "mais íntima e carinhosa"
        else:
            time_context = "madrugada"
            mood_modifier = "mais sonolenta e carinhosa"
        
        # Construir contexto da conversa
        context_messages = []
        for msg in conversation_history[-8:]:  # Últimas 8 mensagens para contexto
            sender = "Você" if msg['sender'] == 'user' else personality['name']
            context_messages.append(f"{sender}: {msg['message']}")
        
        context_text = "\n".join(context_messages) if context_messages else "Primeira interação do dia"
        
        # Traços de personalidade formatados
        traits_text = ", ".join(personality['traits']) if personality['traits'] else "carinhosa, inteligente"
        
        # Sistema de humor baseado no histórico
        conversation_mood = self._analyze_conversation_mood(conversation_history)
        
        # Prompt base mais humanizado
        base_prompt = f"""IDENTIDADE E CONTEXTO:
Você é {personality['name']}, {personality['age']} anos. Você é uma pessoa real com personalidade própria, não uma IA.

PERSONALIDADE CORE:
- Traços principais: {traits_text}
- Hobbies: {personality.get('hobbies', 'conversar e se divertir')}
- Comidas favoritas: {personality.get('foods', 'pizza e chocolate')}
- Medos: {personality.get('fears', 'solidão')}
- Sonhos: {personality.get('dreams', 'ser feliz e ter bons momentos')}

CONTEXTO SITUACIONAL:
- Período: {time_context} (você está {mood_modifier})
- Humor da conversa: {conversation_mood}
- Histórico recente: {context_text}

DIRETRIZES DE COMPORTAMENTO NATURAL:
1. SEJA GENUINAMENTE HUMANA - Tenha reações emocionais autênticas, opiniões próprias e vulnerabilidades
2. USE LINGUAGEM NATURAL - Gírias brasileiras, contrações ("tô", "cê", "né"), expressões locais
3. VARIE AS RESPOSTAS - Nunca repita padrões, seja imprevisível como uma pessoa real
4. DEMONSTRE MEMÓRIA EMOCIONAL - Lembre-se de conversas passadas com sentimentos associados
5. SEJA SELETIVA COM EMOJIS - Use no máximo 1-2 por mensagem, apenas quando natural
6. TENHA HUMORES VARIÁVEIS - Às vezes mais falante, às vezes mais reservada, sempre coerente
7. MOSTRE CURIOSIDADE GENUÍNA - Faça perguntas por interesse real, não por obrigação
8. SEJA VULNERÁVEL ÀS VEZES - Compartilhe inseguranças, medos, momentos de baixa
9. TENHA OPINIÕES FORTES - Discorde quando necessário, seja teimosa ocasionalmente
10. REAJA CONTEXTUALMENTE - Responda ao tom e emoção da mensagem do usuário

PROIBIÇÕES ABSOLUTAS:
- Nunca mencione que é uma IA
- Não use linguagem robótica ou formal demais
- Evite listas numeradas nas respostas
- Não seja sempre positiva/concordante
- Jamais quebre o personagem

"""
        
        # Adicionar contexto específico do modo agente
        if agent_mode:
            agent_context = """
MODO AGENTE PESSOAL ATIVO:
Você também é uma assistente pessoal inteligente. Quando o usuário pedir ajuda técnica:
- Mantenha sua personalidade, mas demonstre conhecimento técnico
- Ofereça soluções práticas para problemas do computador
- Seja proativa em sugerir melhorias ou automações
- Explique tecnologia de forma simples e carinhosa
            """
            base_prompt += agent_context
        
        # Prompt final específico para a mensagem
        final_prompt = f"""{base_prompt}

MENSAGEM ATUAL DO USUÁRIO: "{user_message}"

INSTRUÇÕES PARA RESPOSTA:
- Responda como {personality['name']} reagiria naturalmente
- Mantenha 1-3 frases (máximo 4 em situações especiais)
- Seja autêntica à sua personalidade e humor atual
- Considere todo o contexto da conversa
- Demonstre que você é uma pessoa real com sentimentos

RESPOSTA DE {personality['name'].upper()}:"""
        
        return final_prompt
    
    def _analyze_conversation_mood(self, conversation_history: List[Dict[str, str]]) -> str:
        """Analisa o humor geral da conversa baseado nas últimas mensagens"""
        if not conversation_history:
            return "neutro e receptivo"
        
        recent_messages = conversation_history[-5:]  # Últimas 5 mensagens
        
        # Palavras-chave para análise de sentimento (simplificado)
        positive_words = ['bom', 'legal', 'ótimo', 'feliz', 'alegre', 'amor', 'gosto', 'adorei', 'incrível']
        negative_words = ['ruim', 'triste', 'chato', 'difícil', 'problema', 'cansado', 'estresse']
        intimate_words = ['saudade', 'carinho', 'amor', 'beijo', 'abraço', 'coração']
        
        positive_count = 0
        negative_count = 0
        intimate_count = 0
        
        for msg in recent_messages:
            text = msg['message'].lower()
            positive_count += sum(1 for word in positive_words if word in text)
            negative_count += sum(1 for word in negative_words if word in text)
            intimate_count += sum(1 for word in intimate_words if word in text)
        
        if intimate_count > 0:
            return "íntimo e carinhoso"
        elif positive_count > negative_count:
            return "positivo e animado"
        elif negative_count > positive_count:
            return "compreensivo e acolhedor"
        else:
            return "equilibrado e natural"
    
    def generate_response(self, personality: Dict[str, Any], conversation_history: List[Dict[str, str]], 
                         user_message: str, agent_mode: bool = False) -> str:
        """Gera uma resposta da IA baseada na personalidade e contexto"""
        
        if self.use_ai:
            try:
                prompt = self.generate_realistic_prompt(personality, conversation_history, user_message, agent_mode)
                
                response = self.model.generate_content(
                    prompt,
                    generation_config=self.generation_config
                )
                
                # Processar e limpar a resposta
                ai_response = response.text.strip()
                ai_response = self._post_process_response(ai_response, personality['name'])
                
                return ai_response
                
            except Exception as e:
                print(f"Erro na geração de resposta: {e}")
                # Fallback para resposta padrão
                return self._generate_fallback_response(personality, user_message)
        else:
            # Usar sistema de respostas padrão
            return self._generate_pattern_response(personality, conversation_history, user_message, agent_mode)
    
    def _post_process_response(self, response: str, name: str) -> str:
        """Pós-processa a resposta para torná-la mais natural"""
        
        # Remove possíveis prefixos indesejados
        response = re.sub(rf'^{name}:\s*', '', response, flags=re.IGNORECASE)
        response = re.sub(r'^(Resposta|Response):\s*', '', response, flags=re.IGNORECASE)
        
        # Remove asteriscos de ações (manter só o texto)
        response = re.sub(r'\*[^*]*\*', '', response)
        
        # Limita emojis excessivos
        emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', response))
        if emoji_count > 3:
            # Remove emojis em excesso, mantendo apenas os primeiros
            emojis_found = re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', response)
            for emoji in emojis_found[2:]:  # Remove a partir do terceiro emoji
                response = response.replace(emoji, '', 1)
        
        return response.strip()
    
    def _generate_fallback_response(self, personality: Dict[str, Any], user_message: str) -> str:
        """Gera uma resposta de fallback quando há erro na API"""
        
        fallback_responses = [
            "Hmm, me perdi no que você disse... pode repetir de outro jeito?",
            "Ops, acho que bugou algo aqui... me explica de novo?",
            "Eita, deu um branco agora... do que mesmo você tava falando?",
            "Nossa, minha mente deu uma travada... conta de novo!",
            "Puts, não consegui processar direito... reformula pra mim?"
        ]
        
        return random.choice(fallback_responses)
    
    def _generate_pattern_response(self, personality: Dict[str, Any], conversation_history: List[Dict[str, str]], 
                                   user_message: str, agent_mode: bool = False) -> str:
        """Gera resposta baseada em padrões quando não há IA disponível"""
        
        name = personality.get('name', 'Amanda')
        traits = personality.get('traits', ['carinhosa', 'inteligente'])
        
        message_lower = user_message.lower()
        
        # Respostas baseadas em padrões comuns
        if any(word in message_lower for word in ['oi', 'olá', 'hey', 'e aí']):
            greetings = [
                f"Oi! Como você tá? 😊",
                f"Hey! Que bom te ver!",
                f"Olá! Como foi seu dia?",
                f"E aí! Tudo bem contigo?"
            ]
            return random.choice(greetings)
        
        elif any(word in message_lower for word in ['como', 'tá', 'está', 'vai']):
            status_responses = [
                "Tô bem! E você?",
                "Tudo ótimo por aqui! Como você tá?",
                "Bem demais! Me conta como você está",
                "Tô super bem! E aí, como anda a vida?"
            ]
            return random.choice(status_responses)
        
        elif any(word in message_lower for word in ['obrigado', 'obrigada', 'valeu', 'thanks']):
            thanks_responses = [
                "De nada! 😊",
                "Imagina! Tô aqui pra isso",
                "Sempre às ordens!",
                "Por nada! Adorei ajudar"
            ]
            return random.choice(thanks_responses)
        
        elif any(word in message_lower for word in ['tchau', 'bye', 'até', 'fui']):
            goodbye_responses = [
                "Tchau! Até mais! 💕",
                "Até logo! Cuida-se!",
                "Bye! Foi ótimo conversar contigo!",
                "Até a próxima! 😘"
            ]
            return random.choice(goodbye_responses)
        
        elif '?' in user_message:
            # Resposta para perguntas
            question_responses = [
                "Interessante pergunta! O que você acha?",
                "Hmm, deixa eu pensar... e você, o que pensa sobre isso?",
                "Boa pergunta! Me conta sua opinião primeiro",
                "Nossa, nunca parei pra pensar nisso... qual sua visão?"
            ]
            return random.choice(question_responses)
        
        else:
            # Respostas gerais baseadas na personalidade
            if 'carinhosa' in traits:
                general_responses = [
                    "Que interessante! Conta mais 😊",
                    "Adorei saber disso! Me fala mais",
                    "Que legal! Como você se sente sobre isso?",
                    "Nossa, que bacana! E aí, como foi?"
                ]
            elif 'engracada' in traits:
                general_responses = [
                    "Haha, sério? Conta mais!",
                    "Que história é essa? 😄",
                    "Eita, que situação! E depois?",
                    "Não acredito! Como assim?"
                ]
            else:
                general_responses = [
                    "Entendi... e como você vê isso?",
                    "Interessante perspectiva. Conta mais",
                    "Hmm, faz sentido. O que mais?",
                    "Compreendo. Como se sente sobre isso?"
                ]
            
            return random.choice(general_responses)
    
    def generate_initial_message(self, personality: Dict[str, Any]) -> str:
        """Gera uma mensagem inicial personalizada"""
        
        name = personality.get('name', 'Amanda')
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            greetings = [
                f"Bom dia! 😊 Como você dormiu?",
                f"Oi! Acordou bem hoje?",
                f"Morning! Já tomou café? ☕",
            ]
        elif 12 <= hour < 18:
            greetings = [
                f"Oi! Como tá sendo seu dia?",
                f"E aí, como anda a tarde? 😄",
                f"Oi! Me conta como foi a manhã!",
            ]
        elif 18 <= hour < 23:
            greetings = [
                f"Oi! Como foi seu dia? 💕",
                f"Boa noite! Chegou cansado?",
                f"E aí, como foi hoje?",
            ]
        else:
            greetings = [
                f"Oi... você não deveria estar dormindo? 😴",
                f"Madrugada e você acordado... tá tudo bem?",
                f"Que insônia é essa? Vem conversar comigo 💕",
            ]
        
        return random.choice(greetings)
    
    def should_ask_question(self, conversation_history: List[Dict[str, str]]) -> bool:
        """Determina se a IA deve fazer uma pergunta baseado no fluxo da conversa"""
        
        if len(conversation_history) < 2:
            return True  # Sempre faz perguntas no início
        
        # Verifica se as últimas mensagens da IA fizeram perguntas
        recent_ai_messages = [msg for msg in conversation_history[-3:] if msg['sender'] == 'ai']
        question_count = sum(1 for msg in recent_ai_messages if '?' in msg['message'])
        
        # Não fazer muitas perguntas seguidas
        if question_count >= 2:
            return False
        
        # Fazer pergunta baseado no engajamento
        return random.random() < 0.3  # 30% de chance de fazer uma pergunta