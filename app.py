from flask import Flask, flash, request, jsonify, redirect, url_for, render_template
import flask_excel as excel
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from datetime import datetime
import pandas
# please uncomment the following line if you use pyexcel < 0.2.2
# import pyexcel.ext.xls

app = Flask(__name__)
excel.init_excel(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@:localhost/hughes_pom'
app.secret_key = b'_5#y2uadfkl97dasf9L"F4Q8z\n\xec]/'
db = SQLAlchemy(app)


class MasterFileUpload(db.Model):
    __tablename__ = 'master_fileupload'
    id = db.Column('fileup_id', db.Integer, primary_key=True)
    title = db.Column('upload_file', db.String(80))
    number_of_columns = db.Column('col_no', db.Integer)
    procedure_name = db.Column('dest_table', db.String(80))

    def __init__(self, title, number_of_columns=0, procedure_name=''):
        self.title=title
        self.number_of_columns = number_of_columns
        self.procedure_name = procedure_name

    def __repr__(self):
        return '<MFU %r>' % self.title

#db.create_all()

def get_file_extension(filename):
    try:
        file_extension = filename.split('.')[-1]
        if file_extension in ['csv', 'xlsx']:
            return file_extension
    except:
        return False


def get_file_object(file, extension):
    try:
        if extension == 'csv':
            return pandas.read_csv(file)
        elif extension == 'xlsx':
            return pandas.read_excel(file)
    except:
        return False


def get_file_headers(file_object):
    return list(file_object.columns.values)

# TODO: Get column from DB using upload file name
def get_number_of_columns(master_file):
    try:
        return db.session.query(MasterFileUpload).filter_by(title=master_file).one().number_of_columns
    except Exception as e:
        print e
        return -1


def save_to_db(file_object, file_headers):
    # TODO: For each sheet if excel
    try:
        file_objects = list(file_object.fillna('').to_records(index=False))
        sql_str="INSERT INTO import_data (%s) VALUES " % format(', '.join(["c{}".format(i+1) for i in range(len(file_headers))]))

        # for row in file_objects:
        #     sql_str += str(row)
        #     print(sql_str)
        #     sql_str += ", "

        for row in file_objects:
            print row
            encoded_str=[]
            for i in row:
                encoded_str.append(str(i))
            sql_str += str(tuple(encoded_str))
            sql_str += ", "

        print(sql_str[:-2])
        # db.engine.execute(sql_str[:-2])
        return True
    except Exception as e:
        print e
        return False

def run_proc(master_file):
    try:
        proc_name = db.session.query(MasterFileUpload).filter_by(title=master_file).one().procedure_name
        #db.engine.execute("CALL %s ;" % proc_name)
    except Exception as e:
        print e
        return False


@app.route("/", methods=['GET', 'POST'])
def upload_file():
    errors=[]
    file_types = MasterFileUpload.query.all()

    if request.method == 'POST':
        master_file = request.form['upload_file']
        uploaded_file = request.files['file']
        upload_file_name = uploaded_file.filename

        file_extension = get_file_extension(upload_file_name)
        print(file_extension)
        if not file_extension:
            flash('File extension should be csv or xlsx', 'error')
            return render_template('home.html',file_types = file_types)
        file_object = get_file_object(uploaded_file, file_extension)

        file_headers = get_file_headers(file_object)
        if not file_headers:
            flash('File Headers error', 'error')
            return render_template('home.html', file_types = file_types)

        expected_column_len = get_number_of_columns(master_file)
        if expected_column_len == -1:
            flash("Please select correct file type.")
            return render_template('home.html', file_types=file_types)

        if expected_column_len != len(file_headers):
            flash("Please upload file with %s columns " % expected_column_len)
            return render_template('home.html', file_types=file_types)

        if save_to_db(file_object, file_headers):
            flash("File uploaded successfully", 'success')
        else:
            flash("File could not be uploaded successfully")
        procedure_run = run_proc(master_file)
        if not procedure_run:
            flash("Query failed for procedure - %s with error:" % \
                db.session.query(MasterFileUpload).filter_by(title=master_file).one().procedure_name)
            return render_template('home.html', file_types=file_types)
    return render_template('home.html', file_types = file_types)



if __name__ == "__main__":
    app.run()
