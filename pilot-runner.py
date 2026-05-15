#!/usr/bin/env python3
"""
Pilot Runner — G8 M1 T1 L2 Day 1: Rigid Motions & Translations

Runs the 7-step lesson cycle in a Matrix room.
Posts slide images + prompts, tracks student responses.

Usage:
  python3 pilot-runner.py --room "!team7-1:class.epaphrodit.us" [--step 1]

Dependencies:
  pip install matrix-nio pillow
"""

import json
import os
import sys
import asyncio
import time
from pathlib import Path

SLIDE_DIR = os.path.expanduser("~/projects/matrix-classroom/pilot-slides")
LESSON_FILE = os.path.expanduser("~/projects/matrix-classroom/pilot-lesson-m1t1l2.json")

# ── Step → slide folder mapping ──────────────────────
STEP_SLIDES = {
    1: "bell-ringer",   # custom prompt, no TEA slide
    2: "hook",          # slides 16-23
    3: "di",            # slides 24-33
    4: "talk",          # slides 34-37
    5: "di",            # slides 38-40 (extra di)
    6: "practice",      # custom prompt
    7: "closure",       # custom prompt
}

def load_lesson():
    with open(LESSON_FILE) as f:
        return json.load(f)

def print_step(lesson, step_num):
    """Print a step's content for manual execution or bot instruction."""
    steps = lesson["steps"]
    step = next(s for s in steps if s["step"] == step_num)
    
    print(f"\n{'='*60}")
    print(f"  STEP {step_num}: {step['name']}  ({step['timer']} min)")
    print(f"{'='*60}\n")
    print(f"PROMPT:\n{step['prompt']}\n")
    
    if step.get("slide_range"):
        print(f"SLIDES: {step['slide_range'][0]}-{step['slide_range'][1]}")
        folder = STEP_SLIDES[step_num]
        slide_dir = os.path.join(SLIDE_DIR, folder)
        if os.path.exists(slide_dir):
            files = sorted(os.listdir(slide_dir))
            print(f"IMAGES ({len(files)} files):")
            for f in files:
                print(f"  MEDIA:{os.path.join(slide_dir, f)}")
    
    if step.get("discourse_stems"):
        print(f"\nDISCOURSE STEMS ({len(step['discourse_stems'])}):")
        for s in step["discourse_stems"]:
            print(f"  {s}")
    
    if step.get("teacher_note"):
        print(f"\n📝 TEACHER NOTE: {step['teacher_note']}")
    
    print(f"\n{'─'*60}")
    print(f"  After posting, wait {step['timer']} min, then type:")
    next_step = step_num + 1
    if next_step <= len(steps):
        print(f"  → 'Bot, run Step {next_step}'")
    else:
        print(f"  → Lesson complete! Collect Exit Tickets.")

def print_all(lesson):
    """Print the full lesson plan."""
    print(f"\n{'#'*60}")
    print(f"  {lesson['pilot_name']}")
    print(f"  Estimated: {lesson['estimated_time']}")
    print(f"  TEKS: {', '.join(lesson['teks'])}")
    print(f"  Materials: {', '.join(lesson['materials'])}")
    print(f"{'#'*60}\n")
    
    for step in lesson["steps"]:
        print_step(lesson, step["step"])

def tracker_init():
    """Initialize a per-student tracker CSV."""
    tracker_path = os.path.expanduser("~/projects/matrix-classroom/pilot-tracker.csv")
    if not os.path.exists(tracker_path):
        with open(tracker_path, "w") as f:
            f.write("timestamp,student,step,response_type,response\n")
        print(f"Tracker created: {tracker_path}")
    return tracker_path

def tracker_log(tracker_path, student, step, response_type, response):
    """Log a student response."""
    from datetime import datetime
    with open(tracker_path, "a") as f:
        ts = datetime.now().isoformat()
        # Escape commas in response
        resp = response.replace('"', '""')
        f.write(f'{ts},"{student}",{step},"{response_type}","{resp}"\n')
    print(f"  ✓ Logged: {student} → Step {step}")

if __name__ == "__main__":
    lesson = load_lesson()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--track":
        # Log mode: python3 pilot-runner.py --track "jacklynn" 2 "bell_ringer" "answer text"
        tracker_path = tracker_init()
        tracker_log(tracker_path, sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    elif len(sys.argv) > 1 and sys.argv[1] == "--step":
        step_num = int(sys.argv[2])
        print_step(lesson, step_num)
    else:
        tracker_path = tracker_init()
        print_all(lesson)
        print(f"\nTracker ready at: {tracker_path}")
        print(f"To log a response: python3 pilot-runner.py --track <student> <step> <type> <response>")
        print(f"To view a step: python3 pilot-runner.py --step <number>")
