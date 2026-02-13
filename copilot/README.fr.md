[English](./README.md) | [한국어](./README.kr.md) | [日本語](./README.jp.md) | [中文](./README.zh.md) | [Français](./README.fr.md)

# AI Web Crawler 🕷️

Outil d'exploration de sites web et de conversion de documents alimenté par LLM.

## Fonctionnalités clés

- ✅ **Prise en charge de plusieurs fournisseurs LLM** : OpenAI (ChatGPT), Anthropic (Claude), Google (Gemini)
- ✅ **Vérification automatique des connexions API** : état de connexion en temps réel pour chaque fournisseur
- ✅ **Chargement dynamique des modèles** : charge automatiquement les derniers modèles disponibles via les API
- ✅ **Intégration des variables d'environnement système** : gestion sécurisée des clés API et chargement automatique
- ✅ **Exploration flexible** : exploration d'une page unique ou d'un site complet
- ✅ **Plusieurs formats de sortie** : Markdown, HTML, texte
- ✅ **Affinage du contenu par IA** : structuration et amélioration du contenu avec les LLM
- ✅ **GUI conviviale** : interface intuitive basée sur Streamlit
- ✅ **Affichage de progression en temps réel** : visualisation de l'avancement de l'exploration
- ✅ **Exécution locale** : entièrement open source, fonctionne uniquement avec des clés API

## Aperçu UI

![AI Web Crawler UI](docs/images/main.png)
![Running](docs/images/run.png)

Grâce à l'interface Streamlit intuitive, vous pouvez démarrer l'exploration immédiatement sans configuration complexe.

### Structure principale de l'écran

1. **Barre latérale (Paramètres)**
   - **État de connexion** : valide automatiquement les clés API chargées depuis les variables d'environnement et affiche des indicateurs type feu tricolore (✅/❌/⚪).
   - **Sélection du fournisseur et du modèle** : choisissez les fournisseurs LLM connectés (OpenAI, Anthropic, Gemini) et les derniers modèles disponibles depuis leurs API.
   - **Options d'exploration** : configurez le mode page unique/site complet, le nombre maximal de pages et les formats de sortie (.md, .html, .txt).

2. **Zone principale (Travail)**
   - **Saisie d'URL** : entrez l'URL du site à explorer.
   - **État d'avancement** : affiche la progression et l'état de la tâche en temps réel.
   - **Résultats et téléchargement** : prévisualisez et téléchargez les résultats après la fin de l'exploration.

## Installation

### 1. Cloner le dépôt
```bash
git clone <repository-url>
cd Copilot
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Installer Playwright (requis par Crawl4AI)
```bash
playwright install
```

### 4. Configurer les variables d'environnement

**Définir les clés API comme variables d'environnement système (recommandé)**

#### macOS / Linux
```bash
# Ajouter à ~/.zshrc (zsh) ou ~/.bashrc (bash)
export OPENAI_API_KEY="sk-your-openai-key-here"
export ANTHROPIC_API_KEY="sk-ant-your-anthropic-key-here"
export GOOGLE_API_KEY="AIza-your-google-key-here"

# Appliquer après enregistrement
source ~/.zshrc  # ou source ~/.bashrc
```

#### Windows

**Méthode 1 : Paramètres système (GUI)**
1. `Control Panel` → `System` → `Advanced system settings`
2. Cliquez sur `Environment Variables`
3. Dans `User variables`, cliquez sur `New`
4. Saisissez les noms et valeurs des variables :
   - `OPENAI_API_KEY` = `your_key_here`
   - `ANTHROPIC_API_KEY` = `your_key_here`
   - `GOOGLE_API_KEY` = `your_key_here`

**Méthode 2 : PowerShell**
```powershell
# Exécuter PowerShell en tant qu'administrateur
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'your_key_here', 'User')
[System.Environment]::SetEnvironmentVariable('ANTHROPIC_API_KEY', 'your_key_here', 'User')
[System.Environment]::SetEnvironmentVariable('GOOGLE_API_KEY', 'your_key_here', 'User')
```

**Méthode 3 : CMD**
```cmd
setx OPENAI_API_KEY "your_key_here"
setx ANTHROPIC_API_KEY "your_key_here"
setx GOOGLE_API_KEY "your_key_here"
```

#### Docker
```bash
docker run -e OPENAI_API_KEY=your_key \
           -e ANTHROPIC_API_KEY=your_key \
           -e GOOGLE_API_KEY=your_key \
           your_image
```

#### Utiliser un fichier `.env` (optionnel)
Au lieu des variables d'environnement système, créez un fichier `.env` dans le répertoire du projet :
```bash
# Créer .env
cp .env.example .env

# Modifier .env
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_API_KEY=your_google_key_here
```

> ⚠️ **Note de sécurité** : ne jamais committer les fichiers `.env` dans Git (déjà inclus dans `.gitignore`)

## Utilisation

### Lancer l'application
```bash
# Activer l'environnement virtuel (première fois uniquement)
source venv/bin/activate  # macOS/Linux
# ou
venv\Scripts\activate  # Windows

# Lancer l'app Streamlit
streamlit run app.py
```

L'application s'ouvre automatiquement dans votre navigateur (généralement http://localhost:8501).

### Étapes
1. **Vérification automatique de connexion** : au démarrage, les clés API sont chargées depuis les variables d'environnement et chaque fournisseur est vérifié
   - ✅ Vert : connecté et disponible
   - ❌ Rouge : échec de connexion (vérifier la clé API)
   - ⚪ Gris : aucune clé API
2. **Choisir le fournisseur LLM** : sélectionnez un fournisseur connecté (saisie manuelle de clé API possible pour les fournisseurs non connectés)
3. **Choisir le modèle** : sélectionnez parmi les derniers modèles disponibles récupérés automatiquement depuis les API
4. **Entrer l'URL** : saisissez l'adresse du site à explorer
5. **Configurer les options d'exploration** :
   - Page unique ou site complet
   - Nombre maximal de pages (mode site complet)
   - Format de sortie
7. **Démarrer l'exploration** : cliquez sur le bouton
8. **Télécharger les résultats** : téléchargez les fichiers de sortie après la fin

## Structure du projet
```
Copilot/
├── ai_web_crawler/
│   ├── models/
│   │   └── llm_providers.py    # LLM integration layer
│   ├── utils/
│   │   ├── crawler.py          # Crawling logic
│   │   └── file_exporter.py    # File export utility
│   └── output/                 # Output directory
├── app.py                      # Streamlit app
├── requirements.txt            # Dependencies
├── .env.example               # Environment variable example
├── .gitignore                 # Git ignored files
├── ENV_SETUP_GUIDE.md         # Detailed environment setup guide
└── README.md                  # Documentation
```

## Stack technique

- **Crawling**: [Crawl4AI](https://github.com/unclecode/crawl4ai) - LLM-friendly web crawler
- **GUI**: [Streamlit](https://streamlit.io/) - Fast and simple web app framework
- **LLM Integration**:
  - OpenAI API (ChatGPT)
  - Anthropic API (Claude)
  - Google Generative AI (Gemini)
- **Output formats**: Markdown, HTML, plain text

## Exemples d'utilisation

### Exemple 1 : Explorer une seule page de documentation
```
URL: https://code.claude.com/docs/ko/overview
Mode: Single page
Output: Markdown
```

### Exemple 2 : Explorer un site de documentation complet
```
URL: https://code.claude.com/docs/ko/overview
Mode: Full site
Max pages: 50
Output: HTML
LLM refinement: ON
```

## Licence

Ce projet est distribué sous licence MIT.

## Contribution

Les contributions sont les bienvenues. N'hésitez pas à ouvrir des issues ou soumettre des PR.

## Références

- [Crawl4AI GitHub](https://github.com/unclecode/crawl4ai)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [OpenAI API](https://platform.openai.com/docs)
- [Anthropic API](https://docs.anthropic.com/)
- [Google Gemini API](https://ai.google.dev/)
