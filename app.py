from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flash messages

DATA_FILE = 'data.json'

# -------------------- Utility Functions --------------------
def load_data():
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        return {"budget": 0, "expenses": []}
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"budget": 0, "expenses": []}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# -------------------- Routes --------------------
@app.route('/')
def index():
    data = load_data()
    return render_template("index.html", data=data)

@app.route('/set_budget', methods=['POST'])
def set_budget():
    try:
        budget = float(request.form['budget'])
    except ValueError:
        flash("Invalid budget value.", "danger")
        return redirect(url_for('index'))
    data = load_data()
    data['budget'] = budget
    save_data(data)
    flash("Budget updated successfully.", "success")
    return redirect(url_for('index'))

@app.route('/add_expense', methods=['POST'])
def add_expense():
    description = request.form['description']
    try:
        amount = float(request.form['amount'])
    except ValueError:
        flash("Invalid amount value.", "danger")
        return redirect(url_for('index'))

    edit_index = request.form.get('edit_index')
    data = load_data()
    expenses = data['expenses']
    budget = data['budget']
    current_total = sum(item['amount'] for item in expenses)

    if edit_index:
        old_amount = expenses[int(edit_index)]['amount']
        new_total = current_total - old_amount + amount
    else:
        new_total = current_total + amount

    if new_total > budget:
        flash('Budget limit exceeded! Cannot add this expense.', 'danger')
        return redirect(url_for('index'))

    if edit_index:
        expenses[int(edit_index)] = {"description": description, "amount": amount}
        flash('Expense updated successfully.', 'success')
    else:
        expenses.append({"description": description, "amount": amount})
        flash('Expense added successfully.', 'success')

    save_data(data)
    return redirect(url_for('index'))

@app.route('/edit/<int:index>')
def edit_expense(index):
    data = load_data()
    if 0 <= index < len(data['expenses']):
        expense = data['expenses'][index]
        return render_template('index.html', data=data, edit_index=index, expense=expense)
    flash("Invalid expense index.", "danger")
    return redirect(url_for('index'))

@app.route('/delete/<int:index>')
def delete_expense(index):
    data = load_data()
    if 0 <= index < len(data['expenses']):
        del data['expenses'][index]
        save_data(data)
        flash("Expense deleted.", "success")
    else:
        flash("Invalid index.", "danger")
    return redirect(url_for('index'))

@app.route('/statistics')
def statistics():
    data = load_data()
    total_spent = sum(exp['amount'] for exp in data['expenses'])
    balance = data['budget'] - total_spent
    return render_template('statistics.html', data=data, balance=balance, total_spent=total_spent)

@app.route('/clear')
def clear():
    save_data({"budget": 0, "expenses": []})
    flash("Data cleared.", "success")
    return redirect(url_for('index'))

# -------------------- Run --------------------
if __name__ == '__main__':
    app.run(debug=True)
