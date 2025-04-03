# DeGhiblify

A Streamlit application that transforms Ghibli-style anime characters into realistic human portraits using OpenAI's API.

## Features

- Upload any Ghibli-style anime character image
- Transform it into a realistic human portrait
- Download the result

## How It Works

The app uses a two-step AI process:
1. GPT-4 Vision analyzes the anime character and creates a detailed description
2. DALL-E 3 generates a photorealistic human based on that description

## Project Structure

```
DeGhiblify
├── app.py                # Main entry point for the Streamlit application
├── src                   # Source code for the application
│   ├── openai_client.py  # Manages interactions with the OpenAI API
│   ├── image_processor.py # Handles image processing tasks
│   └── utils.py          # Utility functions for the application
├── config                # Configuration settings
│   └── settings.py       # Contains API keys and other settings
├── .env.example          # Template for environment variables
├── .gitignore            # Specifies files to ignore in Git
├── requirements.txt      # Lists project dependencies
└── README.md             # Documentation for the project
```

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/harekrishnarai/DeGhiblify.git
   cd DeGhiblify
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up your OpenAI API key:
   - Copy `.env.example` to `.env` and add your API key
   - Or enter it directly in the app when prompted

## Usage

Run the Streamlit app:
```
streamlit run app.py
```

Then open your browser and go to `http://localhost:8501` to use the application.

## Requirements

- Python 3.8+
- OpenAI API key with access to GPT-4 Vision and DALL-E 3

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.