# FunderCal - Discord Bot for FunderPro Calendar Events

A Discord bot that fetches economic calendar events from FunderPro for specific currency pairs and time periods.

## Features

- Fetch economic calendar events for any currency pair (e.g., XAU/USD, EUR/USD)
- Filter events by time period (next 2 days, 7 days, etc.)
- Displays events with impact level, country, date, time, and status
- Discord integration with easy-to-use commands

## Prerequisites

- Python 3.8 or higher
- Chrome browser installed
- FunderPro account
- Discord bot token

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Anthony-Dominguez/FunderCal.git
   cd FunderCal
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   - Copy `.env.example` to `.env`
   - Fill in your credentials:
     ```
     FUNDERPRO_USERNAME=your_email@example.com
     FUNDERPRO_PASSWORD=your_password
     DISCORD_TOKEN=your_discord_bot_token
     ```

## Discord Bot Setup

1. **Create a Discord Application:**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Click "New Application" and give it a name
   - Go to "Bot" section and click "Add Bot"
   - Copy the token and add it to your `.env` file

2. **Invite Bot to Server:**
   - Go to "OAuth2" > "URL Generator"
   - Select "bot" scope and "Send Messages" permission
   - Use the generated URL to invite the bot to your server

## Usage

1. **Start the bot:**
   ```bash
   python app.py
   ```

2. **Use Discord commands:**
   - `!calendar <days> <currency_pair>` - Fetch calendar events
   - `!ping` - Test if bot is responsive

   **Examples:**
   - `!calendar 2 XAU/USD` - Get XAU/USD events for next 2 days
   - `!calendar 7 EUR/USD` - Get EUR/USD events for next 7 days

## Command Format

```
!calendar [number_of_days] [currency_pair]
```

- `number_of_days`: How many days ahead to fetch events (e.g., 2, 7)
- `currency_pair`: The trading pair to analyze (e.g., XAU/USD, EUR/USD, GBP/USD)

## Example Output

The bot will display events in a formatted message showing:
- Event name and description
- Impact level (High, Medium, Low)
- Country/Region
- Date and time
- Current status
- Additional information if available

## Dependencies

- `selenium` - Web scraping automation
- `webdriver-manager` - Automatic Chrome driver management
- `beautifulsoup4` - HTML parsing
- `python-dotenv` - Environment variable management
- `discord.py` - Discord bot framework

## Troubleshooting

- **"Currency pair not found"**: Make sure you're using the exact format as shown on FunderPro (e.g., XAU/USD, not XAUUSD)
- **Login issues**: Verify your FunderPro credentials in the `.env` file
- **Bot not responding**: Check that the Discord token is correct and the bot has proper permissions

## Security Note

- Never commit your `.env` file to version control
- Keep your credentials secure and don't share them
- The bot runs headless Chrome for web scraping

## License

This project is for educational purposes. Please respect FunderPro's terms of service when using this bot.# FunderCal
