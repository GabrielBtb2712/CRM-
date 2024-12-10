import speech_recognition as sr
import tempfile
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from asgiref.sync import sync_to_async
from api.models import Pacientes, Citas, Usuarios, RegistrosClinicos, Doctores, TipoTratamiento, Tratamientos
from gtts import gTTS
import os
import time

# Variable global para almacenar si el audio está habilitado para cada usuario
audio_habilitado = {}

# Token del bot
TOKEN = "7929273729:AAHijVdqGhZkKoPphDzulgwFx5x54RUT-3Q"

# Función para convertir texto a voz y enviar el archivo de audio
async def enviar_voz(update, context, texto):
    if audio_habilitado.get(update.effective_chat.id, False):  # Verifica si el audio está habilitado
        tts = gTTS(text=texto, lang='es')  # Generar el archivo de voz en español
        audio_path = "respuesta.mp3"
        tts.save(audio_path)  # Guardar el archivo de voz en un archivo MP3

        # Verificar si la interacción es por un mensaje o un callback
        if update.message:
            with open(audio_path, 'rb') as audio_file:
                await update.message.reply_voice(voice=audio_file)
        elif update.callback_query:
            with open(audio_path, 'rb') as audio_file:
                await update.callback_query.message.reply_voice(voice=audio_file)

        # Eliminar el archivo de audio después de enviarlo
        os.remove(audio_path)
    else:
        # Si el audio está deshabilitado, enviar el texto en lugar de voz
        if update.message:
            await update.message.reply_text(texto)
        elif update.callback_query:
            await update.callback_query.message.reply_text(texto)

# Función para manejar mensajes de audio (grabados con el ícono de micrófono en Telegram)
async def manejar_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        # Obtener el archivo de audio desde el mensaje (audio grabado con el micrófono en Telegram)
        audio_file = await update.message.voice.get_file()

        # Intentar obtener el archivo hasta 5 veces
        for attempt in range(5):
            try:
                # Descargar el archivo de audio de Telegram
                file_path = audio_file.file_path
                file = await context.bot.get_file(file_path)
                file.download('audio.ogg')  # Descargamos el archivo en formato OGG
                break  # Si lo conseguimos, salimos del bucle
            except Exception as e:
                print(f"Intento {attempt+1}: Error al obtener el archivo de audio: {str(e)}")
                time.sleep(2)  # Esperar 2 segundos antes de reintentar
        else:
            raise Exception("No se pudo obtener el archivo de audio después de varios intentos.")

        # Convertir el archivo OGG a WAV utilizando pydub
        from pydub import AudioSegment
        audio = AudioSegment.from_ogg("audio.ogg")
        audio.export("audio.wav", format="wav")

        # Usar SpeechRecognition para convertir el audio a texto
        recognizer = sr.Recognizer()

        # Cargar el archivo WAV y procesarlo
        with sr.AudioFile("audio.wav") as source:
            audio_data = recognizer.record(source)

        # Convertir audio a texto usando Google Speech Recognition
        texto = recognizer.recognize_google(audio_data, language="es-ES")

        await update.message.reply_text(f"Texto reconocido: {texto}")
        await mostrar_menu(update, context)
    except Exception as e:
        await update.message.reply_text(f"Error al procesar el audio: {str(e)}")

# Función para enviar el menú principal
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Consultar Paciente", callback_data="consultar_paciente")],
        [InlineKeyboardButton("Ver Doctores", callback_data="doctores")],
        [InlineKeyboardButton("Ver Tipos de Tratamientos", callback_data="tratamientos")],
        [InlineKeyboardButton("Ver Tratamientos Registrados", callback_data="registro_tratamientos")],
        [InlineKeyboardButton("Activar Audio", callback_data="audio_on")],
        [InlineKeyboardButton("Desactivar Audio", callback_data="audio_off")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    bienvenida = "👋 ¡Hola! Bienvenido a tu asistente de citas médicas. Selecciona una opción:"
    await update.message.reply_text(bienvenida, reply_markup=reply_markup)

# Función para manejar los botones del menú
async def manejar_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "audio_on":
        audio_habilitado[update.effective_chat.id] = True
        await query.edit_message_text("🎤 Las respuestas en audio ahora están habilitadas.")
        await mostrar_menu(update, context)  # Reabrir el menú inmediatamente
    elif query.data == "audio_off":
        audio_habilitado[update.effective_chat.id] = False
        await query.edit_message_text("🔇 Las respuestas en audio ahora están deshabilitadas.")
        await mostrar_menu(update, context)  # Reabrir el menú inmediatamente

# Función para manejar mensajes de texto
async def manejar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        mensaje = update.message.text.strip()

        if mensaje.isdigit():
            paciente_id = int(mensaje)
            paciente = await obtener_paciente(paciente_id)
            citas = await obtener_citas(paciente_id)

            if citas:
                respuesta = f"Próximas citas para el paciente con ID {paciente_id}:\n"
                for cita in citas:
                    doctor = f"{cita.doctor.usuario.nombre} {cita.doctor.usuario.apellido}" if cita.doctor else "Sin asignar"
                    fecha = cita.fecha.strftime('%d/%m/%Y') if cita.fecha else "Sin fecha"
                    hora = cita.hora.strftime('%H:%M') if cita.hora else "Sin hora"
                    respuesta += (
                        f"- Fecha: {fecha}\n"
                        f"  Hora: {hora}\n"
                        f"  Servicio: {cita.servicio}\n"
                        f"  Estado: {cita.estado}\n"
                        f"  Doctor: {doctor}\n"
                        f"  Descripción: {cita.descripcion or 'Sin descripción'}\n"
                        f"  Comentarios: {cita.comentarios or 'Sin comentarios'}\n\n"
                    )
                await enviar_voz(update, context, respuesta)
            else:
                respuesta = f"El paciente con ID {paciente_id} no tiene citas programadas."
                await enviar_voz(update, context, respuesta)

            # Reabrir el menú
            await mostrar_menu(update, context)
        else:
            respuesta = "⚠️ No entendí eso. Por favor, selecciona una opción del menú o escribe un ID válido."
            await enviar_voz(update, context, respuesta)
            await mostrar_menu(update, context)
    except Exception as e:
        await update.message.reply_text(f"Error inesperado: {str(e)}")

# Función para mostrar el menú principal
async def mostrar_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Consultar Paciente", callback_data="consultar_paciente")],
        [InlineKeyboardButton("Ver Doctores", callback_data="doctores")],
        [InlineKeyboardButton("Ver Tipos de Tratamientos", callback_data="tratamientos")],
        [InlineKeyboardButton("Ver Tratamientos Registrados", callback_data="registro_tratamientos")],
        [InlineKeyboardButton("Activar Audio", callback_data="audio_on")],
        [InlineKeyboardButton("Desactivar Audio", callback_data="audio_off")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:  # Si el mensaje proviene de texto
        await update.message.reply_text("🔄 ¿Qué más necesitas? Selecciona una opción:", reply_markup=reply_markup)
    elif update.callback_query:  # Si el mensaje proviene de un botón
        await update.callback_query.message.reply_text("🔄 ¿Qué más necesitas? Selecciona una opción:", reply_markup=reply_markup)

# Funciones de consulta a la base de datos
@sync_to_async
def obtener_paciente(paciente_id):
    return Pacientes.objects.get(pk=paciente_id)

@sync_to_async
def obtener_citas(paciente_id):
    return list(
        Citas.objects.filter(paciente_id=paciente_id)
        .select_related("doctor__usuario")
        .order_by("fecha", "hora")
    )

@sync_to_async
def obtener_doctores():
    return list(Doctores.objects.select_related("especialidad", "usuario"))

@sync_to_async
def obtener_tipos_tratamientos():
    return list(TipoTratamiento.objects.all())

@sync_to_async
def obtener_tratamientos_registrados():
    return list(Tratamientos.objects.select_related("tipo_tratamiento").all())

# Configuración principal del bot
def main():
    print("Iniciando el bot...")
    app = ApplicationBuilder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(manejar_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_mensaje))
    app.add_handler(MessageHandler(filters.VOICE, manejar_audio))  # Handler para audios grabados

    print("Bot configurado y ejecutándose...")
    app.run_polling()

if __name__ == "__main__":
    main()
