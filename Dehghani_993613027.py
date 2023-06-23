from pyswip import Prolog
import tkinter as tk


# STEP1: Define the knowledge base of illnesses and their symptoms
def read_from_file(filename):
    lines = []
    with open(filename) as file:
        file_lines = file.readlines()
        for line in file_lines:
            lines.append(line)
    return lines


def parse_illnesses(illnesses):
    statements = []
    for illness in illnesses:
        if " symptoms are " in illness:
            illness_name, symptoms_text = illness.split(" symptoms are ")
            symptom_list = symptoms_text.split(", ")
            symptom_list[-1] = symptom_list[-1].split(" ")[1][:-2]
            statements.append([illness_name.lower(), symptom_list])
        else:
            # It's cancer
            statements.append(['cancer', ['fatigue', 'weight_loss', 'pain']])

    return statements


def create_knowledge_base(statements):
    prolog = Prolog()
    for illness_name, symptoms_list in statements:
        for symptom in symptoms_list:
            prolog.assertz(f"symptom({symptom}, {illness_name.replace(' ', '_')})")
    return prolog


################################################################################################
# STEP2: Define a function to diagnose illnesses based on symptoms
def diagnose(symptom_list):
    possible_illnesses = list()
    global knowledge_base
    for symptom in symptom_list:
        query_result = list(knowledge_base.query(f"symptom({symptom}, Illness)"))
        for result in query_result:
            possible_illnesses.append(result["Illness"])

    # Finding the most repeated illnesses in possible_illnesses list
    max_count = 0
    most_repeated = list()
    for i in range(len(possible_illnesses)):
        current_count = 0
        for j in range(len(possible_illnesses)):
            if i == j:
                continue
            if possible_illnesses[i] == possible_illnesses[j]:
                current_count += 1
        if current_count > max_count:
            most_repeated = list()
            most_repeated.append(possible_illnesses[i])
            max_count = current_count
        elif current_count == max_count:
            most_repeated.append(possible_illnesses[i])
    # Making most_repeated list unique
    most_repeated = list(set(most_repeated))
    return most_repeated

################################################################################################
# STEP3: Define a function to ask yes/no questions about the remaining symptoms to decide on the illness


def find_diff_symptoms(prolog, symptoms1, illness2):
    symptoms2 = [x['X'] for x in list(prolog.query(f'symptom(X, {illness2})'))]
    return [x for x in symptoms1 if x not in symptoms2]


def ask_question(illnesses):
    # Enabling YES and NO Button
    yes_button.config(state=tk.NORMAL)
    no_button.config(state=tk.NORMAL)

    # TODO: Define a function to diagnose illnesses based on user answers to yes/no questions
    global knowledge_base
    remaining_symptoms = list()

    for i in range(len(illnesses)):
        diff = [x['Symptom'] for x in list(knowledge_base.query(f'symptom(Symptom, {illnesses[i]})'))]
        for j in range(len(illnesses)):
            if j == i:
                continue
            diff = find_diff_symptoms(knowledge_base, diff, illnesses[j])
        remaining_symptoms.extend([x for x in diff])

    if remaining_symptoms:
        question_symptom = remaining_symptoms.pop()
        question_label.config(text="Do you have {}?".format(question_symptom))
        yes_button.config(command=lambda: on_question_answer(question_symptom, True, illnesses))
        no_button.config(command=lambda: on_question_answer(question_symptom, False, illnesses))
    else:
        with open("diagnosed_illness.txt", "w") as f:
            f.write(", ".join(illnesses))
        root.destroy()


def on_question_answer(symptom, answer, illnesses):
    if answer:
        new_illnesses = []
        for illness in illnesses:
            query_result = list(knowledge_base.query(f"symptom({symptom}, {illness})"))
            if query_result:
                new_illnesses.append(illness)
        illnesses = new_illnesses
    else:
        new_illnesses = []
        for illness in illnesses:
            query_result = list(knowledge_base.query(f"symptom({symptom}, {illness})"))
            if not query_result:
                new_illnesses.append(illness)
        illnesses = new_illnesses
    if len(illnesses) == 1:
        with open("diagnosed_illness.txt", "w") as f:
            f.write(illnesses[0])
        root.destroy()
    else:
        ask_question(illnesses)

################################################################################################
# The code is for GUI creation and functionality
# You don't need to directly change it

# "Next" button click event


def on_next_click():
    symptom = symptom_entry.get()
    if symptom:
        symptoms.append(symptom.replace(' ', '_'))
        symptom_entry.delete(0, tk.END)


# Finish button click event
def on_finish_click():
    illnesses = diagnose(symptoms)
    if len(illnesses) == 1:
        with open("diagnosed_illness.txt", "w") as f:
            f.write(illnesses[0])
        root.destroy()
    else:
        ask_question(illnesses)


if __name__ == '__main__':
    # Read illnesses from file
    prolog_statements = parse_illnesses(read_from_file('illnesses.txt'))
    knowledge_base = create_knowledge_base(prolog_statements)
    # Create the GUI
    root = tk.Tk()
    root.title("Illness Diagnosis System")

    # Create the symptom entry field
    symptom_label = tk.Label(root, text="Enter a symptom:")
    symptom_label.grid(row=0, column=0, padx=5, pady=5)
    symptom_entry = tk.Entry(root)
    symptom_entry.grid(row=0, column=1, padx=5, pady=5)

    # Create the "Next" button
    next_button = tk.Button(root, text="Next", command=on_next_click)
    next_button.grid(row=1, column=0, padx=5, pady=5)

    # Create the "Finish" button
    finish_button = tk.Button(root, text="Finish", command=on_finish_click)
    finish_button.grid(row=1, column=1, padx=5, pady=5)

    # Create the question label
    question_label = tk.Label(root, text="")
    question_label.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

    # Create the "Yes" button
    yes_button = tk.Button(root, text="Yes")
    yes_button.grid(row=3, column=0, padx=5, pady=5)

    # Create the "No" button
    no_button = tk.Button(root, text="No")
    no_button.grid(row=3, column=1, padx=5, pady=5)

    # Buttons are disabled at first
    yes_button.config(state=tk.DISABLED)
    no_button.config(state=tk.DISABLED)

    # Initialize the symptoms list
    symptoms = []

    # Start the GUI
    root.mainloop()
