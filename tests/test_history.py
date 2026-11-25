import numpy as np
from core.history import ImageHistory

def test_undo_redo_and_branching():
    history=ImageHistory(limit=3)
    a=np.zeros((4,4),dtype=np.uint8); b=np.ones((4,4),dtype=np.uint8)
    history.push("a",a); history.push("b",b)
    assert np.array_equal(history.undo(),a)
    assert np.array_equal(history.redo(),b)
    history.undo(); history.push("new",a)
    assert history.redo() is None
