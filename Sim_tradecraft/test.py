from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import datetime as dt
import itertools
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'  # Change this in production

WORK_START = dt.time(9, 0)
WORK_END = dt.time(17, 0)
SLOT_MINUTES = 30
PLANNING_HORIZON_DAYS = 60


@dataclass
class Task:
    title: str
    deadline: dt.date
    duration_hours: float
    priority: int = 3  # 1–5
    repeat: Optional[str] = None  # None | 'weekly' | 'monthly' | 'yearly'
    fixed_start: Optional[dt.datetime] = None  # for fixed-time tasks
    id: int = field(default_factory=lambda: Task._next_id())

    _id_counter: int = 0

    @classmethod
    def _next_id(cls):
        cls._id_counter += 1
        return cls._id_counter

    def to_dict(self):
        d = asdict(self)
        d['deadline'] = self.deadline.isoformat()
        if self.fixed_start:
            d['fixed_start'] = self.fixed_start.isoformat()
        return d


@dataclass
class ScheduledBlock:
    task_id: int
    title: str
    start: dt.datetime
    end: dt.datetime
    fixed: bool = False

    def to_dict(self):
        return {
            'task_id': self.task_id,
            'title': self.title,
            'start': self.start.isoformat(),
            'end': self.end.isoformat(),
            'fixed': self.fixed
        }


class Scheduler:
    def __init__(self):
        self.tasks: List[Task] = []
        self.blocks: List[ScheduledBlock] = []
        self.slot = dt.timedelta(minutes=SLOT_MINUTES)

    # ---------------- Task management ----------------
    def add_task(self, title, deadline_str, duration_hours, priority=3, repeat=None, fixed_start_str=None):
        deadline = dt.datetime.strptime(deadline_str, "%Y-%m-%d").date()
        fixed_start = None
        if fixed_start_str:
            fixed_start = dt.datetime.strptime(fixed_start_str, "%Y-%m-%d %H:%M")
        t = Task(title=title, deadline=deadline, duration_hours=duration_hours, priority=priority, repeat=repeat,
                 fixed_start=fixed_start)
        self.tasks.append(t)
        if repeat:
            self._generate_recurrences(t)
        return t.id

    def _generate_recurrences(self, base: Task):
        step = None
        if base.repeat == 'weekly':
            step = dt.timedelta(weeks=1)
        elif base.repeat == 'monthly':
            step = 'monthly'
        elif base.repeat == 'yearly':
            step = 'yearly'
        else:
            return

        today = dt.date.today()
        horizon = today + dt.timedelta(days=PLANNING_HORIZON_DAYS)

        def add_months(d: dt.date, months: int) -> dt.date:
            month = d.month - 1 + months
            year = d.year + month // 12
            month = month % 12 + 1
            day = min(d.day,
                      [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31,
                       30, 31, 30, 31][month - 1])
            return dt.date(year, month, day)

        next_date = base.deadline
        while True:
            if isinstance(step, dt.timedelta):
                next_date = next_date + step
            elif step == 'monthly':
                next_date = add_months(next_date, 1)
            elif step == 'yearly':
                next_date = dt.date(next_date.year + 1, next_date.month, next_date.day)
            if next_date > horizon:
                break
            self.tasks.append(Task(
                title=base.title,
                deadline=next_date,
                duration_hours=base.duration_hours,
                priority=base.priority,
                repeat=base.repeat,
                fixed_start=dt.datetime.combine(next_date, base.fixed_start.time()) if base.fixed_start else None
            ))

    def list_tasks(self):
        return sorted(self.tasks, key=lambda x: (x.deadline, -x.priority))

    def delete_task(self, task_id: int, mode: str = "single"):
        task = next((t for t in self.tasks if t.id == task_id), None)
        if not task:
            return False
        if mode == "all" and task.repeat:
            self.tasks = [t for t in self.tasks if not (t.title == task.title and t.repeat == task.repeat)]
        else:
            self.tasks = [t for t in self.tasks if t.id != task_id]
        return True

    def change_duration(self, task_id: int, new_duration: float):
        task = next((t for t in self.tasks if t.id == task_id), None)
        if not task:
            return False
        task.duration_hours = new_duration
        self.optimize()  # Recalculate schedule to avoid overlaps
        return True

    # ---------------- Scheduling ----------------
    def optimize(self):
        self.blocks.clear()
        if not self.tasks:
            return

        today = dt.date.today()
        horizon = today + dt.timedelta(days=PLANNING_HORIZON_DAYS)

        # Generate slots for each day
        def generate_slots(day: dt.date):
            start = dt.datetime.combine(day, WORK_START)
            end = dt.datetime.combine(day, WORK_END)
            slots = []
            t = start
            while t + self.slot <= end:
                slots.append(t)
                t += self.slot
            return slots

        day_slots: Dict[dt.date, List[dt.datetime]] = {}
        d = today
        while d <= horizon:
            day_slots[d] = generate_slots(d)
            d += dt.timedelta(days=1)

        # Place fixed tasks first
        for task in [t for t in self.tasks if t.fixed_start]:
            start = task.fixed_start
            end = start + dt.timedelta(hours=task.duration_hours)
            self.blocks.append(ScheduledBlock(task_id=task.id, title=task.title, start=start, end=end, fixed=True))
            # remove occupied slots
            cur = start
            while cur < end:
                if cur in day_slots.get(cur.date(), []):
                    day_slots[cur.date()].remove(cur)
                cur += self.slot

        # Sort flexible tasks by deadline & priority
        flex_tasks = sorted([t for t in self.tasks if not t.fixed_start], key=lambda t: (t.deadline, -t.priority))

        for task in flex_tasks:
            remaining = dt.timedelta(hours=task.duration_hours)
            day = today
            while remaining > dt.timedelta(0) and day <= task.deadline:
                slots = day_slots.get(day, [])
                while remaining > dt.timedelta(0) and slots:
                    start = slots.pop(0)
                    end = start + self.slot
                    self.blocks.append(ScheduledBlock(task_id=task.id, title=task.title, start=start, end=end))
                    remaining -= self.slot
                day_slots[day] = slots
                day += dt.timedelta(days=1)

        self.blocks = self._merge_blocks(self.blocks)

    def _merge_blocks(self, blocks: List[ScheduledBlock]) -> List[ScheduledBlock]:
        blocks = sorted(blocks, key=lambda b: (b.start, b.task_id))
        merged = []
        for key, group in itertools.groupby(blocks, key=lambda b: (b.task_id, b.fixed)):
            group = list(group)
            group.sort(key=lambda b: b.start)
            cur = group[0]
            for b in group[1:]:
                if b.start == cur.end and b.title == cur.title:
                    cur = ScheduledBlock(task_id=cur.task_id, title=cur.title, start=cur.start, end=b.end,
                                         fixed=cur.fixed)
                else:
                    merged.append(cur)
                    cur = b
            merged.append(cur)
        return merged

    # ---------------- Views ----------------
    def agenda_for(self, day: dt.date):
        return sorted([b for b in self.blocks if b.start.date() == day], key=lambda b: b.start)

    def agenda_all(self):
        return sorted(self.blocks, key=lambda b: b.start)


# Global scheduler instance (in production, you might want to use a database)
scheduler = Scheduler()


# ---------------- Flask Routes ----------------

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/tasks')
def tasks():
    task_list = scheduler.list_tasks()
    return render_template('tasks.html', tasks=task_list)


@app.route('/add_task', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        title = request.form['title']
        deadline = request.form['deadline']
        duration = float(request.form['duration'])
        priority = int(request.form['priority'])
        repeat = request.form['repeat'] if request.form['repeat'] != 'none' else None
        fixed_start = request.form['fixed_start'] if request.form['fixed_start'] else None

        try:
            task_id = scheduler.add_task(title, deadline, duration, priority, repeat, fixed_start)
            flash(f'Task "{title}" added successfully!', 'success')
            return redirect(url_for('tasks'))
        except ValueError as e:
            flash(f'Error adding task: {str(e)}', 'error')

    return render_template('add_task.html')


@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    task = next((t for t in scheduler.tasks if t.id == task_id), None)
    if task and task.repeat:
        return render_template('delete_task.html', task=task)
    else:
        if scheduler.delete_task(task_id, "single"):
            flash('Task deleted successfully!', 'success')
        else:
            flash('Task not found!', 'error')
        return redirect(url_for('tasks'))


@app.route('/delete_task/<int:task_id>/<mode>')
def delete_task_with_mode(task_id, mode):
    if scheduler.delete_task(task_id, mode):
        flash('Task(s) deleted successfully!', 'success')
    else:
        flash('Task not found!', 'error')
    return redirect(url_for('tasks'))


@app.route('/change_duration/<int:task_id>', methods=['GET', 'POST'])
def change_duration(task_id):
    task = next((t for t in scheduler.tasks if t.id == task_id), None)
    if not task:
        flash('Task not found!', 'error')
        return redirect(url_for('tasks'))

    if request.method == 'POST':
        new_duration = float(request.form['duration'])
        if scheduler.change_duration(task_id, new_duration):
            flash('Duration updated and schedule re-optimized!', 'success')
        else:
            flash('Error updating duration!', 'error')
        return redirect(url_for('tasks'))

    return render_template('change_duration.html', task=task)


@app.route('/optimize')
def optimize():
    scheduler.optimize()
    flash('Schedule optimized!', 'success')
    return redirect(url_for('agenda'))


@app.route('/agenda')
def agenda():
    blocks = scheduler.agenda_all()
    today = dt.date.today()
    return render_template('agenda.html', blocks=blocks, today=today)


@app.route('/today')
def today():
    today = dt.date.today()
    blocks = scheduler.agenda_for(today)
    return render_template('today.html', blocks=blocks, today=today)


@app.route('/api/tasks')
def api_tasks():
    tasks = [t.to_dict() for t in scheduler.list_tasks()]
    return jsonify(tasks)


@app.route('/api/agenda')
def api_agenda():
    blocks = [b.to_dict() for b in scheduler.agenda_all()]
    return jsonify(blocks)


# ---------------- Templates ----------------

@app.template_filter('datetime')
def datetime_filter(value):
    if isinstance(value, str):
        value = dt.datetime.fromisoformat(value)
    return value.strftime('%Y-%m-%d %H:%M')


@app.template_filter('date')
def date_filter(value):
    if isinstance(value, str):
        value = dt.date.fromisoformat(value)
    return value.strftime('%Y-%m-%d')


@app.template_filter('time')
def time_filter(value):
    if isinstance(value, str):
        value = dt.datetime.fromisoformat(value)
    return value.strftime('%H:%M')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)