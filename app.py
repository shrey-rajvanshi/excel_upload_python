from flask import Flask, request, jsonify, redirect, url_for, render_template
import flask_excel as excel
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
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


@app.route("/upload", methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        print("Master file upload is " + request.form.get('file_type'))
        print(request.files)
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