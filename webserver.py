from flask import Flask, render_template, redirect, url_for, request, send_file
from werkzeug.utils import secure_filename
import pymysql.cursors
import os
import uuid

app = Flask(__name__)
BASE_DIR = 'http://192.168.2.250/media/'
@app.route("/diagnosis")
def diagnosis():
    #try:
    #    connection = pymysql.connect(host='192.168.2.250',
    #                                 port=3306,
    #                                 user='LOCMAN',
    #                                 password='A1s@d3f4G5',
    #                                 db='Umbrellas',
    #                                 charset='utf8',
    #                                 cursorclass=pymysql.cursors.DictCursor)
    #    with connection:
    #        cur = connection.cursor()
    #        print(id)
    #        cur.execute("SELECT id, fsrar_id FROM mainpage_checks WHERE id = %s", id)
    #        print("tick")
    #        rows = cur.fetchall()
    #        for row in rows:
    #            fsrarid = row.get('fsrar_id')
    #        print(fsrarid)
    #    connection.close()
    #except:
    #    pass
    fsrarid = '010000005002'
    return render_template('index.html', fsrarid=fsrarid)

@app.route("/info/certificate/RSA")
def oldutm():
    return redirect(url_for('diagnosis'), code=302)

#@app.route("/opt/in/QueryPartner/111")
def allowed_file(filename):
        ALLOWED_EXTENSIONS = set(['xml', 'xsd'])
        return '.' in filename and \
               filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def uniqueID():
    return uuid.uuid4()

#@app.route("/opt/in/QueryRests_v2", methods=['GET', 'POST'])
def QueryRest_v2():
        UPLOAD_FOLDER = 'querys/queryrests_v2'
        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        if request.method == 'POST':
            file = request.files['xml_file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                print(filename)
                print(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return render_template('answer.html', unique_id = uniqueID())


@app.route("/opt/in/<type_doc>", methods=['GET', 'POST'])
def Query(type_doc):
        UPLOAD_FOLDER = 'querys/' + type_doc
        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        UID = uniqueID()
        fsrarid = '010000005002'
        id = '37'
        if request.method == 'POST':
            file = request.files['xml_file']
            print(file)
            if file and allowed_file(file.filename):
                print('File')
                filename = fsrarid + '_' + str(UID) + '_' + type_doc + '.xml'
                print('File name is: ', filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                try:
                    connection = pymysql.connect(host='192.168.2.250',
                                                 port=3306,
                                                 user='LOCMAN',
                                                 password='A1s@d3f4G5',
                                                 db='Umbrellas',
                                                 charset='utf8',
                                                 cursorclass=pymysql.cursors.DictCursor)
                    with connection:
                        cur = connection.cursor()
                        cur.execute("INSERT INTO mainpage_queryes(dot_id, fsrar_id, query, type, unique_id, unique_id_utm, Ticket, Reply, status) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');" % (
                                id, fsrarid, 'queryes/' + type_doc + '/' + filename, type_doc, UID, 'utm', 'Ticket', 'Reply', '0'))
                        print("tick")
                    connection.close()
                except Exception as e:
                    print('Error: ', e)
                return render_template('answer.html', unique_id = UID)


@app.route("/media/Queryes/<type_doc>/<document>")
def document(type_doc = None, document = None):
    if 'Ticket' in document:
        tmp = document.split('_')
        document = tmp[0] + '_' + tmp[1] + '_' + tmp[2] + '.xml'
    print('1c came here', type_doc, document)
    path = 'querys/' + type_doc + '/' + document
    print(path)
    return send_file(path, as_attachment=True)

@app.route("/opt/out")
def list_documents():
    fsrarid = '010000005002'
    try:
        connection = pymysql.connect(host='192.168.2.250',
                                     port=3306,
                                     user='LOCMAN',
                                     password='A1s@d3f4G5',
                                     db='Umbrellas',
                                     charset='utf8',
                                     cursorclass=pymysql.cursors.DictCursor)
        with connection:
            cur = connection.cursor()
            cur.execute("SELECT * FROM mainpage_queryes WHERE fsrar_id = '%s' AND status = '2';" % (fsrarid))
            replyes = cur.fetchall()
            print(replyes[0])
            print(replyes[0]['unique_id'])
            print(BASE_DIR + replyes[0]['Reply'][:-4])
        connection.close()
    except Exception as e:
        print('Error: ', e)
    return render_template("list.xml", replyes = replyes, BASE_DIR = BASE_DIR)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8081)