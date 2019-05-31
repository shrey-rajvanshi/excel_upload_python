from flask import Flask, request, jsonify, redirect, url_for, render_template
import flask_excel as excel
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas
# please uncomment the following line if you use pyexcel < 0.2.2
# import pyexcel.ext.xls

app = Flask(__name__)
excel.init_excel(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tmp.db'
db = SQLAlchemy(app)


class MasterFileUpload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    number_of_columns = db.Column(db.Integer)
    procedure_name = db.Column(db.String(80))

    def __init__(self, title, number_of_columns=0, procedure_name=''):
        self.title=title
        self.number_of_columns = number_of_columns
        self.procedure_name = procedure_name

    def __repr__(self):
        return '<MFU %r>' % self.title

db.create_all()

def get_file_extension(filename):
    try:
        file_extension = filename.split('.')[-1]
        if file_extension in ['csv', 'xlxs']:
            return file_extension
    except:
        return False


def get_file_object(file, extension):
    print(file, extension)
    try:
        if extension == 'csv':
            return pandas.read_csv(file)
        elif extension == 'xlxs':
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
        a = file_object.to_sql('import_data', db.engine)
        print a
        return True
    except Exception as e:
        print e
        return False


@app.route("/upload", methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        master_file = request.form['upload_file']
        uploaded_file = request.files['file']
        upload_file_name = uploaded_file.filename
        print(upload_file_name)
        file_extension = get_file_extension(upload_file_name)
        if not file_extension:
            # TODO: Append to error json
            return 'file extension error'
        file_object = get_file_object(uploaded_file, file_extension)
        print file_object
        # if not file_object.bool():
        #     # TODO: Append to error json
        #     return 'file object error'
        file_headers = get_file_headers(file_object)
        print file_headers
        if not file_headers:
            # TODO: Append to error json
            return 'file header error'
        master_file_number_of_columns = get_number_of_columns(master_file)
        if master_file_number_of_columns != len(file_headers):
            # TODO: Return error json
            return
        if save_to_db(file_object, file_headers):
            return jsonify({"result": "True"})
        else:
            return jsonify({"result": "False"})
    file_types = MasterFileUpload.query.all()
    return render_template('home.html', file_types = file_types)


@app.route("/download", methods=['GET'])
def download_file():
    return excel.make_response_from_array([[1, 2], [3, 4]], "csv")


@app.route("/import", methods=['GET', 'POST'])
def doimport():
    if request.method == 'POST':
        print(request.files)
        return redirect(url_for('.handson_table'), code=302)
    return '''
    <!doctype html>
    <title>Upload an excel file</title>
    <h1>Excel file upload (xls, xlsx, ods please)</h1>
    <form action="" method=post enctype=multipart/form-data><p>
    <input type=file name=file><input type=submit value=Upload>
    </form>
    '''


@app.route("/export", methods=['GET'])
def doexport():
    return excel.make_response_from_tables(db.session, [MasterFileUpload], "xls")


@app.route("/custom_export", methods=['GET'])
def docustomexport():
    query_sets = Category.query.filter_by(id=1).all()
    column_names = ['id', 'name']
    return excel.make_response_from_query_sets(query_sets, column_names, "xls")


@app.route("/handson_view", methods=['GET'])
def handson_table():
    return excel.make_response_from_tables(
        db.session, [MasterFileUpload], 'handsontable.html')


if __name__ == "__main__":
    app.run()