import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Optional


class PastaWindow:
    def obter_pasta(self) -> Optional[Path]:
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)

        pasta = filedialog.askdirectory(
            title="Selecione a pasta para salvar as faturas",
            parent=root,
        )
        root.destroy()

        if pasta:
            return Path(pasta)
        return None
