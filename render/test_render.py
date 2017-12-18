# -*- coding: utf-8 -*-

from render.document import OutputDocumentSimple
from render.render_data import SAMPLE_HIERARCHY
from render.writers import *

WriterFactory.register_writer('media', MediaWriter)
WriterFactory.register_writer('para', GenericWriter)
WriterFactory.register_writer('para_block', ParaBlockWriter)
WriterFactory.register_writer('speech', SpeechWriter)
WriterFactory.register_writer('text', SimpleTextWriter)

BaseItemWriter.write(out, SAMPLE_HIERARCHY)

print(out.text())
