# Namorada Virtual - Cortana 💻❤️

Este projeto é um chatbot chamado **Cortana**, uma namorada virtual que
interage com os usuários de forma natural e personalizada.\
O sistema utiliza **Python** e uma interface Gráfica moderna em Tkinter, que abre uma janela principal ao ser executada. Essa janela permite a interação com a **Cortana** de forma simples e intuitiva. para
oferecer uma experiência mais imersiva.

---

## 📂 Estrutura do Projeto

    GirlfriendAI/
    │
    ├── namorada_virtual/
    │   ├── main_application.py      # Arquivo principal para rodar o sistema
    │   ├── setup_install.py         # Script de instalação automática
    │   │
    │   ├── src/                     # Código-fonte da aplicação
    │   │   ├── models/
    │   │   ├── services/
    │   │   │   ├── database_system.py
    │   │   │   ├── ai_personality_system.py
    │   │   │   └── personal_agent_system.py
    │   │
    │   ├── static/                  # Arquivos estáticos (CSS, imagens, JS)
    │   │   └── style.css
    │   │
    │   └── templates/               # Templates HTML da aplicação
    │       └── virtual_girlfriend_app.html
    │
    ├── requirements.txt             # Dependências do projeto
    └── README.md                    # Documentação do projeto

---

## 🌐 Versão Web

A versão web da Cortana (interface em HTML/CSS executada no navegador) ainda não está disponível.
No momento, a aplicação funciona apenas na versão desktop com Tkinter, abrindo uma janela própria ao ser executada.

🔧 Futuramente, a versão web poderá ser implementada usando Flask ou Django, permitindo acesso direto pelo navegador.

---

## ✨ Funcionalidades

-   💬 **Interação natural** com o usuário.\
-   🧠 **Memória de conversas**, permitindo lembrar interações
    anteriores.\
-   🎭 **Personalidade configurável** (hobbies, medos, sonhos, gostos).\
-   🌐 **Interface Web em HTML/CSS** para uso via navegador.

---

## ⚙️ Instalação

Para facilitar a configuração, use o script `setup_install.py`.\
No terminal, execute:

```bash
python namorada_virtual/setup_install.py
```

Esse script irá ensinar como rodar o sistema e instalar todas as dependências necessárias automaticamente.

---

## ▶️ Como Executar

Atualmente a aplicação não pode ser iniciada com python -m namorada_virtual.main_application, pois a estrutura do projeto ainda não está configurada como pacote.

🔹 Opção 1 – Rodando pelo VS Code

Abra a pasta do projeto no VS Code.

Localize o arquivo main_application.py.

Clique em Run Code (ou use Ctrl+F5).

A janela principal da Cortana será aberta.

🔹 Opção 2 – Rodando pelo terminal

Se preferir rodar direto no terminal, vá até a pasta onde está o arquivo main_application.py e execute:

 ```bash
        cd namorada_virtual
        python main_application.py
 ```

---

## 🤝 Contribuições

Contribuições são bem-vindas!\
Abra uma _issue_ ou envie um _pull request_ com melhorias.

---
