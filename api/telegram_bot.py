from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from asgiref.sync import sync_to_async
from api.models import Pacientes, Citas, Usuarios, RegistrosClinicos, Doctores, TipoTratamiento, Tratamientos
from gtts import gTTS
import os
import tempfile
from api.models import AudioTemporal
from django.core.files import File
from pydub import AudioSegment
import time
import speech_recognition as sr  # Agregué la importación de SpeechRecognition

# Variables globales
paciente_consultado = {}
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

# Función para enviar el menú principal
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    paciente_consultado.pop(update.effective_chat.id, None)

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

    if query.data == "consultar_paciente":
        await query.edit_message_text("Por favor, escribe el ID del paciente que deseas consultar.")
    elif query.data == "doctores":
        doctores = await obtener_doctores()
        if doctores:
            respuesta = "👩‍⚕️👨‍⚕️ Lista de doctores disponibles:\n\n"
            for doctor in doctores:
                nombre = f"{doctor.usuario.nombre} {doctor.usuario.apellido}"
                especialidad = doctor.especialidad.nombre
                respuesta += f"- {nombre}: {especialidad}\n"
        else:
            respuesta = "⚠️ No hay doctores disponibles en este momento."
        await enviar_voz(update, context, respuesta)
        await mostrar_menu(update, context)
    elif query.data == "tratamientos":
        tratamientos = await obtener_tipos_tratamientos()
        if tratamientos:
            respuesta = "💉 Lista de tipos de tratamientos disponibles:\n\n"
            for tratamiento in tratamientos:
                respuesta += f"- {tratamiento.tipo_tratamiento}\n"
        else:
            respuesta = "⚠️ No hay tratamientos disponibles en este momento."
        await enviar_voz(update, context, respuesta)
        await mostrar_menu(update, context)
    elif query.data == "registro_tratamientos":
        tratamientos = await obtener_tratamientos_registrados()
        if tratamientos:
            respuesta = "📋 Lista de tratamientos registrados:\n\n"
            for tratamiento in tratamientos:
                tipo_tratamiento = tratamiento.tipo_tratamiento.tipo_tratamiento
                fecha_inicio = tratamiento.fecha_inicio.strftime('%d/%m/%Y') if tratamiento.fecha_inicio else "Sin fecha"
                fecha_fin = tratamiento.fecha_fin.strftime('%d/%m/%Y') if tratamiento.fecha_fin else "Sin fecha"
                respuesta += (
                    f"- Descripción: {tratamiento.descripcion}\n"
                    f"  Costo: ${tratamiento.costo}\n"
                    f"  Fecha Inicio: {fecha_inicio}\n"
                    f"  Fecha Fin: {fecha_fin}\n"
                    f"  Tipo: {tipo_tratamiento}\n\n"
                )
        else:
            respuesta = "⚠️ No hay tratamientos registrados en este momento."
        await enviar_voz(update, context, respuesta)
        await mostrar_menu(update, context)
    elif query.data == "audio_on":
        audio_habilitado[update.effective_chat.id] = True
        await query.edit_message_text("🎤 Las respuestas en audio ahora están habilitadas.")
        await mostrar_menu(update, context)
    elif query.data == "audio_off":
        audio_habilitado[update.effective_chat.id] = False
        await query.edit_message_text("🔇 Las respuestas en audio ahora están deshabilitadas.")
        await mostrar_menu(update, context)

# Función para manejar mensajes de texto
async def manejar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global paciente_consultado

    try:
        mensaje = update.message.text.strip()

        if mensaje.isdigit():
            paciente_id = int(mensaje)
            paciente = await obtener_paciente(paciente_id)
            paciente_consultado[update.effective_chat.id] = paciente_id

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

# Función para manejar audio
async def manejar_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        # Obtener el archivo de voz
        voice = update.message.voice
        if not voice:
            await update.message.reply_text("No se encontró un archivo de voz.")
            return

        # Obtener el archivo desde Telegram
        file = await context.bot.get_file(voice.file_id)
        ogg_path = "audio.ogg"
        wav_path = "audio.wav"

        # Descargar el archivo a la ubicación temporal
        await file.download_to_drive(ogg_path)
        print(f"Archivo descargado en: {ogg_path}")

        # Guardar el archivo en la base de datos temporal usando sync_to_async
        await guardar_audio_en_bd(update.effective_chat.id, ogg_path, f"{voice.file_id}.ogg")

        # Convertir el archivo OGG a WAV usando pydub
        audio = AudioSegment.from_file(ogg_path, format="ogg")
        audio.export(wav_path, format="wav")
        print(f"Archivo convertido a WAV en: {wav_path}")

        # Usar SpeechRecognition para convertir el audio a texto
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)

        texto = recognizer.recognize_google(audio_data, language="es-ES").strip().lower()

        # Opciones del menú y acciones relacionadas
        if texto == "consultar paciente":
            await update.message.reply_text("Has seleccionado Consultar Paciente.")
            await mostrar_menu(update, context)
        elif texto == "ver doctores":
            doctores = await obtener_doctores()
            respuesta = "Lista de doctores:\n" + "\n".join(
                [f"{doctor.usuario.nombre} - {doctor.especialidad.nombre}" for doctor in doctores]
            )
            await update.message.reply_text(respuesta)
        elif texto == "ver tipos de tratamientos":
            tratamientos = await obtener_tipos_tratamientos()
            respuesta = "Tipos de tratamientos disponibles:\n" + "\n".join(
                [tratamiento.tipo_tratamiento for tratamiento in tratamientos]
            )
            await update.message.reply_text(respuesta)
        elif texto == "ver tratamientos registrados":
            tratamientos = await obtener_tratamientos_registrados()
            respuesta = "Tratamientos registrados:\n" + "\n".join(
                [f"{tratamiento.descripcion} - Costo: {tratamiento.costo}" for tratamiento in tratamientos]
            )
            await update.message.reply_text(respuesta)
        elif texto == "activar audio":
            audio_habilitado[update.effective_chat.id] = True
            await update.message.reply_text("🎤 Las respuestas en audio ahora están habilitadas.")
        elif texto == "desactivar audio":
            audio_habilitado[update.effective_chat.id] = False
            await update.message.reply_text("🔇 Las respuestas en audio ahora están deshabilitadas.")
        else:
            await update.message.reply_text("No entendí eso. Por favor, selecciona una opción del menú.")

        # Limpieza de archivos locales
        os.remove(ogg_path)
        os.remove(wav_path)

    except sr.UnknownValueError:
        await update.message.reply_text("No se pudo reconocer el audio. Intenta enviar otro.")
    except sr.RequestError as e:
        await update.message.reply_text(f"Error al procesar el audio: {e}")
    except Exception as e:
        await update.message.reply_text(f"Error inesperado: {str(e)}")

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
def guardar_audio_en_bd(usuario_id, file_path, file_name):
    with open(file_path, "rb") as file_obj:
        audio_temporal = AudioTemporal(usuario_id=usuario_id)
        audio_temporal.archivo.save(file_name, File(file_obj))
        audio_temporal.save()

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
