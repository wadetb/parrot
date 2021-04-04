import os
import web

# When running Flask in development mode, the reloader respawns the root process as a
# subprocess to manage reloading. We only want to fire up the background thread and other
# systems running as that subprocess, not the root process.
if 'WERKZEUG_RUN_MAIN' in os.environ:
    import sm
    sm.start()

web.serve()
