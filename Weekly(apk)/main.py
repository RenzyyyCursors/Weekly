__version__ = "1.0.0"

import json
import os
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import BooleanProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import (
    Screen,
    ScreenManager,
    SlideTransition,
)
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput


class TaskRow(BoxLayout):
    def __init__(self, app, day, index, task, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(48),
            spacing=dp(8),
            padding=(dp(4), dp(4)),
            **kwargs
        )

        self.app = app
        self.day = day
        self.index = index

        checkbox = CheckBox(
            size_hint_x=None,
            width=dp(40),
            active=task["completed"]
        )

        checkbox.bind(
            active=self.on_checkbox_changed
        )

        self.add_widget(checkbox)

        self.label = Label(
            text=task["text"],
            halign="left",
            valign="middle",
            color=(0.95, 0.95, 0.97, 1),
            font_size=dp(14)
        )

        self.label.bind(
            size=lambda instance, value:
            setattr(instance, "text_size", (value[0], None))
        )

        self.add_widget(self.label)

        delete_button = Button(
            text="×",
            size_hint_x=None,
            width=dp(40),
            background_normal="",
            background_color=(0.8, 0.15, 0.15, 1),
            color=(1, 1, 1, 1),
            font_size=dp(20)
        )

        delete_button.bind(
            on_release=self.delete_task
        )

        self.add_widget(delete_button)

        self.update_visual(task["completed"])

    def on_checkbox_changed(self, checkbox, value):
        self.app.tasks[self.day][self.index]["completed"] = value
        self.app.save_tasks()
        self.update_visual(value)

        self.app.update_day(self.day)

    def update_visual(self, completed):
        if completed:
            self.label.color = (0.45, 0.45, 0.47, 1)
        else:
            self.label.color = (0.95, 0.95, 0.97, 1)

    def delete_task(self, *_):
        self.app.delete_task(
            self.day,
            self.index
        )


class DayCard(BoxLayout):
    def __init__(self, app, day, **kwargs):
        super().__init__(
            orientation="vertical",
            spacing=dp(8),
            padding=dp(10),
            **kwargs
        )

        self.app = app
        self.day = day

        # Day title
        self.title = Label(
            text=day,
            size_hint_y=None,
            height=dp(42),
            font_size=dp(21),
            bold=True,
            color=(1, 0.84, 0.1, 1)
        )

        self.add_widget(self.title)

        # Task counter
        self.counter = Label(
            text="0 / 0",
            size_hint_y=None,
            height=dp(24),
            font_size=dp(12),
            color=(0.55, 0.55, 0.58, 1)
        )

        self.add_widget(self.counter)

        # Scrollable tasks
        scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True
        )

        self.task_container = GridLayout(
            cols=1,
            spacing=dp(4),
            size_hint_y=None
        )

        self.task_container.bind(
            minimum_height=self.task_container.setter(
                "height"
            )
        )

        scroll.add_widget(self.task_container)

        self.add_widget(scroll)

        # Add task input
        bottom = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(48),
            spacing=dp(6)
        )

        self.input = TextInput(
            hint_text="Add a task...",
            multiline=False,
            size_hint_x=1,
            font_size=dp(14),
            padding=(dp(10), dp(12)),
            background_normal="",
            background_color=(0.07, 0.07, 0.08, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 0.84, 0.1, 1)
        )

        self.input.bind(
            on_text_validate=self.add_task
        )

        bottom.add_widget(self.input)

        add_button = Button(
            text="+",
            size_hint_x=None,
            width=dp(48),
            background_normal="",
            background_color=(1, 0.84, 0.1, 1),
            color=(0, 0, 0, 1),
            font_size=dp(22),
            bold=True
        )

        add_button.bind(
            on_release=self.add_task
        )

        bottom.add_widget(add_button)

        self.add_widget(bottom)

        self.refresh()

    def add_task(self, *_):
        text = self.input.text.strip()

        if not text:
            return

        self.app.add_task(
            self.day,
            text
        )

        self.input.text = ""

    def refresh(self):
        self.task_container.clear_widgets()

        tasks = self.app.tasks.get(
            self.day,
            []
        )

        completed = 0

        for index, task in enumerate(tasks):
            if task["completed"]:
                completed += 1

            self.task_container.add_widget(
                TaskRow(
                    self.app,
                    self.day,
                    index,
                    task
                )
            )

        self.counter.text = (
            f"{completed} / {len(tasks)}"
        )


class DayScreen(Screen):
    def __init__(self, app, days, **kwargs):
        super().__init__(**kwargs)

        self.app = app
        self.days = days

        root = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=dp(8)
        )

        self.cards = BoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=1
        )

        for day in days:
            card = DayCard(
                app,
                day,
                size_hint_x=1
            )

            self.cards.add_widget(card)

        root.add_widget(self.cards)

        navigation = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(48),
            spacing=dp(8)
        )

        previous = Button(
            text="‹ Previous",
            background_normal="",
            background_color=(0.12, 0.12, 0.13, 1),
            color=(1, 1, 1, 1)
        )

        previous.bind(
            on_release=lambda *_:
            self.app.previous_screen()
        )

        navigation.add_widget(previous)

        self.page_label = Label(
            text="",
            font_size=dp(13),
            color=(0.55, 0.55, 0.58, 1)
        )

        navigation.add_widget(
            self.page_label
        )

        next_button = Button(
            text="Next ›",
            background_normal="",
            background_color=(0.12, 0.12, 0.13, 1),
            color=(1, 1, 1, 1)
        )

        next_button.bind(
            on_release=lambda *_:
            self.app.next_screen()
        )

        navigation.add_widget(next_button)

        root.add_widget(navigation)

        self.add_widget(root)

    def refresh(self):
        for card in self.cards.children:
            card.refresh()


class MainScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)

        self.app = app

        root = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=dp(8)
        )

        # Header
        header = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(65),
            spacing=dp(8)
        )

        title_box = BoxLayout(
            orientation="vertical"
        )

        title = Label(
            text="WEEKLY",
            halign="left",
            valign="bottom",
            font_size=dp(25),
            bold=True,
            color=(1, 1, 1, 1)
        )

        title.bind(
            size=lambda instance, value:
            setattr(instance, "text_size", value)
        )

        subtitle = Label(
            text="Stay on top of your week",
            halign="left",
            valign="top",
            font_size=dp(11),
            color=(0.5, 0.5, 0.53, 1)
        )

        subtitle.bind(
            size=lambda instance, value:
            setattr(instance, "text_size", value)
        )

        title_box.add_widget(title)
        title_box.add_widget(subtitle)

        header.add_widget(title_box)

        reset_button = Button(
            text="↻ Reset Week",
            size_hint_x=None,
            width=dp(115),
            background_normal="",
            background_color=(0.13, 0.13, 0.14, 1),
            color=(1, 0.84, 0.1, 1),
            font_size=dp(12)
        )

        reset_button.bind(
            on_release=lambda *_:
            self.app.confirm_reset_week()
        )

        header.add_widget(reset_button)

        fields_button = Button(
            text="⌫ Reset Fields",
            size_hint_x=None,
            width=dp(115),
            background_normal="",
            background_color=(0.16, 0.06, 0.06, 1),
            color=(1, 0.27, 0.23, 1),
            font_size=dp(12)
        )

        fields_button.bind(
            on_release=lambda *_:
            self.app.confirm_reset_fields()
        )

        header.add_widget(fields_button)

        root.add_widget(header)

        # Week information
        week_label = Label(
            text="",
            size_hint_y=None,
            height=dp(28),
            font_size=dp(12),
            color=(0.5, 0.5, 0.53, 1)
        )

        self.week_label = week_label

        root.add_widget(week_label)

        # Screens
        self.screen_manager = ScreenManager(
            transition=SlideTransition(
                duration=0.2
            )
        )

        self.page_screens = []

        groups = [
            ["Sunday", "Monday", "Tuesday"],
            ["Wednesday", "Thursday", "Friday"],
            ["Saturday"]
        ]

        for index, days in enumerate(groups):
            screen = DayScreen(
                app,
                days,
                name=f"page_{index}"
            )

            self.page_screens.append(screen)
            self.screen_manager.add_widget(screen)

        root.add_widget(
            self.screen_manager
        )

        self.add_widget(root)

    def refresh(self):
        week = datetime.now().isocalendar().week

        self.week_label.text = (
            f"Week {week}  •  "
            f"{datetime.now().strftime('%d %B %Y')}"
        )

        for screen in self.page_screens:
            screen.refresh()

        self.update_page_label()

    def update_page_label(self):
        current = self.screen_manager.current

        number = (
            self.page_screens.index(
                self.screen_manager.get_screen(current)
            ) + 1
        )

        self.page_screens[
            number - 1
        ].page_label.text = (
            f"Page {number} / 3"
        )


class WeeklyTodoApp(App):

    BG = (0.02, 0.02, 0.025, 1)

    DAYS = [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday"
    ]

    def build(self):

        Window.clearcolor = self.BG

        self.tasks = {
            day: []
            for day in self.DAYS
        }

        self.data_file = os.path.join(
            self.user_data_dir,
            "tasks.json"
        )

        self.load_tasks()

        self.main_screen = MainScreen(
            self,
            name="main"
        )

        self.sm = ScreenManager()

        self.sm.add_widget(
            self.main_screen
        )

        self.sm.current = "main"

        # Check automatic weekly reset periodically.
        Clock.schedule_interval(
            self.check_automatic_reset,
            30
        )

        self.check_automatic_reset()

        return self.sm

    # --------------------------------------------------
    # STORAGE
    # --------------------------------------------------

    def load_tasks(self):

        try:
            if not os.path.exists(
                self.data_file
            ):
                return

            with open(
                self.data_file,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            if not isinstance(data, dict):
                return

            for day in self.DAYS:

                loaded = data.get(
                    day,
                    []
                )

                if not isinstance(
                    loaded,
                    list
                ):
                    continue

                cleaned = []

                for task in loaded:

                    if not isinstance(
                        task,
                        dict
                    ):
                        continue

                    text = str(
                        task.get(
                            "text",
                            ""
                        )
                    ).strip()

                    if not text:
                        continue

                    cleaned.append(
                        {
                            "text": text,
                            "completed": bool(
                                task.get(
                                    "completed",
                                    False
                                )
                            )
                        }
                    )

                self.tasks[day] = cleaned

        except (
            OSError,
            json.JSONDecodeError,
            TypeError,
            ValueError
        ):
            self.tasks = {
                day: []
                for day in self.DAYS
            }

    def save_tasks(self):

        os.makedirs(
            os.path.dirname(
                self.data_file
            ),
            exist_ok=True
        )

        temp_file = (
            self.data_file + ".tmp"
        )

        try:

            with open(
                temp_file,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    self.tasks,
                    file,
                    indent=2,
                    ensure_ascii=False
                )

            os.replace(
                temp_file,
                self.data_file
            )

        except OSError:
            try:
                if os.path.exists(
                    temp_file
                ):
                    os.remove(temp_file)
            except OSError:
                pass

    # --------------------------------------------------
    # TASKS
    # --------------------------------------------------

    def add_task(
        self,
        day,
        text
    ):

        self.tasks[day].append(
            {
                "text": text,
                "completed": False
            }
        )

        self.save_tasks()
        self.update_day(day)

    def delete_task(
        self,
        day,
        index
    ):

        if (
            day not in self.tasks
            or index < 0
            or index >= len(
                self.tasks[day]
            )
        ):
            return

        del self.tasks[day][index]

        self.save_tasks()
        self.update_day(day)

    def update_day(self, day):

        for screen in (
            self.main_screen.page_screens
        ):

            if day in screen.days:

                screen.refresh()
                break

    def refresh_all(self):

        self.main_screen.refresh()

    # --------------------------------------------------
    # RESET WEEK
    # --------------------------------------------------

    def confirm_reset_week(self):

        content = BoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=dp(15)
        )

        message = Label(
            text=(
                "Are you sure you want to reset "
                "this week?\n\n"
                "All completed tasks will be "
                "unchecked.\n"
                "Your task fields will stay."
            ),
            halign="center",
            valign="middle"
        )

        message.bind(
            size=lambda instance, value:
            setattr(
                instance,
                "text_size",
                value
            )
        )

        content.add_widget(message)

        buttons = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(45),
            spacing=dp(8)
        )

        cancel = Button(
            text="Cancel"
        )

        reset = Button(
            text="Reset",
            background_normal="",
            background_color=(
                1,
                0.84,
                0.1,
                1
            ),
            color=(0, 0, 0, 1)
        )

        buttons.add_widget(cancel)
        buttons.add_widget(reset)

        content.add_widget(buttons)

        popup = Popup(
            title="Reset Week",
            content=content,
            size_hint=(0.9, None),
            height=dp(260),
            auto_dismiss=False
        )

        cancel.bind(
            on_release=popup.dismiss
        )

        reset.bind(
            on_release=lambda *_:
            self.reset_week(popup)
        )

        popup.open()

    def reset_week(self, popup):

        for day in self.DAYS:

            for task in self.tasks[day]:
                task["completed"] = False

        self.save_tasks()
        self.refresh_all()

        popup.dismiss()

    # --------------------------------------------------
    # RESET FIELDS
    # --------------------------------------------------

    def confirm_reset_fields(self):

        content = BoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=dp(15)
        )

        message = Label(
            text=(
                "Are you sure you want to delete "
                "all fields?\n\n"
                "Every task from every day "
                "will be removed."
            ),
            halign="center",
            valign="middle"
        )

        message.bind(
            size=lambda instance, value:
            setattr(
                instance,
                "text_size",
                value
            )
        )

        content.add_widget(message)

        buttons = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(45),
            spacing=dp(8)
        )

        cancel = Button(
            text="Cancel"
        )

        delete = Button(
            text="Delete All",
            background_normal="",
            background_color=(
                0.8,
                0.15,
                0.15,
                1
            )
        )

        buttons.add_widget(cancel)
        buttons.add_widget(delete)

        content.add_widget(buttons)

        popup = Popup(
            title="Reset Fields",
            content=content,
            size_hint=(0.9, None),
            height=dp(250),
            auto_dismiss=False
        )

        cancel.bind(
            on_release=popup.dismiss
        )

        delete.bind(
            on_release=lambda *_:
            self.reset_fields(popup)
        )

        popup.open()

    def reset_fields(self, popup):

        self.tasks = {
            day: []
            for day in self.DAYS
        }

        self.save_tasks()
        self.refresh_all()

        popup.dismiss()

    # --------------------------------------------------
    # NAVIGATION
    # --------------------------------------------------

    def current_page(self):

        current = (
            self.main_screen
            .screen_manager.current
        )

        return int(
            current.split("_")[1]
        )

    def next_screen(self):

        current = self.current_page()

        if current >= 2:
            return

        self.main_screen.screen_manager.transition = (
            SlideTransition(
                direction="left",
                duration=0.2
            )
        )

        self.main_screen.screen_manager.current = (
            f"page_{current + 1}"
        )

        self.main_screen.update_page_label()

    def previous_screen(self):

        current = self.current_page()

        if current <= 0:
            return

        self.main_screen.screen_manager.transition = (
            SlideTransition(
                direction="right",
                duration=0.2
            )
        )

        self.main_screen.screen_manager.current = (
            f"page_{current - 1}"
        )

        self.main_screen.update_page_label()

    # --------------------------------------------------
    # AUTOMATIC WEEKLY RESET
    # --------------------------------------------------

    def check_automatic_reset(self, *_):

        now = datetime.now()

        # Python weekday:
        # Monday = 0
        # Sunday = 6
        if now.weekday() != 6:
            return

        today = now.strftime(
            "%Y-%m-%d"
        )

        reset_file = os.path.join(
            self.user_data_dir,
            ".last_reset"
        )

        try:

            if os.path.exists(
                reset_file
            ):

                with open(
                    reset_file,
                    "r",
                    encoding="utf-8"
                ) as file:

                    last_reset = (
                        file.read().strip()
                    )

                if last_reset == today:
                    return

            # Sunday = reset everything.
            self.tasks = {
                day: []
                for day in self.DAYS
            }

            self.save_tasks()

            os.makedirs(
                os.path.dirname(
                    reset_file
                ),
                exist_ok=True
            )

            with open(
                reset_file,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(today)

            self.refresh_all()

        except OSError:
            pass


if __name__ == "__main__":
    WeeklyTodoApp().run()