# 📥 YouTube Video & Audio Downloader

Um script poderoso e automatizado em Python para realizar o download de vídeos individuais ou playlists completas 
do YouTube diretamente pelo terminal. O projeto suporta escolha de resoluções personalizadas e extração automatizada 
de áudio convertida para MP3.

---

## 🛠️ Pré-requisitos (Atenção!)

Para que o script funcione perfeitamente no **Windows**, você precisa ter instalado no sistema:

1. **Python 3.13+** (ou a versão utilizada no seu ambiente).
2. **Node.js** (necessário para contornar algumas restrições de criptografia de assinaturas do YouTube).
3. **FFmpeg** (essencial para realizar a junção de vídeo/áudio em alta qualidade e conversão de MP3).
   * *Nota:* Certifique-se de que o executável do FFmpeg está adicionado às **Variáveis de Ambiente (PATH)** do seu Windows.

### 📦 Instalação das Dependências Python

Antes de rodar o script, instale as bibliotecas necessárias utilizando o terminal:
```bash
pip install -r requirements.txt
```

---

## 📖 Manual de uso

Ao executar o script, você pode passar os seguintes argumentos para personalizar o seu download:

| Parâmetro | Nome Completo | Descrição | Padrão (Default) |
| :--- | :--- | :--- | :--- |
| `url` | URL do Alvo | Link do vídeo ou da playlist.<br>**⚠ SEMPRE USE ASPAS DUPLAS ""** | *Obrigatório* |
| `-r` | `--resolution` | Define a resolução máxima do vídeo (ex: 1080p, 720p, 480p). | `1080` |
| `-o` | `--output_path` | Nome da pasta onde o arquivo será salvo.<br>*(Não utilize espaços no nome!)* | Youtube_Downloads |
| `-a` | `--audio_only` | Flag que ativa o modo económico. Baixa apenas o áudio e converte em MP3. | *Desativado* |

---

👥 Desenvolvedores
Sinta-se à vontade para entrar em contato ou pull requests para melhorias!

@Marcos Xavier</br>
📧 Email: sis.marcosxavier@gmail.com</br>
🐙 GitHub: @marcosxavierdev</br>
@Brenno m4lp4rt1d0</br>
📧 Email: sbrennopqd@gmail.com</br>
🐙 GitHub: @M4lp4rt1d0-mir</br>

🔧 Versão Atual do Projeto: 1.4.6