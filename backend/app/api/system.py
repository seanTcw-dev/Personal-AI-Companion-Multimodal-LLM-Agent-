from fastapi import APIRouter, HTTPException
import subprocess
import sys
import os

router = APIRouter()

# ====== System Audio Control via ctypes (Windows keybd_event) ======

import ctypes

VK_VOLUME_MUTE  = 0xAD
KEYEVENTF_KEYUP = 0x0002

def _read_actual_mute_state() -> bool:
    """Read the actual Windows system mute state via PowerShell inline C#."""
    ps_script = r"""
Add-Type -TypeDefinition @'
using System; using System.Runtime.InteropServices;
[ComImport, Guid("BCDE0395-E52F-467C-8E3D-C4579291692E")] class MMDevCo {}
[Guid("A95664D2-9614-4F35-A746-DE8DB63617E6"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IMMDevEn { void _1(); void GetDef(int f, int r, [MarshalAs(UnmanagedType.Interface)] out object p); }
[Guid("D666063F-1587-4E43-81F1-B948E807363F"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IMMDev { void Act([MarshalAs(UnmanagedType.LPStruct)] Guid id, int c, IntPtr p, [MarshalAs(UnmanagedType.Interface)] out object o); }
[Guid("5CDF2C82-841E-4546-9722-0CF74078229A"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IAEV { void _1();void _2();void _3();void _4();void _5();void _6();void _7();void _8();void _9();void _10();void _11();void _12();
    void GetMute([MarshalAs(UnmanagedType.Bool)] out bool m); }
public class AudioState {
    public static bool GetMute() {
        var e = (IMMDevEn)new MMDevCo(); object d;
        e.GetDef(0, 1, out d);
        var iid = new Guid("5CDF2C82-841E-4546-9722-0CF74078229A"); object v;
        ((IMMDev)d).Act(iid, 23, IntPtr.Zero, out v);
        bool m; ((IAEV)v).GetMute(out m); return m;
    }
}
'@ -ErrorAction SilentlyContinue
[AudioState]::GetMute()
"""
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
            capture_output=True, text=True, timeout=8
        )
        return result.stdout.strip().lower() == "true"
    except Exception:
        return False  # Assume unmuted if we can't read

# Initialize with the actual system state at startup
_system_muted: bool = _read_actual_mute_state()
print(f"🔊 System mute state at startup: {'MUTED' if _system_muted else 'UNMUTED'}")

VK_CONTROL = 0x11
VK_W       = 0x57

def _press_mute_key():
    """Send VK_VOLUME_MUTE as a true system-wide keypress via Windows keybd_event API."""
    ctypes.windll.user32.keybd_event(VK_VOLUME_MUTE, 0, 0, 0)
    ctypes.windll.user32.keybd_event(VK_VOLUME_MUTE, 0, KEYEVENTF_KEYUP, 0)

def _press_ctrl_w():
    """Send Ctrl+W to close the active browser tab."""
    import time
    time.sleep(0.2)  # Brief delay so the browser regains focus after the API call
    ctypes.windll.user32.keybd_event(VK_CONTROL, 0, 0, 0)           # Ctrl down
    ctypes.windll.user32.keybd_event(VK_W, 0, 0, 0)                 # W down
    ctypes.windll.user32.keybd_event(VK_W, 0, KEYEVENTF_KEYUP, 0)  # W up
    ctypes.windll.user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)  # Ctrl up

VK_LWIN = 0x5B
VK_SNAPSHOT = 0x2C

def _press_print_screen():
    """Send Win + PrintScreen to capture a full screen image and save it to the Pictures/Screenshots folder."""
    import time
    time.sleep(0.2)
    ctypes.windll.user32.keybd_event(VK_LWIN, 0, 0, 0)               # Win down
    ctypes.windll.user32.keybd_event(VK_SNAPSHOT, 0, 0, 0)           # PrtScn down
    ctypes.windll.user32.keybd_event(VK_SNAPSHOT, 0, KEYEVENTF_KEYUP, 0) # PrtScn up
    ctypes.windll.user32.keybd_event(VK_LWIN, 0, KEYEVENTF_KEYUP, 0)     # Win up

@router.post("/close-tab")
async def close_browser_tab():
    """Send Ctrl+W keystroke to close the active browser tab."""
    import asyncio
    try:
        await asyncio.get_event_loop().run_in_executor(None, _press_ctrl_w)
        return {"status": "ok", "message": "Ctrl+W sent — browser tab should close"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send close key: {str(e)}")

@router.post("/screenshot")
async def take_screenshot():
    """Simulate Win+PrintScreen and copy the resulting file to user_files/pdf_uploads."""
    import asyncio
    import glob
    import shutil
    try:
        await asyncio.get_event_loop().run_in_executor(None, _press_print_screen)
        
        # Give Windows 1.5 seconds to flush the screenshot to disk
        await asyncio.sleep(1.5)
        
        user_profile = os.environ.get('USERPROFILE', '')
        pictures_dir = os.path.join(user_profile, 'Pictures', 'Screenshots')
        
        if os.path.exists(pictures_dir):
            list_of_files = glob.glob(os.path.join(pictures_dir, '*.png'))
            if list_of_files:
                # Get the most recently created screenshot
                latest_file = max(list_of_files, key=os.path.getctime)
                
                # Setup destination directory in backend/user_files/pdf_uploads
                current_dir = os.path.dirname(os.path.abspath(__file__))
                backend_dir = os.path.dirname(os.path.dirname(current_dir))
                dest_dir = os.path.join(backend_dir, "user_files", "pdf_uploads")
                os.makedirs(dest_dir, exist_ok=True)
                
                # Generate new unique filename
                import time
                dest_file = os.path.join(dest_dir, f"screenshot_{int(time.time())}.png")
                shutil.copy2(latest_file, dest_file)
                
                return {"status": "ok", "message": f"Screenshot copied to {dest_file}"}

        return {"status": "ok", "message": "Screenshot captured via Win+PrtScn"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to copy screenshot: {str(e)}")

@router.post("/toggle-mute")
async def toggle_system_mute():
    """Toggle system mute key + track state server-side."""
    global _system_muted
    import asyncio
    try:
        await asyncio.get_event_loop().run_in_executor(None, _press_mute_key)
        _system_muted = not _system_muted
        return {
            "status": "ok",
            "muted": _system_muted,
            "message": f"System audio {'muted' if _system_muted else 'unmuted'}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to toggle mute: {str(e)}")

@router.get("/mute-status")
async def get_mute_status():
    """Return the server-tracked mute state."""
    return {"muted": _system_muted}


PET_PROCESS = None

@router.post("/desktop-mode")
async def start_desktop_pet():
    global PET_PROCESS
    
    if PET_PROCESS is not None:
        if PET_PROCESS.poll() is None:
            return {"status": "already_running", "pid": PET_PROCESS.pid}
        else:
            PET_PROCESS = None

    try:
        # Determine python executable path
        python_exe = sys.executable
        # Get absolute path to backend directory (3 levels up from this file: app/api/system.py -> app/api -> app -> backend)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(os.path.dirname(current_dir))
        script_path = os.path.join(backend_dir, "pet_process.py")
        
        # Launch the process
        # We use Popen to let it run in background
        PET_PROCESS = subprocess.Popen([python_exe, script_path])
        
        return {"status": "started", "pid": PET_PROCESS.pid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/desktop-pet/stop")
async def stop_desktop_pet():
    global PET_PROCESS
    
    if PET_PROCESS is None:
        return {"status": "not_running"}
        
    try:
        PET_PROCESS.terminate()
        PET_PROCESS.wait(timeout=2)
    except subprocess.TimeoutExpired:
        PET_PROCESS.kill()
    except Exception as e:
        # If process already gone
        pass
        
    PET_PROCESS = None
    return {"status": "stopped"}
