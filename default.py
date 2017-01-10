# -*- coding: utf-8 -*-
#------------------------------------------------------------
# XBMC entry point
#------------------------------------------------------------

import os
import sys

from core import config
from core import logger

logger.info("mitele.default init...")

librerias = xbmc.translatePath( os.path.join( config.get_runtime_path(), 'lib' ) )
sys.path.append (librerias)

from platformcode import launcher

if sys.argv[1] == "1":
    # Esto solo se ejecuta la primera vez que entramos en el plugin
    launcher.start()

launcher.run()