import tkinter as tk
from pynput import keyboard
from langdetect import detect
import threading
from PIL import Image
import pyperclip
import sys
import os

# פונקציה לקבלת נתיב קובץ נכון
def get_milton_file(file_name):
    # אם אנחנו בתוך exe (מאוחד), נעשה שימוש ב- MEIPASS
    if hasattr(sys, '_MEIPASS'):
        # תחום בתוך exe
        return os.path.join(sys._MEIPASS, file_name)
    else:
        # פתח את הקובץ בתיקיית העבודה (למשל בזמן פיתוח)
        return os.path.join(os.path.dirname(__file__), file_name)

# המילונים להמרה בין עברית לאנגלית ולהפך
heb_to_eng = {
    'א': 't', 'ב': 'c', 'ג': 'd', 'ד': 's', 'ה': 'v', 'ו': 'u', 'ז': 'z',
    'ח': 'j', 'ט': 'p', 'י': 'h', 'כ': 'f', 'ל': 'k', 'מ': 'n', 'נ': 'b',
    'ס': 'x', 'ע': 'g', 'פ': ';', 'צ': 'm', 'ק': 'l', 'ר': 'r', 'ש': 'a',
    'ת': ',', 'ם': 'o', 'ק': 'e', 'ן': 'i','ך': 'l','פ': 'p','/': 'q','\'': 'w','ט': 'y'
}
eng_to_heb = {
    't': 'א', 'c': 'ב', 'd': 'ג', 's': 'ד', 'v': 'ה', 'u': 'ו', 'z': 'ז',
    'j': 'ח', 'p': 'ט', 'h': 'י', 'f': 'כ', 'k': 'ל', 'n': 'מ', 'b': 'נ',
    'x': 'ס', 'g': 'ע', ';': 'פ', 'm': 'צ', 'l': 'ק', 'r': 'ר', 'a': 'ש',
    ',': 'ת' , 'o': 'ם', 'e': 'ק', 'i': 'ן', 'q': '/','w': '\'', 'y': 'ט'
}

# קריאה לקובץ heb_words.txt
heb_words_file_path = get_milton_file('bible_he.txt')
with open(heb_words_file_path, 'r', encoding='utf-8') as file:
    heb_words = file.read().splitlines()

# קריאה לקובץ eng_words.txt
eng_words_file_path = get_milton_file('bible_en.txt')
with open(eng_words_file_path, 'r', encoding='utf-8') as file:
    eng_words = file.read().splitlines()

 
# פונקציה שתמיר את התו הקלד לשפה ההפוכה
def detect_and_correct(text):
    corrected_text = ""
    for char in text:
        if char in heb_to_eng:
            corrected_text += heb_to_eng[char]  # המרת עברית לאנגלית
        elif char in eng_to_heb:
            corrected_text += eng_to_heb[char]  # המרת אנגלית לעברית
        else:
            corrected_text += char  # אם התו לא נמצא בהמרה, הוסף אותו כפי שהוא
    return corrected_text

# פונקציה שתשדר את התיקון לחלון Tkinter
def show_correction(correction):
    text_var.set(correction)  # עדכון טקסט בחלון
    # אם החלון ממוזער, מציג אותו מחדש 
    if not window.state() == 'normal':
        window.deiconify()  # מבטל את המינימיזציה של החלון

def on_click(event):
    # העתקת הטקסט ללוח
    pyperclip.copy(text_var.get())
    print(f"Copied to clipboard: {text_var.get()}")  # דיבוג

typed_text = []

# פונקציה שתבדוק אם המילה תקינה
def is_word_valid(word):
    try:
        # זיהוי השפה של המילה
        language = detect(word)
        print(f"Language: {language}") #
        
        # אם השפה היא עברית, נבדוק במילון עברי
        if language == 'he':
            if word in heb_words:
                return True
        # אם השפה היא אנגלית, נבדוק במילון אנגלי
        elif language == 'sw' or 'en':
            if word in eng_words:
                return True
        
    except Exception as e:
        print(f"Error detecting language for word '{word}': {e}")
        
    return False  # אם המילה לא נמצאה במילון המתאים

# פונקציה שתקבל את המילה שהוקלדה ותחליט אם להוסיף לרשימה
def on_type(key):
    global typed_text
    try:
        if hasattr(key, 'char') and key.char is not None and key.char.isprintable():
            # הוספת התו לרשימה
            typed_text.append(key.char)  
            print(f"Typed text so far: {''.join(typed_text)}")  # דיבוג

        elif key == keyboard.Key.space:  
            # ברגע שלחצנו רווח, נבצע בדיקה
            text = ''.join(typed_text).strip()  # איסוף הטקסט הנוכחי
            print(f"Text to check: {text}")  # דיבוג
            
            # הפרדת מילים מהטקסט
            words = text.split()
            typed_text = []  # איפוס הרשימה לאחר העיבוד
            for word in words:
                if not is_word_valid(word):  # אם המילה לא תקינה
                    typed_text.append(word)  # הוספת המילה לרשימה
                    typed_text.append(" ")

                else:
                    print(f"Valid word: {word}")  # דיבוג אם המילה תקינה
                    
            process_text(text)  # טיפול בטקסט

        elif key == keyboard.Key.backspace:
            typed_text.pop()
            print(f"Text after backspace: {''.join(typed_text)}") 
        elif key == keyboard.Key.enter or (hasattr(key, 'char') and key.char in '.!?'):
            # אם סיימנו משפט (למשל אחרי אנטר או תו סיום משפט), נבצע את העיבוד
            text = ''.join(typed_text).strip()  # איסוף כל הטקסט
            process_text(text)  # טיפול בטקסט
            typed_text.clear()  # איפוס הטקסט לאחר תיקון
            
    except Exception as e:
        print(f"Error: {e}")

# פונקציה לטיפול בטקסט המוקלד
def process_text(text):
    if text:  # אם יש טקסט
        # אם המילה לא תקינה, הצג תיקון
        if not is_word_valid(text):
            corrected_text = detect_and_correct(text)  # תיקון המשפט
            print(f"Corrected text: {corrected_text}")  # דיבוג
            if corrected_text != text:
                show_correction(corrected_text)  # הצגת התיקון


# הפעלת המאזין למקלדת ברקע
def start_listener():
    with keyboard.Listener(on_press=on_type) as listener:
        listener.join()

# יצירת חלון Tkinter
def create_window():
    global text_var, window
    # יצירת חלון חדש
    window = tk.Tk()
    window.title("תיקון שפה")
    window.geometry("150x150")  # גודל החלון
    window.resizable(False, False)  # למנוע שינוי גודל
    window.attributes("-topmost", True)

    # יצירת תווית להציג את התיקון
    text_var = tk.StringVar()
    label = tk.Label(window, textvariable=text_var, font=("Arial", 12), wraplength=100)
    label.pack(pady=30)

    # כפתור סגירה של החלון
    close_button = tk.Button(window, text="סגור", command=window.quit)
    close_button.pack(pady=10)
    label.bind("<Button-1>", on_click)
    
    # מינימיזציה של החלון בתחילה
    window.iconify()

    # הרצת חלון Tkinter
    window.mainloop()

# הפעלת המאזין והחלון ברקע
if __name__ == "__main__":
    # הרצת המאזין למקלדת
    threading.Thread(target=start_listener, daemon=True).start()
    
    # יצירת והפעלת חלון Tkinter
    create_window()
