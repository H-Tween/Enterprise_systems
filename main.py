import tkinter as tk
from tkinter import filedialog, messagebox
import fitz  # PyMuPDF for PDF processing
from docx import Document  # for Word document processing
from fpdf import FPDF
from openai import OpenAI
from customtkinter import *

# Initialise OpenAI API key
api_key = ''

# Initialise OpenAI client
client = OpenAI(api_key=api_key)

# # Initialise root Tkinter window
# root = tk.Tk()
# root.title("Medical Document Analysis")
# root.geometry("500x400")
# root.configure(bg="#f5f5f5")
# root.resizable(False, False)  # Prevent resizing for consistent layout

# Initialise CustomTkinter
app = CTk()
app.geometry("500x400")
app.title("Medical Document Analysis")


# Store extracted text
extracted_text = ""


# Function to show pop-up messages (success, error, or warning)
def show_message(title, message, message_type="info"):
    # Create a Toplevel window as a pop-up dialog
    popup = CTkToplevel(app)
    popup.geometry("300x150")
    popup.title(title)

    temp_label = CTkLabel(popup, text=message, font=("Arial", 12), text_color="#FFCC70", wraplength=250)
    temp_label.pack(pady=30)

    # Adding a close button
    close_button = CTkButton(popup, text="Close", command=popup.destroy, corner_radius=10,
                             fg_color="#FFCC70", hover_color="#FF9E4A")
    close_button.pack(pady=10)

    if message_type == "error":
        temp_label.configure(text_color="#ff4d4d")  # Red for error messages
        close_button.configure(fg_color="#f44336", hover_color="#e53935")  # Red for error close button
    elif message_type == "warning":
        temp_label.configure(text_color="#ff9800")  # Orange for warning messages
        close_button.configure(fg_color="#ff9800", hover_color="#f57c00")  # Orange close button


# Function to check file type, extract text, and update button
def attach_file():
    global extracted_text
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf"), ("Word Files", "*.docx")])
    if file_path:
        if file_path.endswith(".pdf"):
            extracted_text = extract_text_from_pdf(file_path)
        elif file_path.endswith(".docx"):
            extracted_text = extract_text_from_docx(file_path)
        else:
            show_message("Error", "Please upload a PDF or Word document.")
            return

        if extracted_text:
            attach_button.configure(fg_color="green", text="File Attached")
        else:
            show_message("Error", "Could not extract text from the file.")


# Function to extract text from PDF
def extract_text_from_pdf(file_path):
    text = ""
    try:
        with fitz.open(file_path) as pdf:
            for page in pdf:
                text += page.get_text()
    except Exception as e:
        show_message("Error", f"Could not read PDF: {e}")
    return text


# Function to extract text from Word document
def extract_text_from_docx(file_path):
    text = ""
    try:
        doc = Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        show_message("Error", f"Could not read Word document: {e}")
    return text



# Function to call ChatGPT and get response
def call_chatgpt(prompt):
    try:
        # ChatGPT context and prompt
        messages = [
            {"role": "system",
             "content": "You are an assistant at a hospital. Your job is to analyze text provided to determine the necessary medicine, dosage, and any other relevant information."},
            {"role": "user", "content": f"Document Text:\n{extracted_text}\n\nUser's prompt:\n{prompt}"}
        ]

        # Request completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=1500,
            temperature=0.7
        )
        # Extract and return the generated text
        return response.choices[0].message.content.strip()
    except Exception as e:
        show_message("Error", f"Could not get response from ChatGPT: {e}")
        return ""


# Function to convert response to PDF and save
def save_response_as_pdf(response_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, response_text)

    output_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
    if output_path:
        pdf.output(output_path)
        show_message("Success", f"PDF saved as {output_path}")


# Function to handle prompt submission
def submit_prompt():
    user_prompt = prompt_text.get()
    if not user_prompt:
        show_message("Warning", "Please enter a prompt.")
        return
    if not extracted_text:
        show_message("Warning", "Please attach a document first.")
        return

    response = call_chatgpt(user_prompt)
    if response:
        save_response_as_pdf(response)


# # UI Elements
# attach_button = tk.Button(root, text="Attach File", command=attach_file, bg="lightgray")
# attach_button.pack(pady=10)
#
# prompt_label = tk.Label(root, text="Enter your prompt:")
# prompt_label.pack()
#
# prompt_text = tk.Text(root, height=5, width=40, wrap="word")
# prompt_text.pack(pady=5)
#
# submit_button = tk.Button(root, text="Submit", command=submit_prompt, bg="lightblue")
# submit_button.pack(pady=20)

# Run the GUI
# root.mainloop()

# UI Elements
set_appearance_mode("dark")

label = CTkLabel(master=app,
                       text="Medical Document Analysis",
                       font=("Arial", 24),
                       text_color="#FFCC70")
label.place(relx=0.5, rely=0.1, anchor="center")

attach_button = CTkButton(master=app,
                               text="Attach File",
                               command=lambda: attach_file(),
                               fg_color="#6200EE",
                               hover_color="#3700B3",
                               border_color="#FFCC70",
                               border_width=2,
                               corner_radius=12,
                               font=("Arial", 16, "bold"))
attach_button.place(relx=0.5, rely=0.3, anchor="center")

prompt_text = CTkEntry(master=app,
                           placeholder_text="Enter your prompt here...",
                           width=350,
                           height=40,
                           text_color="#FFFFFF",
                           placeholder_text_color="#FFCC70",
                           font=("Arial", 14))
prompt_text.place(relx=0.5, rely=0.5, anchor="center")

submit_button = CTkButton(master=app,
                               text="Submit",
                               command=submit_prompt,
                               fg_color="#FF5722",
                               hover_color="#D84315",
                               border_color="#FFCC70",
                               border_width=2,
                               corner_radius=12,
                               font=("Arial", 16, "bold"))
submit_button.place(relx=0.5, rely=0.75, anchor="center")


app.mainloop()