from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock

import threading
import http.server
import socketserver
import os
import sys

PORT = 8080


def get_base_dir():
    """Папка, где искать assets (внутри APK или рядом)."""
    try:
        # Kivy на Android распаковывает ресурсы сюда
        from android.storage import app_storage_path  # noqa
    except Exception:
        pass
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = get_base_dir()
DIRECTORY = os.path.join(BASE_DIR, "assets", "code")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def log_message(self, format, *args):
        pass


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def start_server():
    """Запуск HTTP-сервера в фоне."""
    if not os.path.isdir(DIRECTORY):
        print(f"Ошибка: не найдена папка {DIRECTORY}")
        return
    with ReusableTCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()


def open_browser(url):
    """Открыть браузер на Android через Intent (Pyjnius)."""
    try:
        from jnius import autoclass, cast
        Intent = autoclass('android.content.Intent')
        Uri = autoclass('android.net.Uri')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')

        intent = Intent(Intent.ACTION_VIEW)
        intent.setData(Uri.parse(url))

        current_activity = cast('android.app.Activity', PythonActivity.mActivity)
        current_activity.startActivity(intent)
        return True
    except Exception as e:
        print(f"Не удалось открыть браузер: {e}")
        return False


class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=40, spacing=20, **kwargs)

        self.add_widget(Label(
            text="Презентация запущена!\n\n"
                 "Если браузер не открылся сам —\n"
                 "нажми кнопку ниже.",
            halign='center',
            font_size='18sp'
        ))

        btn = Button(
            text="Открыть презентацию",
            size_hint=(1, 0.3),
            font_size='20sp'
        )
        btn.bind(on_press=self.open_presentation)
        self.add_widget(btn)

    def open_presentation(self, instance):
        open_browser(f"http://localhost:{PORT}/index.html")


class PresentationApp(App):
    def build(self):
        # Запускаем сервер в фоне
        threading.Thread(target=start_server, daemon=True).start()

        # Через 1.5 сек автоматически пытаемся открыть браузер
        Clock.schedule_once(
            lambda dt: open_browser(f"http://localhost:{PORT}/index.html"),
            1.5
        )

        return MainLayout()


if __name__ == '__main__':
    PresentationApp().run()
