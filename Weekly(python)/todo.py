import customtkinter as ctk
import json
import os
from tkinter import messagebox
from datetime import datetime, timedelta


class WeeklyTodoApp(ctk.CTk):
    """
    Minimal Apple/macOS-inspired weekly To-Do application.

    Layout:
        Sunday      Monday      Tuesday      Wednesday
        Thursday    Friday      Saturday     Week Counter
    """

    DAYS = [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
    ]

    DATA_FILE = "tasks.json"

    # ---------------------------------------------------------------
    # Apple-inspired yellow / black palette
    # ---------------------------------------------------------------

    BG = "#000000"
    CARD = "#111111"
    CARD_HOVER = "#181818"
    INPUT_BG = "#0B0B0B"

    YELLOW = "#FFD60A"
    YELLOW_HOVER = "#E5BD00"

    TEXT = "#F5F5F7"
    SECONDARY = "#86868B"
    BORDER = "#242424"

    RED = "#FF453A"
    RED_HOVER = "#D93630"

    def __init__(self):
        super().__init__()

        # -----------------------------------------------------------
        # Window
        # -----------------------------------------------------------

        self.title("Weekly")
        self.geometry("1250x800")
        self.minsize(850, 600)

        self.configure(fg_color=self.BG)

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")

        # -----------------------------------------------------------
        # Data
        # -----------------------------------------------------------

        self.tasks = {
            day: []
            for day in self.DAYS
        }

        self.entries = {}
        self.task_frames = {}
        self.count_labels = {}

        self.last_reset_week = None

        self.protocol(
            "WM_DELETE_WINDOW",
            self.close_app
        )

        self.load_tasks()
        self.build_interface()
        self.refresh_all()

        # Automatic Sunday reset
        self.schedule_reset()

    # ===============================================================
    # MAIN INTERFACE
    # ===============================================================

    def build_interface(self):
        """Build the complete application."""

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # -----------------------------------------------------------
        # Header
        # -----------------------------------------------------------

        header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=30,
            pady=(25, 15)
        )

        header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header,
            text="Weekly",
            font=ctk.CTkFont(
                size=32,
                weight="bold"
            ),
            text_color=self.TEXT
        )

        title.grid(
            row=0,
            column=0,
            sticky="w"
        )

        subtitle = ctk.CTkLabel(
            header,
            text="Your week, beautifully simple.",
            font=ctk.CTkFont(
                size=13
            ),
            text_color=self.SECONDARY
        )

        subtitle.grid(
            row=1,
            column=0,
            sticky="w",
            pady=(2, 0)
        )

        # -----------------------------------------------------------
        # Header buttons
        # -----------------------------------------------------------

        button_frame = ctk.CTkFrame(
            header,
            fg_color="transparent"
        )

        button_frame.grid(
            row=0,
            column=1,
            rowspan=2,
            sticky="e"
        )

        # -----------------------------------------------------------
        # Reset Week Button
        # Keeps task fields but unchecks all ticks
        # -----------------------------------------------------------

        reset_button = ctk.CTkButton(
            button_frame,
            text="↻  Reset Week",
            width=115,
            height=34,
            corner_radius=9,
            fg_color="transparent",
            hover_color="#1C1C1C",
            border_width=1,
            border_color="#333333",
            text_color=self.YELLOW,
            font=ctk.CTkFont(
                size=12,
                weight="bold"
            ),
            command=self.manual_reset
        )

        reset_button.grid(
            row=0,
            column=0,
            padx=(0, 8)
        )

        # -----------------------------------------------------------
        # Reset Fields Button
        # Deletes all task fields completely
        # -----------------------------------------------------------

        delete_all_button = ctk.CTkButton(
            button_frame,
            text="⌫  Reset Fields",
            width=115,
            height=34,
            corner_radius=9,
            fg_color="transparent",
            hover_color="#2A1717",
            border_width=1,
            border_color="#4A2222",
            text_color=self.RED,
            font=ctk.CTkFont(
                size=12,
                weight="bold"
            ),
            command=self.delete_all_fields
        )

        delete_all_button.grid(
            row=0,
            column=1
        )

        # -----------------------------------------------------------
        # 2 x 4 grid
        # -----------------------------------------------------------

        self.grid_container = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.grid_container.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=25,
            pady=(0, 25)
        )

        for column in range(4):
            self.grid_container.grid_columnconfigure(
                column,
                weight=1,
                uniform="day_columns"
            )

        for row in range(2):
            self.grid_container.grid_rowconfigure(
                row,
                weight=1,
                uniform="day_rows"
            )

        # Create seven days
        for index, day in enumerate(self.DAYS):

            row = index // 4
            column = index % 4

            self.create_day_card(
                day,
                row,
                column
            )

        # Week counter occupies row 2, column 4
        self.create_week_card(
            row=1,
            column=3
        )

    # ===============================================================
    # DAY CARD
    # ===============================================================

    def create_day_card(
        self,
        day,
        row,
        column
    ):
        """Create one day card."""

        card = ctk.CTkFrame(
            self.grid_container,
            fg_color=self.CARD,
            corner_radius=16,
            border_width=1,
            border_color=self.BORDER
        )

        card.grid(
            row=row,
            column=column,
            sticky="nsew",
            padx=6,
            pady=6
        )

        card.grid_columnconfigure(
            0,
            weight=1
        )

        card.grid_rowconfigure(
            1,
            weight=1
        )

        # -----------------------------------------------------------
        # Card header
        # -----------------------------------------------------------

        header = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=16,
            pady=(15, 8)
        )

        header.grid_columnconfigure(
            0,
            weight=1
        )

        day_label = ctk.CTkLabel(
            header,
            text=day,
            font=ctk.CTkFont(
                size=17,
                weight="bold"
            ),
            text_color=self.TEXT
        )

        day_label.grid(
            row=0,
            column=0,
            sticky="w"
        )

        count_label = ctk.CTkLabel(
            header,
            text="0",
            font=ctk.CTkFont(
                size=12
            ),
            text_color=self.SECONDARY
        )

        count_label.grid(
            row=0,
            column=1,
            sticky="e"
        )

        self.count_labels[day] = count_label

        # -----------------------------------------------------------
        # Task list
        # -----------------------------------------------------------

        task_frame = ctk.CTkScrollableFrame(
            card,
            fg_color="transparent",
            scrollbar_button_color="#333333",
            scrollbar_button_hover_color="#555555"
        )

        task_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=8,
            pady=3
        )

        task_frame.grid_columnconfigure(
            0,
            weight=1
        )

        self.task_frames[day] = task_frame

        # -----------------------------------------------------------
        # Input area
        # -----------------------------------------------------------

        bottom = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        bottom.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=12,
            pady=(7, 13)
        )

        bottom.grid_columnconfigure(
            0,
            weight=1
        )

        entry = ctk.CTkEntry(
            bottom,
            height=36,
            corner_radius=9,
            border_width=1,
            border_color=self.BORDER,
            fg_color=self.INPUT_BG,
            text_color=self.TEXT,
            placeholder_text="Add task...",
            placeholder_text_color="#666666",
            font=ctk.CTkFont(
                size=12
            )
        )

        entry.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 6)
        )

        entry.bind(
            "<Return>",
            lambda event, d=day:
                self.add_task(d)
        )

        self.entries[day] = entry

        add_button = ctk.CTkButton(
            bottom,
            text="+",
            width=36,
            height=36,
            corner_radius=9,
            fg_color=self.YELLOW,
            hover_color=self.YELLOW_HOVER,
            text_color="#000000",
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            ),
            command=lambda d=day:
                self.add_task(d)
        )

        add_button.grid(
            row=0,
            column=1
        )

    # ===============================================================
    # WEEK COUNTER
    # ===============================================================

    def create_week_card(
        self,
        row,
        column
    ):
        """Create the final grid card containing the week counter."""

        card = ctk.CTkFrame(
            self.grid_container,
            fg_color=self.YELLOW,
            corner_radius=16
        )

        card.grid(
            row=row,
            column=column,
            sticky="nsew",
            padx=6,
            pady=6
        )

        card.grid_rowconfigure(
            0,
            weight=1
        )

        card.grid_columnconfigure(
            0,
            weight=1
        )

        content = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        content.grid(
            row=0,
            column=0
        )

        label = ctk.CTkLabel(
            content,
            text="WEEK",
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            ),
            text_color="#000000"
        )

        label.pack()

        self.week_number_label = ctk.CTkLabel(
            content,
            text="1",
            font=ctk.CTkFont(
                size=64,
                weight="bold"
            ),
            text_color="#000000"
        )

        self.week_number_label.pack(
            pady=(0, 0)
        )

        total = ctk.CTkLabel(
            content,
            text="/ 54",
            font=ctk.CTkFont(
                size=17,
                weight="bold"
            ),
            text_color="#000000"
        )

        total.pack()

        self.update_week_counter()

    # ===============================================================
    # TASK OPERATIONS
    # ===============================================================

    def add_task(self, day):
        """Add a task to a day."""

        entry = self.entries[day]

        text = entry.get().strip()

        if not text:
            entry.focus_set()
            return

        self.tasks[day].append({
            "text": text,
            "completed": False
        })

        entry.delete(
            0,
            "end"
        )

        self.save_tasks()
        self.refresh_day(day)

        entry.focus_set()

    def delete_task(
        self,
        day,
        index
    ):
        """Delete a task."""

        if 0 <= index < len(self.tasks[day]):

            del self.tasks[day][index]

            self.save_tasks()
            self.refresh_day(day)

    def toggle_task(
        self,
        day,
        index,
        checkbox,
        label
    ):
        """Toggle task completion."""

        if not (
            0 <= index < len(self.tasks[day])
        ):
            return

        completed = bool(
            checkbox.get()
        )

        self.tasks[day][index][
            "completed"
        ] = completed

        if completed:

            label.configure(
                text_color="#666666",
                font=ctk.CTkFont(
                    size=12,
                    overstrike=True
                )
            )

        else:

            label.configure(
                text_color=self.TEXT,
                font=ctk.CTkFont(
                    size=12,
                    overstrike=False
                )
            )

        self.save_tasks()

        self.update_count(day)

    # ===============================================================
    # TASK RENDERING
    # ===============================================================

    def refresh_all(self):
        """Refresh all seven days."""

        for day in self.DAYS:
            self.refresh_day(day)

        self.update_week_counter()

    def refresh_day(self, day):
        """Redraw one day's task list."""

        container = self.task_frames[day]

        for widget in container.winfo_children():
            widget.destroy()

        tasks = self.tasks.get(
            day,
            []
        )

        if not tasks:

            empty = ctk.CTkLabel(
                container,
                text="No tasks",
                font=ctk.CTkFont(
                    size=12
                ),
                text_color="#555555"
            )

            empty.grid(
                row=0,
                column=0,
                pady=35
            )

        else:

            for index, task in enumerate(tasks):

                self.create_task_row(
                    day,
                    index,
                    task
                )

        self.update_count(day)

    def create_task_row(
        self,
        day,
        index,
        task
    ):
        """Create an individual task row."""

        container = self.task_frames[day]

        row = ctk.CTkFrame(
            container,
            fg_color="#181818",
            corner_radius=9
        )

        row.grid(
            row=index,
            column=0,
            sticky="ew",
            padx=2,
            pady=3
        )

        row.grid_columnconfigure(
            1,
            weight=1
        )

        completed = bool(
            task.get(
                "completed",
                False
            )
        )

        checkbox = ctk.CTkCheckBox(
            row,
            text="",
            width=22,
            height=22,
            checkbox_width=18,
            checkbox_height=18,
            corner_radius=5,
            border_width=2,
            fg_color=self.YELLOW,
            hover_color=self.YELLOW_HOVER,
            border_color="#666666",
            checkmark_color="#000000",
            command=lambda:
                self.toggle_task(
                    day,
                    index,
                    checkbox,
                    label
                )
        )

        checkbox.grid(
            row=0,
            column=0,
            padx=(9, 5),
            pady=8
        )

        if completed:
            checkbox.select()

        label = ctk.CTkLabel(
            row,
            text=task.get(
                "text",
                ""
            ),
            anchor="w",
            justify="left",
            font=ctk.CTkFont(
                size=12,
                overstrike=completed
            ),
            text_color=(
                "#666666"
                if completed
                else self.TEXT
            )
        )

        label.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=2,
            pady=7
        )

        delete = ctk.CTkButton(
            row,
            text="×",
            width=25,
            height=25,
            corner_radius=7,
            fg_color="transparent",
            hover_color="#2A1717",
            text_color="#777777",
            font=ctk.CTkFont(
                size=17
            ),
            command=lambda:
                self.delete_task(
                    day,
                    index
                )
        )

        delete.grid(
            row=0,
            column=2,
            padx=(3, 7)
        )

    # ===============================================================
    # COUNTERS
    # ===============================================================

    def update_count(self, day):
        """Update task count."""

        total = len(
            self.tasks[day]
        )

        completed = sum(
            1
            for task in self.tasks[day]
            if task.get(
                "completed",
                False
            )
        )

        self.count_labels[day].configure(
            text=f"{completed}/{total}"
        )

    def update_week_counter(self):
        """
        Display the current week number.

        ISO week numbers run from 1 to 53.
        The UI displays the requested /54 format.
        """

        week = datetime.now().isocalendar().week

        week = min(
            max(week, 1),
            54
        )

        if hasattr(
            self,
            "week_number_label"
        ):
            self.week_number_label.configure(
                text=str(week)
            )

    # ===============================================================
    # MANUAL RESET FUNCTIONS
    # ===============================================================

    def manual_reset(self):
        """
        Reset the week by unchecking all tasks.

        Task text/fields remain untouched.
        """

        confirm = messagebox.askyesno(
            "Reset Week",
            "Are you sure you want to reset this week?\n\n"
            "All completed tasks will be unchecked.\n"
            "Your task fields will stay.",
            icon="warning"
        )

        if not confirm:
            return

        # Keep every task, only reset completion
        for day in self.DAYS:

            for task in self.tasks[day]:

                task["completed"] = False

        self.save_tasks()
        self.refresh_all()

    def delete_all_fields(self):
        """
        Delete every task from every day.
        """

        confirm = messagebox.askyesno(
            "Reset Fields",
            "Are you sure you want to delete all fields?\n\n"
            "Every task from every day will be permanently removed.",
            icon="warning"
        )

        if not confirm:
            return

        self.tasks = {
            day: []
            for day in self.DAYS
        }

        self.save_tasks()
        self.refresh_all()

    # ===============================================================
    # JSON PERSISTENCE
    # ===============================================================

    def save_tasks(self):
        """Safely save tasks to tasks.json."""

        temp_file = self.DATA_FILE + ".tmp"

        try:

            with open(
                temp_file,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    self.tasks,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            os.replace(
                temp_file,
                self.DATA_FILE
            )

        except (
            OSError,
            TypeError,
            ValueError
        ) as error:

            print(
                f"Could not save tasks: {error}"
            )

            try:

                if os.path.exists(
                    temp_file
                ):
                    os.remove(
                        temp_file
                    )

            except OSError:
                pass

    def load_tasks(self):
        """Load and validate tasks.json."""

        if not os.path.exists(
            self.DATA_FILE
        ):
            return

        try:

            with open(
                self.DATA_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            if not isinstance(
                data,
                dict
            ):
                return

            for day in self.DAYS:

                raw_tasks = data.get(
                    day,
                    []
                )

                if not isinstance(
                    raw_tasks,
                    list
                ):
                    continue

                valid_tasks = []

                for task in raw_tasks:

                    if not isinstance(
                        task,
                        dict
                    ):
                        continue

                    text = task.get(
                        "text"
                    )

                    if not isinstance(
                        text,
                        str
                    ):
                        continue

                    text = text.strip()

                    if not text:
                        continue

                    valid_tasks.append({
                        "text": text,
                        "completed": bool(
                            task.get(
                                "completed",
                                False
                            )
                        )
                    })

                self.tasks[day] = valid_tasks

        except (
            OSError,
            json.JSONDecodeError,
            TypeError,
            ValueError
        ) as error:

            print(
                f"Could not load tasks: {error}"
            )

            self.tasks = {
                day: []
                for day in self.DAYS
            }

    # ===============================================================
    # AUTOMATIC WEEKLY RESET
    # ===============================================================

    def schedule_reset(self):
        """Schedule the next Sunday midnight."""

        now = datetime.now()

        # Python:
        # Monday = 0
        # Sunday = 6

        days_until_sunday = (
            6 - now.weekday()
        ) % 7

        next_sunday = (
            now
            + timedelta(
                days=days_until_sunday
            )
        ).replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

        if next_sunday <= now:

            next_sunday += timedelta(
                days=7
            )

        delay = int(
            (
                next_sunday - now
            ).total_seconds() * 1000
        )

        self.after(
            max(delay, 1000),
            self.perform_reset
        )

    def perform_reset(self):
        """
        Automatically clear all tasks at Sunday midnight.
        """

        now = datetime.now()

        if (
            now.weekday() == 6
            and now.hour == 0
            and now.minute == 0
        ):

            week_id = (
                now.date()
                .isocalendar()[:2]
            )

            if (
                self.last_reset_week
                != week_id
            ):

                self.last_reset_week = (
                    week_id
                )

                # Automatic weekly reset
                # completely clears the week.
                self.tasks = {
                    day: []
                    for day in self.DAYS
                }

                self.save_tasks()
                self.refresh_all()

        self.schedule_reset()

    # ===============================================================
    # CLOSE
    # ===============================================================

    def close_app(self):
        """Save data before closing."""

        self.save_tasks()
        self.destroy()


# ===============================================================
# START APPLICATION
# ===============================================================

if __name__ == "__main__":

    app = WeeklyTodoApp()

    app.mainloop()