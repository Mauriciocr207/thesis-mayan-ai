import re
from typing import Optional

from phonemizer import phonemize as _espeak_phonemize
from phonemizer.separator import Separator

_ES_SEPARATOR = Separator(phone=" ", word="|", syllable="")

# Mapa IPA (salida de espeak) → etiquetas Kaldi-friendly. Reutiliza las
# etiquetas del inventario maya cuando el fonema es equivalente y añade
# nuevas (F, G, NY, NG, LY, RR) para sonidos propios del español.
# Diptongos se expanden a dos fonemas separados por espacio.
IPA_TO_KALDI: dict[str, str] = {
    # Vocales
    "a": "A", "e": "E", "i": "I", "o": "O", "u": "U",
    "ɛ": "E", "ɔ": "O",
    # Diptongos
    "aɪ": "A I", "eɪ": "E I", "oɪ": "O I", "aʊ": "A U", "eʊ": "E U",
    # Oclusivas
    "p": "P", "b": "B", "t": "T", "d": "D", "k": "K", "ɡ": "G", "g": "G",
    # Fricativas / aproximantes (alófonos de b/d/g → mismo fonema)
    "β": "B", "ð": "D", "ɣ": "G",
    "f": "F", "s": "S", "θ": "S",
    "x": "J", "h": "J",
    "ʃ": "X", "ʝ": "Y",
    # Nasales
    "m": "M", "n": "N", "ɲ": "NY", "ŋ": "NG",
    # Líquidas
    "l": "L", "ʎ": "LY",
    "r": "RR", "ɾ": "R",
    # Aproximantes
    "w": "W", "j": "Y",
    # Africadas
    "tʃ": "CH", "ts": "TS",
    # Oclusiva glotal
    "ʔ": "GLOT",
}

# Diacríticos IPA que descartamos antes del lookup (acento primario,
# secundario y marca de longitud — no los distinguimos a nivel fonémico).
_IPA_DIACRITICS = set("ˈˌːˑ")


def ipa_phone_to_kaldi(phone: str) -> Optional[list[str]]:
    """Mapea un token IPA de espeak a una lista de etiquetas Kaldi.
    Devuelve `None` si no hay mapeo conocido."""
    clean = "".join(ch for ch in phone if ch not in _IPA_DIACRITICS)
    mapped = IPA_TO_KALDI.get(clean)
    return mapped.split() if mapped is not None else None


# Caracteres que se recortan en los extremos de cada palabra.
# Nota: `'` NO se recorta porque es fonema en maya (glotal).
_BOUNDARY_PUNCT = '.,;:!¡?¿()[]{}"«»“”‘’—–-…\t\n\r'

# Reglas de ortografía colonial → moderna (Yucatec).
# Orden importa: proteger dígrafos antes de reescribir letras simples.
_COLONIAL_RULES = [
    (re.compile(r"ch'"), "\x01"),      # proteger ch'
    (re.compile(r"ch"), "\x02"),        # proteger ch
    (re.compile(r"dz"), "ts"),          # dz → ts
    (re.compile(r"qu([ei])"), r"k\1"),  # que/qui → ke/ki
    (re.compile(r"c"), "k"),            # c → k (en cualquier otra posición)
    (re.compile(r"z"), "s"),            # z → s
    (re.compile(r"\x01"), "ch'"),
    (re.compile(r"\x02"), "ch"),
]


def modernize_orthography(word: str) -> str:
    """Convierte ortografía colonial Yucatec a la moderna."""
    out = word
    for pattern, repl in _COLONIAL_RULES:
        out = pattern.sub(repl, out)
    return out


def normalize_word(word: str) -> str:
    """Normaliza una palabra: lowercase y strip de puntuación en extremos."""
    return word.lower().strip(_BOUNDARY_PUNCT)


class MayaPhonemeTokenizer:
    def __init__(self):
        self.g2p_dict = {
            # Rearticuladas
            "a'a": "A_RG",
            "e'e": "E_RG",
            "i'i": "I_RG",
            "o'o": "O_RG",
            "u'u": "U_RG",

            # Largas tono alto
            "áa": "AA_H",
            "ée": "EE_H",
            "íi": "II_H",
            "óo": "OO_H",
            "úu": "UU_H",

            # Largas tono bajo
            "aa": "AA_L",
            "ee": "EE_L",
            "ii": "II_L",
            "oo": "OO_L",
            "uu": "UU_L",

            # Glotalizadas vocales
            "a'": "A_G",
            "e'": "E_G",
            "i'": "I_G",
            "o'": "O_G",
            "u'": "U_G",

            # Consonantes complejas
            "ch'": "CH_G",
            "ts'": "TS_G",
            "ch": "CH",
            "ts": "TS",

            # Consonantes simples
            "b": "B",
            "j": "J",
            "k'": "K_G",
            "k": "K",
            "l": "L",
            "m": "M",
            "n": "N",
            "p'": "P_G",
            "p": "P",
            "r": "R",
            "s": "S",
            "t'": "T_G",
            "t": "T",
            "w": "W",
            "x": "X",
            "y": "Y",

            # Vocales cortas
            "a": "A",
            "e": "E",
            "i": "I",
            "o": "O",
            "u": "U",

            # Préstamos
            "d": "D",

            # Glotal aislado (p.ej. word-final tras rearticulada: `chi'i'`).
            "'": "GLOT",
        }

    def _tokenize_word(self, word: str) -> list[str]:
        """Convierte una palabra en lista de fonemas. Lanza ValueError si hay símbolo OOV."""
        aux = word.lower()
        phonemes: list[str] = []
        while aux:
            matched = False
            for j in (3, 2, 1):
                if j > len(aux):
                    continue
                p = aux[:j]
                if p in self.g2p_dict:
                    phonemes.append(self.g2p_dict[p])
                    aux = aux[j:]
                    matched = True
                    break
            if not matched:
                raise ValueError(
                    f"Símbolo no soportado '{aux[0]}' en palabra '{word}'"
                )
        return phonemes

    def _try_tokenize_word(self, word: str) -> Optional[list[str]]:
        """Versión tolerante: devuelve None si la palabra tiene símbolos OOV."""
        try:
            return self._tokenize_word(word)
        except ValueError:
            return None

    def tokenize(self, phrase: str) -> str:
        """Tokeniza una frase. Si una palabra no es fonemizable por el
        tokenizer maya (p.ej. préstamos del español), cae a `phonemizer`
        con backend espeak y lengua española, y remapea cada símbolo IPA
        de vuelta al inventario Kaldi con `IPA_TO_KALDI`. Devuelve los
        fonemas en el mismo formato: separados por espacio, con `SIL`
        entre palabras.
        """
        words = phrase.lower().split()
        tokens: list[str] = []
        for w in words:
            phones = self._try_tokenize_word(w)
            if phones is None:
                es = _espeak_phonemize(
                    w,
                    language="es",
                    backend="espeak",
                    separator=_ES_SEPARATOR,
                    strip=True,
                    njobs=1,
                )
                phones = []
                for ipa in es.replace("|", " ").split():
                    mapped = ipa_phone_to_kaldi(ipa)
                    if mapped is not None:
                        phones.extend(mapped)
            tokens.append(" ".join(phones))
        return " SIL ".join(tokens)
    
    @property
    def phones(self):
        ipa_to_kaldi = set(IPA_TO_KALDI.values())
        phones = set(self.g2p_dict.values())

        nonsilence_lines = sorted(phones | ipa_to_kaldi)

        nonsilence_lines = [phone for phone in nonsilence_lines if ' ' not in phone]

        return nonsilence_lines
