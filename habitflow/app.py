from flask import Flask, render_template,request,redirect,url_for,jsonify
from database import *
from google import genai

app=Flask(__name__)
client=genai.Client()
@app.route("/")
def home():
    habits=get_all_habits()
    streaks={h["id"]:get_streak(h["id"]) for h in habits}

    habit_data_for_ai = []
    for h in habits:
        habit_data_for_ai.append({
            "name": h["name"],
            "category": h["category"],
            "streak_days": streaks.get(h["id"], 0),
            "reminders": f"{', '.join(h['reminder_days'])} at {h['reminder_time']}"
        })

    prompt = f"""
    You are an elite habit-coaching AI assistant for an app called HabitFlow. 
    The user's theme is soft, pastel, cute, organized, and encouraging.
    Analyze their current habit tracking data:
    {habit_data_for_ai}
    
    Provide two specific outputs formatted clearly as clean HTML text snippets:
    1. A short, motivating weekly report highlighting strong habits, slipping ones, or noticeable patterns. Keep it brief (2-3 sentences) and ultra-encouraging. Use soft bullet points if necessary.
    2. Exactly 3 new custom habit suggestions based on their categories or what would balance their current lifestyle. Formatted only as <li> elements.
    
    Format your output text EXACTLY like this so I can easily parse it in Python:
    ===SUMMARY===
    <p>Your summary text here...</p>
    ===SUGGESTIONS===
    <li>Suggestion 1</li>
    <li>Suggestion 2</li>
    <li>Suggestion 3</li>
    """
    try:
        # Use the explicit .models namespace from the official SDK
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        raw_text = response.text
        print("DEBUG RAW TEXT:", raw_text)  # Watch your terminal log!

        # Cleaner parsing logic
        if "===SUMMARY===" in raw_text and "===SUGGESTIONS===" in raw_text:
            summary_html = raw_text.split("===SUMMARY===")[1].split("===SUGGESTIONS===")[0].strip()
            suggestions_html = raw_text.split("===SUGGESTIONS===")[1].strip()
            
            # Wipe away code formatting wrappers if the AI attaches them
            summary_html = summary_html.replace("```html", "").replace("```", "").strip()
            suggestions_html = suggestions_html.replace("```html", "").replace("```", "").strip()
        else:
            summary_html = f"<p>{raw_text}</p>"
            suggestions_html = "<li>Check insights above! ✨</li>"

    except Exception as e:
        # This will print the EXACT error message in your VS Code terminal window so we can see it!
        print(f"❌ GEMINI SDK ERROR DETAILS: {e}")
        
        summary_html = "<p>Your habits are blooming beautifully! Complete today's items to view updated insights. ✨</p>"
        suggestions_html = "<li>🌸 Try drinking a glass of water right after waking up.</li><li>🌷 Dedicate 5 minutes to stretching before bed.</li>"

    return render_template("index.html",habits=habits,streaks=streaks,summary=summary_html, suggestions=suggestions_html)

# --- Feature 3: Async Done Button for Milestone Popup ---
@app.route("/mark_done_async/<int:habit_id>", methods=["POST"])
def done_async(habit_id):
    # 1. Update the database state exactly like your normal route did
    mark_done(habit_id)
    
    # 2. Get the updated streak count
    new_streak = get_streak(habit_id)
    habits = get_all_habits()
    habit = next((h for h in habits if h["id"] == habit_id), None)
    habit_name = habit["name"] if habit else "habit"

    # 3. Check if they crossed a specific cute milestone
    milestones = [1, 7, 14, 21, 30, 60, 90, 100] # Added 1 day so you can test it immediately!
    is_milestone = new_streak in milestones
    
    message = ""
    if is_milestone:
        message = f"Incredible job! You've kept your '{habit_name}' streak blooming beautifully for {new_streak} day{'s' if new_streak > 1 else ''}! Keep up that wonderful energy. ✨🌷"

    return jsonify({
        "success": True,
        "new_streak": new_streak,
        "is_milestone": is_milestone,
        "message": message
    })

@app.route("/add",methods=["GET","POST"])
def add_habit():
    if request.method=="POST":
        name=request.form["name"]
        category=request.form["category"]
        reminder_days=request.form.getlist("reminder_days")
        reminder_time=request.form["reminder_time"]
        add_habits(name,category,reminder_days,reminder_time)
        return redirect(url_for("home"))
    return render_template("add.html")

@app.route("/edit/<int:habit_id>",methods=['GET','POST'])
def edit(habit_id):
    habits=get_all_habits()
    habit=next((h for h in habits if h["id"]==habit_id),None)
    if request.method=="POST":
        name=request.form["name"]
        category=request.form["category"]
        reminder_days=request.form.getlist("reminder_days")
        reminder_time=request.form["reminder_time"]
        edit_habit(habit_id,name,category,reminder_days,reminder_time)
        return redirect(url_for("home"))
    return render_template("edit.html",habit=habit)

@app.route("/delete/<int:habit_id>")
def delete(habit_id):
    delete_habit(habit_id)
    return redirect(url_for("home"))

@app.route("/mark_done/<int:habit_id>")
def done(habit_id):
    mark_done(habit_id)
    return redirect(url_for("home"))


if __name__== "__main__":
    initialize()
    app.run(debug=True,port=3000)