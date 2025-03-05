#!/usr/bin/env python3
import PySimpleGUI as sg
import json
import random
from dataclasses import dataclass, field
from typing import List
from fpdf import FPDF

@dataclass
class QuizQuestion:
    question: str
    correctAnswer: str
    wrongAnswers: List[str]
    timeout: int = field(default=10)

    def __repr__(self):
        return self.question

questionList = []


def create_pdf(quiz_title, questions):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt=quiz_title, ln=True, align='C')

    for i, question in enumerate(questions):
        pdf.cell(200, 10, txt=f"{i + 1}. {question.question}", ln=True)
        
        all_answers = [question.correctAnswer] + question.wrongAnswers
        random.shuffle(all_answers)
        
        for j, answer in enumerate(all_answers):
            pdf.cell(200, 10, txt=f"  {chr(65 + j)}) {answer}", ln=True)
        pdf.cell(200, 10, txt="", ln=True)

    pdf_file_path = f"output/{quiz_title}.pdf"
    pdf.output(pdf_file_path)
    sg.popup("Quiz saved as PDF!", title="Success")
    
def save_as_txt(quiz_title, questions):
    with open(f"output/{quiz_title}.txt", 'w') as f:
        f.write(f"{quiz_title}\n")
        for i, question in enumerate(questions):
            f.write(f"{i + 1}. {question.question}\n")
            
            all_answers = [question.correctAnswer] + question.wrongAnswers
            random.shuffle(all_answers)
            
            for j, answer in enumerate(all_answers):
                f.write(f"  {chr(65 + j)}) {answer}\n")
            f.write("\n")
    sg.popup("Quiz saved as TXT!", title="Success")

mainWinowLayout = [
    [sg.Text("Title of Quiz:"), sg.InputText(key='quiz_name')],
    [sg.Listbox(questionList, size=(125, 25), key='quizquestionentry', enable_events=True), sg.Text(key='textbox', size=(20, 10))],
    [sg.Button('Open'), sg.Button('Save'), sg.Button("Edit Question"), sg.Button("Add Question"), sg.Button("Delete Question")],
    [sg.Radio('PDF', 'OUTPUT_FORMAT', key='pdf', default=True), sg.Radio('TXT', 'OUTPUT_FORMAT', key='txt')],
    [sg.Button('Quit')]
]

mainWindow = sg.Window('Quiz Creator', mainWinowLayout)

def make_questionEditorWindow():
    questionEditorLayout = [
        [sg.Text('Enter the question:'), sg.InputText(key='question')],
        [sg.Text('Enter the correct answer:'), sg.InputText(key='correct_answer')],
        [sg.Text('Enter the wrong answers:'), sg.InputText(key='wrong_answers')],
        [sg.Button('Add'), sg.Button('Cancel')]
    ]
    
    questionEditorWindow = sg.Window('Question Editor', questionEditorLayout, finalize=True)
    return questionEditorWindow

while True:
    event, values = mainWindow.read()
    
    if event == 'quizquestionentry':
        if len(values['quizquestionentry']) > 0:
            answers = ("correct answer:", values['quizquestionentry'][0].correctAnswer, "wrong answers:", values['quizquestionentry'][0].wrongAnswers)
            outputtext = "Correct answer: \n" + answers[1] + "\n Wrong answers:\n" + str(answers[3])
            mainWindow["textbox"].update(outputtext)
    
    if event == sg.WIN_CLOSED or event == 'Quit':
        print("Bye...")
        break

    if event == 'Edit Question':
        try:
            index = int(''.join(map(str, mainWindow["quizquestionentry"].get_indexes())))
            quizQuestion = questionList[index]
        except ValueError:
            sg.Popup("Select a question to edit!")
            continue

        questionEditorWindow = make_questionEditorWindow()
        questionEditorWindow['question'].update(quizQuestion.question)
        questionEditorWindow['correct_answer'].update(quizQuestion.correctAnswer)
        questionEditorWindow['wrong_answers'].update(', '.join(quizQuestion.wrongAnswers))
        
        editorEvent, editorValues = questionEditorWindow.read()
        if editorEvent == 'Add':
            question = editorValues['question']
            correct_answer = editorValues['correct_answer']
            wrong_answers = editorValues['wrong_answers'].split(',')
            newquestion = QuizQuestion(question, correct_answer, wrong_answers)
            questionList[index] = newquestion  
            questionEditorWindow.close()
            mainWindow["quizquestionentry"].update(questionList)
        if editorEvent == 'Cancel':
            questionEditorWindow.close()

    if event == 'Add Question':
        questionEditorWindow = make_questionEditorWindow()
        editorEvent, editorValues = questionEditorWindow.read()
        if editorEvent == 'Add':
            question = editorValues['question']
            correct_answer = editorValues['correct_answer']
            wrong_answers = editorValues['wrong_answers'].split(',')
            newquestion = QuizQuestion(question, correct_answer, wrong_answers)
            questionList.append(newquestion)
            questionEditorWindow.close()
            mainWindow["quizquestionentry"].update(questionList)
        if editorEvent == 'Cancel':
            questionEditorWindow.close()
        
    if event == 'Save':
        quiz_title = values['quiz_name']
        if values['pdf']:
            create_pdf(quiz_title, questionList)
        elif values['txt']:
            save_as_txt(quiz_title, questionList)

    if event == 'Open':
        try:
            filename = sg.popup_get_file('Open', no_window=True, initial_folder="quizzes",
                                          file_types=(("All JSON Files", "*.json"), ("All Files", "*.*")))
            with open(filename, 'r') as file:
                quizDicts = json.load(file)
                questionList = []
                for q in quizDicts["listOfQuestions"]:
                    qq = QuizQuestion(**q)
                    questionList.append(qq)
                mainWindow["quizquestionentry"].update(questionList)
                titleofquiz = quizDicts["title"]
                mainWindow["quiz_name"].update(titleofquiz)
        except TypeError:
            pass
    
    if event == 'Delete Question':
        try:
            index = int(''.join(map(str, mainWindow["quizquestionentry"].get_indexes())))
            questionList.pop(index)
        except ValueError:
            sg.Popup("Select a question to delete!")

        mainWindow["quizquestionentry"].update(questionList)

mainWindow.close()

