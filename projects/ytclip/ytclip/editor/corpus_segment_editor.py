import math
from pathlib import Path
from typing import Generic, List, Literal, Tuple, TypeVar, TypedDict
from ytclip.paths import Paths
from ytclip.download.audio_processor import AudioProcessor, get_audio_processor
from ytclip.models.video_annotation import Segment, VideoAnnotation
from rich.console import Console
from rich.panel import Panel
from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl
import sounddevice as sd
import soundfile as sf
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

from ytclip.utils.time_tunning import decrement_digit, increment_digit

T = TypeVar("T")

class PaginationDict(TypedDict, Generic[T]):
  window_scroll: Tuple[int, int]
  page_size: int
  paginated_data: List[T]
  page: int
  total_pages: int
  idx: int
  
class StateDict(TypedDict):
  screen: Literal["videos", "segments", "tunning_times"]
  current_video: VideoAnnotation | None
  current_segment: Segment | None
  editing: Literal["start", "end"]
  editing_single_time: bool
  time_position: int
  audio_processor: AudioProcessor | None

class CorpusSegmentEditor:
    def __init__(self, videos: List[VideoAnnotation], paths: Paths):
        self.paths = paths
        self.is_first_load: bool = True
        self.video_pagination: PaginationDict[VideoAnnotation] = {
            "window_scroll": (0, 10),
            "page_size": 10,
            "paginated_data": [],
            "page": 0,
            "total_pages": 0,
            "idx": 0
        }
        self.seg_pagination: PaginationDict[Segment] = {
            "window_scroll": (0, 10),
            "page_size": 10,
            "paginated_data": [],
            "page": 0,
            "total_pages": 0,
            "idx": 0
        }
        self.state: StateDict = {
            "screen": "videos",
            "current_video": None,
            "current_segment": None,
            "editing": None,
            "editing_single_time": False,
            "time_position": 5,
            "audio_processor": None
        }
        self.data = videos
        self.console = Console()
        self.kb = KeyBindings()
        self._init_navigation(self.kb)
        
    def run(self):
        dummy_layout = Layout(Window(FormattedTextControl(
          self._get_default_layout()
        )))
        app = Application(
            key_bindings=self.kb,
            layout=dummy_layout,
            # full_screen=True,
        )
        app.run()
        
    def _get_default_layout(self):
        lines = ""
        lines += "🎤 KINAI - ASR Maya\n"
        lines += "press ENTER to begin\n"
        return lines
    
    def draw(self):
        self.draw_menu()
        if self.state["screen"] == "videos":
            self.draw_videos()
        elif self.state["screen"] == "segments":
            self.draw_segments()
        elif self.state["screen"] == "tunning_times":
            self.draw_tunning_times()

    def draw_videos(self):
        self.console.print("↑ ↓ navegar | ENTER seleccionar")
        self.paginate(self.data, self.video_pagination)
        init, _ = self.video_pagination["window_scroll"]
        
        self.console.print(Panel.fit(
            f"[bold]Page:[/bold] { self.video_pagination["page"] } / { self.video_pagination["total_pages"] }",
            title="Videos",
            border_style="cyan"
        ))
        
        for i, video in enumerate(self.video_pagination["paginated_data"]):
            index = init + i
            prefix = "👉 " if index == self.video_pagination["idx"] else "   "
            self.console.print(f"{prefix}{video.title}")
            
    def draw_segments(self):
        current_video = self.state["current_video"]
        
        if not current_video:
          self.state["screen"] = "videos"
          self.draw()
          return
        
        self.paginate(current_video.segments, self.seg_pagination)
        init, _ = self.seg_pagination["window_scroll"]
        
        self.console.print("↑ ↓ navegar | ENTER seleccionar | <- -> ")
        self.console.print(Panel.fit(
            f"[bold]Title:[/bold] {current_video.title}\n[bold]URL:[/bold] {current_video.url}\n"
            f"[bold]Segments:[/bold] {len(current_video.segments)}\npage: { self.seg_pagination["page"] } / { self.seg_pagination["total_pages"] }",
            title="Video Info",
            border_style="cyan"
        ))
        for i, segment in enumerate(self.seg_pagination["paginated_data"]):
            index = init + i
            prefix = "👉 " if index == self.seg_pagination["idx"] else "   "
            self.console.print(f"{prefix}{segment.maya} ---- {segment.start} - {segment.end}")
            
    def draw_tunning_times(self):
        current_video = self.state["current_video"]
        if not current_video:
          self.state["screen"] = "videos"
          self.draw()
          return
        
        self.paginate(current_video.segments, self.seg_pagination)
        
        self.console.print("↑ ↓ navegar | ENTER seleccionar | <- -> ")
        self.console.print(Panel.fit(
            f"[bold]Title:[/bold] {current_video.title}\n[bold]URL:[/bold] {current_video.url}\n"
            f"[bold]Segments:[/bold] {len(current_video.segments)}\npage: { self.seg_pagination["page"] } / { self.seg_pagination["total_pages"] }",
            title="Video Info",
            border_style="cyan"
        ))
        
        for segment in self.seg_pagination["paginated_data"]:
            is_current_segment = self.state["current_segment"].utt_id == segment.utt_id
            is_start_editing = is_current_segment and self.state["editing"] == "start"
            is_end_editing = is_current_segment and self.state["editing"] == "end"
            
            segment_mayan = f"{"👉 [bold cyan]" if is_current_segment else "   "}{segment.maya}{"[/bold cyan]" if is_current_segment else ""}"
            
            time_start = segment.start
            time_end = segment.end
            
            if is_current_segment and self.state["editing_single_time"]:
                if self.state["editing"] == "start":
                    pos = self.state["time_position"]
                    time_start = self.highlight_digit(time_start, pos)
                if self.state["editing"] == "end":
                    pos = self.state["time_position"]
                    time_end = self.highlight_digit(time_end, pos)
              
            time_start = f"{"[underline green]" if is_start_editing else ""}{time_start}{"[/underline green]" if is_start_editing else ""}"
            time_end = f"{"[underline green]" if is_end_editing else ""}{time_end}{"[/underline green]" if is_end_editing else ""}"
            
            self.console.print(f"{segment_mayan} ---- {time_start} - {time_end}")
        
    def draw_menu(self):
        self.console.clear()
        self.console.print(Panel.fit(
            "[bold cyan]🎤 KINAI - ASR Maya[/bold cyan]",
            border_style="blue"
        ))
        
    def audio_viewer(self, path):
        data, sr = sf.read(path)
    
        if data.ndim > 1:  # stereo → mono para simplificar
            data = data.mean(axis=1)
    
        duration = len(data) / sr
        time = np.linspace(0, duration, len(data))
    
        fig, ax = plt.subplots(figsize=(10, 4))
        plt.subplots_adjust(bottom=0.25)
    
        ax.plot(time, data)
        ax.set_title("Audio Waveform")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude")
    
        # -------- botones ----------
        ax_play = plt.axes([0.2, 0.1, 0.1, 0.075])
        ax_stop = plt.axes([0.35, 0.1, 0.1, 0.075])
        
        # ----------- BUTTONS ---------------
    
        btn_play = Button(ax_play, "Play")
        btn_stop = Button(ax_stop, "Stop")
    
        def play(_):
            sd.stop()
            sd.play(data, sr)
    
        def stop(_):
            sd.stop()
    
        btn_play.on_clicked(play)
        btn_stop.on_clicked(stop)
        
        def on_key(event):
            if event.key == "escape":
                sd.stop()
                plt.close(fig)
            elif event.key == "1":
                play(None)
            elif event.key == "2":
                stop(None)
    
        fig.canvas.mpl_connect("key_press_event", on_key)
    
        plt.show()
        
    def show_audio(self, path):
        self.audio_viewer(path)
    
    def _init_navigation(self, kb: KeyBindings):
        @kb.add("up")
        def _(event):
            if self.state["screen"] == "videos":
                self.video_pagination["idx"] = (self.video_pagination["idx"] - 1) % len(self.data)
            elif self.state["screen"] == "segments":
                segs = self.state["current_video"].segments
                self.seg_pagination["idx"] = (self.seg_pagination["idx"] - 1) % len(segs)
            elif self.state["screen"] == "tunning_times":
                if self.state["editing"] == "start" and self.state["editing_single_time"]:
                    time = self.state["current_segment"].start_td
                    time_position = self.state["time_position"]
                    self.state["current_segment"].start_td = increment_digit(time, time_position)
                elif self.state["editing"] == "end" and self.state["editing_single_time"]:
                    time = self.state["current_segment"].end_td
                    time_position = self.state["time_position"]
                    self.state["current_segment"].end_td = increment_digit(time, time_position)
            self.draw()

        @kb.add("down")
        def _(event):
            if self.state["screen"] == "videos":
                self.video_pagination["idx"] = (self.video_pagination["idx"] + 1) % len(self.data)
            elif self.state["screen"] == "segments":
                segs = self.state["current_video"].segments
                self.seg_pagination["idx"] = (self.seg_pagination["idx"] + 1) % len(segs)
            elif self.state["screen"] == "tunning_times":
                if self.state["editing"] == "start" and self.state["editing_single_time"]:
                    time = self.state["current_segment"].start_td
                    time_position = self.state["time_position"]
                    self.state["current_segment"].start_td = decrement_digit(time, time_position)
                elif self.state["editing"] == "end" and self.state["editing_single_time"]:
                    time = self.state["current_segment"].end_td
                    time_position = self.state["time_position"]
                    self.state["current_segment"].end_td = decrement_digit(time, time_position)
            
            self.draw()
            
        @kb.add("right")
        def _(event):
           if self.state["screen"] == "tunning_times":
                if self.state["editing"] == "start" and not self.state["editing_single_time"]:
                    self.state["editing"] = "end"
                
                elif self.state["editing_single_time"] and self.state["time_position"] < 8:
                    self.state["time_position"] += 1
           self.draw()
        
        @kb.add("left")
        def _(event):
            if self.state["screen"] == "tunning_times":
                if self.state["editing"] == "end" and not self.state["editing_single_time"]:
                    self.state["editing"] = "start"
                    
                elif self.state["editing_single_time"] and self.state["time_position"] > 0:
                    self.state["time_position"] -= 1
                    
            self.draw()

        @kb.add("enter")
        def _(event):
            if self.is_first_load:
                self.is_first_load = False
            elif not self.is_first_load and self.state["screen"] == "videos":
                video = self.data[self.video_pagination["idx"]]
                self.state["current_video"] = video
                self.state["audio_processor"] = get_audio_processor(video, self.paths)
                self.seg_pagination["idx"] = 0
                self.state["screen"] = "segments"
            elif not self.is_first_load and self.state["screen"] == "segments":
              seg_id = self.seg_pagination["idx"]
              segment = self.state["current_video"].segments[seg_id]
              self.state["current_segment"] = segment
              self.state["screen"] = "tunning_times"
              self.state["editing"] = "start"
            elif not self.is_first_load and self.state["screen"] == "tunning_times":
              self.state["editing_single_time"] = True
                
            self.draw()

        @kb.add("backspace")
        def _(event):
            if self.state["screen"] == "segments":
                self.state["screen"] = "videos"
                self.seg_pagination = {
                   "window_scroll": (0, 10),
                   "page_size": 10,
                   "paginated_data": [],
                   "page": 0,
                   "total_pages": 0,
                   "idx": 0
                }
            elif self.state["screen"] == "tunning_times":
                if self.state["editing_single_time"]:
                  self.state["editing_single_time"] = False
                  self.state["time_position"] = 5
                else:
                  self.state["screen"] = "segments"
                  self.state["current_segment"] = None
                
            self.draw()
            
        @kb.add("m")
        def _(event):
          print("clicking m...")
            
        @kb.add("space")
        def _(event):
            if self.state["screen"] == "tunning_times" and self.state["audio_processor"]:
              segment = self.state["current_segment"]
              self.state["audio_processor"].segment_audio(segment, force=True)
              audio_path = self.paths.segments_folder / f"{segment.utt_id}.wav"
              self.show_audio(audio_path)

        @kb.add("c-c")
        def _(event):
            event.app.exit()
        
    def paginate(self, items: List, pagination: dict):
        if not items:
          pagination["paginated_data"] = []
          return
          
        current_index = pagination["idx"]
        init, end = pagination["window_scroll"]
        data = pagination["paginated_data"]
        
        if not data or not (init <= current_index < end):
           page = current_index // pagination["page_size"] + 1
           init = pagination["page_size"] * (page - 1)
           end = min(init + pagination["page_size"], len(items))
           visible_items = []
           for i in range(init, end):
               visible_items.append(items[i])
           pagination["paginated_data"] = visible_items
           pagination["window_scroll"] = (init, end)
           pagination["page"] = page
           pagination["total_pages"] = math.ceil(len(items) / pagination["page_size"])

    def highlight_digit(self, time_str: str, digit_pos: int) -> str:
        char_map = [0, 1, 3, 4, 6, 7, 9, 10, 11]

        if digit_pos < 0 or digit_pos >= len(char_map):
            return time_str

        chars = list(time_str)
        idx = char_map[digit_pos]

        chars[idx] = f"[bold red]{chars[idx]}[/bold red]"
        return "".join(chars)