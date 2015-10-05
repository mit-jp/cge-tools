from pelican import signals
from pelican.readers import MarkdownReader


class MDLReader(MarkdownReader):

    def read(self, source_path):
        """Parse content and metadata of markdown files"""
        content, metadata = super(MDLReader, self).read(source_path)
        print(metadata)
        return content, metadata


def add_reader(readers):
    readers.reader_classes['md'] = MDLReader


# This is how pelican works.
def register():
    signals.readers_init.connect(add_reader)
