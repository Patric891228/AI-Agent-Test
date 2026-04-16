class StubTranslator:
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        return f"[{source_lang}->{target_lang}] translated: {text}"
