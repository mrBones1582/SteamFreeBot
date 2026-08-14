import os
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch

from app import main


class FakeSmtp:
    messages = []

    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def starttls(self, **kwargs):
        pass

    def login(self, user, password):
        pass

    def send_message(self, message):
        self.messages.append(message)


class RecipientTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        main.DB = Path(self.temp.name) / 'test.db'
        FakeSmtp.messages = []
        os.environ['MAIL_TO'] = 'legacy@example.com'
        os.environ['SMTP_HOST'] = 'smtp.example.com'
        os.environ['MAIL_FROM'] = 'sender@example.com'
        os.environ['SMTP_STARTTLS'] = 'false'
        main.conn().close()

    def tearDown(self):
        self.temp.cleanup()

    def test_legacy_mail_to_is_seeded_only_once(self):
        main.seed_initial_recipient()
        main.seed_initial_recipient()
        with main.conn() as database:
            count = database.execute('SELECT COUNT(*) FROM mail_recipients').fetchone()[0]
        self.assertEqual(count, 1)

    def test_expired_recipient_is_stopped_and_can_be_resumed(self):
        yesterday = (main.local_today() - timedelta(days=1)).isoformat()
        created = main.create_recipient(main.RecipientPayload(email='expired@example.com', delivery_end_date=yesterday))
        self.assertEqual(created['stopped'], 1)

        resumed = main.toggle_recipient(created['id'])
        self.assertEqual(resumed['stopped'], 0)
        self.assertIsNone(resumed['delivery_end_date'])


    def test_daily_mail_is_skipped_when_no_free_promotions_exist(self):
        main.seed_initial_recipient()
        with patch.object(main, 'send_mail') as mocked_send:
            ok, result = main.daily_mail()

        self.assertFalse(ok)
        self.assertEqual(result, 'No active Free to Keep promotions; daily mail skipped')
        mocked_send.assert_not_called()

    def test_daily_mail_is_sent_when_free_promotion_exists(self):
        main.seed_initial_recipient()
        now = main.datetime.now(main.timezone.utc).isoformat()
        with main.conn() as database:
            database.execute(
                """INSERT INTO promotions(
                    appid,title,url,original_price,current_price,current_price_value,
                    discount_percent,japanese_supported,genre_keys,genre_names,header_image,
                    first_seen,last_seen,active,notified
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    999999, 'Free Test', 'https://store.steampowered.com/app/999999/',
                    '¥1,000', '無料', 0, 100, 1, 'RPG', 'RPG', '',
                    now, now, 1, 0,
                ),
            )
            database.commit()

        with patch.object(main, 'send_mail', return_value=(True, 'sent')) as mocked_send:
            ok, result = main.daily_mail()

        self.assertTrue(ok)
        self.assertEqual(result, 'sent')
        mocked_send.assert_called_once()
        subject, body = mocked_send.call_args.args
        self.assertIn('期間限定無料 1件', subject)
        self.assertIn('Free Test', body)

    def test_mail_is_sent_individually_to_active_recipients(self):
        main.create_recipient(main.RecipientPayload(email='one@example.com'))
        main.create_recipient(main.RecipientPayload(email='two@example.com'))
        stopped = main.create_recipient(main.RecipientPayload(email='stop@example.com'))
        main.toggle_recipient(stopped['id'])

        with patch.object(main.smtplib, 'SMTP', FakeSmtp):
            ok, result = main.send_mail('subject', 'body')

        self.assertTrue(ok)
        self.assertEqual(result, 'sent to 2 recipient(s)')
        self.assertEqual({message['To'] for message in FakeSmtp.messages}, {'one@example.com', 'two@example.com'})


if __name__ == '__main__':
    unittest.main()
