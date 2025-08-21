"""
ZENO Flask Web Application
Modern web interface for the AI assistant
"""
import asyncio
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from pathlib import Path

from config import Config
from core.assistant import ZenoAssistant

# Initialize Flask app
app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

# Initialize ZENO assistant
zeno = None

def get_zeno():
    """Get or create ZENO assistant instance"""
    global zeno
    if zeno is None:
        zeno = ZenoAssistant()
    return zeno

@app.route('/')
def index():
    """Main interface page"""
    assistant = get_zeno()
    status = assistant.get_status()
    return render_template('index.html', status=status, config=Config)

@app.route('/api/status')
def api_status():
    """Get assistant status"""
    assistant = get_zeno()
    status = assistant.get_status()
    return jsonify(status)

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """Process chat message"""
    try:
        data = request.get_json()
        user_input = data.get('message', '').strip()
        
        if not user_input:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get assistant and process input
        assistant = get_zeno()
        
        # Run async function in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response = loop.run_until_complete(
                assistant.process_input(user_input, "text")
            )
        finally:
            loop.close()
        
        return jsonify(response)
        
    except Exception as e:
        logging.error(f"Chat API error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/mode', methods=['POST'])
def api_set_mode():
    """Set assistant mode"""
    try:
        data = request.get_json()
        mode = data.get('mode')
        
        if not mode:
            return jsonify({'error': 'Mode is required'}), 400
        
        assistant = get_zeno()
        success = assistant.set_mode(mode)
        
        if success:
            return jsonify({'success': True, 'mode': mode})
        else:
            return jsonify({'error': 'Invalid mode'}), 400
            
    except Exception as e:
        logging.error(f"Mode API error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/speech/start', methods=['POST'])
def api_start_speech():
    """Start speech recognition"""
    try:
        assistant = get_zeno()
        
        def speech_callback(text):
            # Store recognized text in session for retrieval
            session['last_speech'] = text
        
        success = assistant.speech.start_listening(speech_callback)
        
        return jsonify({'success': success})
        
    except Exception as e:
        logging.error(f"Speech start API error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/speech/stop', methods=['POST'])
def api_stop_speech():
    """Stop speech recognition"""
    try:
        assistant = get_zeno()
        assistant.speech.stop_listening()
        
        # Return any recognized text
        recognized_text = session.pop('last_speech', '')
        
        return jsonify({'success': True, 'text': recognized_text})
        
    except Exception as e:
        logging.error(f"Speech stop API error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/speech/speak', methods=['POST'])
def api_speak():
    """Convert text to speech"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        assistant = get_zeno()
        assistant.speech.speak(text, async_speech=True)
        
        return jsonify({'success': True})
        
    except Exception as e:
        logging.error(f"Speak API error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/memory/summary')
def api_memory_summary():
    """Get memory summary"""
    try:
        assistant = get_zeno()
        if not assistant.memory:
            return jsonify({'error': 'Memory not enabled'}), 400
        
        summary = assistant.memory.get_conversation_summary()
        return jsonify(summary)
        
    except Exception as e:
        logging.error(f"Memory API error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/skills')
def api_skills():
    """Get available skills information"""
    try:
        from skills.skill_manager import SkillManager
        skill_manager = SkillManager()
        skills = skill_manager.get_available_skills()
        return jsonify(skills)
        
    except Exception as e:
        logging.error(f"Skills API error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/models/refresh', methods=['POST'])
def api_refresh_models():
    """Refresh available AI models"""
    try:
        assistant = get_zeno()
        assistant.ai_handler.refresh_models()
        
        model_info = assistant.ai_handler.get_model_info()
        return jsonify(model_info)
        
    except Exception as e:
        logging.error(f"Model refresh API error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Ensure directories exist
    Config.ensure_directories()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the app
    print(f"\n🤖 ZENO Personal AI Assistant")
    print(f"🌐 Starting web interface at http://{Config.FLASK_HOST}:{Config.FLASK_PORT}")
    print(f"📁 Data directory: {Config.DATA_DIR}")
    print(f"🎯 Current mode: {Config.DEFAULT_MODE}")
    print(f"🎤 Wake word: '{Config.WAKE_WORD}'")
    
    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG
    )