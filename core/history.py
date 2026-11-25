"""Undo/redo history for non-destructive image operations."""
from dataclasses import dataclass
import numpy as np

@dataclass
class HistoryEntry:
    label: str
    image: np.ndarray

class ImageHistory:
    def __init__(self, limit=30):
        self.limit=max(1,int(limit)); self.entries=[]; self.index=-1
    def push(self,label,image):
        if self.index < len(self.entries)-1: self.entries=self.entries[:self.index+1]
        self.entries.append(HistoryEntry(label,np.array(image,copy=True)))
        self.entries=self.entries[-self.limit:]; self.index=len(self.entries)-1
    def undo(self):
        if self.index <= 0: return None
        self.index-=1; return np.array(self.entries[self.index].image,copy=True)
    def redo(self):
        if self.index >= len(self.entries)-1: return None
        self.index+=1; return np.array(self.entries[self.index].image,copy=True)
    @property
    def can_undo(self): return self.index > 0
    @property
    def can_redo(self): return 0 <= self.index < len(self.entries)-1
