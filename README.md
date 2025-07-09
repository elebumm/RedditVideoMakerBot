# Reddit Video Maker Bot 🎥

![Logo Screenshot](./assets/redditVideoMaker.png)

> **Automate viral Reddit video creation with zero video editing skills required!**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Discord](https://img.shields.io/discord/980117851434864690?color=7289DA&label=Discord&logo=discord&logoColor=white)](https://discord.gg/qfQSx45xCV)
[![Documentation](https://img.shields.io/badge/Documentation-Available-brightgreen)](https://reddit-video-maker-bot.netlify.app/)

All done WITHOUT video editing or asset compiling. Just pure ✨**programming magic**✨.

Created by Lewis Menelaws & [TMRRW](https://tmrrwinc.ca)

<a target="_blank" href="https://tmrrwinc.ca">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://user-images.githubusercontent.com/6053155/170528535-e274dc0b-7972-4b27-af22-637f8c370133.png">
  <source media="(prefers-color-scheme: light)" srcset="https://user-images.githubusercontent.com/6053155/170528582-cb6671e7-5a2f-4bd4-a048-0e6cfa54f0f7.png">
  <img src="https://user-images.githubusercontent.com/6053155/170528582-cb6671e7-5a2f-4bd4-a048-0e6cfa54f0f7.png" width="350">
</picture>
</a>

## 🌟 Features

### 🎬 **Video Creation**
- **Automated Reddit scraping** - Pull hot posts from any subreddit
- **Text-to-speech generation** - Convert Reddit posts and comments to natural speech
- **Dynamic video assembly** - Combine background footage with Reddit content
- **Custom thumbnails** - Auto-generate eye-catching thumbnails
- **Multiple output formats** - Create videos optimized for different platforms

### 🎙️ **Text-to-Speech Providers**
- **TikTok TTS** - 50+ voices including Disney characters, multiple languages
- **AWS Polly** - Premium neural voices with natural intonation
- **Google Translate** - Free multilingual TTS
- **Streamlabs Polly** - Streamer-friendly voice options
- **ElevenLabs** - AI-powered ultra-realistic voices
- **System TTS** - Use your operating system's built-in voices

### 🎨 **Customization Options**
- **Background videos** - Minecraft, GTA, nature scenes, or add your own
- **Background music** - Add ambient music to enhance viewer experience
- **Voice settings** - Random voice selection or consistent narrator
- **Visual effects** - Opacity, transitions, and comment styling
- **Content filtering** - NSFW filtering and content moderation
- **Story mode** - Include the full Reddit post text

### 🖥️ **User Interface**
- **Web-based GUI** - Easy-to-use browser interface at `localhost:4000`
- **Command-line interface** - Full control via terminal
- **Settings management** - Centralized configuration system
- **Background manager** - Add/remove background videos easily

### 🔧 **Advanced Features**
- **Duplicate detection** - Prevents creating videos from already processed posts
- **Multi-language support** - Create videos in various languages
- **Batch processing** - Generate multiple videos automatically
- **Custom Reddit threads** - Target specific posts by ID
- **Light/Dark mode** - Theme support for better user experience

## 🎯 Demo & Examples

### Video Explainer
[![Tutorial Video](https://user-images.githubusercontent.com/6053155/173631669-1d1b14ad-c478-4010-b57d-d79592a789f2.png)](https://www.youtube.com/watch?v=3gjcY_00U1w)

### Sample Output
https://user-images.githubusercontent.com/66544866/173453972-6526e4e6-c6ef-41c5-ab40-5d275e724e7c.mp4

## 🚀 Quick Start

### Prerequisites
- **Python 3.10 or 3.11** (Required)
- **FFmpeg** (Auto-installed)
- **Reddit API Access** (Free)

### Installation

#### 🐍 **Method 1: Standard Installation**
```bash
# Clone the repository
git clone https://github.com/elebumm/RedditVideoMakerBot.git
cd RedditVideoMakerBot

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
python -m playwright install
python -m playwright install-deps
```

#### 🔥 **Method 2: Auto-Installer (Linux/macOS)** *Experimental!!!*
```bash
bash <(curl -sL https://raw.githubusercontent.com/elebumm/RedditVideoMakerBot/master/install.sh)
```

### First Run
1. **Start the bot:**
   ```bash
   python main.py
   ```

2. **Reddit API Setup:**
   - Visit [Reddit Apps](https://www.reddit.com/prefs/apps)
   - Create a new "script" application
   - Use any redirect URL (e.g., `https://jasoncameron.dev`)
   - The bot will guide you through the configuration

3. **Configure settings:**
   - Follow the interactive prompts
   - Or use the web GUI at `http://localhost:4000`

4. **Generate your first video!** 🎉

## 🎛️ Configuration

### Web Interface

<!-- ![Web Interface Screenshot](./assets/redditVideoMakerInterface.png) {Please add this} -->

Launch the GUI for easy configuration:
```bash
python GUI.py
```
Navigate to `http://localhost:4000` to access:
- **Settings Panel** - Configure all bot options
- **Background Manager** - Add/remove background videos
- **Video Dashboard** - View generated content

### Command Line
Edit `config.toml` directly or delete specific lines to reconfigure:
```toml
[reddit]
[reddit.thread]
subreddit = "AskReddit"
post_id = ""  # Leave empty for random posts
max_comment_length = 500

[settings]
times_to_run = 1
opacity = 0.9
transition = 0.2
```

## 🎵 Text-to-Speech Configuration

### TikTok TTS (Default)
```toml
[settings.tts]
voice_choice = "tiktok"
tiktok_voice = "en_us_001"  # Female voice
tiktok_sessionid = "your_session_id"  # Required
```

**Available voices:**
- **Disney**: Ghost Face, Chewbacca, C3PO, Stitch, Stormtrooper
- **English**: Multiple male/female variants
- **International**: French, German, Spanish, Japanese, Korean, and more

### AWS Polly
```toml
[settings.tts]
voice_choice = "awspolly"
aws_polly_voice = "Joanna"  # Neural voice
```

### ElevenLabs (Premium)
```toml
[settings.tts]
voice_choice = "elevenlabs"
elevenlabs_api_key = "your_api_key"
elevenlabs_voice_name = "Rachel"
```

## 🎬 Background Customization

### Add Custom Backgrounds
1. **Via Web Interface:**
   - Go to `http://localhost:4000/backgrounds`
   - Click "Add background video"
   - Provide YouTube URL and details

2. **Via JSON Configuration:**
   ```json
   {
     "my_background": [
       "https://youtube.com/watch?v=VIDEO_ID",
       "background.mp4",
       "Creator Name",
       "center"
     ]
   }
   ```

### Built-in Backgrounds
- **Minecraft gameplay** - Classic parkour and building
- **GTA V gameplay** - Driving and action sequences  
- **Nature scenes** - Relaxing landscapes and timelapses
- **Abstract animations** - Colorful motion graphics

## 🛠️ Advanced Usage

### Batch Processing
```bash
# Generate 5 videos from r/AskReddit
python main.py --times 5 --subreddit AskReddit
```

### Target Specific Posts
```bash
# Create video from specific Reddit post
python main.py --post-id abc123xyz
```

### Story Mode
Enable story mode to include the full Reddit post text:
```toml
[settings]
storymode = true
storymodemethod = 0  # 0 = full post, 1 = sentence by sentence
```

## 🔊 Audio Features

### Background Music
- **Automatic audio extraction** from background videos
- **Volume control** - Adjust music vs. speech balance
- **Audio synchronization** - Perfect timing with visual content

### Voice Settings
- **Random voice selection** - Different voice per video
- **Consistent narrator** - Same voice throughout
- **Silence duration** - Control pauses between comments
- **Voice translation** - Multi-language support

## 📁 Project Structure

```
RedditVideoMakerBot/
├── main.py                 # Main application entry point
├── GUI.py                  # Web interface server
├── config.toml            # Configuration file
├── requirements.txt       # Python dependencies
├── TTS/                   # Text-to-speech engines
│   ├── TikTok.py         # TikTok TTS implementation
│   ├── aws_polly.py      # AWS Polly integration
│   ├── elevenlabs.py     # ElevenLabs API
│   └── ...
├── video_creation/        # Video generation modules
│   ├── final_video.py    # Video assembly
│   ├── background.py     # Background processing
│   └── voices.py         # Voice management
├── reddit/               # Reddit API integration
├── utils/                # Utility functions
├── assets/               # Static assets
└── results/              # Generated videos
```

## 🤝 Contributing

We welcome contributions! See our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Fork and clone the repository
git clone https://github.com/your-username/RedditVideoMakerBot.git

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt  # If available

# Run tests
python -m pytest
```
### Current Roadmap

- [ ] Creating better documentation and adding a command line interface.
- [x] Allowing the user to choose background music for their videos.
- [x] Allowing users to choose a reddit thread instead of being randomized.
- [x] Allowing users to choose a background that is picked instead of the Minecraft one.
- [x] Allowing users to choose between any subreddit.
- [x] Allowing users to change voice.
- [x] Checks if a video has already been created
- [x] Light and Dark modes
- [x] NSFW post filter

## 📊 Performance & Optimization

### System Requirements
- **CPU**: Multi-core recommended for faster processing
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space for temporary files
- **Network**: Stable internet for Reddit API and TTS services

### Performance Tips
- **Use SSD storage** for faster video rendering
- **Close unnecessary applications** during processing
- **Batch process** multiple videos for efficiency
- **Configure video quality** based on target platform

## 🐛 Troubleshooting

### Common Issues

**Python Version Error:**
```bash
# Ensure you're using Python 3.10 or 3.11
python --version
```

**TikTok TTS Issues:**
- Ensure `tiktok_sessionid` is properly configured
- Check the [documentation](https://reddit-video-maker-bot.netlify.app/) for session ID extraction

**FFmpeg Not Found:**
```bash
# The bot will attempt to install FFmpeg automatically
# If this fails, install manually based on your OS
```

**Reddit API Errors:**
- Verify your Reddit app credentials
- Check API rate limits
- Ensure subreddit exists and is accessible

### Getting Help
- 📚 **Documentation**: [reddit-video-maker-bot.netlify.app](https://reddit-video-maker-bot.netlify.app/)
- 💬 **Discord**: [Join our community](https://discord.gg/qfQSx45xCV)
- 🐞 **Issues**: [GitHub Issues](https://github.com/elebumm/RedditVideoMakerBot/issues)

## 🎨 Customization Examples

### Create Gaming Content
```toml
[reddit.thread]
subreddit = "gaming"
post_id = ""

[settings]
background_choice = "minecraft-parkour"
opacity = 0.8
```

### Educational Content
```toml
[reddit.thread]
subreddit = "todayilearned"

[settings.tts]
voice_choice = "awspolly"
aws_polly_voice = "Matthew"  # Professional male voice
```

### Storytelling Videos
```toml
[reddit.thread]
subreddit = "nosleep"

[settings]
storymode = true
background_choice = "dark-ambiance"
```

## 📈 Analytics & Monitoring

### Video Output Tracking
- **Generated video count** - Track your content creation
- **Processing time** - Monitor performance metrics
- **File sizes** - Optimize for different platforms
- **Error logging** - Debug issues efficiently

### Quality Metrics
- **Audio quality** - Ensure clear speech
- **Video resolution** - Optimize for target platforms
- **Render speed** - Track processing efficiency

## 🔒 Privacy & Legal

### Data Handling
- **Local processing** - All video generation happens on your machine
- **No data collection** - The bot doesn't store or transmit your content
- **Reddit API compliance** - Respects Reddit's terms of service
- **Rate limiting** - Prevents API abuse

### Content Guidelines
- **Manual upload** - You control what gets published
- **Content filtering** - Built-in NSFW detection
- **Fair use** - Respect intellectual property rights
- **Platform guidelines** - Follow TikTok, YouTube, Instagram rules

## 🌍 Community

### Discord Server
Join our community for:
- **Technical support** - Get help with setup and configuration
- **Feature requests** - Suggest new improvements
- **Showcase** - Share your generated content
- **Collaboration** - Connect with other creators

### Contributing Guidelines
- **Code style** - Follow PEP 8 for Python code
- **Testing** - Include tests for new features
- **Documentation** - Update docs for any changes
- **Issue tracking** - Use GitHub Issues for bugs and features

## 📄 License

This project is licensed under the GNU General Public License License - see the [LICENSE](LICENSE) file for details.

### Third-Party Licenses
- **Roboto Fonts** - [Apache License V2](https://www.apache.org/licenses/LICENSE-2.0)
- **Dependencies** - See individual package licenses in `requirements.txt`

## 🙏 Acknowledgments

### Developers and Maintainers

- **Elebumm (Lewis)** - Founder and Lead Developer ([Github](https://github.com/elebumm))
- **Jason Cameron** - Maintainer and Core Contributor ([Github](https://github.com/JasonLovesDoggo))
- **OpenSourceSimon** - Feature Development ([Github](https://github.com/OpenSourceSimon))
- **CallumIO** - UI/UX Improvements ([Github](https://github.com/CallumIO))
- **Verq** - Performance Optimization ([Github](https://github.com/CordlessCoder))
- **LukaHietala** - Feature implementations ([Github](https://github.com/LukaHietala))
- **Freebiell** - Bug fixes and improvements ([Github](https://github.com/FreebieII))
- **Aman Raza** - Code optimization ([Github](https://github.com/electro199))
- **Cyteon** - Documentation improvements ([Github](https://github.com/cyteon))

### Motivation 🤔

These videos on TikTok, YouTube and Instagram get **MILLIONS** of views across all platforms and require very little effort. The only original thing being done is the editing and gathering of all materials...

**...but what if we can automate that process?** 🤔

### Disclaimers 🚨

- **Manual Upload Required** - This bot generates video files that you must upload manually to avoid community guideline issues
- **API Compliance** - Respects Reddit's API terms and rate limits
- **Educational Purpose** - Designed for learning and legitimate content creation

---

<div align="center">

**Made with ❤️**

[⭐ Star on GitHub](https://github.com/elebumm/RedditVideoMakerBot) • [🐛 Report Issues](https://github.com/elebumm/RedditVideoMakerBot/issues) • [💬 Join Discord](https://discord.gg/qfQSx45xCV)

</div>


