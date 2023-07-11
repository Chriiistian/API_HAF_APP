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

# Ruta para el inicio de sesión
@app.route('/login', methods=['POST'])
def login():
    # Obtiene los datos del inicio de sesión desde la solicitud
    datos_login = request.get_json()

    # Extraer los datos del inicio de sesión
    email = datos_login['email']
    passw = datos_login['password']

    # Verificar las credenciales de inicio de sesión en la base de datos
    cur = conn.cursor()
    cur.execute("SELECT id, u_name, type_user, email FROM users WHERE email = %s AND passw = %s", (email, passw))
    user = cur.fetchone()

    if user is not None:
        # Las credenciales de inicio de sesión son correctas
        user_data = {
            'id': user[0],
            'name': user[1],
            'type_user': user[2],
            'email': user[3]
        }
        return jsonify({'mensaje': 'Inicio de sesión exitoso', 'user': user_data})
    else:
        # Las credenciales de inicio de sesión son incorrectas
        return jsonify({'mensaje': 'Credenciales de inicio de sesión incorrectas'}), 401


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
            'name': item[1],
            'price': item[2],
            'descripcion': item[3],
            'qty': item[4],
            'category': item[5]
        }
        lista_items.append(item_dict)

    # Retorna los ítems en formato JSON
    return jsonify(lista_items)

# Ruta para crear órdenes de compra
@app.route('/ordenes', methods=['POST'])
def crear_ordenes_compra():
    # Obtiene los datos de las órdenes desde la solicitud
    datos_ordenes = request.get_json()

    # Obtener el último ID de orden de compra
    cur = conn.cursor()
    cur.execute("SELECT MAX(id) FROM shop")
    last_order_id = cur.fetchone()[0]
    if last_order_id is None:
        last_order_id = 0

    for datos_orden in datos_ordenes:
        # Generar un nuevo ID para la orden de compra
        new_order_id = last_order_id + 1

        # Extraer los datos de cada orden
        value = datos_orden['valor']
        shop_date = datos_orden['fecha']
        id_item = datos_orden['id_item']
        id_user = datos_orden['id_user']

        # Insertar la orden de compra en la base de datos
        cur.execute("INSERT INTO shop (id, id_user, id_item, shop_date, value) VALUES (%s, %s, %s, %s, %s)",
                    (new_order_id, id_user, id_item, shop_date, value))
        conn.commit()

        # Actualizar el último ID de orden de compra
        last_order_id = new_order_id

    # Retorna una respuesta de éxito en formato JSON
    return jsonify({'mensaje': 'Órdenes de compra creadas correctamente'})

# Ruta para obtener las compras del usuario
@app.route('/purchases', methods=['GET'])
def obtener_compras():
    # Obtiene el ID de usuario de la solicitud
    user_id = request.args.get('user_id')

    # Lógica para obtener las compras del usuario desde la base de datos
    cur = conn.cursor()
    cur.execute("SELECT * FROM shop WHERE id_user = %s", (user_id,))
    purchases = cur.fetchall()

    # Preparar los datos de las compras en una lista de diccionarios
    lista_compras = []
    for purchase in purchases:
        purchase_dict = {
            'id': purchase[0],
            'amount': purchase[4],
            'date': purchase[3],
        }
        lista_compras.append(purchase_dict)

    # Retorna las compras en formato JSON
    return jsonify(lista_compras)

# Ruta para cambiar la contraseña
@app.route('/change_password', methods=['POST'])
def change_password():
    # Obtiene los datos del cambio de contraseña desde la solicitud
    datos_cambio = request.get_json()

    # Extraer los datos del cambio de contraseña
    current_password = datos_cambio['current_password']
    new_password = datos_cambio['new_password']
    user_id = datos_cambio['user_id']

    # Verificar las credenciales de inicio de sesión en la base de datos
    cur = conn.cursor()
    cur.execute("SELECT passw FROM users WHERE id = %s", (user_id,))
    user_password = cur.fetchone()

    if user_password is not None and user_password[0] == current_password:
        # Cambiar la contraseña en la base de datos
        cur.execute("UPDATE users SET passw = %s WHERE id = %s", (new_password, user_id))
        conn.commit()

        # Retorna una respuesta de éxito en formato JSON
        return jsonify({'mensaje': 'La contraseña ha sido cambiada exitosamente'})
    else:
        # La contraseña actual es incorrecta
        return jsonify({'mensaje': 'La contraseña actual es incorrecta'}), 401

if __name__ == '__main__':
    app.run(debug=True, port=8000)
