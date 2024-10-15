import google.generativeai as gemini

def upload_file(name, mime_type, file):
    return gemini.upload_file(
        path=file,
        name=name,
        mime_type=mime_type
    )