from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

# Initialize database
def init_db():
    conn = sqlite3.connect('employees.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            basic_salary INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# Get employees from database
def get_employees():
    conn = sqlite3.connect('employees.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, basic_salary FROM employees")
    data = cursor.fetchall()
    conn.close()
    # Return as list of tuples for template compatibility
    return data

# Initialize database on startup
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        basic = float(request.form['basic_salary'])
        
        # Insert into database
        conn = sqlite3.connect('employees.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO employees (name, basic_salary) VALUES (?, ?)", (name, basic))
        conn.commit()
        conn.close()
        
        return "Employee Added Successfully!"
    
    return render_template('add_employee.html')

@app.route('/add_default')
def add_default():
    conn = sqlite3.connect('employees.db')
    cursor = conn.cursor()

    employees_list = [
        ("Mahesh", 20000),
        ("Kumar", 25000),
        ("Arun", 18000),
        ("Priya", 30000),
        ("Sanjay", 22000)
    ]

    # Check if employees already exist to prevent duplicates
    cursor.execute("SELECT COUNT(*) FROM employees")
    count = cursor.fetchone()[0]
    
    if count == 0:
        cursor.executemany("INSERT INTO employees (name, basic_salary) VALUES (?, ?)", employees_list)
        conn.commit()
        message = "Default employees inserted successfully!"
    else:
        message = "Default employees already exist in database."

    conn.close()
    return message

@app.route('/cleanup_duplicates')
def cleanup_duplicates():
    conn = sqlite3.connect('employees.db')
    cursor = conn.cursor()
    
    # Remove duplicates by keeping only the first occurrence of each name
    cursor.execute('''
        DELETE FROM employees 
        WHERE id NOT IN (
            SELECT MIN(id) 
            FROM employees 
            GROUP BY name
        )
    ''')
    
    conn.commit()
    deleted_count = cursor.rowcount
    conn.close()
    
    return f"Cleaned up {deleted_count} duplicate employee records."

@app.route('/calculate_salary')
def calculate_salary():
    data = get_employees()
    return render_template("calculate_salary.html", employees=data)

@app.route('/payslip', methods=['POST'])
def generate_payslip():
    name = request.form['name']
    basic = float(request.form['basic'])
    overtime = float(request.form['overtime'])
    
    # Calculate tax (let's assume 10% tax)
    tax = basic * 0.1
    
    # Salary calculation formula: Basic Salary + Overtime - Tax Deductions
    total_salary = basic + overtime - tax
    
    return render_template('payslip.html',
                           name=name,
                           basic=basic,
                           overtime=overtime,
                           tax=tax,
                           total_salary=total_salary)

if __name__ == '__main__':
    app.run(debug=True)
