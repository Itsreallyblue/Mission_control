import re

_voice_import_error = None

try:
    import sounddevice as sd
    import whisper
except Exception as exc:
    sd = None
    whisper = None
    _voice_import_error = exc
else:
    # Use the ME6S microphone (Windows WASAPI)
    sd.default.device = (2, None)

_model = None


def voice_support_available():
    return sd is not None and whisper is not None


def _load_model():
    if whisper is None:
        message = (
            "Voice support requires the optional packages 'whisper' and 'sounddevice'. "
            "Install them with pip to enable voice commands."
        )
        if _voice_import_error is not None:
            message += f"\nUnderlying import error: {_voice_import_error}"
        raise ImportError(message)
    global _model
    if _model is None:
        print("Loading voice model...")
        _model = whisper.load_model("base")
    return _model


def listen(duration=3, language="en"):
    if sd is None:
        raise ImportError(
            "Voice capture requires the optional package 'sounddevice'. "
            "Install it with pip to enable voice commands."
        )
    model = _load_model()
    sample_rate = 16000
    print("\n🎙️ Listening...")
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="float32"
    )
    sd.wait()
    audio = audio.flatten()
    print("Processing...")
    result = model.transcribe(audio, language=language, fp16=False)
    command = result["text"].strip().lower()
    print(f"Recognised: {command}")
    return command


def _normalize_text(command):
    return (command or "").strip().lower()


def _contains_wake_word(command, wake_word):
    command = _normalize_text(command)
    wake_word = _normalize_text(wake_word)
    if not wake_word:
        return True
    if wake_word in command:
        return True
    for prefix in ("hey ", "ok ", "okay "):
        if command.startswith(prefix + wake_word):
            return True
    return False


def _strip_wake_word(command, wake_word):
    command = _normalize_text(command)
    wake_word = _normalize_text(wake_word)
    for prefix in ("hey ", "ok ", "okay "):
        prefix_wake = prefix + wake_word
        if command.startswith(prefix_wake):
            return command[len(prefix_wake):].strip()
    if wake_word and wake_word in command:
        return command.replace(wake_word, "").strip()
    return command


def wait_for_wake_word(wake_word="orion"):
    print(f"\nSay the wake word '{wake_word}' to activate voice commands.")
    while True:
        command = listen()
        if _contains_wake_word(command, wake_word):
            stripped = _strip_wake_word(command, wake_word)
            if stripped:
                return stripped
            print("Speak your command after the wake word.")
        else:
            print("Wake word not detected. Please say the wake word to continue.")


def get_voice_command(prompt=None, wake_word="orion"):
    if prompt:
        print(prompt)
    return wait_for_wake_word(wake_word)


def parse_yes_no(command):
    normalized = _normalize_text(command)
    if normalized in {"y", "yes", "yeah", "sure", "affirmative", "correct", "true", "sure thing"}:
        return True
    if normalized in {"n", "no", "nope", "negative", "nah"}:
        return False
    if normalized.startswith("y"):
        return True
    if normalized.startswith("n"):
        return False
    return None


def parse_int(command):
    normalized = _normalize_text(command)
    if not normalized:
        return None
    digits = re.findall(r"\d+", normalized)
    if digits:
        return int(digits[0])

    word_to_num = {
        "zero": 0,
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
        "eleven": 11,
        "twelve": 12,
        "thirteen": 13,
        "fourteen": 14,
        "fifteen": 15,
        "sixteen": 16,
        "seventeen": 17,
        "eighteen": 18,
        "nineteen": 19,
        "twenty": 20,
    }
    for word, value in word_to_num.items():
        if word in normalized:
            return value
    return None
