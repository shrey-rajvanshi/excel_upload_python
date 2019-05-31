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

def get_file_extension(file):
    file_name = file.filename
    try:
        file_extension = file_name.split('.')[-1]
        if file_extension in ['.csv', '.xlxs']:
            return file_extension
    except:
        return False


def get_file_object(file):
    try:
        if file_extension == '.csv':
            return panda.read_csv(file)
        elif file_extension == '.xlxs':
            return panda.read_excel(file)
    except:
        return False


def get_file_headers(file_object):
    return file_object.columns.values

# TODO: Get column from DB using upload file name
def get_number_of_columns(master_file):
    pass


def save(file_object):
    # TODO: For each sheet if excel
    file_object_dict = file_object.to_dict()
    for row in file_object_dict:
        # TODO: If type date then take first value
        pass

@app.route("/upload", methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        master_file = request.form['upload_file']
        uploaded_file = request.files['file']
        upload_file_name = uploaded_file.filename
        file_extension = get_file_extension(upload_file_name)
        if not file_extension:
            # TODO: Return error json
            return
        file_object = get_file_object(file)
        if not file_object:
            # TODO: Return error json
            return
        file_headers = get_file_headers(file_object)
        if not file_headers:
            # TODO: Return error json
            return
        master_file_number_of_columns = get_number_of_columns(master_file)
        if master_file_number_of_columns != len(file_headers):
            # TODO: Return error json
            return
        return jsonify({"result": request.get_array('file')})
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