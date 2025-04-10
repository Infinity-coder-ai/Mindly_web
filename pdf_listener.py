from nicegui import ui
import pyttsx3
from PyPDF2 import PdfReader
import io
import threading
import tempfile
import os

def show_pdf_listener(container):
    """Display the PDF listener interface"""
    with container:
        ui.label('PDF Listener').classes('text-xl font-semibold mb-4')
        with ui.column().classes('w-full gap-4'):
            ui.label('Upload PDF documents to listen to their content').classes('text-gray-600')
            
            # Create a container for the audio controls
            audio_container = ui.element('div').classes('w-full mt-4')
            
            # File upload section
            with ui.card().classes('w-full p-4'):
                ui.label('Upload PDF').classes('font-bold mb-2')
                with ui.upload(auto_upload=True, on_upload=lambda e: handle_pdf_upload(e, audio_container)).classes('w-full'):
                    ui.button('Select File').props('flat color=purple')
                ui.label('Supported formats: PDF').classes('text-xs text-gray-500 mt-1')

def extract_text_from_pdf(file_content):
    """Extract text from PDF content"""
    pdf_reader = PdfReader(io.BytesIO(file_content))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def text_to_speech(text, filename, audio_container):
    """Convert text to speech and save as audio file"""
    try:
        # Initialize the text-to-speech engine
        engine = pyttsx3.init()
        
        # Create temporary file for audio
        temp_dir = tempfile.gettempdir()
        audio_path = os.path.join(temp_dir, f"{filename}.mp3")
        
        # Convert text to speech and save
        engine.save_to_file(text, audio_path)
        engine.runAndWait()
        
        # Update UI with audio player
        with audio_container:
            ui.label(f'Listening to: {filename}').classes('font-bold mt-4 mb-2')
            
            with ui.card().classes('w-full p-4'):
                ui.label('Audio Player').classes('font-bold mb-2')
                
                # Add audio player
                ui.audio(audio_path).classes('w-full')
                
                # Add controls row
                with ui.row().classes('mt-4 gap-2'):
                    # Download audio button
                    ui.button('Download Audio', 
                             on_click=lambda: ui.download(src=audio_path, filename=f"{filename}.mp3")
                            ).props('icon=download color=green')
                    
                    # Close button
                    ui.button('Close', on_click=lambda: (
                        audio_container.clear(),
                        os.remove(audio_path) if os.path.exists(audio_path) else None
                    )).props('icon=close color=red')
        
        # Clean up temporary file after 5 minutes
        ui.timer(300.0, lambda: os.remove(audio_path) if os.path.exists(audio_path) else None, once=True)
                
    except Exception as e:
        ui.notify(f'Error converting to speech: {str(e)}', color='negative')
        print(f"Text-to-speech error: {str(e)}")

def handle_pdf_upload(event, audio_container):
    """Handle PDF file upload and convert to audio"""
    try:
        filename = event.name
        
        # Clear the audio container
        audio_container.clear()
        
        # Display processing message
        ui.notify('Processing PDF, please wait...', color='info')
        
        # Get the file content
        if hasattr(event, 'content'):
            if hasattr(event.content, 'read'):
                file_content = event.content.read()
            else:
                file_content = event.content
        else:
            raise Exception("No file content found in upload event")

        # Extract text from PDF
        text = extract_text_from_pdf(file_content)
        
        if not text.strip():
            raise Exception("No readable text found in the PDF")
            
        # Convert text to speech in a separate thread to prevent UI blocking
        thread = threading.Thread(
            target=text_to_speech,
            args=(text, filename.rsplit('.', 1)[0], audio_container)
        )
        thread.start()
        
        ui.notify(f'Converting {filename} to audio...', color='positive')
        
    except Exception as e:
        ui.notify(f'Error processing PDF: {str(e)}', color='negative')
        print(f"PDF processing error: {str(e)}")
        
        # Show error details in the container
        with audio_container:
            ui.label('Error Processing PDF').classes('text-lg font-bold text-red-500 mt-4')
            ui.label(str(e)).classes('text-sm text-red-500')
            ui.label('Please try a different PDF file').classes('text-sm mt-2') 