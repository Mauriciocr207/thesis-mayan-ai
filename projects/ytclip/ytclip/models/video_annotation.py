from dataclasses import dataclass
from datetime import timedelta
from typing import List

DIGITS_BASES = [
    3_600 * 10 * 1_000,     # Decenas de horas
    3_600 * 1_000,          # Horas
    60 * 10 * 1_000,        # Decenas de minutos
    60 * 1_000,             # Minutos
    10 * 1_000,             # Decenas de segundos
    1 * 1_000,              # Segundos
    100,                    # Centenas de milisegundos
    10,                     # Decenas de milisegundos
    1                       # Milisegundos
]

@dataclass
class Segment:
    utt_id: str
    maya: str
    spanish: str
    start: str  # HH:MM:SS
    end: str    # HH:MM:SS
    spk_id: str = ""
    
    def __post_init__(self):
      self.start = self._timedelta_to_str(self._str_to_timedelta(self.start))
      self.end = self._timedelta_to_str(self._str_to_timedelta(self.end))
      self._start_td = self._str_to_timedelta(self.start)
      self._end_td = self._str_to_timedelta(self.end)

    @property
    def start_td(self):
      return self._start_td
    
    @property
    def end_td(self):
      return self._end_td
    
    @start_td.setter
    def start_td(self, time: timedelta):
        time = max(timedelta(0), time)
        
        if time > self._end_td:
            time = self._end_td
        
        self._start_td = time
        self.start = self._timedelta_to_str(time)
    
    @end_td.setter
    def end_td(self, time: timedelta):
        time = max(timedelta(0), time)
        
        if time < self._start_td:
            time = self._start_td
            
        self._end_td = time
        self.end = self._timedelta_to_str(time)
      
    def _str_to_timedelta(self, time_str: str) -> timedelta:
        time = time_str.split(".")
        ms = int(time[1] if len(time) > 1 else "000")
        hours, mins, secs = map(int, time[0].split(":"))
        return timedelta(
            hours=hours,
            minutes=mins,
            seconds=secs,
            milliseconds=ms
        )
        
    def _timedelta_to_str(self, td: timedelta) -> str:
        total_ms = int(td.total_seconds() * 1000)

        hours = total_ms // (3600 * 1000)
        total_ms %= (3600 * 1000)

        minutes = total_ms // (60 * 1000)
        total_ms %= (60 * 1000)

        seconds = total_ms // 1000
        milliseconds = total_ms % 1000

        return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"
    
    def to_dict(self):
        return {
            "utt_id": self.utt_id,
            "maya": self.maya,
            "spanish": self.spanish,
            "start": self.start,
            "end": self.end,
            "spk_id": self.spk_id,
        }

class Metadata:
    age: str

@dataclass
class VideoAnnotation:
    url: str
    title: str
    segments: List[Segment]
    metadata: Metadata
    
    @staticmethod
    def from_dict(data) -> "VideoAnnotation":
        vid_id = VideoAnnotation._get_url_id(data["url"])
        segments = []
        for idx, seg_dict in enumerate(data["segments"]):
            # Honra un utt_id explícito (ej. spk-based) si viene en el JSON;
            # si no, cae al id derivado de la url + posición.
            utt_id = seg_dict.get("utt_id") or f"{vid_id}_{idx:04}"
            segments.append(Segment(
                utt_id=utt_id,
                maya=seg_dict["maya"],
                spanish=seg_dict["spanish"],
                start=seg_dict["start"],
                end=seg_dict["end"],
                spk_id=seg_dict.get("spk_id", ""),
            ))
        
        return VideoAnnotation(
            url=data["url"],
            title=data["title"],
            segments=segments,
            metadata=data.get("metadata") or {}
        )
    
    @staticmethod
    def _get_url_id(url: str):
      import re
      if url.startswith("http"):
        raw = url.split("v=")[1]
      else:
        # local path: use parent_stem (e.g. recordings/ana/grabacion_1.wav -> ana_grabacion_1)
        from pathlib import Path
        p = Path(url)
        raw = f"{p.parent.name}_{p.stem}"
      # Kaldi no permite espacios en utt_id / recording_id; normalizamos.
      return re.sub(r"[^A-Za-z0-9_-]+", "_", raw).strip("_")
    
    def to_dict(self):
        return {
            "url": self.url,
            "title": self.title,
            "segments": [s.to_dict() for s in self.segments],
            "metadata": self.metadata or {},
        }
