# SteamFreeBot

English | [日本語](README.ja.md)

SteamFreeBot is a FastAPI application that collects discounted titles from the Steam Store and provides a web interface for filtering deals of 80% off or more. It can send email notifications for limited-time promotions that are 100% off and currently priced at zero.

## Features

- Periodic collection of discounted Steam Store titles
- English/Japanese interface switcher (English by default)
- Filters for discount rate, price, English or Japanese language support, genre, and game/DLC type
- Compact list and card views
- Email notifications for limited-time free promotions
- Recipient creation, editing, deletion, suspension, and delivery end dates
- Configurable Steam fetch mode, User-Agent, Session Cookie, and fallback behavior
- SQLite persistence

## Run with Docker

1. Clone this repository.
2. Copy `.env.example` to `.env`.
3. Add SMTP settings if email delivery is required.
4. Start the application:

```bash
docker compose up -d --build
```

Open `http://localhost:8000` after the container starts.

The recipient administration page is available at `http://localhost:8000/admin/recipients`.

## Gmail setup

Use a Google app password in `SMTP_PASSWORD`, not your normal Google Account password. Keep secrets in `.env` only and never commit that file.

## Tests

```bash
python -m unittest discover -s tests -v
```

## Security

This public edition does not include user authentication. Add an authenticated reverse proxy, VPN, or another access-control layer before exposing the administration pages to the internet.

Never commit any of the following:

- `.env`
- SQLite databases
- SMTP passwords
- Steam Session Cookies
- Logs or backups

## Notes

- Changes to Steam HTML or API behavior may temporarily break collection.
- This project is not affiliated with Steam or Valve Corporation.
- Review the applicable service terms, rate limits, and email provider policies before use.

## Contributing

Issues and pull requests are welcome. Check that submissions contain no credentials or personal information.

## License

No license has been selected yet. The repository owner should choose an appropriate open-source license before allowing reuse, modification, or redistribution.
