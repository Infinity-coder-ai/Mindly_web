from nicegui import ui
from database import Database

db = Database()

def show_notes(container, user_id):
    """Display the notes interface"""
    with container:
        ui.label('Notes').classes('text-xl font-semibold mb-4')
        with ui.column().classes('w-full gap-4'):
            ui.label('Choose your note format').classes('text-gray-600')
            
            # Note format selection with clear descriptions
            with ui.row().classes('w-full gap-4'):
                with ui.card().classes('flex-grow p-6 cursor-pointer hover:shadow-lg transition-shadow').on('click', lambda: show_flashcards(container, user_id)):
                    with ui.column().classes('items-center gap-3'):
                        ui.icon('style').classes('text-3xl text-blue-600')
                        ui.label('Quick Memory Cards').classes('text-lg font-semibold')
                        ui.label('Formulas & Key Concepts').classes('text-sm text-gray-600 mb-2')
                        with ui.column().classes('text-xs text-gray-600 text-center'):
                            ui.label('• Mathematical formulas')
                            ui.label('• Scientific equations')
                            ui.label('• Important definitions')
                            ui.label('• Quick reference notes')
                
                with ui.card().classes('flex-grow p-6 cursor-pointer hover:shadow-lg transition-shadow').on('click', lambda: show_essays(container, user_id)):
                    with ui.column().classes('items-center gap-3'):
                        ui.icon('article').classes('text-3xl text-green-600')
                        ui.label('Essays & Long Notes').classes('text-lg font-semibold')
                        ui.label('Detailed study content').classes('text-sm text-gray-600 mb-2')
                        with ui.column().classes('text-xs text-gray-600 text-center'):
                            ui.label('• Comprehensive notes')
                            ui.label('• Detailed explanations')
                            ui.label('• Chapter summaries')
                            ui.label('• Research content')

def show_flashcards(container, user_id):
    """Display flashcards interface"""
    container.clear()
    with container:
        ui.label('Quick Memory Cards').classes('text-xl font-semibold mb-4')
        with ui.column().classes('w-full gap-4'):
            # Add new flashcard button
            with ui.row().classes('w-full justify-between items-center'):
                ui.label('Your Formulas & Concepts').classes('font-bold')
                ui.button('Add Formula/Concept', on_click=lambda: show_add_flashcard_dialog(user_id)).classes('bg-blue-600 text-white text-sm')
            
            ui.label('Store important formulas and concepts for quick reference').classes('text-sm text-gray-600 mb-4')
            
            # Load existing flashcards
            load_flashcards(user_id)

def show_essays(container, user_id):
    """Display essays interface"""
    container.clear()
    with container:
        ui.label('Essays & Long Notes').classes('text-xl font-semibold mb-4')
        with ui.column().classes('w-full gap-4'):
            # Add new essay button
            with ui.row().classes('w-full justify-between items-center'):
                ui.label('Your Study Notes').classes('font-bold')
                ui.button('Add Long Note', on_click=lambda: show_add_essay_dialog(user_id)).classes('bg-green-600 text-white text-sm')
            
            ui.label('Write detailed notes and comprehensive study content').classes('text-sm text-gray-600 mb-4')
            
            # Load existing essays
            load_essays(user_id)

def show_add_flashcard_dialog(user_id):
    """Show dialog to add a new flashcard"""
    with ui.dialog() as dialog, ui.card().classes('p-4 w-[500px]'):
        ui.label('Add Formula or Concept').classes('text-lg font-bold mb-4')
        
        title = ui.input('Title (e.g., "Pythagorean Theorem", "Newton\'s Second Law")').classes('w-full mb-3')
        content = ui.textarea('Formula/Content').classes('w-full mb-3 font-mono').props('rows=3')
        
        # Example placeholder with better formatting
        with ui.card().classes('w-full p-3 bg-gray-50 mb-4'):
            ui.label('Examples:').classes('font-semibold mb-2')
            with ui.column().classes('gap-2 text-sm'):
                with ui.row().classes('w-full'):
                    ui.label('Title:').classes('font-semibold w-24')
                    ui.label('Pythagorean Theorem')
                with ui.row().classes('w-full'):
                    ui.label('Formula:').classes('font-semibold w-24')
                    ui.label('a² + b² = c²').classes('font-mono')
                ui.separator()
                with ui.row().classes('w-full'):
                    ui.label('Title:').classes('font-semibold w-24')
                    ui.label('Quadratic Formula')
                with ui.row().classes('w-full'):
                    ui.label('Formula:').classes('font-semibold w-24')
                    ui.label('x = (-b ± √(b² - 4ac)) / 2a').classes('font-mono')
        
        with ui.row().classes('w-full justify-end gap-2 mt-4'):
            ui.button('Cancel', on_click=dialog.close).props('flat')
            ui.button('Save Formula', on_click=lambda: save_flashcard(
                user_id,
                title.value,
                content.value,
                dialog
            )).classes('bg-blue-600 text-white')
    
    dialog.open()

def show_add_essay_dialog(user_id):
    """Show dialog to add a new essay"""
    with ui.dialog() as dialog, ui.card().classes('p-4 w-[800px]'):
        ui.label('Add Long Study Note').classes('text-lg font-bold mb-4')
        
        title = ui.input('Title of your note').classes('w-full mb-2')
        category = ui.input('Subject/Topic').classes('w-full mb-2')
        content = ui.textarea('Your detailed notes').classes('w-full mb-2').props('rows=15')
        
        # Formatting tips
        with ui.column().classes('text-xs text-gray-600 mb-4'):
            ui.label('Tips for good notes:')
            ui.label('• Use headings to organize content')
            ui.label('• Include examples and explanations')
            ui.label('• Add references if applicable')
        
        with ui.row().classes('w-full justify-end gap-2 mt-4'):
            ui.button('Cancel', on_click=dialog.close).props('flat')
            ui.button('Save Note', on_click=lambda: save_essay(
                user_id,
                title.value,
                content.value,
                category.value,
                dialog
            )).classes('bg-green-600 text-white')
    
    dialog.open()

def save_flashcard(user_id, title, content, dialog):
    """Save a new flashcard to the database"""
    if not title or not content:
        ui.notify('Title and content are required', color='warning')
        return
        
    try:
        cursor = db.connection.cursor()
        cursor.execute("""
            INSERT INTO flashcards (user_id, title, content)
            VALUES (%s, %s, %s)
        """, (user_id, title, content))
        db.connection.commit()
        cursor.close()
        
        ui.notify('Formula/concept saved successfully', color='positive')
        dialog.close()
        load_flashcards(user_id)
    except Exception as e:
        ui.notify(f"Error saving formula/concept: {str(e)}", color='negative')

def save_essay(user_id, title, content, category, dialog):
    """Save a new essay to the database"""
    if not title or not content:
        ui.notify('Title and content are required', color='warning')
        return
        
    try:
        cursor = db.connection.cursor()
        cursor.execute("""
            INSERT INTO essays (user_id, title, content, category)
            VALUES (%s, %s, %s, %s)
        """, (user_id, title, content, category))
        db.connection.commit()
        cursor.close()
        
        ui.notify(f'Study note "{title}" saved successfully', color='positive')
        dialog.close()
        load_essays(user_id)
    except Exception as e:
        ui.notify(f"Error saving note: {str(e)}", color='negative')

def load_flashcards(user_id):
    """Load flashcards from database"""
    try:
        cursor = db.connection.cursor(dictionary=True)
        print("check this yask",user_id )
        cursor.execute("""
            SELECT * FROM flashcards 
            WHERE user_id = %s 
            ORDER BY created_at DESC
        """, (user_id,))
        flashcards = cursor.fetchall()
        cursor.close()
        
        with ui.column().classes('w-full gap-2 mt-2'):
            for card in flashcards:
                with ui.card().classes('w-full p-4 hover:shadow-md transition-shadow'):
                    # Title area
                    with ui.row().classes('w-full justify-between items-center mb-3'):
                        ui.label(card['title']).classes('text-lg font-semibold text-blue-600')
                        ui.button(icon='delete', on_click=lambda card_id=card['id']: delete_flashcard(card_id, user_id)).classes('text-red-600')
                    
                    # Formula/content area with better formatting for mathematical content
                    with ui.card().classes('w-full p-4 bg-blue-50 flex items-center justify-center'):
                        ui.label(card['content']).classes('font-mono text-xl text-center')
                    
                    # Creation date in footer
                    with ui.row().classes('w-full justify-end mt-2'):
                        ui.label(card['created_at'].strftime('%Y-%m-%d %H:%M')).classes('text-xs text-gray-600')

    except Exception as e:
        ui.notify(f"Error loading formulas/concepts: {str(e)}", color='negative')

def load_essays(user_id):
    """Load essays from database"""
    try:
        cursor = db.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM essays 
            WHERE user_id = %s 
            ORDER BY created_at DESC
        """, (user_id,))
        essays = cursor.fetchall()
        cursor.close()
        
        with ui.column().classes('w-full gap-4 mt-2'):
            for essay in essays:
                with ui.card().classes('w-full p-6 hover:shadow-md transition-shadow'):
                    # Header with title and category
                    with ui.row().classes('w-full justify-between items-center mb-4'):
                        with ui.column().classes('gap-1'):
                            ui.label(essay['title']).classes('text-xl font-semibold')
                            if essay['category']:
                                ui.label(essay['category']).classes('text-sm text-green-600')
                        ui.button(icon='delete', on_click=lambda essay_id=essay['id']: delete_essay(essay_id, user_id)).classes('text-red-600')
                    
                    # Content area with proper formatting
                    with ui.card().classes('w-full p-4 bg-gray-50'):
                        ui.markdown(essay['content']).classes('prose max-w-none')
                    
                    # Footer with metadata
                    with ui.row().classes('w-full justify-end mt-2'):
                        ui.label(essay['created_at'].strftime('%Y-%m-%d %H:%M')).classes('text-xs text-gray-600')

    except Exception as e:
        ui.notify(f"Error loading essays: {str(e)}", color='negative')

def delete_flashcard(card_id, user_id):
    """Delete a flashcard"""
    try:
        cursor = db.connection.cursor()
        cursor.execute("DELETE FROM flashcards WHERE id = %s AND user_id = %s", (card_id, user_id))
        db.connection.commit()
        cursor.close()
        
        ui.notify('Formula/concept deleted', color='positive')
        load_flashcards(user_id)
    except Exception as e:
        ui.notify(f"Error deleting formula/concept: {str(e)}", color='negative')

def delete_essay(essay_id, user_id):
    """Delete an essay"""
    try:
        cursor = db.connection.cursor()
        cursor.execute("DELETE FROM essays WHERE id = %s AND user_id = %s", (essay_id, user_id))
        db.connection.commit()
        cursor.close()
        
        ui.notify('Study note deleted', color='positive')
        load_essays(user_id)
    except Exception as e:
        ui.notify(f"Error deleting note: {str(e)}", color='negative') 