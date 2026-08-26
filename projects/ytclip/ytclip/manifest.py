import json
from pathlib import Path
import pandas as pd
from ytclip.models.video_annotation import VideoAnnotation
from ytclip.utils.format_json import format_json

class SpokenDictionaryManifest:
  def __init__(self, segment_file: Path):
    with open(segment_file, encoding="utf-8") as f:
      data = json.load(f)
    self.videos = [VideoAnnotation.from_dict(video) for video in data]
    
  def save_segments_json(self, output_file: Path):
    output_file.parent.mkdir(parents=True, exist_ok=True)
    print("Generating segments...")
    data = [video.to_dict() for video in self.videos]
    file_path = str(output_file)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    format_json(path=file_path)

  def save_manifest_csv(self, output_file: Path):
    output_file.parent.mkdir(parents=True, exist_ok=True)
    print("Generating manifest...")

    df = self.get_segment_file_to_df()

    file_path = str(output_file)
    df.to_csv(file_path, index=False, encoding="utf-8")

  def get_segment_file_to_df(self):
    rows = []
    
    for video in self.videos:
      for seg in video.segments:
        rows.append({
          "utt_id": seg.utt_id,
          "maya": seg.maya,
          "spanish": seg.spanish,
          "spk_id": seg.spk_id,
          "start": seg.start,
          "end": seg.end,
        })

    return pd.DataFrame(rows)
    