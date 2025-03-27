from flask import Flask, jsonify, request
from heyoo import WhatsApp
import openai
from openai import OpenAI
import config

client = OpenAI(api_key=config.openaiKey)

app = Flask(__name__)
#CUANDO RECIBAMOS LAS PETICIONES EN ESTA RUTA
@app.route("/chatbot/", methods=["POST", "GET"])
def chatbot():
    #SI HAY DATOS RECIBIDOS VIA GET
    if request.method == "GET":
        #SI EL TOKEN ES IGUAL AL QUE RECIBIMOS
        if request.args.get('hub.verify_token') == config.token:
            #ESCRIBIMOS EN EL NAVEGADOR EL VALOR DEL RETO RECIBIDO DESDE FACEBOOK
            return request.args.get('hub.challenge')
        else:
            #SI NO SON IGUALES RETORNAMOS UN MENSAJE DE ERROR
          return "Error de autentificacion."
    #RECIBIMOS TODOS LOS DATOS ENVIADO VIA JSON
    data=request.get_json()
    print("D:", data)
    #EXTRAEMOS EL NUMERO DE TELEFONO Y EL MENSAJE
    checkNumber = data['entry'][0]['changes'][0]['value']
    print("C:", checkNumber)
    if checkNumber.get('messages'):
        telefonoCliente=data['entry'][0]['changes'][0]['value']['messages'][0]['from']
    else:
        telefonoCliente=data['entry'][0]['changes'][0]['value']['statuses'][0]['recipient_id']
    print("N:",  telefonoCliente)
    nombreCliente=data['entry'][0]['changes'][0]['value']['contacts'][0]['profile']['name']
    #EXTRAEMOS EL TELEFONO DEL CLIENTE
    mensaje=data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
    #EXTRAEMOS EL ID DE WHATSAPP DEL ARRAY
    idWA=data['entry'][0]['changes'][0]['value']['messages'][0]['id']
    #EXTRAEMOS EL TIEMPO DE WHATSAPP DEL ARRAY
    timestamp=data['entry'][0]['changes'][0]['value']['messages'][0]['timestamp']
    #ESCRIBIMOS EL NUMERO DE TELEFONO Y EL MENSAJE EN EL ARCHIVO TEXTO
    #SI HAY UN MENSAJE
    print("M:", mensaje)
    if mensaje is not None:
      respuesta = generate_response(mensaje)
      enviar(telefonoCliente,respuesta)
      #RETORNAMOS EL STATUS EN UN JSON
      return jsonify({"status": "success"}, 200)

def generate_response(prompt):
    prompt = (f"{prompt}")

    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Eres un asistente que tiene muchos conocimientos sobre Inteligencia Artificial."},
        {
            "role": "user",
            "content": prompt
        }
      ]
    )

    message = completion.choices[0].message.content
    print("response", message)
    return message

def enviar(telefonoRecibe,respuesta):
  #TOKEN DE ACCESO DE FACEBOOK
  token=config.whatsapp_token
  #IDENTIFICADOR DE N MERO DE TELEFONO
  idNumeroTelefono=config.idTelefono
  #INICIALIZAMOS ENVIO DE MENSAJES
  mensajeWa=WhatsApp(token,idNumeroTelefono)
  telefonoRecibe=telefonoRecibe.replace("521","52")
  #ENVIAMOS UN MENSAJE DE TEXTO
  #respuesta = "Hola " + str(nombreCliente) + " ," + str(respuesta)
  mensajeWa.send_message(respuesta,telefonoRecibe)

#INICIAMOS EL SERVIDOR
if __name__ == "__main__":
  app.run(debug=True)
