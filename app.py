### Backend usando Pyhton Flask y MongoDB con JWT y Bcrypt ###
### Universidad Anahuac Mayab
### Prog de Dispositivos Móviles

#Importamos todo lo necesario para que funcione el backend
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from models import mongo, init_db
from config import Config
from bson import ObjectId
from flask_bcrypt import Bcrypt
from flask_jwt_extended import get_jwt_identity


#Inicializamos la aplicación y usamos el config file
app = Flask(__name__) #sintaxis para inicializar flask porque la app es de Flask
app.config.from_object(Config)

#Inicializamos a bcrypt y jwt
bcrypt = Bcrypt(app)
jwt=JWTManager(app)

#Inicializamos el acceso a MongoDB
init_db(app)


#Definimos el endpoint para registrar un usuario
#Utilizamos el decorador @app.route('/') para definir la ruta de la URL e inmediantament después
#la función que se ejecutará en esa ruta

#Endpoint para registrar un usuario
@app.route('/register', methods=['POST']) #ruta
def register(): #inmediatamente se pone la función que se rebe ejecutar tras poner la ruta
    data = request.get_json() 
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if mongo.db.users.find_one({"email": email}):
        return jsonify({"msg": "Ese usuario ya existe"}), 400 
     
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    

    result = mongo.db.users.insert_one({
        "username":username, 
        "email":email,
        "password":hashed_password})

    if result.acknowledged:
        return jsonify({"msg": "Usuario Creado Correctamente"}), 201
    else:
        return jsonify({"msg": "Hubo un error, no se pudieron guardar los datos"}), 400

# Endpoint para la ruta login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = mongo.db.users.find_one({"email": email})

    if user and bcrypt.check_password_hash(user['password'], password): #si el usuario existe y el password introducido es igual al password hasheado...
        access_token= create_access_token(identity=str(user["_id"]))
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Credenciales incorrectas"}), 401


# Endpoint para el registro del sistema (Planta de tratamiento de aguas residuales AQUOX)
@app.route('/sistema', methods=['POST'])
@jwt_required()
def create_sistema():
    data = request.get_json()
    titulo = data.get('titulo')
    codigo_sistema = data.get('codigo_sistema')

    #Obtener la identidad del usuario a partir del JWT
    user_id = get_jwt_identity()
    
     #Verificar si el código del sistema ya está registrado por el mismo usuario
    if mongo.db.sistemas.find_one({"codigo_sistema": codigo_sistema, "user_id": user_id}):
        return jsonify({"msg": "Ya has registrado este sistema anteriormente"}), 400

    #Insertar los datos para el nuevo sistema
    result = mongo.db.sistemas.insert_one({
        "user_id": user_id,  # Relaciona el sistema con el usuario
        "titulo": titulo,
        "codigo_sistema": codigo_sistema,
        "csv_link": ""  # Esto lo agregaremos más adelante
    })

    if result.acknowledged:
        return jsonify({"msg": "Sistema registrado correctamente"}), 201
    else:
        return jsonify({"msg": "Error al registrar el sistema"}), 400


#Endpoint para obtener información de los sistemas registrados
@app.route('/sistema', methods=['GET'])
@jwt_required()
def get_sistemas():
    user_id = get_jwt_identity()

    # Buscar todos los sistemas asociados al usuario actual
    sistemas = list(mongo.db.sistemas.find({"user_id": user_id}, {"_id": 0, "user_id":0}))

    return jsonify(sistemas), 200


# Endpoint para actualización de datos del sistema
@app.route('/sistema/<codigo_sistema>', methods=['PUT'])
@jwt_required()
def update_sistema(codigo_sistema):
    data = request.get_json()
    new_titulo = data.get('titulo')
    new_csv_link = data.get('csv_link')

    # Crear el diccionario de campos a actualizar solo si no están vacíos
    update_fields = {}
    if new_titulo:
        update_fields['titulo'] = new_titulo
    if new_csv_link:
        update_fields['csv_link'] = new_csv_link


    # Realizar la actualización para los campos que se modificaron
    result = mongo.db.sistemas.update_one(
        {"codigo_sistema": codigo_sistema, "user_id": get_jwt_identity()},
        {"$set": update_fields}
    )

    if result.modified_count > 0:
        return jsonify({"msg": "Sistema actualizado con éxito"}), 200
    else:
        return jsonify({"msg": "No se pudo actualizar el sistema"}), 400


# Endpoint para eliminar un sistema registrado
@app.route('/sistema/<codigo_sistema>', methods=['DELETE'])
@jwt_required()
def delete_sistema(codigo_sistema):
    result = mongo.db.sistemas.delete_one({
        "codigo_sistema": codigo_sistema, "user_id": get_jwt_identity()
    })

    if result.deleted_count > 0:
        return jsonify({"msg": "Sistema eliminado con éxito"}), 200
    else:
        return jsonify({"msg": "No se pudo eliminar el sistema"}), 400




#En Python, cada archivo tiene una variable especial llamada __name__.
#Si el archivo se esta ejecutando directamente (no importado como un módulo en otro archivo),
#__name__ se establece en '__main__'
#Esta condición verifica si el archivo actual es el archivo principal que se está ejecutando,
#Si es así, ejecuta el bloque de código dentro de la condición.
#app.run() inicia el servidor web de Flask
#El argumento debug=True inicia el servidor web de desarrollo de Flask con el modo de
#depuración activado, lo que permite ver errores detallados y reiniciar automáticamente
#el servidor cuando se se realizan cambios en el código. (SERIA COMO EL NODEMON)

if __name__ == '__main__':
    app.run(debug=True)
