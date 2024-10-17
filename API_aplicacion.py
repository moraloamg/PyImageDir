#EN PROCESO DE CONSTRUCCIÓN, SOLO HAY EJEMPLOS.
#TODO AQUI SE DEBERÍA DE ABRIR O ARRANCAR LA APLICACION CON FLASK O COSAS SIMILARES, O QUIZA HACERLO EN OTRO ARCHIVO DE PYTHON
#TODO ¿UTILIZAR PYINSTALLER?
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/submit-form', methods=['POST'])
def submit_form():
    data = request.json
    folder_path = data.get('folder_path')
    width = data.get('ancho')
    height = data.get('alto')
    option1 = data.get('opcion1')
    option2 = data.get('opcion2')
    
    # Aquí puedes trabajar con los archivos del directorio y otros datos
    response = {
        'folder_path': folder_path,
        'ancho': width,
        'alto': height,
        'opcion1': option1,
        'opcion2': option2
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
