from flask import Flask, render_template, request, redirect
from reconstruction import sfm, mvs, meshing

app = Flask(__name__)

@app.route("/")
def homepage():
    return render_template("index.html")

@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist('file')

    for file in files:
        if file.filename:
            file.save(f'colmap/images/{file.filename}')

    sfm.run_sfm()
    mvs.run_mvs()
    meshing.generate_mesh()

    return redirect('/')

if __name__ == "__app__":
    app.run(debug=True)