"""Punto de entrada del programa y de su ensayo reproducible."""
import argparse
import tkinter as tk
from tkinter import messagebox

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--self-check',metavar='CARPETA')
    parser.add_argument('--screenshots',action='store_true')
    args=parser.parse_args()
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError,OSError): pass
    root=tk.Tk()
    if args.self_check:
        from santarosa.selfcheck import execute
        try: execute(root,args.self_check,args.screenshots)
        except Exception:
            import traceback
            from pathlib import Path
            Path(args.self_check).mkdir(parents=True,exist_ok=True)
            Path(args.self_check,'error.txt').write_text(traceback.format_exc(),encoding='utf-8')
            root.destroy();raise
    else:
        from santarosa.ui import Desktop
        Desktop(root)
        root.mainloop()

if __name__=='__main__': main()
