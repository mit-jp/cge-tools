from pelican import signals
from pelican.readers import MarkdownReader

# Expect a viz directory under content with the python methods in it.
from content import viz


class VizReader(MarkdownReader):

    def render_viz(self, viz_name):
        try:
            render_function = getattr(viz, 'render_' + viz_name)
            data = render_function()
        except AttributeError as e:
            print(e)
            data = '<p>Error: Viz named <code>%s</code> is not available</p>' % viz_name
        return data

    def read(self, source_path):
        "Parses content and handles viz parameter"

        content, metadata = super(VizReader, self).read(source_path)

        if 'viz' in metadata.keys():
            metadata['viz_rendered'] = self.render_viz(metadata['viz'])
        if 'viz_extra' in metadata.keys():
            metadata['viz_extra_rendered'] = self.render_viz(metadata['viz_extra'])

        return content, metadata


def add_reader(readers):
    readers.reader_classes['md'] = VizReader


# This is how pelican works.
def register():
    signals.readers_init.connect(add_reader)
