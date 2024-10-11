import google.generativeai as gemini

class GeminiFileStorage:

    @staticmethod
    def upload(file):
        return gemini.upload_file(path=file)
