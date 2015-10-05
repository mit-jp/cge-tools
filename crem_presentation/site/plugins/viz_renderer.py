from pelican import signals
from pelican.readers import MarkdownReader

# Expect a viz directory under content with the python methods in it.
from content import viz


class VizReader(MarkdownReader):

    def read(self, source_path):
        "Parses content and handles viz parameter"

        content, metadata = super(VizReader, self).read(source_path)

        if metadata['viz']:
            viz_name = metadata['viz']
            try:
                render_function = getattr(viz, 'render_' + viz_name)
                metadata['viz_rendered'] = render_function()
            except AttributeError:
                metadata['viz_rendered'] = '<p>Error: Viz named <code>%s</code> is not available</p>' % viz_name

        return content, metadata


def add_reader(readers):
    readers.reader_classes['md'] = VizReader


# This is how pelican works.
def register():
    signals.readers_init.connect(add_reader)
