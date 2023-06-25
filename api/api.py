import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configuración de la conexión a la base de datos PostgreSQL
conn = psycopg2.connect(
    host="mf.torresproject.com",
    database="postgres",
    user="postgres",
    password="Max2025",
    port="5433"
)

# Ruta para obtener información de los usuarios
@app.route('/users', methods=['GET'])
def obtener_usuarios():
    # Lógica para obtener los usuarios de la base de datos
    cur = conn.cursor()
    cur.execute("SELECT u_name, email FROM users")
    usuarios = cur.fetchall()

    # Retorna los usuarios en formato JSON
    return jsonify(usuarios)

# Ruta para obtener información de los ítems
@app.route('/items', methods=['GET'])
def obtener_items():
    # Lógica para obtener los ítems de la base de datos
    cur = conn.cursor()
    cur.execute("SELECT * FROM items")
    items = cur.fetchall()

    # Preparar los datos de los ítems en una lista de diccionarios
    lista_items = []
    for item in items:
        item_dict = {
            'id': item[0],
            'nombre': item[1],
            'precio': item[2],
            'descripcion': item[3]
        }
        lista_items.append(item_dict)

    # Retorna los ítems en formato JSON
    return jsonify(lista_items)

# Ruta para autenticar usuarios
@app.route('/login', methods=['POST'])
def iniciar_sesion():
    # Obtiene los datos de inicio de sesión desde la solicitud
    datos_sesion = request.get_json()

    # Lógica para autenticar al usuario
    usuario = datos_sesion['usuario']
    contraseña = datos_sesion['contraseña']

    # Verificar las credenciales del usuario en la base de datos
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE u_name = %s AND pass = %s", (usuario, contraseña))
    resultado = cur.fetchone()

    if resultado:
        # Autenticación exitosa
        return jsonify({'mensaje': 'Inicio de sesión exitoso'})
    else:
        # Autenticación fallida
        return jsonify({'mensaje': 'Error al iniciar sesión'})

# Ruta para crear una orden de compra
@app.route('/ordenes', methods=['POST'])
def crear_orden_compra():
    # Obtiene los datos de la orden desde la solicitud
    datos_orden = request.get_json()

    # Extraer los datos de la orden
    id_user = datos_orden['id_usuario']
    id_item = datos_orden['id_item']
    shop_date = datos_orden['fecha']
    value = datos_orden['valor']

    # Insertar la orden de compra en la base de datos
    cur = conn.cursor()
    cur.execute("INSERT INTO shop (id_user, id_item, shop_date, value) VALUES (%s, %s, %s, %s)",
                (id_user, id_item, shop_date, value))
    conn.commit()

    # Retorna una respuesta de éxito en formato JSON
    return jsonify({'mensaje': 'Orden de compra creada correctamente'})

if __name__ == '__main__':
    app.run(debug=True)



