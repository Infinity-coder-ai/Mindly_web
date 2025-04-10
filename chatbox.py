from nicegui import ui

def show_chatbox(container):
    """Display the chatbox interface"""
    with container:
        ui.label('Chatbox').classes('text-xl font-semibold mb-4')
        with ui.column().classes('w-full gap-4'):
            ui.label('Connect with tutors and fellow students').classes('text-gray-600')
            
            # Chat display area
            with ui.card().classes('w-full'):
                ui.label('Chat Messages').classes('font-bold')
                
                # Messages container with scroll
                with ui.scroll_area().classes('p-4 bg-gray-100 rounded-lg min-h-80 w-full'):
                    with ui.column().classes('gap-2 w-full'):
                        # Sample messages
                        with ui.row().classes('justify-start w-full'):
                            with ui.card().classes('bg-white p-3 max-w-[70%]'):
                                ui.label('Professor Johnson').classes('text-xs text-blue-600 font-bold')
                                ui.label('Welcome to the course discussion! Feel free to ask any questions.').classes('text-sm')
                                ui.label('10:30 AM').classes('text-xs text-gray-500 text-right')
                        
                        with ui.row().classes('justify-end w-full'):
                            with ui.card().classes('bg-blue-100 p-3 max-w-[70%]'):
                                ui.label('You').classes('text-xs text-blue-800 font-bold')
                                ui.label('Thank you! When is the next assignment due?').classes('text-sm')
                                ui.label('10:31 AM').classes('text-xs text-gray-500 text-right')
                        
                        with ui.row().classes('justify-start w-full'):
                            with ui.card().classes('bg-white p-3 max-w-[70%]'):
                                ui.label('Professor Johnson').classes('text-xs text-blue-600 font-bold')
                                ui.label('The next assignment is due Friday at 11:59 PM. Don\'t forget to check the rubric!').classes('text-sm')
                                ui.label('10:32 AM').classes('text-xs text-gray-500 text-right')
            
            # Message input area with button
            with ui.row().classes('w-full gap-2 items-center'):
                message_input = ui.input('Type your message...').classes('flex-grow')
                ui.button('Send', on_click=lambda: send_message(message_input)).classes('bg-blue-600 text-white')

def send_message(input_field):
    """Handle sending a message"""
    if input_field.value.strip():
        ui.notify(f'Message sent: {input_field.value}', color='positive')
        input_field.value = ''
    else:
        ui.notify('Please enter a message', color='warning') 