# 🎒 Student Onboarding Flow

When a student DMs the bot for the first time (no prior DM history), follow this flow.

---

## Step 1: Welcome

```
Hey [name]! Welcome to the Matrix classroom 👋

I'm Hermes, the class AI helper. Before we get started, I'd like to ask you a few quick questions so I can help you better. Sound good?
```

Wait for their response.

---

## Step 2: Ask 5 questions

Ask one at a time. Wait for an answer before moving to the next.

**Q1 — Feelings about math**
```
First one — how do you feel about math class? Like, do you enjoy it, find it okay, or not really your thing?
```

**Q2 — Strength**
```
Cool, thanks. What's one topic or skill in math you feel pretty confident about?
```

**Q3 — Growth area**
```
What about the opposite — what's something in math you'd like to get better at?
```

**Q4 — Problem-solving habits**
```
When you get stuck on a math problem, what do you usually do? Give up, ask someone, try different ways?
```

**Q5 — Work preference**
```
Last one — do you prefer working alone or with a partner when doing math?
```

---

## Step 3: Save profile

After all 5 questions answered, save to:

```
/home/abe/projects/matrix-classroom/student-profiles/[username].md
```

Use the template at `/home/abe/projects/matrix-classroom/student-profiles/_TEMPLATE.md`.
Replace bracketed placeholders with actual answers.

Then verify the file was saved:
```
read_file(path="/home/abe/projects/matrix-classroom/student-profiles/[username].md")
```

Also save the answers to Honcho as conclusions:
```
honcho_conclude(conclusion="Student [name] feels [feeling] about math")
honcho_conclude(conclusion="Student [name] is confident in [topic]")
honcho_conclude(conclusion="Student [name] wants to improve at [topic]")
honcho_conclude(conclusion="Student [name] copes with being stuck by [strategy]")
honcho_conclude(conclusion="Student [name] prefers working [alone/partner]")
```
Verify Honcho saved correctly: `honcho_profile(peer="[username]")` should show new facts.

---

## Step 4: Confirm + offer help

```
Thanks [name]! I've saved your answers. Now how can I help you today? Got a math question, or want to practice something?
```

---

## Edge cases

- **Student doesn't want to answer** → "No problem! If you ever change your mind, just ask. What can I help you with?"
- **Student gives one-word answers** → Accept it, save it, move on
- **Already has a profile** → Don't re-onboard. Check `student-profiles/[username].md` exists first.
- **File write fails** → Still save to Honcho conclusions. Note in DM: "I saved your info. Let me know if you need anything!"
