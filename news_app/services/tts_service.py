# news_app/services/tts_service.py

import os
import logging
from io import BytesIO
from typing import Optional

# Microsoft Azure Cognitive Services Speech (Primary - High Quality Neural Voices)
try:
    import azure.cognitiveservices.speech as speechsdk
    AZURE_TTS_AVAILABLE = True
except ImportError:
    AZURE_TTS_AVAILABLE = False
    speechsdk = None

# Fallback to gTTS if Azure is not available
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    gTTS = None

logger = logging.getLogger(__name__)


def _create_azure_tts_audio(text: str, lang: str = 'vi') -> Optional[bytes]:
    """
    Create high-quality audio using Microsoft Azure Cognitive Services Speech with Neural voices.
    Requires AZURE_TTS_KEY and AZURE_TTS_REGION environment variables to be set.
    """
    if not AZURE_TTS_AVAILABLE:
        logger.warning("Azure Cognitive Services Speech not available. Install: pip install azure-cognitiveservices-speech")
        return None
    
    # Check for authentication
    azure_key = os.getenv('AZURE_TTS_KEY')
    azure_region = os.getenv('AZURE_TTS_REGION')
    
    if not azure_key:
        logger.warning("AZURE_TTS_KEY not set. Falling back to gTTS.")
        return None
    
    if not azure_region:
        logger.warning("AZURE_TTS_REGION not set. Falling back to gTTS.")
        return None
    
    try:
        # Initialize the speech config
        speech_config = speechsdk.SpeechConfig(subscription=azure_key, region=azure_region)
        
        # Voice selection based on language with high-quality Neural voices
        if lang == 'vi':
            # Premium Vietnamese Neural voices - you can customize this
            # Available options: vi-VN-HoaiMyNeural (Female), vi-VN-NamMinhNeural (Male)
            speech_config.speech_synthesis_voice_name = "vi-VN-HoaiMyNeural"  # Female Neural voice
        else:
            # Fallback for other languages (English)
            speech_config.speech_synthesis_voice_name = "en-US-AriaNeural"  # English Neural voice
        
        # Set output format to MP3 for web compatibility
        speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Audio16Khz128KBitRateMonoMp3)
        
        # Create synthesizer with in-memory output (no audio config needed)
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
        
        # Perform the text-to-speech synthesis
        result = synthesizer.speak_text_async(text).get()
        
        # Check result
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            logger.info(f"✅ Generated high-quality TTS audio using Azure Neural Voice ({speech_config.speech_synthesis_voice_name})")
            return result.audio_data
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            logger.error(f"❌ Azure TTS synthesis canceled: {cancellation_details.reason}")
            if cancellation_details.error_details:
                logger.error(f"❌ Azure TTS error details: {cancellation_details.error_details}")
            return None
        else:
            logger.error(f"❌ Azure TTS synthesis failed with reason: {result.reason}")
            return None
        
    except Exception as e:
        logger.error(f"❌ Azure TTS failed: {e}")
        return None


def _create_gtts_audio_fallback(text: str, lang: str = 'vi') -> Optional[bytes]:
    """
    Fallback to gTTS if Azure TTS is not available.
    """
    if not GTTS_AVAILABLE:
        logger.error("Neither Azure TTS nor gTTS is available!")
        return None
        
    try:
        logger.info("🔄 Using gTTS fallback (lower quality)")
        tts = gTTS(text=text, lang=lang, slow=False)
        
        audio_fp = BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        
        return audio_fp.getvalue()
    except Exception as e:
        logger.error(f"❌ gTTS fallback failed: {e}")
        return None


def text_to_audio_bytes(text: str, lang: str = 'vi') -> Optional[BytesIO]:
    """
    Legacy function for backward compatibility.
    Returns BytesIO object for existing code compatibility.
    """
    audio_bytes = create_audio_from_text(text, lang)
    if audio_bytes:
        buf = BytesIO(audio_bytes)
        return buf
    return None


def create_audio_from_text(text: str, lang: str = 'vi') -> Optional[bytes]:
    """
    Create high-quality audio from text using Microsoft Azure Neural TTS as primary,
    with gTTS as fallback. Returns raw audio bytes for file storage.
    
    Args:
        text: The text to convert to speech
        lang: Language code ('vi' for Vietnamese, 'en' for English)
    
    Returns:
        bytes: Raw MP3 audio data, or None if generation failed
    """
    if not text or not text.strip():
        logger.warning("Empty text provided for TTS generation")
        return None
    
    # Truncate very long text to avoid API limits and costs
    if len(text) > 5000:
        text = text[:5000] + "..."
        logger.info("Truncated text to 5000 characters for TTS")
    
    # Try Azure TTS first (high quality Neural voices)
    audio_bytes = _create_azure_tts_audio(text, lang)
    if audio_bytes:
        return audio_bytes
    
    # Fallback to gTTS
    logger.warning("Falling back to gTTS due to Azure TTS unavailability")
    audio_bytes = _create_gtts_audio_fallback(text, lang)
    if audio_bytes:
        return audio_bytes
    
    logger.error("All TTS methods failed!")
    return None


def get_available_vietnamese_voices():
    """
    Get list of available Vietnamese Neural voices for Azure TTS.
    Call this function to see voice options for customization.
    """
    return {
        "vi-VN-HoaiMyNeural": "Female Vietnamese Neural Voice - Natural and expressive",
        "vi-VN-NamMinhNeural": "Male Vietnamese Neural Voice - Clear and professional"
    }